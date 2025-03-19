import React, { useEffect, useState } from 'react';
import {
  Paper,
  Typography,
  Button,
  Box,
  FormControl,
  Autocomplete,
  TextField,
  Chip,
  CircularProgress,
  FormControlLabel,
  Checkbox
} from '@mui/material';

import { fetchStocks, fetchStockData } from '../store/sagas/stockGraphSaga';
import { useSelector, useDispatch } from 'react-redux';

const StockSelector = () => {
  const [selectedStocks, setSelectedStocks] = useState([]);
  const [loadLatestData, setLoadLatestData] = useState(false);
  const [inputValue] = useState('');
  const dispatch = useDispatch();
  
  const {
    stocks,
    fetchingStockStats
  } = useSelector(state => state.stockGraph);
  
  useEffect(() => {
    dispatch(fetchStocks());
  }, [dispatch]);

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
    dispatch(fetchStockData({selectedStocks, loadLatestData}));
  };
  
  const handleRemoveStock = (stockToRemove) => {
    setSelectedStocks(selectedStocks.filter(stock => stock !== stockToRemove));
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Stock Selection
      </Typography>
      
      <Box sx={{ 
        display: 'flex', 
        gap: 2, 
        alignItems: 'flex-start'
      }}>
        <FormControl sx={{ flex: 1 }}>
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
                    onDelete={() => handleRemoveStock(option.symbol)}
                  />
                );
              })
            }
            ListboxProps={{
              style: {
                maxHeight: '250px'
              }
            }}
          />
        </FormControl>

        <Button
          variant="contained"
          color="primary"
          onClick={handleFetchStockData}
          disabled={selectedStocks.length === 0 || fetchingStockStats}
          sx={{ 
            minWidth: '200px',
            height: '56px',
            position: 'relative'
          }}
        >
          {fetchingStockStats ? (
            <>
              <CircularProgress
                size={24}
                sx={{
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  marginTop: '-12px',
                  marginLeft: '-12px',
                  color: 'white'
                }}
              />
            </>
          ) : (
            'Fetch Stock Data'
          )}
        </Button>
      </Box>
      <Box sx={{ display: 'flex', alignItems: 'center' }}>
        <FormControlLabel
          control={
            <Checkbox
              checked={loadLatestData}
              onChange={(e) => setLoadLatestData(e.target.checked)}
              name="loadLatestData"
              color="primary"
            />
          }
          label="Load latest data"
        />
      </Box>
    </Paper>
  );
};

export default StockSelector; 