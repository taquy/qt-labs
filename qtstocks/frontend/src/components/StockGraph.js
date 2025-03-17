import React, { useState, useEffect } from 'react';
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
import Plot from 'react-plotly.js';
import axios from 'axios';
import { API_ENDPOINTS } from '../config';
import { format } from 'date-fns';

const StockGraph = ({ 
  selectedMetric, 
  metrics, 
  handleMetricChange, 
  loading, 
  graphData,
  setGraphData 
}) => {
  const [availableStocks, setAvailableStocks] = useState([]);
  const [selectedStocks, setSelectedStocks] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchStocksWithStats = async () => {
      try {
        const response = await axios.get(API_ENDPOINTS.stocksWithStats, {
          withCredentials: true
        });
        setAvailableStocks(response.data.stocks);
      } catch (err) {
        setError('Failed to fetch stocks with stats');
      }
    };

    fetchStocksWithStats();
  }, []);

  const handleStockChange = (event, newValue) => {
    setSelectedStocks(newValue);
    // Trigger graph update with new selection
    updateGraph(newValue.map(stock => stock.symbol), selectedMetric);
  };

  const updateGraph = async (symbols, metric) => {
    if (symbols.length === 0) {
      setGraphData(null);
      return;
    }

    try {
      const response = await axios.post(API_ENDPOINTS.updateGraph, {
        stocks: symbols,
        metric: metric
      }, {
        withCredentials: true
      });
      setGraphData(JSON.parse(response.data));
    } catch (err) {
      setError('Failed to update graph');
      setGraphData(null);
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
            renderOption={(props, option) => (
              <Tooltip 
                title={`Last updated: ${format(new Date(option.last_updated), 'PPpp')}`}
                placement="right"
              >
                <Box component="li" {...props}>
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
            )}
            renderTags={(tagValue, getTagProps) =>
              tagValue.map((option, index) => {
                const { key, ...chipProps } = getTagProps({ index });
                return (
                  <Tooltip 
                    key={key}
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
            onChange={(e) => {
              handleMetricChange(e);
              if (selectedStocks.length > 0) {
                updateGraph(selectedStocks.map(stock => stock.symbol), e.target.value);
              }
            }}
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
        ) : graphData ? (
          <Plot
            data={graphData.data}
            layout={graphData.layout}
            config={{ responsive: true }}
          />
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