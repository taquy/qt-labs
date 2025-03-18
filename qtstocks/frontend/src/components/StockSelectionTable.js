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
  Stack
} from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';

const StockSelectionTable = ({ stocks, onStockSelect, onRemoveStocks }) => {

  // Select state from Redux store
  const {
    availableStocks,
    metrics
  } = useSelector(state => state.stockGraph);

  const [selected, setSelected] = React.useState([]);

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
    onRemoveStocks(selected);
    setSelected([]);
  };

  return (
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
              <TableCell>Symbol</TableCell>
              <TableCell>Name</TableCell>
              {Object.entries(metrics).map(([key, label]) => (
                <TableCell key={key}>{label}</TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {availableStocks.map((stock) => (
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
  );
};

export default StockSelectionTable; 