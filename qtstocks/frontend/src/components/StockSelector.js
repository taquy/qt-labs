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

import { fetchStocks, fetchStockData, pullStockList } from '../store/actions/stocks';
import { useSelector, useDispatch } from 'react-redux';
import { LoaderActions, ErrorActions, MessageActions } from '../store/slices/stocks';

const StockSelector = () => {
  const [selectedStocks, setSelectedStocks] = useState([]);
  const [loadLatestData, setLoadLatestData] = useState(false);
  const [forceFetchStocks, setForceFetchStocks] = useState(false);
  const [fetchNextPage, setFetchNextPage] = useState(false);
  const [firstLoad, setFirstLoad] = useState(true);
  const dispatch = useDispatch();

  // Add UUID generator function
  const generateUniqueId = () => {
    return Math.random().toString(36).substring(2) + Date.now().toString(36);
  };

  const [query, setQuery] = useState({
    page: 1,
    per_page: 20,
    exchanges: [],
    search: '',
    refresh: false
  });
  
  const {
    stocks,
    loaders,
    exchanges,
    errors,
    messages
  } = useSelector(state => state.stocks);

  // Add debounced search effect
  useEffect(() => {
    const notAllowFetch = query.search === '' && !forceFetchStocks && !firstLoad && !fetchNextPage;
    if (notAllowFetch) return;
    const timer = setTimeout(() => {
      if (firstLoad || forceFetchStocks) {
        dispatch(fetchStocks({ ...query, page: 1, refresh: true }));
      } else {
        dispatch(fetchStocks({ ...query, refresh: false }));
      }
      setForceFetchStocks(false);
      setFirstLoad(false);
      setFetchNextPage(false);
    }, 500);
    return () => clearTimeout(timer);
  }, [query, dispatch, forceFetchStocks, stocks.current_page, firstLoad, fetchNextPage]);

  const handleScroll = (event) => {
    const listbox = event.target;
    if (
      query.page === stocks.current_page && stocks.has_next && !fetchNextPage &&
      listbox.scrollTop + listbox.clientHeight >= listbox.scrollHeight - 10
    ) {
      setQuery(prevQuery => ({ ...prevQuery, page: prevQuery.page + 1 }));
      setFetchNextPage(true);
    }
  };

  // Function to highlight matching text
  const highlightMatch = (text, search) => {
    if (!search) return text;
    const parts = text.split(new RegExp(`(${search})`, 'gi'));
    return parts.map((part, index) =>
      part.toLowerCase() === search.toLowerCase() ?
        <span key={generateUniqueId()} style={{ backgroundColor: '#fff59d' }}>{part}</span> : part
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

  const handleOnChange = (event, newValue) => {
    setSelectedStocks(newValue.map(stock => typeof stock === 'string' ? stock : stock.symbol));
  };

  const handleOnInputChange = (event, newInputValue) => {
    setQuery(prevQuery => ({ ...prevQuery, search: newInputValue, refresh: true }));
    if (!newInputValue.trim()) {
     setForceFetchStocks(true);     
    }
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
            freeSolo
            options={stocks.items || []}
            getOptionLabel={(option) => {
              if (typeof option === 'string') return option;
              return `${option.symbol} - ${option.name} (${option.exchange})`;
            }}
            value={selectedStocks.map(symbol => (stocks.items || []).find(s => s.symbol === symbol) || { symbol, name: '' })}
            onChange={handleOnChange}
            onInputChange={handleOnInputChange}
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
                <Box component="li" key={generateUniqueId()} {...otherProps}>
                  <Box sx={{ display: 'flex', flexDirection: 'column' }}>
                    <Typography variant="body1">
                      {highlightMatch(option.symbol, query.search)}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {highlightMatch(option.name + ' (' + option.exchange + ')', query.search)}
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
                  checked={query.exchanges.includes(exchange)}
                  onChange={(e) => {
                    const newExchanges = e.target.checked ? [...query.exchanges, exchange] : query.exchanges.filter(ex => ex !== exchange);
                    setQuery(prevQuery => ({ ...prevQuery, exchanges: newExchanges, page: 1 }));
                    setForceFetchStocks(true);
                  }}
                  name={exchange}
                  color="primary"
                />
              }
              label={exchange}
            />
          ))}
        </Box>
        {messages[MessageActions.PULL_STOCK_LIST] && (
          <Box sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="body1" color="success">
              {messages[MessageActions.PULL_STOCK_LIST]}
            </Typography>
          </Box>
        )}
         {errors[ErrorActions.STOCK_SELECTOR] && (
          <Box sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="body1" color="error">
              {errors[ErrorActions.STOCK_SELECTOR]}
            </Typography>
          </Box>
        )}
      </Box>
    </Paper>
  );
};

export default StockSelector; 