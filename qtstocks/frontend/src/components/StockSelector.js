import React, { use, useEffect, useState } from 'react';
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

import { fetchStocks, fetchStockData, pullStockList } from '../store/actions/stocks';
import { useSelector, useDispatch } from 'react-redux';
import { LoaderActions } from '../store/slices/stocks';

const StockSelector = () => {
  const [selectedStocks, setSelectedStocks] = useState([]);
  const [loadLatestData, setLoadLatestData] = useState(false);
  const [selectedExchanges, setSelectedExchanges] = useState([]);
  const [isAllowedToFetchMoreStocks, setIsAllowedToFetchMoreStocks] = useState(true);
  const [page, setPage] = useState(1);
  const [inputValue] = useState('');
  const dispatch = useDispatch();
  
  const {
    stocks,
    loaders,
    exchanges
  } = useSelector(state => state.stocks);

  useEffect(() => {
    setIsAllowedToFetchMoreStocks(!loaders[LoaderActions.FETCH_STOCKS] && stocks.has_next);
  }, [page, stocks.current_page, loaders, stocks.has_next]);

  useEffect(() => {
    if (isAllowedToFetchMoreStocks && page !== stocks.current_page) {
      dispatch(fetchStocks({page, per_page: 20}));
    }
  }, [dispatch, page, isAllowedToFetchMoreStocks, stocks.current_page]);

  const handleScroll = (event) => {
    const listbox = event.target;
    if (
      isAllowedToFetchMoreStocks && page === stocks.current_page &&
      listbox.scrollTop + listbox.clientHeight >= listbox.scrollHeight - 10
    ) {
      setPage(prevPage => prevPage + 1);
    }
  };

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

  const handlePullStockList = () => {
    dispatch(pullStockList());
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
            options={stocks.items || []}
            getOptionLabel={(option) => `${option.symbol} - ${option.name}`}
            value={selectedStocks.map(symbol => (stocks.items || []).find(s => s.symbol === symbol) || { symbol, name: '' })}
            onChange={(event, newValue) => {
              setSelectedStocks(newValue.map(stock => stock.symbol));
            }}
            filterOptions={(options, { inputValue }) => {
              if (!options || !Array.isArray(options)) return [];
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
                size="small"
                InputProps={{
                  ...params.InputProps,
                  endAdornment: (
                    <>
                      {loaders[LoaderActions.FETCH_STOCKS] && (
                        <CircularProgress size={20} sx={{ mr: 1 }} />
                      )}
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
              },
              onScroll: handleScroll
            }}
          />
        </FormControl>

        <Button
          variant="contained"
          color="primary"
          onClick={handleFetchStockData}
          disabled={selectedStocks.length === 0 || loaders[LoaderActions.FETCH_STOCK_DATA]}
          sx={{ 
            minHeight: '40px',
            position: 'relative'
          }}
        >
          {loaders[LoaderActions.FETCH_STOCK_DATA] ? (
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

        <Button
          variant="contained"
          color="primary"
          onClick={handlePullStockList}
          disabled={loaders[LoaderActions.PULL_STOCK_LIST]}
          sx={{ 
            minHeight: '40px',
            position: 'relative'
          }}
        >
          {loaders[LoaderActions.PULL_STOCK_LIST] ? (
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
            'Pull Stock Lists'
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
          label="Fetch latest data"
        />
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, ml: 2 }}>
          {exchanges.map((exchange) => (
            <FormControlLabel
              key={exchange}
              control={
                <Checkbox
                  checked={selectedExchanges.includes(exchange)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedExchanges([...selectedExchanges, exchange]);
                    } else {
                      setSelectedExchanges(selectedExchanges.filter(ex => ex !== exchange));
                    }
                  }}
                  name={exchange}
                  color="primary"
                />
              }
              label={exchange}
            />
          ))}
        </Box>
      </Box>
    </Paper>
  );
};

export default StockSelector; 