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
  Checkbox,
  Tooltip
} from '@mui/material';

import { pullStockStats, pullStockList, fetchExchanges, fetchStocks } from '../../store/actions/stocks';
import { fetchSettings } from '../../store/actions/settings';
import { useSelector, useDispatch } from 'react-redux';
import { LoaderActions, ErrorActions, MessageActions } from '../../store/slices/stocks';
import { SettingsTypes } from '../../store/slices/settings';
import { saveSettings } from '../../store/actions/settings';
import { setMessage } from '../../store/actions/stocks';
const StockSelector = () => {
  const [selectedStocks, setSelectedStocks] = useState([]);
  const [loadLatestData, setLoadLatestData] = useState(false);
  const [fetchNextPage, setFetchNextPage] = useState(false);
  const [firstLoad, setFirstLoad] = useState(true);
  const dispatch = useDispatch();
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
    messages,
  } = useSelector(state => state.stocks);

  const { settings } = useSelector(state => state.settings);

  useEffect(() => {
    dispatch(fetchSettings(SettingsTypes.STOCK_SELECTOR));
    dispatch(fetchExchanges());
  }, [dispatch]);

  // Add debounced search effect
  useEffect(() => {
    if (!query) return;
    const timer = setTimeout(() => {
      if (firstLoad) {
        dispatch(fetchStocks({ ...query, page: 1 }));
      } else {
        dispatch(fetchStocks({ ...query }));
      }
      setFetchNextPage(false);
    }, 500);
    return () => clearTimeout(timer);
  }, [query, dispatch, firstLoad, fetchNextPage]);

  useEffect(() => {
    if (firstLoad) return;
    dispatch(saveSettings(SettingsTypes.STOCK_SELECTOR, { 
      exchanges: query.exchanges, 
      loadLatestData 
    }));
  }, [query, loadLatestData, dispatch, firstLoad]);

  useEffect(() => {
    if (!settings || !settings[SettingsTypes.STOCK_SELECTOR] || !firstLoad) return
      const currentSettings = settings[SettingsTypes.STOCK_SELECTOR];
      setLoadLatestData(currentSettings.loadLatestData || false);
      setQuery(prevQuery => ({ ...prevQuery, 
        exchanges: currentSettings.exchanges || [], 
        loadLatestData: currentSettings.loadLatestData || false 
      }));
      setFirstLoad(false);
  }, [settings, firstLoad]);

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
      query.page === stocks.current_page && stocks.has_next && !fetchNextPage &&
      listbox.scrollTop + listbox.clientHeight >= listbox.scrollHeight - 10
    ) {
      setQuery(prevQuery => ({ ...prevQuery, page: prevQuery.page + 1, refresh: false  }));
      setFetchNextPage(true);
    }
  };

  const handleFetchStockData = () => {
    dispatch(pullStockStats({selectedStocks, loadLatestData}));
  };

  const handlePullStockList = () => {
    dispatch(pullStockList());
  };

  const handleOnChange = (event, newValue) => {
    setSelectedStocks(newValue.map(stock => typeof stock === 'string' ? stock : stock.symbol));
  };

  const handleOnInputChange = (event, newInputValue) => {
    setQuery({ ...query, search: newInputValue, refresh: true, page: 1 });
  };

  const handleExchangeChange = (exchange) => (event) => {
    const newExchanges = event.target.checked
      ? [...query.exchanges, exchange] 
      : query.exchanges.filter(ex => ex !== exchange);
    setQuery({ ...query, exchanges: newExchanges, refresh: true });
  };

  const safeOptions = Array.isArray(stocks?.items) ? stocks.items : [];
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
            isOptionEqualToValue={(option, value) => option.symbol === value.symbol}
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
              const isSelected = selectedStocks.includes(option.symbol);
              return (
                <Tooltip 
                  key={`tooltip-${option.symbol}`}
                  title={`Last updated: ${new Date(option.last_updated).toLocaleString()}`}
                  placement="right"
                >
                  <Box component="li" {...otherProps}>
                    <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                      <Checkbox
                        checked={isSelected}
                        onChange={(e) => {
                          e.stopPropagation();
                          const newSelected = isSelected
                            ? selectedStocks.filter(s => s !== option.symbol)
                            : [...selectedStocks, option.symbol];
                          setSelectedStocks(newSelected);
                        }}
                        onClick={(e) => e.stopPropagation()}
                        size="small"
                      />
                      <Box sx={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <img 
                            src={option.icon} 
                            alt={`${option.symbol} icon`}
                            style={{ width: 20, height: 20, borderRadius: '50%' }}
                            onError={(e) => {
                              e.target.onerror = null; // Prevent infinite loop
                              e.target.src = 'https://cdn-icons-gif.flaticon.com/7211/7211793.gif';
                            }}
                          />
                          <Typography variant="body1">
                            {option.symbol}
                          </Typography>
                        </Box>
                        <Typography variant="caption" color="text.secondary">
                          {option.name} ({option.exchange})
                        </Typography>
                      </Box>
                    </Box>
                  </Box>
                </Tooltip>
              );
            }}
            renderTags={(tagValue, getTagProps) =>
              tagValue.map((option, index) => {
                const { key, onDelete, ...chipProps } = getTagProps({ index });
                return (
                  <Tooltip 
                    key={`tag-tooltip-${option.symbol}-${index}`}
                    title={`Last updated: ${new Date(option.last_updated).toLocaleString()}`}
                    placement="top"
                  >
                    <Chip
                      key={key}
                      {...chipProps}
                      icon={
                        <img 
                          src={option.icon} 
                          alt={`${option.symbol} icon`}
                          style={{ width: 16, height: 16, borderRadius: '50%' }}
                          onError={(e) => {
                            e.target.onerror = null;
                            e.target.src = 'https://cdn-icons-gif.flaticon.com/7211/7211793.gif';
                          }}
                        />
                      }
                      label={option.symbol}
                      onDelete={(e) => {
                        e.stopPropagation();
                        onDelete(e);
                      }}
                      size="small"
                    />
                  </Tooltip>
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
                  checked={query.exchanges.includes(exchange)}
                  onChange={handleExchangeChange(exchange)}
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
