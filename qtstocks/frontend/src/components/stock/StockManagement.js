import React from 'react';
import { Box, Grid } from '@mui/material';
import StockSelector from './StockSelector';
import StockComparisonGraph from './StockComparisonGraph';
import StockWatchlist from './watchlist/StockWatchlist';

const StockManagement = () => {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <Grid container>
        <Grid item xs={12}>
          <StockSelector />
        </Grid>
        <Grid item xs={12}>
          <StockWatchlist />
        </Grid>
        <Grid item xs={12}>
          <StockComparisonGraph />
        </Grid>
      </Grid>
    </Box>
  );
};

export default StockManagement; 