import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Alert,
  Snackbar,
  Grid
} from '@mui/material';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { API_ENDPOINTS } from '../config';
import StockSelector from './StockSelector';
import StockGraph from './StockGraph';

// Configure axios to include credentials
axios.defaults.withCredentials = true;
axios.defaults.headers.common['Content-Type'] = 'application/json';

const getRequestConfig = () => ({
  headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
  withCredentials: true
});

const METRICS = [
  'Market Cap',
  'Price',
  'EPS',
  'P/E',
  'P/B'
];

const Dashboard = () => {
  const [stocks, setStocks] = useState([]);
  const [selectedStocks, setSelectedStocks] = useState([]);
  const [selectedMetric, setSelectedMetric] = useState(METRICS[0]);
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [inputValue] = useState('');
  const [fetchingData, setFetchingData] = useState(false);
  const [notification, setNotification] = useState({
    open: false,
    message: '',
    severity: 'success'
  });
  const navigate = useNavigate();

  const fetchStocks = useCallback(async () => {
    try {
      setLoading(true);
      const response = await axios.get(API_ENDPOINTS.stocks, getRequestConfig());
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

  const handleDownloadStockList = async () => {
    try {
      await axios.post(API_ENDPOINTS.downloadStockList, {}, getRequestConfig());
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
    if (selectedStocks.length === 0) {
      setError('Please select at least one stock to fetch data');
      return;
    }
    
    setFetchingData(true);
    try {
      await axios.post(API_ENDPOINTS.fetchStockData, {
        symbols: selectedStocks
      }, getRequestConfig());
      setError('');
      
      setNotification({
        open: true,
        message: `Successfully fetched data for stocks:\n${selectedStocks.join(', ')}`,
        severity: 'success'
      });
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('isLoggedIn');
        navigate('/login');
      } else {
        setError('Failed to fetch stock data');
        setNotification({
          open: true,
          message: 'Failed to fetch stock data',
          severity: 'error'
        });
      }
    } finally {
      setFetchingData(false);
    }
  };

  const handleLogout = async () => {
    try {
      await axios.post(API_ENDPOINTS.logout, {}, getRequestConfig());
      localStorage.removeItem('token');
      localStorage.removeItem('isLoggedIn');
      delete axios.defaults.headers.common['Authorization'];
      navigate('/login');
    } catch (err) {
      setError('Failed to logout');
    }
  };

  const handleCloseNotification = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    }
    setNotification(prev => ({ ...prev, open: false }));
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
          <StockSelector
            stocks={stocks}
            selectedStocks={selectedStocks}
            setSelectedStocks={setSelectedStocks}
            handleDownloadStockList={handleDownloadStockList}
            handleFetchStockData={handleFetchStockData}
            highlightMatch={highlightMatch}
            inputValue={inputValue}
            loading={fetchingData}
          />
        </Grid>
        <Grid item xs={12}>
          <StockGraph
            selectedMetric={selectedMetric}
            metrics={METRICS}
            handleMetricChange={handleMetricChange}
            loading={loading}
            graphData={graphData}
            setGraphData={setGraphData}
          />
        </Grid>
      </Grid>

      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={handleCloseNotification}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={handleCloseNotification} 
          severity={notification.severity}
          variant="filled"
          sx={{ 
            width: '100%',
            whiteSpace: 'pre-wrap',
            '& .MuiAlert-message': {
              maxWidth: '300px',
              overflowWrap: 'break-word'
            }
          }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default Dashboard; 