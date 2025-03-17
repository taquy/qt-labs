import React, { useState, useEffect } from 'react';
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
  CircularProgress
} from '@mui/material';
import Plot from 'react-plotly.js';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
  const [stocks, setStocks] = useState([]);
  const [selectedStocks, setSelectedStocks] = useState([]);
  const [selectedMetric, setSelectedMetric] = useState('Price');
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const metrics = ['Price', 'MarketCap', 'EPS', 'P/E', 'P/B'];

  useEffect(() => {
    fetchStocks();
  }, []);

  const fetchStocks = async () => {
    try {
      const response = await axios.get('/api/stocks');
      setStocks(response.data.stocks);
    } catch (err) {
      setError('Failed to fetch stocks');
    }
  };

  const handleStockSelect = (stock) => {
    if (selectedStocks.includes(stock)) {
      setSelectedStocks(selectedStocks.filter(s => s !== stock));
    } else {
      setSelectedStocks([...selectedStocks, stock]);
    }
  };

  const handleMetricChange = (event) => {
    setSelectedMetric(event.target.value);
  };

  const updateGraph = async () => {
    if (selectedStocks.length === 0) return;

    setLoading(true);
    try {
      const response = await axios.post('/api/update_graph', {
        stocks: selectedStocks,
        metric: selectedMetric
      });
      setGraphData(JSON.parse(response.data));
    } catch (err) {
      setError('Failed to update graph');
    }
    setLoading(false);
  };

  const handleDownloadStockList = async () => {
    try {
      await axios.post('/api/download_stock_list');
      fetchStocks();
    } catch (err) {
      setError('Failed to download stock list');
    }
  };

  const handleFetchStockData = async () => {
    try {
      await axios.post('/api/fetch_stock_data');
      fetchStocks();
    } catch (err) {
      setError('Failed to fetch stock data');
    }
  };

  const handleLogout = async () => {
    try {
      await axios.post('/api/logout');
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
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
              {stocks.map((stock) => (
                <Chip
                  key={stock.symbol}
                  label={stock.symbol}
                  onClick={() => handleStockSelect(stock.symbol)}
                  color={selectedStocks.includes(stock.symbol) ? 'primary' : 'default'}
                />
              ))}
            </Box>

            <FormControl sx={{ minWidth: 200, mb: 2 }}>
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