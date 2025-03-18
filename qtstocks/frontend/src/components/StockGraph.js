import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Paper,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  CircularProgress,
  Autocomplete,
  TextField,
  Chip,
  Tooltip,
} from '@mui/material';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip as ChartTooltip,
  Legend
} from 'chart.js';
import { format } from 'date-fns';
import {
  fetchAvailableStocks,
  fetchSettings,
  saveSettings
} from '../store/sagas/stockGraphSaga';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  ChartTooltip,
  Legend
);

const StockGraph = ({ 
  loading,
  setGraphData
}) => {
  const dispatch = useDispatch();
  const [selectedMetric, setSelectedMetric] = useState('market_cap');
  const [chartData, setChartData] = useState();
  const [selectedStocks, setSelectedStocks] = useState([]);

  // Select state from Redux store
  const {
    availableStocks,
    error,
    settings,
    metrics
  } = useSelector(state => state.stockGraph);

  // Initial data loading
  useEffect(() => {
    dispatch(fetchAvailableStocks());
    dispatch(fetchSettings());
  }, [dispatch]);

  useEffect(() => {
    if (!selectedStocks) return;
    const labels = selectedStocks.map(stock => stock.symbol);
    const dataPoints = selectedStocks.map(stock => stock[selectedMetric]);

    // Generate colors for each bar
    const colors = labels.map((_, index) =>
      `hsl(${(index * 360/ labels.length)}, 70%, 50%)`
    );
    const newChartData = {
      labels,
      datasets: [{
        label: metrics[selectedMetric],
        data: dataPoints,
        borderWidth: 1,
        backgroundColor: colors,
        borderColor: colors.map(color => color.replace('50%', '40%')),
        borderRadius: 5,
        hoverBackgroundColor: colors.map(color => color.replace('50%', '60%')),
      }]
    }
    setChartData(newChartData);
  }, [selectedStocks, selectedMetric, metrics]);

  // Load settings when available
  useEffect(() => {
    if (settings?.stockGraph && availableStocks.length > 0) {
      const { selectedSymbols, selectedMetric: savedMetric } = settings.stockGraph;
      // Find and set selected stocks
      const selectedStocksData = availableStocks.filter(stock =>
        selectedSymbols.includes(stock.symbol)
      );
      if (selectedStocksData.length > 0) {
        setSelectedStocks(selectedStocksData);
      }
      if (savedMetric !== selectedMetric) {
        setSelectedMetric(savedMetric);
      };
    }
  }, [settings, selectedMetric, availableStocks, dispatch]);

  const handleStockChange = (event, newValue) => {
    setSelectedStocks(newValue);
    if (newValue.length > 0) {
      dispatch(saveSettings(newValue, selectedMetric));
    } else {
      setGraphData(null);
      dispatch(saveSettings([], selectedMetric));
    }
  };

  const onMetricChange = (event) => {
    const newMetric = event.target.value;
    setSelectedMetric(newMetric);
    dispatch(saveSettings(selectedStocks, newMetric));
  };

  return (
    <Paper sx={{ p: 2, mt: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          Stock Comparison Graph
        </Typography>
      </Box>
      
      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <FormControl sx={{ minWidth: 300 }}>
          <Autocomplete
            multiple
            options={availableStocks}
            getOptionLabel={(option) => `${option.symbol} - ${option.name}`}
            value={selectedStocks}
            onChange={handleStockChange}
            renderInput={(params) => (
              <TextField
                {...params}
                variant="outlined"
                label="Select Stocks with Data"
                placeholder={selectedStocks.length === 0 ? "Type to search..." : ""}
              />
            )}
            renderOption={(props, option) => {
              const { key, ...otherProps } = props;
              return (
                <Tooltip 
                  key={`tooltip-${option.symbol}`}
                  title={`Last updated: ${format(new Date(option.last_updated), 'PPpp')}`}
                  placement="right"
                >
                  <Box component="li" {...otherProps}>
                    <Box sx={{ display: 'flex', flexDirection: 'column' }}>
                      <Typography variant="body1">
                        {option.symbol}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {option.name}
                      </Typography>
                    </Box>
                  </Box>
                </Tooltip>
              );
            }}
            renderTags={(tagValue, getTagProps) =>
              tagValue.map((option, index) => {
                const { key, ...chipProps } = getTagProps({ index });
                return (
                  <Tooltip 
                    key={`tag-tooltip-${option.symbol}-${index}`}
                    title={`Last updated: ${format(new Date(option.last_updated), 'PPpp')}`}
                    placement="top"
                  >
                    <Chip
                      label={option.symbol}
                      {...chipProps}
                      size="small"
                    />
                  </Tooltip>
                );
              })
            }
          />
        </FormControl>

        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Metric</InputLabel>
          <Select
            value={selectedMetric}
            label="Metric"
            onChange={onMetricChange}
          >
            {Object.keys(metrics).map((metric) => (
              <MenuItem key={metric} value={metric}>
                {metrics[metric]}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}

      <Paper sx={{ p: 2 }}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
            <CircularProgress />
          </Box>
        ) : chartData ? (
          <Box sx={{ height: 500, width: '100%' }}>
            <Bar 
              data={chartData} 
              options={{
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                  duration: 750,
                  easing: 'easeInOutQuart'
                },
                // plugins: {
                //   legend: { display: false },
                //   title: {
                //     display: true,
                //     text: `Comparison of ${chartData.metric} across Selected Stocks`,
                //     font: { size: 16 }
                //   },
                //   tooltip: {
                //     callbacks: {
                //       label: (context) => {
                //         const value = context.parsed.y;
                //         return `${chartData.metric}: ${value.toFixed(2)}`;
                //       }
                //     }
                //   }
                // },
                scales: {
                  y: {
                    beginAtZero: true,
                    title: {
                      display: true,
                      text: chartData.metric,
                      font: { size: 14 }
                    },
                    grid: { color: 'rgba(0, 0, 0, 0.1)' }
                  },
                  x: {
                    title: {
                      display: true,
                      text: 'Stock Symbol',
                      font: { size: 14 }
                    },
                    grid: { display: false }
                  }
                }
              }} 
            />
          </Box>
        ) : (
          <Typography variant="body1" color="text.secondary" align="center">
            Select stocks and a metric to display the graph
          </Typography>
        )}
      </Paper>
    </Paper>
  );
};

export default StockGraph; 