import React, { useState } from 'react';
import {
  Paper,
  Box,
  Tabs,
  Tab,
} from '@mui/material';
import StockWatchlistTable from './StockWatchlistTable';
import StockPortfolioTable from './StockPortfolioTable';


const StockTable = () => {
  const [tabValue, setTabValue] = useState(1);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  return (
    <Paper sx={{ p: 2, mt: 3, mb: 3 }}>
      <Box sx={{ width: '100%' }}>
        <Tabs value={tabValue} onChange={handleTabChange} sx={{ mb: 2 }}>
          <Tab label="Stock List" />
          <Tab label="Portfolio Management" />
        </Tabs>
        {tabValue === 0 ? (
          <StockWatchlistTable/>
        ) : (
          <StockPortfolioTable/>
        )}
      </Box>
    </Paper>
  );
};

export default StockTable;
