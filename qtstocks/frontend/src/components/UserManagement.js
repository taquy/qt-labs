import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Paper,
  Typography,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  Stack,
  Chip,
  Tooltip,
  CircularProgress,
  Switch
} from '@mui/material';
import { Edit as EditIcon, Delete as DeleteIcon, Add as AddIcon } from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import { fetchUsers, updateUser, createUser, deleteUser, toggleActive, toggleAdmin, setError, setUsersQuery } from '../store/actions/user';
import { LoaderActions, ErrorActions } from '../store/slices/user';


const UserManagement = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    is_admin: false
  });
  const [forceFetchUsers, setForceFetchUsers] = useState(false);
  const [fetchNextPage, setFetchNextPage] = useState(false);

  const dispatch = useDispatch();
  const { user: currentUser } = useSelector(state => state.auth);
  const { users, error, users_query, loaders } = useSelector(state => state.user);

  useEffect(() => {
    if (!forceFetchUsers && users_query.page === users.current_page && users.has_next && !fetchNextPage) return;
    const timer = setTimeout(() => {
      dispatch(fetchUsers());
      setForceFetchUsers(false);
      setFetchNextPage(false);
    }, 500);
    return () => clearTimeout(timer);
  }, [users_query, dispatch, users.has_next, fetchNextPage, forceFetchUsers, users.current_page]);

  useEffect(() => {
    const errorKeys = Object.keys(error);
    if (errorKeys.length > 0) {
      errorKeys.forEach((key) => {
        if (error[key]) {
          const timer = setTimeout(() => {
            dispatch(setError(key, ''));
          }, 3000);
          return () => clearTimeout(timer);
        }
      });
    }
  }, [error, dispatch]);

  const handleSort = (column) => {
    const sortDirection = users_query.sort_by === column && users_query.sort_direction === 'asc' ? 'desc' : 'asc';
    dispatch(setUsersQuery({
      ...users_query,
      page: 1,
      sort_by: column,
      sort_direction: sortDirection,
      refresh: true
    }));
    setForceFetchUsers(true);
  };

  const handleScroll = useCallback((event) => {
    const { scrollTop, scrollHeight, clientHeight } = event.target;
    // Check if scrolled to bottom (with 20px threshold)
    if (
      users_query.page === users.current_page && users.has_next && !fetchNextPage &&
      scrollHeight - scrollTop <= clientHeight + 20) {
        const page = users_query.page + 1;
        dispatch(setUsersQuery({ ...users_query, page }));
        setFetchNextPage(true);
    }
  }, [dispatch, users_query, users.current_page, users.has_next, fetchNextPage]);

  const handleOpenDialog = (user = null) => {
    if (user) {
      setSelectedUser(user);
      setFormData({
        name: user.name || '',
        email: user.email || '',
        password: '',
      });
    } else {
      setSelectedUser(null);
      setFormData({
        name: '',
        email: '',
        password: '',
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedUser(null);
    setFormData({
      name: '',
      email: '',
      password: '',
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name || !formData.email) return;
    if (selectedUser) {
      await dispatch(updateUser(selectedUser.id, formData));
    } else {
      await dispatch(createUser(formData));
    }
    handleCloseDialog();
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleDelete = async (userId) => {
    await dispatch(deleteUser(userId));
  };

  const handleToggleActive = async (userId) => {
    if (!userId) return;
    await dispatch(toggleActive(userId));
  };

  const handleToggleAdmin = async (userId) => {
    if (!userId) return;
    await dispatch(toggleAdmin(userId));
  };

  const getFeatureChipColor = (feature) => {
    const colors = {
      'google': 'info',
    };
    return colors[feature] || 'default';
  };

  const formatLastLogin = (lastLogin) => {
    if (!lastLogin) return 'Never';
    return new Date(lastLogin).toLocaleString();
  };

  const getUserFeatures = (user) => {
    const features = [];
    if (user.is_google_user) {
      features.push('google');
    }
    features.sort((a, b) => a.localeCompare(b));
    return features;
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          User Management
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <TextField
            size="small"
            placeholder="Search users..."
            value={users_query.search}
            onChange={(e) => {
              dispatch(setUsersQuery({
                ...users_query,
                search: e.target.value,
                page: 1,
                refresh: true
              }));
              setForceFetchUsers(true);
            }}
            sx={{ width: 300 }}
          />
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
          >
            Add User
          </Button>
        </Box>
      </Box>

      {error[ErrorActions.FETCH_USERS] && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error[ErrorActions.FETCH_USERS]}
        </Alert>
      )}

      <TableContainer sx={{ maxHeight: 'calc(100vh - 200px)' }} onScroll={handleScroll}>
        <Table stickyHeader size="small">
          <TableHead>
            <TableRow>
              <TableCell 
                sx={{ py: 1, fontSize: '0.875rem', cursor: 'pointer' }}
                onClick={() => handleSort('name')}
              >
                Name {users_query.sort_by === 'name' && (users_query.sort_direction === 'asc' ? '↑' : '↓')}
              </TableCell>
              <TableCell 
                sx={{ py: 1, fontSize: '0.875rem', cursor: 'pointer' }}
                onClick={() => handleSort('email')}
              >
                Email {users_query.sort_by === 'email' && (users_query.sort_direction === 'asc' ? '↑' : '↓')}
              </TableCell>
              <TableCell sx={{ py: 1, fontSize: '0.875rem' }}>Features</TableCell>
              <TableCell 
                sx={{ py: 1, fontSize: '0.875rem', cursor: 'pointer' }}
                onClick={() => handleSort('last_login')}
              >
                Last Login {users_query.sort_by === 'last_login' && (users_query.sort_direction === 'asc' ? '↑' : '↓')}
              </TableCell>
              <TableCell 
                sx={{ py: 1, fontSize: '0.875rem', cursor: 'pointer' }}
                onClick={() => handleSort('is_active')}
              >
                Active {users_query.sort_by === 'is_active' && (users_query.sort_direction === 'asc' ? '↑' : '↓')}
              </TableCell>
              <TableCell 
                sx={{ py: 1, fontSize: '0.875rem', cursor: 'pointer' }}
                onClick={() => handleSort('is_admin')}
              >
                Admin {users_query.sort_by === 'is_admin' && (users_query.sort_direction === 'asc' ? '↑' : '↓')}
              </TableCell>
              <TableCell sx={{ py: 1, fontSize: '0.875rem' }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users.items.map((user, index) => (
              <TableRow
                key={user.id}
                sx={{ '& > td': { py: 1, fontSize: '0.875rem' } }}
              >
                <TableCell>{user.name}</TableCell>
                <TableCell>{user.email}</TableCell>
                <TableCell>
                  <Stack direction="row" spacing={0.5} flexWrap="wrap" useFlexGap>
                    {getUserFeatures(user).map((feature) => (
                      <Chip
                        key={feature}
                        label={feature.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        color={getFeatureChipColor(feature)}
                        size="small"
                        sx={{ height: '20px' }}
                      />
                    ))}
                  </Stack>
                </TableCell>
                <TableCell>{formatLastLogin(user.last_login)}</TableCell>
                <TableCell>
                  <Stack direction="row" spacing={1}>
                    <Box sx={{ position: 'relative' }}>
                      <Switch
                        checked={Boolean(user.is_active)}
                        onChange={() => handleToggleActive(user.id)}
                        disabled={loaders[LoaderActions.TOGGLE_ACTIVE] || user.id === currentUser?.id}
                        color="primary"
                        size="small"
                      />
                      {loaders[LoaderActions.TOGGLE_ACTIVE] && (
                        <CircularProgress
                          size={16}
                          sx={{
                            position: 'absolute',
                            top: '50%',
                            left: '50%',
                            marginTop: '-8px',
                            marginLeft: '-8px',
                          }}
                        />
                      )}
                    </Box>
                  </Stack>
                </TableCell>
                <TableCell>
                  <Stack direction="row" spacing={1}>
                    <Box sx={{ position: 'relative' }}>
                      <Switch
                        checked={Boolean(user.is_admin)}
                        onChange={() => handleToggleAdmin(user.id)}
                        disabled={loaders[LoaderActions.TOGGLE_ADMIN] || user.id === currentUser?.id}
                        color="secondary"
                        size="small"
                      />
                      {loaders[LoaderActions.TOGGLE_ADMIN] && (
                        <CircularProgress
                          size={16}
                          sx={{
                            position: 'absolute',
                            top: '50%',
                            left: '50%',
                            marginTop: '-8px',
                            marginLeft: '-8px',
                          }}
                        />
                      )}
                    </Box>
                  </Stack>
                </TableCell>
                <TableCell>
                  <Stack direction="row" spacing={0.5}>
                    <Tooltip title="Edit">
                      <IconButton 
                        size="small" 
                        onClick={() => handleOpenDialog(user)}
                        disabled={user.id === currentUser?.id}
                        sx={{ padding: '4px' }}
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton 
                        size="small" 
                        onClick={() => handleDelete(user.id)}
                        disabled={loaders[LoaderActions.DELETE_USER] || user.id === currentUser?.id}
                        sx={{ padding: '4px' }}
                      >
                        {loaders[LoaderActions.DELETE_USER] ? (
                          <CircularProgress size={16} />
                        ) : (
                          <DeleteIcon fontSize="small" />
                        )}
                      </IconButton>
                    </Tooltip>
                  </Stack>
                </TableCell>
              </TableRow>
            ))}
            {loaders[LoaderActions.FETCH_USERS] && (
              <TableRow>
                <TableCell colSpan={7} align="center" sx={{ py: 1 }}>
                  <CircularProgress size={20} />
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog 
        open={openDialog}
        onClose={handleCloseDialog}
        aria-labelledby="dialog-title"
        aria-describedby="dialog-description"
        keepMounted={false}
        disablePortal
        disableEnforceFocus
        disableAutoFocus
      >
        <DialogTitle id="dialog-title">
          {selectedUser ? 'Edit User' : 'Create User'}
        </DialogTitle>
        <DialogContent id="dialog-description">
          <Box 
            component="form" 
            onSubmit={handleSubmit} 
            sx={{ mt: 2 }}
            noValidate
          >
            <TextField
              fullWidth
              label="Name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              margin="normal"
              required
              autoFocus
            />
            <TextField
              fullWidth
              label="Email"
              type="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Password"
              type="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              margin="normal"
              required={!selectedUser}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button 
            onClick={handleSubmit} 
            variant="contained" 
            color="primary"
            type="submit"
          >
            {selectedUser ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default UserManagement; 