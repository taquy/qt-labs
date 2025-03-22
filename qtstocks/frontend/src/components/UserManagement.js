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
  CircularProgress
} from '@mui/material';
import { Edit as EditIcon, Delete as DeleteIcon, Add as AddIcon } from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import { fetchUsers, updateUser, createUser, deleteUser, toggleActive, toggleAdmin } from '../store/actions/user';

const ITEMS_PER_PAGE = 20;

const UserManagement = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [formData, setFormData] = useState({
    name: ''
  });
  const [loadingStates, setLoadingStates] = useState({});
  const [showError, setShowError] = useState(false);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  const observer = useRef();
  const lastUserElementRef = useCallback(node => {
    if (loading) return;
    if (observer.current) observer.current.disconnect();
    observer.current = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && hasMore) {
        setPage(prevPage => prevPage + 1);
      }
    });
    if (node) observer.current.observe(node);
  }, [loading, hasMore]);

  const dispatch = useDispatch();
  const { user: currentUser } = useSelector(state => state.auth);
  const { users, error } = useSelector(state => state.user);
  
  useEffect(() => {
    if (page === 1) {
      dispatch(fetchUsers(1, ITEMS_PER_PAGE));
    }
  }, [dispatch]);

  useEffect(() => {
    if (error) {
      setShowError(true);
      const timer = setTimeout(() => {
        setShowError(false);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  useEffect(() => {
    if (page > 1) {
      setLoading(true);
      dispatch(fetchUsers(page, ITEMS_PER_PAGE))
        .finally(() => setLoading(false));
    }
  }, [dispatch, page]);

  const handleOpenDialog = (user = null) => {
    if (user) {
      setSelectedUser(user);
      setFormData({
        name: user.name
      });
    } else {
      setSelectedUser(null);
      setFormData({
        name: ''
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedUser(null);
    setFormData({
      name: ''
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (selectedUser) {
        await dispatch(updateUser(selectedUser.id, formData));
      } else {
        await dispatch(createUser(formData));
      }
      handleCloseDialog();
      // Reset to first page and refresh
      setPage(1);
      dispatch(fetchUsers(1, ITEMS_PER_PAGE));
    } catch (error) {
      console.error('Error submitting form:', error);
    }
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
    setLoadingStates(prev => ({ ...prev, [`active_${userId}`]: true }));
    try {
      await dispatch(toggleActive(userId));
    } finally {
      setLoadingStates(prev => ({ ...prev, [`active_${userId}`]: false }));
    }
  };

  const handleToggleAdmin = async (userId) => {
    setLoadingStates(prev => ({ ...prev, [`admin_${userId}`]: true }));
    try {
      await dispatch(toggleAdmin(userId));
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

      <TableContainer sx={{ maxHeight: 'calc(100vh - 300px)' }}>
        <Table stickyHeader>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Features</TableCell>
              <TableCell>Last Login</TableCell>
              <TableCell>Active</TableCell>
              <TableCell>Admin</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users.map((user, index) => (
              <TableRow
                key={user.id}
                ref={index === users.length - 1 ? lastUserElementRef : null}
              >
                <TableCell>{user.name}</TableCell>
                <TableCell>{user.email}</TableCell>
                <TableCell>
                  <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                    {getUserFeatures(user).map((feature) => (
                      <Chip
                        key={feature}
                        label={feature.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        color={getFeatureChipColor(feature)}
                        size="small"
                      />
                    ))}
                  </Stack>
                </TableCell>
                <TableCell>{formatLastLogin(user.last_login)}</TableCell>
                <TableCell>
                  <Stack direction="row" spacing={2}>
                    <Box sx={{ position: 'relative' }}>
                      <Checkbox
                        checked={user.is_active}
                        onChange={() => handleToggleActive(user.id)}
                        disabled={loadingStates[`active_${user.id}`] || user.id === currentUser?.id}
                        color="primary"
                      />
                      {loadingStates[`active_${user.id}`] && (
                        <CircularProgress
                          size={20}
                          sx={{
                            position: 'absolute',
                            top: '50%',
                            left: '50%',
                            marginTop: '-10px',
                            marginLeft: '-10px',
                          }}
                        />
                      )}
                    </Box>
                  </Stack>
                </TableCell>
                <TableCell>
                  <Stack direction="row" spacing={2}>
                    <Box sx={{ position: 'relative' }}>
                      <Box sx={{ position: 'relative' }}>
                        <Checkbox
                          checked={user.is_admin}
                          onChange={() => handleToggleAdmin(user.id)}
                          disabled={loadingStates[`admin_${user.id}`] || user.id === currentUser?.id}
                          color="secondary"
                        />
                        {loadingStates[`admin_${user.id}`] && (
                          <CircularProgress
                            size={20}
                            sx={{
                              position: 'absolute',
                              top: '50%',
                              left: '50%',
                              marginTop: '-10px',
                              marginLeft: '-10px',
                            }}
                          />
                        )}
                      </Box>
                      {loadingStates[`admin_${user.id}`] && (
                        <CircularProgress
                          size={20}
                          sx={{
                            position: 'absolute',
                            top: '50%',
                            left: '50%',
                            marginTop: '-10px',
                            marginLeft: '-10px',
                          }}
                        />
                      )}
                    </Box>
                  </Stack>
                </TableCell>
                <TableCell>
                  <Stack direction="row" spacing={1}>
                    <Tooltip title="Edit">
                      <IconButton 
                        size="small" 
                        onClick={() => handleOpenDialog(user)}
                        disabled={user.id === currentUser?.id}
                      >
                        <EditIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton 
                        size="small" 
                        onClick={() => handleDelete(user.id)}
                        disabled={loadingStates[`delete_${user.id}`] || user.id === currentUser?.id}
                      >
                        {loadingStates[`delete_${user.id}`] ? (
                          <CircularProgress size={20} />
                        ) : (
                          <DeleteIcon />
                        )}
                      </IconButton>
                    </Tooltip>
                  </Stack>
                </TableCell>
              </TableRow>
            ))}
            {loading && (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  <CircularProgress />
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={openDialog} onClose={handleCloseDialog}>
        <DialogTitle>
          {selectedUser ? 'Edit User' : 'Add New User'}
        </DialogTitle>
        <form onSubmit={handleSubmit}>
          <DialogContent>
            <Stack spacing={2} sx={{ mt: 1 }}>
              <TextField
                label="Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                fullWidth
                required
              />
            </Stack>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Cancel</Button>
            <Button type="submit" variant="contained" color="primary">
              {selectedUser ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Paper>
  );
};

export default UserManagement; 