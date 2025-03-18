import React, { useState } from 'react';
import {
  Paper,
  Typography,
  Button,
  Box,
  FormControl,
  Autocomplete,
  TextField,
  Chip,
  CircularProgress
} from '@mui/material';

import { useSelector } from 'react-redux';

const StockSelector = () => {
  const [selectedStocks, setSelectedStocks] = useState([]);
  const [inputValue, setInputValue] = useState('');

  const {
    stocks,
  } = useSelector(state => state.stockGraph);

  // Function to highlight matching text
  const highlightMatch = (text, search) => {
    if (!search) return text;
    const parts = text.split(new RegExp(`(${search})`, 'gi'));
    return parts.map((part, index) =>
      part.toLowerCase() === search.toLowerCase() ? 
        <span key={index} style={{ backgroundColor: '#fff59d' }}>{part}</span> : part
    );
  };

  const handleFetchStockData = () => {
    console.log('Fetching stock data');
  };
  
  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Stock Selection
      </Typography>
      
      <Box sx={{ mb: 2 }}>
        <Button
          variant="contained"
          color="success"
          onClick={handleFetchStockData}
          disabled={selectedStocks.length === 0}
        ></Button>
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
              InputProps={{
                ...params.InputProps,
                endAdornment: (
                  <>
                    {params.InputProps.endAdornment}
                  </>
                ),
              }}
            />
          )}
          renderOption={(props, option) => {
            const { key, ...otherProps } = props;
            return (
              <Box component="li" key={key} {...otherProps}>
                <Box sx={{ display: 'flex', flexDirection: 'column' }}>
                  <Typography variant="body1">
                    {highlightMatch(option.symbol, inputValue)}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {highlightMatch(option.name, inputValue)}
                  </Typography>
                </Box>
              </Box>
            );
          }}
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
    </Paper>
  );
};

export default StockSelector; 