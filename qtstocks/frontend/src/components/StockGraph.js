import React, { useEffect, useState, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Paper,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Autocomplete,
  TextField,
  Chip,
  Tooltip,
  Button,
  Stack
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
} from '../store/sagas/stockGraphSaga';

import {
  fetchSettings,
  saveSettings
} from '../store/sagas/settingsSaga';
import jsPDF from 'jspdf';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  ChartTooltip,
  Legend
);

const StockGraph = () => {
  const dispatch = useDispatch();
  const [selectedMetric, setSelectedMetric] = useState('market_cap');
  const [chartData, setChartData] = useState();
  const [currentChartData, setCurrentChartData] = useState();
  const [selectedStocks, setSelectedStocks] = useState([]);
  const chartRef = useRef(null);

  // Select state from Redux store
  const {
    availableStocks,
    error,
    metrics
  } = useSelector(state => state.stockGraph);

  const { settings } = useSelector(state => state.settings);

  // Initial data loading
  useEffect(() => {
    dispatch(fetchSettings());
    dispatch(fetchAvailableStocks());
  }, [dispatch]);

  useEffect(() => {
    if (!selectedStocks) return;

    const allCharts = {};
    // Generate colors for each bar
    for (let metric of Object.keys(metrics)) {
      let dataPoints = selectedStocks.map(stock => stock[metric]);
      let labels = selectedStocks.map(stock => stock.symbol);
      let colors = labels.map((_, index) =>
        `hsl(${(index * 360/ labels.length)}, 70%, 50%)`
      );
      // Sort labels and dataPoints together based on dataPoints values
      const sortedIndices = dataPoints
        .map((value, index) => ({ value, index }))
        .sort((a, b) => b.value - a.value)
        .map(item => item.index);

      labels = sortedIndices.map(i => labels[i]);
      dataPoints = sortedIndices.map(i => dataPoints[i]);
      colors = sortedIndices.map(i => colors[i]);
      const newChartData = {
        labels,
        datasets: [{
          label: metrics[metric],
          data: dataPoints,
          borderWidth: 1,
          backgroundColor: colors,
          borderColor: colors.map(color => color.replace('50%', '40%')),
          borderRadius: 5,
          hoverBackgroundColor: colors.map(color => color.replace('50%', '60%')),
        }],
        title: {
          display: true,
          text: `Comparison of ${metrics[metric]} across selected stocks`,
          font: { size: 16 }
        }
      }
      allCharts[metric] = newChartData;
    }
    setChartData(allCharts);
    setCurrentChartData(allCharts[selectedMetric]);
  }, [selectedStocks, selectedMetric, metrics]);

  // Load settings when available
  useEffect(() => {
    if (settings?.stockGraph && availableStocks.length > 0) {
      const { selectedSymbols, selectedMetric: savedMetric } = settings.stockGraph;
      // Find and set selected stocks
      const selectedStocksData = availableStocks.filter(stock =>
        selectedSymbols.includes(stock.symbol)
      )
      if (selectedStocksData.length > 0) {
        setSelectedStocks(selectedStocksData);
      }
      setSelectedMetric(savedMetric);
    }
  }, [settings, availableStocks, dispatch]);

  const handleStockChange = (event, newValue) => {
    setSelectedStocks(newValue);
    if (newValue.length > 0) {
      dispatch(saveSettings(newValue, selectedMetric));
    } else {
      setChartData(null);
      dispatch(saveSettings([], selectedMetric));
    }
  };

  const onMetricChange = (event) => {
    const newMetric = event.target.value;
    setSelectedMetric(newMetric);
    dispatch(saveSettings(selectedStocks, newMetric));
  };

  const exportToPDF = async () => {
    try {
      if (!chartRef.current) return;

      const chart = chartRef.current;
      const canvas = chart.canvas;

      // Create PDF
      const pdf = new jsPDF('p', 'mm', 'a4');
      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();
      const margin = 20;
      const contentWidth = pageWidth - (margin * 2);

      // Calculate dimensions to maintain aspect ratio
      const imgWidth = contentWidth;
      const imgHeight = (canvas.height * contentWidth) / canvas.width;

      // Add title
      pdf.setFontSize(16);
      pdf.text(chartData.title.text, margin, margin);

      // Add the chart image
      pdf.addImage(
        canvas.toDataURL('image/png'),
        'PNG',
        margin,
        margin + 10,
        imgWidth,
        imgHeight
      );

      // Add footer with metric information
      pdf.setFontSize(10);
      pdf.text(`Metric: ${chartData.datasets[0].label}`, margin, pageHeight - margin);
      pdf.text(`Generated on: ${new Date().toLocaleString()}`, margin, pageHeight - margin + 5);

      // Save the PDF
      pdf.save('stock-chart.pdf');
    } catch (error) {
      console.error('Error exporting PDF:', error);
    }
  };

  if (error) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="body1" color="error">
          {error}
        </Typography>
      </Box>
    );
  }

  if (!currentChartData || Object.keys(currentChartData).length === 0) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="body1" color="text.secondary">
          No data available. Please select stocks to view their charts.
        </Typography>
      </Box>
    );
  }

  return (
    <Paper sx={{ p: 2, mt: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          Stock Comparison Graph
        </Typography>
        <Stack direction="row" spacing={2} alignItems="center">
          <Button
            variant="contained"
            color="primary"
            onClick={exportToPDF}
            disabled={!currentChartData || Object.keys(currentChartData).length === 0}
          >
            Export PDF
          </Button>
        </Stack>
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

      <Paper sx={{ p: 2 }}>
        {currentChartData ? (
          <Box sx={{ height: 500, width: '100%' }}>
            <Bar 
              ref={chartRef}
              data={currentChartData} 
              options={{
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                  duration: 750,
                  easing: 'easeInOutQuart'
                },
                plugins: {
                  legend: { display: false },
                  title: currentChartData.title
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    title: {
                      display: true,
                      text: currentChartData.metric,
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