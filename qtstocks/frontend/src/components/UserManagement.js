import React, { useState, useEffect, useRef, useCallback } from 'react';
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
  Checkbox,
  CircularProgress,
  FormControlLabel,
  Switch
} from '@mui/material';
import { Edit as EditIcon, Delete as DeleteIcon, Add as AddIcon } from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import { fetchUsers, updateUser, createUser, deleteUser, toggleActiveRequest, toggleAdminRequest } from '../store/actions/user';

const ITEMS_PER_PAGE = 20;

const UserManagement = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    is_admin: false
  });
  const [loadingStates, setLoadingStates] = useState({});
  const [showError, setShowError] = useState(false);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  const observer = useRef();

  const dispatch = useDispatch();
  const { user: currentUser } = useSelector(state => state.auth);
  const { users, error, hasMore: apiHasMore, total, pages, currentPage } = useSelector(state => state.user);
  
  const lastUserElementRef = useCallback(node => {
    if (loading) return;
    if (observer.current) observer.current.disconnect();
    observer.current = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && hasMore) {
        setPage(prevPage => prevPage + 1);
        setLoading(true);
        dispatch(fetchUsers(page + 1, ITEMS_PER_PAGE))
          .then(() => {
            setLoading(false);
          })
          .catch(() => {
            setLoading(false);
          });
      }
    });
    if (node) observer.current.observe(node);
  }, [loading, hasMore, page, dispatch]);

  useEffect(() => {
    if (page === 1) {
      dispatch(fetchUsers(1, ITEMS_PER_PAGE));
    }
  }, [dispatch, page]);

  useEffect(() => {
    if (error) {
      setShowError(true);
      const timer = setTimeout(() => {
        setShowError(false);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  const handleOpenDialog = (user = null) => {
    if (user) {
      setSelectedUser(user);
      setFormData({
        name: user.name || '',
        email: user.email || '',
        password: '',
        is_admin: user.is_admin || false
      });
    } else {
      setSelectedUser(null);
      setFormData({
        name: '',
        email: '',
        password: '',
        is_admin: false
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
      is_admin: false
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name || !formData.email) return;

    try {
      if (selectedUser) {
        await dispatch(updateUser(selectedUser.id, formData));
      } else {
        await dispatch(createUser(formData));
      }
      handleCloseDialog();
    } catch (error) {
      console.error('Error submitting form:', error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleDelete = async (userId) => {
    setLoadingStates(prev => ({ ...prev, [`delete_${userId}`]: true }));
    try {
      await dispatch(deleteUser(userId));
      // Reset to first page and refresh
      setPage(1);
      dispatch(fetchUsers(1, ITEMS_PER_PAGE));
    } catch (error) {
      console.error('Error deleting user:', error);
    } finally {
      setLoadingStates(prev => ({ ...prev, [`delete_${userId}`]: false }));
    }
  };

  const handleToggleActive = async (userId) => {
    if (!userId) return;
    setLoadingStates(prev => ({ ...prev, [`active_${userId}`]: true }));
    try {
      await dispatch(toggleActiveRequest(userId));
    } finally {
      setLoadingStates(prev => ({ ...prev, [`active_${userId}`]: false }));
    }
  };

  const handleToggleAdmin = async (userId) => {
    if (!userId) return;
    setLoadingStates(prev => ({ ...prev, [`admin_${userId}`]: true }));
    try {
      await dispatch(toggleAdminRequest(userId));
    } finally {
      setLoadingStates(prev => ({ ...prev, [`admin_${userId}`]: false }));
    }
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
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add User
        </Button>
      </Box>

      {showError && error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <TableContainer sx={{ maxHeight: 'calc(100vh - 200px)' }}>
        <Table stickyHeader size="small">
          <TableHead>
            <TableRow>
              <TableCell sx={{ py: 1, fontSize: '0.875rem' }}>Name</TableCell>
              <TableCell sx={{ py: 1, fontSize: '0.875rem' }}>Email</TableCell>
              <TableCell sx={{ py: 1, fontSize: '0.875rem' }}>Features</TableCell>
              <TableCell sx={{ py: 1, fontSize: '0.875rem' }}>Last Login</TableCell>
              <TableCell sx={{ py: 1, fontSize: '0.875rem' }}>Active</TableCell>
              <TableCell sx={{ py: 1, fontSize: '0.875rem' }}>Admin</TableCell>
              <TableCell sx={{ py: 1, fontSize: '0.875rem' }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users.map((user, index) => (
              <TableRow
                key={user.id}
                ref={index === users.length - 1 ? observer : null}
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
                      <Checkbox
                        checked={user.is_active}
                        onChange={() => handleToggleActive(user.id)}
                        disabled={loadingStates[`active_${user.id}`] || user.id === currentUser?.id}
                        color="primary"
                        size="small"
                      />
                      {loadingStates[`active_${user.id}`] && (
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
                      <Checkbox
                        checked={user.is_admin}
                        onChange={() => handleToggleAdmin(user.id)}
                        disabled={loadingStates[`admin_${user.id}`] || user.id === currentUser?.id}
                        color="secondary"
                        size="small"
                      />
                      {loadingStates[`admin_${user.id}`] && (
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
                        disabled={loadingStates[`delete_${user.id}`] || user.id === currentUser?.id}
                        sx={{ padding: '4px' }}
                      >
                        {loadingStates[`delete_${user.id}`] ? (
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
            {loading && (
              <TableRow>
                <TableCell colSpan={7} align="center" sx={{ py: 1 }}>
                  <CircularProgress size={20} />
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={openDialog} onClose={handleCloseDialog}>
        <DialogTitle>{selectedUser ? 'Edit User' : 'Create User'}</DialogTitle>
        <DialogContent>
          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="Name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              margin="normal"
              required
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
            <FormControlLabel
              control={
                <Switch
                  name="is_admin"
                  checked={formData.is_admin}
                  onChange={handleInputChange}
                />
              }
              label="Admin"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained" color="primary">
            {selectedUser ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default UserManagement; 