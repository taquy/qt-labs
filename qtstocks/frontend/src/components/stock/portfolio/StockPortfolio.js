
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
  Button,
  Chip,
  DialogActions,
  FormControl,
  Autocomplete,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent
} from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { fetchStats, removeStats, exportCsv } from '../../../store/actions/stocks';
import { fetchSettings, saveSettings } from '../../../store/actions/settings';
import { Delete, Download, ViewColumn, Add as AddIcon } from '@mui/icons-material';
import { ErrorActions } from '../../../store/slices/stocks';
import { SettingsTypes } from '../../../store/slices/settings';

// Portfolio Management Component
const StockPortfolio = ({ stats }) => {
  const [portfolio, setPortfolio] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedStocks, setSelectedStocks] = useState([]);
  const [newPosition, setNewPosition] = useState({
    name: '',
    description: '',
    stocks: []
  });

  const handleAddPosition = () => {
    if (selectedStocks.length > 0) {
      setPortfolio([...portfolio, {
        ...newPosition,
        stocks: selectedStocks
      }]);
      setOpenDialog(false);
      setNewPosition({
        name: '',
        description: '',
        stocks: []
      });
      setSelectedStocks([]);
    }
  };

  const handleRemoveStock = (stockToRemove) => {
    setSelectedStocks(selectedStocks.filter(stock => stock !== stockToRemove));
  };

  const handleOnChange = (event, newValue) => {
    setSelectedStocks(newValue.map(stock => typeof stock === 'string' ? stock : stock.symbol));
  };

  const handleOnInputChange = (event, newInputValue) => {
    // You can add search functionality here if needed
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Portfolios</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
        >
          Add Portfolio
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Stocks</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {portfolio.map((position) => (
              <TableRow key={`${position.name}`}>
                <TableCell>{position.name}</TableCell>
                <TableCell>{position.description}</TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {position.stocks.map((stock) => (
                      <Chip
                        key={stock}
                        label={stock}
                        size="small"
                      />
                    ))}
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog 
        open={openDialog} 
        onClose={() => setOpenDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>New Portfolio</DialogTitle>
        <DialogContent sx={{ minWidth: 400 }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 2 }}>
            <TextField
              label="Name"
              value={newPosition.name}
              onChange={(e) => setNewPosition({ ...newPosition, name: e.target.value })}
              fullWidth
            />
            <TextField
              label="Description"
              multiline
              rows={4}
              value={newPosition.description}
              onChange={(e) => setNewPosition({ ...newPosition, description: e.target.value })}
              fullWidth
            />
            <FormControl fullWidth>
              <Autocomplete
                multiple
                options={stats}
                getOptionLabel={(option) => {
                  if (typeof option === 'string') return option;
                  return `${option.symbol} - ${option.name}`;
                }}
                value={selectedStocks.map(symbol => stats.find(s => s.symbol === symbol) || { symbol, name: '' })}
                onChange={handleOnChange}
                onInputChange={handleOnInputChange}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    variant="outlined"
                    label="Select Stocks"
                    placeholder={selectedStocks.length === 0 ? "Type to search..." : ""}
                    size="small"
                  />
                )}
                renderOption={(props, option) => {
                  const { key, ...otherProps } = props;
                  return (
                    <Box component="li" {...otherProps}>
                      <Box sx={{ display: 'flex', flexDirection: 'column' }}>
                        <Typography variant="body1">
                          {option.symbol}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {option.name}
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
                    maxHeight: '200px'
                  }
                }}
              />
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button 
            onClick={handleAddPosition}
            variant="contained"
            disabled={!newPosition.name || !newPosition.description || selectedStocks.length === 0}
          >
            Add
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default StockPortfolio;
