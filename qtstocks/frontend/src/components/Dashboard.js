import React from 'react';
import { Typography, Grid, Paper } from '@mui/material';
import { useSelector } from 'react-redux';

const Dashboard = () => {
  const { stats } = useSelector(state => state.stocks);

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 240 }}>
          <Typography variant="h6" gutterBottom>
            Quick Stats
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h4" color="primary">
                  {stats?.length || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Stocks
                </Typography>
              </Paper>
            </Grid>
            {/* Add more stat cards as needed */}
          </Grid>
        </Paper>
      </Grid>
    </Grid>
  );
};

export default Dashboard; 