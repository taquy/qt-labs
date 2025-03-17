import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  CircularProgress,
  Autocomplete,
  TextField
} from '@mui/material';
import Plot from 'react-plotly.js';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { API_ENDPOINTS } from '../config';

// Configure axios to include credentials
axios.defaults.withCredentials = true;
axios.defaults.headers.common['Content-Type'] = 'application/json';

const Dashboard = () => {
  const [stocks, setStocks] = useState([]);
  const [selectedStocks, setSelectedStocks] = useState([]);
  const [selectedMetric, setSelectedMetric] = useState('Price');
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [inputValue] = useState('');
  const navigate = useNavigate();

  const metrics = ['Price', 'MarketCap', 'EPS', 'P/E', 'P/B'];

  const fetchStocks = useCallback(async () => {
    try {
      setLoading(true);
      const response = await axios.get(API_ENDPOINTS.stocks, {
        withCredentials: true
      });
      setStocks(response.data.stocks);
    } catch (err) {
      if (err.response?.status === 401) {
        // Unauthorized - redirect to login
        localStorage.removeItem('token');
        localStorage.removeItem('isLoggedIn');
        navigate('/login');
      } else {
        setError('Failed to fetch stocks');
      }
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  useEffect(() => {
    // Check if user is logged in and has token
    const token = localStorage.getItem('token');
    if (!token || !localStorage.getItem('isLoggedIn')) {
      navigate('/login');
      return;
    }
    // Set authorization header
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    fetchStocks();
  }, [navigate, fetchStocks]);

  // Function to highlight matching text
  const highlightMatch = (text, search) => {
    if (!search) return text;
    const parts = text.split(new RegExp(`(${search})`, 'gi'));
    return parts.map((part, index) => 
      part.toLowerCase() === search.toLowerCase() ? 
        <span key={index} style={{ backgroundColor: '#fff59d' }}>{part}</span> : part
    );
  };

  const handleMetricChange = (event) => {
    setSelectedMetric(event.target.value);
  };

  const updateGraph = async () => {
    if (selectedStocks.length === 0) return;

    setLoading(true);
    try {
      const response = await axios.post(API_ENDPOINTS.updateGraph, {
        stocks: selectedStocks,
        metric: selectedMetric
      }, {
        withCredentials: true
      });
      setGraphData(JSON.parse(response.data));
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('isLoggedIn');
        navigate('/login');
      } else {
        setError('Failed to update graph');
      }
    }
    setLoading(false);
  };

  const handleDownloadStockList = async () => {
    try {
      await axios.post(API_ENDPOINTS.downloadStockList, {}, {
        withCredentials: true
      });
      fetchStocks();
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('isLoggedIn');
        navigate('/login');
      } else {
        setError('Failed to download stock list');
      }
    }
  };

  const handleFetchStockData = async () => {
    try {
      await axios.post(API_ENDPOINTS.fetchStockData, {}, {
        withCredentials: true
      });
      fetchStocks();
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('isLoggedIn');
        navigate('/login');
      } else {
        setError('Failed to fetch stock data');
      }
    }
  };

  const handleLogout = async () => {
    try {
      await axios.post(API_ENDPOINTS.logout, {}, {
        withCredentials: true
      });
      localStorage.removeItem('token');
      localStorage.removeItem('isLoggedIn');
      delete axios.defaults.headers.common['Authorization'];
      navigate('/login');
    } catch (err) {
      setError('Failed to logout');
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Stock Analysis Dashboard
        </Typography>
        <Button variant="outlined" color="error" onClick={handleLogout}>
          Logout
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Box sx={{ mb: 2 }}>
              <Button
                variant="contained"
                color="primary"
                onClick={handleDownloadStockList}
                sx={{ mr: 2 }}
              >
                Download Stock List
              </Button>
              <Button
                variant="contained"
                color="success"
                onClick={handleFetchStockData}
              >
                Fetch Stock Data
              </Button>
            </Box>

            <Typography variant="subtitle1" gutterBottom>
              Select Stocks:
            </Typography>
            <FormControl sx={{ minWidth: 300, mb: 2 }}>
              <Autocomplete
                multiple
                options={stocks}
                getOptionLabel={(option) => `${option.symbol} - ${option.name}`}
                value={selectedStocks.map(symbol => stocks.find(s => s.symbol === symbol) || { symbol, name: '' })}
                onChange={(event, newValue) => {
                  setSelectedStocks(newValue.map(stock => stock.symbol));
                }}
                filterOptions={(options, { inputValue }) => {
                  const input = inputValue.toLowerCase();
                  return options.filter(option => 
                    option.symbol.toLowerCase().includes(input) || 
                    option.name.toLowerCase().includes(input)
                  );
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    variant="outlined"
                    label="Search Stocks"
                    placeholder={selectedStocks.length === 0 ? "Type to search..." : ""}
                  />
                )}
                renderOption={(props, option) => (
                  <Box component="li" {...props}>
                    <Box sx={{ display: 'flex', flexDirection: 'column' }}>
                      <Typography variant="body1">
                        {highlightMatch(option.symbol, inputValue)}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {highlightMatch(option.name, inputValue)}
                      </Typography>
                    </Box>
                  </Box>
                )}
                renderTags={(tagValue, getTagProps) =>
                  tagValue.map((option, index) => {
                    const { key, ...chipProps } = getTagProps({ index });
                    return (
                      <Chip
                        key={key}
                        label={option.symbol}
                        {...chipProps}
                        size="small"
                      />
                    );
                  })
                }
                sx={{ width: 300 }}
                ListboxProps={{
                  style: {
                    maxHeight: '250px'
                  }
                }}
              />
            </FormControl>

            <FormControl sx={{ minWidth: 200, mb: 2, ml: 2 }}>
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

            <Button
              variant="contained"
              onClick={updateGraph}
              disabled={selectedStocks.length === 0 || loading}
            >
              Update Graph
            </Button>
          </Paper>
        </Grid>

        <Grid item xs={12}>
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
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard; 