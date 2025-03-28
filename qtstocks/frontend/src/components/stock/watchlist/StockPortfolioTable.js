import React, { useState, useEffect } from 'react';
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
  DialogContent,
  IconButton,
  Tooltip
} from '@mui/material';
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { fetchPortfolios, createPortfolio, updatePortfolio, deletePortfolio } from '../../../store/actions/stocks';
import { useDispatch, useSelector } from 'react-redux';

const StockPortfolioTable = ({ stats }) => {
  const [openDialog, setOpenDialog] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [selectedStocks, setSelectedStocks] = useState([]);
  const [newPortfolio, setNewPortfolio] = useState({
    name: '',
    description: '',
    stocks: []
  });
  const dispatch = useDispatch();
  const { portfolios } = useSelector(state => state.stocks);

  useEffect(() => {
    dispatch(fetchPortfolios());
  }, [dispatch]);

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setIsEditing(false);
    setNewPortfolio({
      name: '',
      description: '',
      stocks: []
    });
    setSelectedStocks([]);
  };

  const handleAddPortfolio = () => {
    if (isEditing) {
      dispatch(updatePortfolio({
        id: newPortfolio.id,
        name: newPortfolio.name,
        description: newPortfolio.description,
        stock_symbols: selectedStocks
      }));
    } else {
      dispatch(createPortfolio({
        name: newPortfolio.name,
        description: newPortfolio.description,
        stock_symbols: selectedStocks
      }));
    }
    handleCloseDialog();
  };

  const handleEditPortfolio = (portfolio) => {
    setIsEditing(true);
    setNewPortfolio({
      id: portfolio.id,
      name: portfolio.name,
      description: portfolio.description,
      stocks: portfolio.stocks
    });
    setSelectedStocks(portfolio.stocks.map(stock => stock.symbol));
    setOpenDialog(true);
  };

  const handleDeletePortfolio = (portfolioId) => {
    if (window.confirm('Are you sure you want to delete this portfolio?')) {
      dispatch(deletePortfolio(portfolioId));
    }
  };

  const handleRemoveStock = (stockToRemove) => {
    setSelectedStocks((prevStocks) => prevStocks.filter(stock => stock !== stockToRemove));
  };

  const handleOnChange = (event, newValue) => {
    setSelectedStocks(newValue.map(stock => typeof stock === 'string' ? stock : stock.symbol));
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
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {portfolios.map((portfolio) => (
              <TableRow key={`${portfolio.name}`}>
                <TableCell>{portfolio.name}</TableCell>
                <TableCell>{portfolio.description}</TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {portfolio.stocks.map((stock) => (
                      <Chip
                        key={stock.symbol}
                        label={stock.symbol}
                        size="small"
                        avatar={
                          <img 
                            src={stock.icon} 
                            alt={`${stock} icon`}
                            style={{ width: 20, height: 20, borderRadius: '50%' }}
                            onError={(e) => {
                              e.target.onerror = null;
                              e.target.src = 'https://cdn-icons-gif.flaticon.com/7211/7211793.gif';
                            }}
                          />
                        }
                      />
                    ))}
                  </Box>
                </TableCell>
                <TableCell align="right">
                  <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
                    <Tooltip title="Edit">
                      <IconButton
                        size="small"
                        onClick={() => handleEditPortfolio(portfolio)}
                        color="primary"
                      >
                        <EditIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton
                        size="small"
                        onClick={() => handleDeletePortfolio(portfolio.id)}
                        color="error"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog 
        open={openDialog} 
        onClose={handleCloseDialog}
        maxWidth="sm"
        fullWidth
        disableRestoreFocus
      >
        <DialogTitle>{isEditing ? 'Edit Portfolio' : 'New Portfolio'}</DialogTitle>
        <DialogContent sx={{ minWidth: 400 }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 2 }}>
            <TextField
              label="Name"
              value={newPortfolio.name}
              onChange={(e) => setNewPortfolio({ ...newPortfolio, name: e.target.value })}
              fullWidth
              autoFocus
            />
            <TextField
              label="Description"
              multiline
              rows={4}
              value={newPortfolio.description}
              onChange={(e) => setNewPortfolio({ ...newPortfolio, description: e.target.value })}
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
                renderInput={(params) => (
                  <TextField
                    {...params}
                    variant="outlined"
                    label="Select Stocks"
                    placeholder={selectedStocks.length === 0 ? "Type to search..." : ""}
                    size="small"
                  />
                )}
                renderOption={(props, option) => (
                  <Box component="li" {...props} key={`portfolio-stocks-${option.symbol}`}>
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
                    <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                      {option.name} ({option.exchange})
                    </Typography>
                  </Box>
                )}
                renderTags={(tagValue, getTagProps) =>
                  tagValue.map((option, index) => {
                    const { key, ...chipProps } = getTagProps({ index });
                    return (
                      <Chip
                        key={key}
                        label={option.symbol}
                        {...chipProps}
                        size="small"
                        avatar={
                          <img 
                            src={option.icon} 
                            alt={`${option.symbol} icon`}
                            style={{ width: 20, height: 20, borderRadius: '50%' }}
                            onError={(e) => {
                              e.target.onerror = null; // Prevent infinite loop
                              e.target.src = 'https://cdn-icons-gif.flaticon.com/7211/7211793.gif';
                            }}
                          />
                        }
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
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button 
            onClick={handleAddPortfolio}
            variant="contained"
            disabled={!newPortfolio.name || !newPortfolio.description}
          >
            {isEditing ? 'Update' : 'Add'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default StockPortfolioTable;
