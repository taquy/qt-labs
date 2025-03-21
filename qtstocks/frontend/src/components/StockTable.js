import React, { useEffect, useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Box,
  Typography,
  Checkbox,
  Button,
  Stack,
  TableSortLabel,
  Menu,
  MenuItem,
  Chip,
  IconButton,
  Tooltip
} from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { fetchStats, removeAvailableStock, exportCsv } from '../store/actions/stocks';
import { Delete, Download, ViewColumn } from '@mui/icons-material';
import { ErrorActions } from '../store/slices/stocks';

const StockTable = () => {
  const dispatch = useDispatch();
  const [anchorEl, setAnchorEl] = useState(null);
  const [visibleColumns, setVisibleColumns] = useState({
    symbol: true,
    name: true,
    exchange: true
  });

  // Select state from Redux store
  const {
    stats,
    metrics,
    exportedCsv,
    errors,
  } = useSelector(state => state.stocks);

  const [selected, setSelected] = React.useState([]);
  const [orderBy, setOrderBy] = React.useState('symbol');
  const [order, setOrder] = React.useState('asc');

  useEffect(() => {
    dispatch(fetchStats());
  }, [dispatch]);

  // Initialize visibleColumns when metrics becomes available
  useEffect(() => {
    if (metrics) {
      setVisibleColumns(prev => ({
        ...prev,
        ...Object.keys(metrics).reduce((acc, key) => ({ ...acc, [key]: true }), {})
      }));
    }
  }, [metrics]);

  const handleRequestSort = (property) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const sortStocks = (stocks) => {
    return [...stocks].sort((a, b) => {
      let aValue = a[orderBy];
      let bValue = b[orderBy];
      // Handle numeric values
      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return order === 'asc' ? aValue - bValue : bValue - aValue;
      }
      // Handle string values
      aValue = String(aValue).toLowerCase();
      bValue = String(bValue).toLowerCase();
      return order === 'asc'
        ? aValue.localeCompare(bValue)
        : bValue.localeCompare(aValue);
    });
  };

  const handleSelectAll = (event) => {
    if (event.target.checked) {
      setSelected(stats.map((stock) => stock.symbol));
    } else {
      setSelected([]);
    }
  };

  const handleSelect = (symbol) => {
    setSelected((prev) => {
      if (prev.includes(symbol)) {
        return prev.filter((s) => s !== symbol);
      }
      return [...prev, symbol];
    });
  };

  const handleRemoveSelected = () => {
    const newSelected = selected.filter(id => !stats.includes(id));
    setSelected(newSelected);
    dispatch(removeAvailableStock(newSelected));
  };

  const handleExportCSV = () => {
    dispatch(exportCsv());
  };

  const createSortHandler = (property) => () => {
    handleRequestSort(property);
  };

  useEffect(() => {
    if (exportedCsv) {
      // Create a blob from the CSV data
      const blob = new Blob([exportedCsv], { type: 'text/csv;charset=utf-8;' });

      // Create a link element
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);

      // Set link properties
      link.setAttribute('href', url);
      link.setAttribute('download', `stocks-report-${Date.now()}.csv`);
      link.style.visibility = 'hidden';

      // Append to body, click, and remove
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // Clean up the URL object
      URL.revokeObjectURL(url);
    }
  }, [exportedCsv]);

  const handleColumnToggle = (column) => {
    setVisibleColumns(prev => ({
      ...prev,
      [column]: !prev[column]
    }));
  };

  const handleMenuClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  return (
    <Paper sx={{ p: 2, mt: 3, mb: 3 }}> 
      <Box sx={{ width: '100%', mb: 3 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">
            Selected Stocks
          </Typography>
          <Stack direction="row" spacing={2} alignItems="center">
            <Tooltip title="Toggle Columns">
              <IconButton onClick={handleMenuClick} color="primary">
                <ViewColumn />
              </IconButton>
            </Tooltip>
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleMenuClose}
            >
              <MenuItem onClick={() => handleColumnToggle('symbol')}>
                <Checkbox checked={visibleColumns.symbol} />
                Symbol
              </MenuItem>
              <MenuItem onClick={() => handleColumnToggle('name')}>
                <Checkbox checked={visibleColumns.name} />
                Name
              </MenuItem>
              <MenuItem onClick={() => handleColumnToggle('exchange')}>
                <Checkbox checked={visibleColumns.exchange} />
                Exchange
              </MenuItem>
              {Object.entries(metrics).map(([key, label]) => (
                <MenuItem key={key} onClick={() => handleColumnToggle(key)}>
                  <Checkbox checked={visibleColumns[key]} />
                  {label}
                </MenuItem>
              ))}
            </Menu>
            <Button
              variant="outlined"
              color="primary"
              onClick={handleExportCSV}
              startIcon={<Download />}
            >
              Export CSV
            </Button>
            {selected.length > 0 && (
              <Button
                variant="outlined"
                color="error"
                onClick={handleRemoveSelected}
                startIcon={<Delete />}
              >
                Remove Selected ({selected.length})
              </Button>
            )}
          </Stack>
        </Stack>
        <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
          {Object.entries(visibleColumns).map(([key, visible]) => (
            visible && (
              <Chip
                key={key}
                label={key === 'symbol' ? 'Symbol' : key === 'name' ? 'Name' : key === 'exchange' ? 'Exchange' : metrics[key]}
                onDelete={() => handleColumnToggle(key)}
                size="small"
              />
            )
          ))}
        </Box>
        {errors[ErrorActions.STOCK_TABLE] && (
          <Box sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="body1" color="error">
              {errors[ErrorActions.STOCK_TABLE]}
            </Typography>
          </Box>
        )}  
        <TableContainer 
          component={Paper} 
          sx={{ 
            maxHeight: 400,
            '&::-webkit-scrollbar': {
              width: '8px',
            },
            '&::-webkit-scrollbar-track': {
              background: '#f1f1f1',
            },
            '&::-webkit-scrollbar-thumb': {
              background: '#888',
              borderRadius: '4px',
            },
          }}
        >
          <Table stickyHeader size="small">
            <TableHead>
              <TableRow>
                <TableCell padding="checkbox">
                  <Checkbox
                    indeterminate={selected.length > 0 && selected.length < stats.length}
                    checked={stats.length > 0 && selected.length === stats.length}
                    onChange={handleSelectAll}
                  />
                </TableCell>
                {visibleColumns.symbol && (
                  <TableCell>
                    <TableSortLabel
                      active={orderBy === 'symbol'}
                      direction={orderBy === 'symbol' ? order : 'asc'}
                      onClick={createSortHandler('symbol')}
                    >
                      Symbol
                    </TableSortLabel>
                  </TableCell>
                )}
                {visibleColumns.name && (
                  <TableCell>
                    <TableSortLabel
                      active={orderBy === 'name'}
                      direction={orderBy === 'name' ? order : 'asc'}
                      onClick={createSortHandler('name')}
                    >
                      Name
                    </TableSortLabel>
                  </TableCell>
                )}
                {visibleColumns.exchange && (
                  <TableCell>
                    <TableSortLabel
                      active={orderBy === 'exchange'}
                      direction={orderBy === 'exchange' ? order : 'asc'}
                      onClick={createSortHandler('exchange')}
                    >
                      Exchange
                    </TableSortLabel>
                  </TableCell>
                )}
                {Object.entries(metrics).map(([key, label]) => (
                  visibleColumns[key] && (
                    <TableCell key={key}>
                      <TableSortLabel
                        active={orderBy === key}
                        direction={orderBy === key ? order : 'asc'}
                        onClick={createSortHandler(key)}
                      >
                        {label}
                      </TableSortLabel>
                    </TableCell>
                  )
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {sortStocks(stats).map((stock) => (
                <TableRow
                  key={stock.symbol}
                  hover
                  selected={selected.includes(stock.symbol)}
                  sx={{ cursor: 'pointer' }}
                >
                  <TableCell padding="checkbox">
                    <Checkbox
                      checked={selected.includes(stock.symbol)}
                      onChange={(e) => {
                        e.stopPropagation();
                        handleSelect(stock.symbol);
                      }}
                    />
                  </TableCell>
                  {visibleColumns.symbol && (
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <img 
                          src={stock.icon} 
                          alt={`${stock.symbol} icon`}
                          style={{ width: 20, height: 20 }}
                          onError={(e) => {
                            e.target.onerror = null; // Prevent infinite loop
                            e.target.src = 'https://cdn-icons-gif.flaticon.com/7211/7211793.gif';
                          }}
                        />
                        {stock.symbol}
                      </Box>
                    </TableCell>
                  )}
                  {visibleColumns.name && (
                    <TableCell>{stock.name}</TableCell>
                  )}
                  {visibleColumns.exchange && (
                    <TableCell>{stock.exchange}</TableCell>
                  )}
                  {Object.entries(metrics).map(([key, label]) => (
                    visibleColumns[key] && (
                      <TableCell key={key}>{stock[key]}</TableCell>
                    )
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    </Paper>
  );
};

export default StockTable;
