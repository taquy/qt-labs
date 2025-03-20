import React, { useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Alert,
  Grid
} from '@mui/material';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import StockSelector from './StockSelector';
import StockGraph from './StockGraph';
import StockTable from './StockTable';
import { useDispatch, useSelector } from 'react-redux';
import { logout } from '../store/actions/auth';


// Configure axios to include credentials
axios.defaults.withCredentials = true;
axios.defaults.headers.common['Content-Type'] = 'application/json';

const Dashboard = () => {
  const { error, isLoggedIn } = useSelector(state => state.auth);
  const navigate = useNavigate();
  const dispatch = useDispatch();

  useEffect(() => {
    // Check if user is logged in and has token
    if (!isLoggedIn) navigate('/login');
  }, [navigate, isLoggedIn]);

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
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        <StockSelector/>
        <StockTable />
        <StockGraph />
        </Grid>
    </Container>
  );
};

export default Dashboard; 