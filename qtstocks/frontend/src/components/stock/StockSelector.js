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

import { fetchStocks, pullStockStats, pullStockList } from '../../store/actions/stocks';
import { fetchSettings } from '../../store/actions/settings';
import { useSelector, useDispatch } from 'react-redux';
import { LoaderActions, ErrorActions, MessageActions } from '../../store/slices/stocks';
import { SettingsTypes } from '../../store/slices/settings';
import { saveSettings } from '../../store/actions/settings';
import { setMessage, setStocksQuery } from '../../store/actions/stocks';
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

  const {
    stocks,
    loaders,
    exchanges,
    errors,
    messages,
    stocks_query
  } = useSelector(state => state.stocks);

  const { settings } = useSelector(state => state.settings);

  useEffect(() => {
    dispatch(fetchSettings(SettingsTypes.STOCK_SELECTOR));
  }, [dispatch]);

  // Add debounced search effect
  useEffect(() => {
    if (!stocks_query) return;
    if (stocks_query.search === '' && !forceFetchStocks && !firstLoad && !fetchNextPage) return;
    const timer = setTimeout(() => {
      if (firstLoad || forceFetchStocks) {
        dispatch(fetchStocks({ ...stocks_query, page: 1, refresh: true }));
      } else {
        dispatch(fetchStocks({ ...stocks_query, refresh: false }));
      }
      setForceFetchStocks(false);
      setFirstLoad(false);
      setFetchNextPage(false);
    }, 500);
    return () => clearTimeout(timer);
  }, [stocks_query, dispatch, forceFetchStocks, stocks.current_page, firstLoad, fetchNextPage]);

  useEffect(() => {
    if (firstLoad) return;
    dispatch(saveSettings(SettingsTypes.STOCK_SELECTOR, { exchanges: stocks_query.exchanges, loadLatestData }));
  }, [stocks_query.exchanges, loadLatestData, dispatch, firstLoad]);

  useEffect(() => {
    if (settings && settings[SettingsTypes.STOCK_SELECTOR]) {
      const currentSettings = settings[SettingsTypes.STOCK_SELECTOR];
      setLoadLatestData(currentSettings.loadLatestData || false);
      setStocksQuery(prevQuery => ({ ...prevQuery, exchanges: currentSettings.exchanges || [], loadLatestData: currentSettings.loadLatestData || false }));
    }
  }, [settings]);

  useEffect(() => {
    if (messages[MessageActions.PULL_STOCK_LIST]) {
      setTimeout(() => {
        dispatch(setMessage({ action: MessageActions.PULL_STOCK_LIST, message: "" }));
      }, 3000);
    }
  }, [messages, dispatch]);

  const handleScroll = (event) => {
    const listbox = event.target;
    if (
      stocks_query.page === stocks.current_page && stocks.has_next && !fetchNextPage &&
      listbox.scrollTop + listbox.clientHeight >= listbox.scrollHeight - 10
    ) {
      setStocksQuery(prevQuery => ({ ...prevQuery, page: prevQuery.page + 1 }));
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
    dispatch(pullStockStats({selectedStocks, loadLatestData}));
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
    setStocksQuery(prevQuery => ({ ...prevQuery, search: newInputValue, refresh: true }));
    if (!newInputValue.trim()) {
     setForceFetchStocks(true);     
    }
  }; 

  console.log('stocks:', stocks);
  console.log('stocks?.items:', stocks?.items);

  const safeOptions = Array.isArray(stocks?.items) ? stocks.items : [];
  console.log('safeOptions:', safeOptions);

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
            options={safeOptions}
            getOptionLabel={(option) => {
              if (typeof option === 'string') return option;
              return option?.symbol ? `${option.symbol} - ${option.name} (${option.exchange})` : '';
            }}
            value={selectedStocks.map(symbol => safeOptions.find(s => s?.symbol === symbol) || { symbol, name: '' })}
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
              if (!option) return null;
              const { key, ...otherProps } = props;
              return (
                <Box component="li" key={generateUniqueId()} {...otherProps}>
                  <Box sx={{ display: 'flex', flexDirection: 'column' }}>
                    <Typography variant="body1">
                      {highlightMatch(option.symbol || '', stocks_query?.search || '')}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {highlightMatch((option.name || '') + ' (' + (option.exchange || '') + ')', stocks_query?.search || '')}
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
                    label={option?.symbol || ''}
                    {...chipProps}
                    size="small"
                    onDelete={() => handleRemoveStock(option?.symbol)}
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
          disabled={selectedStocks.length === 0 || loaders[LoaderActions.PULL_STOCK_STATS]}
          sx={{ 
            minHeight: '40px',
            position: 'relative'
          }}
        >
          {loaders[LoaderActions.PULL_STOCK_STATS] ? (
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
            'Fetch Stock Stats'
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
                  checked={stocks_query.exchanges.includes(exchange)}
                  onChange={(e) => {
                    const newExchanges = e.target.checked ? [...stocks_query.exchanges, exchange] : stocks_query.exchanges.filter(ex => ex !== exchange);
                    setStocksQuery(prevQuery => ({ ...prevQuery, exchanges: newExchanges, page: 1 }));
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
