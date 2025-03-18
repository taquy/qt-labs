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
import StockSelectionTable from './StockSelectionTable';
import { fetchStocks } from '../store/sagas/stockGraphSaga';
import { useDispatch, useSelector } from 'react-redux';
import { logout } from '../store/sagas/stockGraphSaga';


// Configure axios to include credentials
axios.defaults.withCredentials = true;
axios.defaults.headers.common['Content-Type'] = 'application/json';

const Dashboard = () => {
  const { error, fetchingData} = useSelector(state => state.stockGraph);
  const navigate = useNavigate();
  const dispatch = useDispatch();

  useEffect(() => {
    // Check if user is logged in and has token
    const token = localStorage.getItem('token');
    if (!token || !localStorage.getItem('isLoggedIn')) {
      navigate('/login');
      return;
    }
    fetchStocks();
  }, [navigate]);

  // Function to highlight matching text
  const highlightMatch = (text, search) => {
    if (!search) return text;
    const parts = text.split(new RegExp(`(${search})`, 'gi'));
    return parts.map((part, index) =>
      part.toLowerCase() === search.toLowerCase() ? 
        <span key={index} style={{ backgroundColor: '#fff59d' }}>{part}</span> : part
    );
  };

  const handleLogout = () => {
    dispatch(logout());
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

      <Grid item xs={12}>
        <StockSelector/>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
          <Box sx={{ 
            mt: 3,
            mb: 3,
            p: 2,
            bgcolor: 'background.paper',
            borderRadius: 1,
            boxShadow: 1
          }}>
            <StockSelectionTable />
          </Box>
        </Grid>
    </Container>
  );
};

export default Dashboard; 