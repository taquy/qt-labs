import React, { useState, useEffect, useCallback } from 'react';
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
  Tooltip
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
import axios from 'axios';
import { API_ENDPOINTS } from '../config';
import { format } from 'date-fns';
import { useNavigate } from 'react-router-dom';

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
  const [availableStocks, setAvailableStocks] = useState([]);
  const [selectedStocks, setSelectedStocks] = useState([]);
  const [error, setError] = useState('');
  const [chartData, setChartData] = useState(null);
  const navigate = useNavigate();

  const updateGraph = useCallback(async (symbols, metric) => {
    if (symbols.length === 0) {
      setChartData(null);
      setGraphData(null);
      return;
    }

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }

      const response = await axios.post(API_ENDPOINTS.updateGraph, {
        stocks: symbols,
        metric: metric
      }, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const { data, metric: responseMetric } = response.data;

      // Generate colors for each bar
      const colors = data.map((_, index) => `hsl(${(index * 360/data.length)}, 70%, 50%)`);

      const chartConfig = {
        labels: data.map(item => item.symbol),
        datasets: [
          {
            label: responseMetric,
            data: data.map(item => item.value),
            backgroundColor: colors,
            borderColor: colors.map(color => color.replace('50%', '40%')),
            borderWidth: 1,
            borderRadius: 5,
            hoverBackgroundColor: colors.map(color => color.replace('50%', '60%')),
          }
        ]
      };

      const options = {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
          duration: 750,
          easing: 'easeInOutQuart'
        },
        plugins: {
          legend: {
            display: false
          },
          title: {
            display: true,
            text: `Comparison of ${responseMetric} across Selected Stocks`,
            font: {
              size: 16
            }
          },
          tooltip: {
            callbacks: {
              label: (context) => {
                const value = context.parsed.y;
                return `${responseMetric}: ${value.toFixed(2)}`;
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: responseMetric,
              font: {
                size: 14
              }
            },
            grid: {
              color: 'rgba(0, 0, 0, 0.1)'
            }
          },
          x: {
            title: {
              display: true,
              text: 'Stock Symbol',
              font: {
                size: 14
              }
            },
            grid: {
              display: false
            }
          }
        }
      };

      setChartData({ data: chartConfig, options });
      setGraphData({ data: chartConfig, options });
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('isLoggedIn');
        navigate('/login');
      } else {
        setError('Failed to update graph');
        setChartData(null);
        setGraphData(null);
      }
    }
  }, [navigate, setGraphData]);

  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          navigate('/login');
          return;
        }

        // Fetch available stocks first
        const stocksResponse = await axios.get(API_ENDPOINTS.stocksWithStats, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        setAvailableStocks(stocksResponse.data.stocks);

        // Then load settings
        const settingsResponse = await axios.get(API_ENDPOINTS.settings, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        const settings = settingsResponse.data.settings;
        if (settings?.stockGraph) {
          const { selectedSymbols, selectedMetric: savedMetric } = settings.stockGraph;
          if (selectedSymbols) {
            // Convert symbols back to full stock objects
            const savedStocks = selectedSymbols
              .map(symbol => stocksResponse.data.stocks.find(stock => stock.symbol === symbol))
              .filter(stock => stock !== undefined); // Filter out any symbols that don't exist anymore
            setSelectedStocks(savedStocks);

            // Update graph with saved settings
            if (savedStocks.length > 0) {
              updateGraph(savedStocks.map(stock => stock.symbol), savedMetric || selectedMetric);
            }
          }
          if (savedMetric && metrics.includes(savedMetric)) {
            handleMetricChange({ target: { value: savedMetric } });
          }
        }
      } catch (err) {
        if (err.response?.status === 401) {
          localStorage.removeItem('token');
          localStorage.removeItem('isLoggedIn');
          navigate('/login');
        } else {
          setError('Failed to initialize graph data');
          console.error('Failed to initialize:', err);
        }
      }
    };

    fetchInitialData();
    // Only run this effect once on mount
  }, [navigate]); // Remove dependencies that cause loops

  const saveSettings = async (stocks, metric) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }

      await axios.put(
        API_ENDPOINTS.updateSetting('stockGraph'),
        {
          value: {
            selectedSymbols: stocks.map(stock => stock.symbol),
            selectedMetric: metric
          }
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('isLoggedIn');
        navigate('/login');
      } else {
        console.error('Failed to save settings:', err);
      }
    }
  };

  const handleStockChange = (event, newValue) => {
    setSelectedStocks(newValue);
    updateGraph(newValue.map(stock => stock.symbol), selectedMetric);
    saveSettings(newValue, selectedMetric);
  };

  const handleMetricChangeWithSave = (e) => {
    handleMetricChange(e);
    if (selectedStocks.length > 0) {
      updateGraph(selectedStocks.map(stock => stock.symbol), e.target.value);
      saveSettings(selectedStocks, e.target.value);
    }
  };

  return (
    <Paper sx={{ p: 2, mt: 3 }}>
      <Typography variant="h6" gutterBottom>
        Stock Comparison Graph
      </Typography>
      
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
            onChange={handleMetricChangeWithSave}
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