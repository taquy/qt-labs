import React, { useState, useEffect } from 'react';
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
  Tooltip
} from '@mui/material';
import { Edit as EditIcon, Delete as DeleteIcon, Add as AddIcon } from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import axios from 'axios';
const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    role: 'user',
    features: []
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const dispatch = useDispatch();
  const { user: currentUser } = useSelector(state => state.auth);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await axios.get('/api/users', { withCredentials: true });
      setUsers(response.data);
    } catch (err) {
      setError('Failed to fetch users');
    }
  };

  const handleOpenDialog = (user = null) => {
    if (user) {
      setSelectedUser(user);
      setFormData({
        username: user.username,
        email: user.email,
        role: user.role,
        features: user.features || []
      });
    } else {
      setSelectedUser(null);
      setFormData({
        username: '',
        email: '',
        role: 'user',
        features: []
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedUser(null);
    setFormData({
      username: '',
      email: '',
      role: 'user',
      features: []
    });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      if (selectedUser) {
        await axios.put(`/api/users/${selectedUser.id}`, formData, { withCredentials: true });
        setSuccess('User updated successfully');
      } else {
        await axios.post('/api/users', formData, { withCredentials: true });
        setSuccess('User created successfully');
      }
      fetchUsers();
      handleCloseDialog();
    } catch (err) {
      setError(err.response?.data?.message || 'An error occurred');
    }
  };

  const handleDelete = async (userId) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      try {
        await axios.delete(`/api/users/${userId}`, { withCredentials: true });
        setSuccess('User deleted successfully');
        fetchUsers();
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to delete user');
      }
    }
  };

  const getFeatureChipColor = (feature) => {
    const colors = {
      'stock_analysis': 'primary',
      'user_management': 'secondary',
      'settings': 'info',
      'export': 'success'
    };
    return colors[feature] || 'default';
  };

  const formatLastLogin = (lastLogin) => {
    if (!lastLogin) return 'Never';
    return new Date(lastLogin).toLocaleString();
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

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Features</TableCell>
              <TableCell>Last Login</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users.map((user) => (
              <TableRow key={user.id}>
                <TableCell>{user.username}</TableCell>
                <TableCell>{user.email}</TableCell>
                <TableCell>
                  <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                    {(user.features || []).map((feature) => (
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
                        disabled={user.id === currentUser?.id}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </Stack>
                </TableCell>
              </TableRow>
            ))}
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
                label="Username"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                fullWidth
                required
              />
              <TextField
                label="Email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                fullWidth
                required
              />
              <TextField
                select
                label="Role"
                value={formData.role}
                onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                fullWidth
                required
              >
                <option value="user">User</option>
                <option value="admin">Admin</option>
              </TextField>
              <TextField
                select
                multiple
                label="Features"
                value={formData.features}
                onChange={(e) => setFormData({ ...formData, features: e.target.value })}
                fullWidth
                required
                SelectProps={{
                  multiple: true,
                  renderValue: (selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((value) => (
                        <Chip
                          key={value}
                          label={value.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          color={getFeatureChipColor(value)}
                          size="small"
                        />
                      ))}
                    </Box>
                  ),
                }}
              >
                <option value="stock_analysis">Stock Analysis</option>
                <option value="user_management">User Management</option>
                <option value="settings">Settings</option>
                <option value="export">Export</option>
              </TextField>
            </Stack>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Cancel</Button>
            <Button type="submit" variant="contained">
              {selectedUser ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Paper>
  );
};

export default UserManagement; 