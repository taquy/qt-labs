import React, { useEffect } from 'react';
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
  updateGraph,
  saveSettings
} from '../store/sagas/stockGraphSaga';
import {
  setSelectedStocks,
  clearChartData,
} from '../store/slices/stockGraphSlice';

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
  selectedMetric, 
  metrics, 
  handleMetricChange, 
  loading, 
  setGraphData 
}) => {
  const dispatch = useDispatch();
  
  // Select state from Redux store
  const {
    availableStocks,
    selectedStocks,
    chartData,
    error
  } = useSelector(state => state.stockGraph);

  // Initial data loading
  useEffect(() => {
    dispatch(fetchAvailableStocks());
    dispatch(fetchSettings());
  }, [dispatch]);

  // Update parent's graph data when chartData changes
  useEffect(() => {
    if (chartData) {
      setGraphData(chartData);
    }
  }, [chartData, setGraphData]);

  const handleStockChange = (event, newValue) => {
    dispatch(setSelectedStocks(newValue));
    if (newValue.length > 0) {
      dispatch(updateGraph(newValue.map(stock => stock.symbol), selectedMetric));
      dispatch(saveSettings(newValue, selectedMetric));
    } else {
      dispatch(clearChartData());
      setGraphData(null);
      dispatch(saveSettings([], selectedMetric));
    }
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
            onChange={handleMetricChange}
          >
            {metrics.map((metric) => (
              <MenuItem key={metric} value={metric}>
                {metric}
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
            <Bar data={chartData.data} options={chartData.options} />
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