import React, { useEffect } from 'react';
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
  TableSortLabel
} from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { fetchAvailableStocks, removeAvailableStock } from '../store/sagas/stockGraphSaga';

const StockSelectionTable = () => {
  const dispatch = useDispatch();

  // Select state from Redux store
  const {
    availableStocks,
    metrics
  } = useSelector(state => state.stockGraph);

  const [selected, setSelected] = React.useState([]);
  const [orderBy, setOrderBy] = React.useState('symbol');
  const [order, setOrder] = React.useState('asc');

  useEffect(() => {
    dispatch(fetchAvailableStocks());
  }, [dispatch]);

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
      setSelected(availableStocks.map((stock) => stock.symbol));
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
    dispatch(removeAvailableStock(selected));
    setSelected([]);
  };

  const createSortHandler = (property) => () => {
    handleRequestSort(property);
  };

  return (
    <Paper sx={{ p: 2, mt: 3, mb: 3 }}> 
      <Box sx={{ width: '100%', mb: 3 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">
            Selected Stocks
          </Typography>
          <Button 
            variant="outlined" 
            color="error" 
            onClick={handleRemoveSelected}
            disabled={selected.length === 0}
          >
            Remove Selected ({selected.length})
          </Button>
        </Stack>
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
                    indeterminate={selected.length > 0 && selected.length < availableStocks.length}
                    checked={availableStocks.length > 0 && selected.length === availableStocks.length}
                    onChange={handleSelectAll}
                  />
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={orderBy === 'symbol'}
                    direction={orderBy === 'symbol' ? order : 'asc'}
                    onClick={createSortHandler('symbol')}
                  >
                    Symbol
                  </TableSortLabel>
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={orderBy === 'name'}
                    direction={orderBy === 'name' ? order : 'asc'}
                    onClick={createSortHandler('name')}
                  >
                    Name
                  </TableSortLabel>
                </TableCell>
                {Object.entries(metrics).map(([key, label]) => (
                  <TableCell key={key}>
                    <TableSortLabel
                      active={orderBy === key}
                      direction={orderBy === key ? order : 'asc'}
                      onClick={createSortHandler(key)}
                    >
                      {label}
                    </TableSortLabel>
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {sortStocks(availableStocks).map((stock) => (
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
                  <TableCell>{stock.symbol}</TableCell>
                  <TableCell>{stock.name}</TableCell>
                  {Object.entries(metrics).map(([key, label]) => (
                    <TableCell key={key}>{stock[key]}</TableCell>
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

export default StockSelectionTable; 