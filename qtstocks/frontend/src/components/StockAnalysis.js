import React from 'react';
import { Box, Grid } from '@mui/material';
import StockSelector from './StockSelector';
import StockGraph from './StockGraph';
import StockTable from './StockTable';

const StockAnalysis = () => {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <Grid container>
        <Grid item xs={12}>
          <StockSelector />
        </Grid>
        <Grid item xs={12}>
          <StockGraph />
        </Grid>
        <Grid item xs={12}>
          <StockTable />
        </Grid>
      </Grid>
    </Box>
  );
};

export default StockAnalysis; 