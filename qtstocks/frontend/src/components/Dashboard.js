import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Alert,
  Grid,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  AppBar,
  Toolbar,
  useTheme,
  useMediaQuery,
  Divider,
  Paper
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  Assessment as AssessmentIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
  Person as PersonIcon
} from '@mui/icons-material';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import StockSelector from './StockSelector';
import StockGraph from './StockGraph';
import StockTable from './StockTable';
import { useDispatch, useSelector } from 'react-redux';
import { logout } from '../store/actions/auth';

// Configure axios to include credentials
axios.defaults.withCredentials = true;
axios.defaults.headers.common['Content-Type'] = 'application/json';

const drawerWidth = 240;

const Dashboard = () => {
  const { error, isLoggedIn, user } = useSelector(state => state.auth);
  const { stats } = useSelector(state => state.stocks);
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileOpen, setMobileOpen] = useState(false);
  const [activeView, setActiveView] = useState('analysis');

  useEffect(() => {
    if (!isLoggedIn) navigate('/login');
  }, [navigate, isLoggedIn]);

  const handleLogout = () => {
    dispatch(logout());
  };

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const drawer = (
    <Box>
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          Stock Admin
        </Typography>
      </Toolbar>
      <Divider />
      <List>
        <ListItem 
          button 
          selected={activeView === 'dashboard'}
          onClick={() => setActiveView('dashboard')}
        >
          <ListItemIcon>
            <DashboardIcon />
          </ListItemIcon>
          <ListItemText primary="Dashboard" />
        </ListItem>
        <ListItem 
          button 
          selected={activeView === 'analysis'}
          onClick={() => setActiveView('analysis')}
        >
          <ListItemIcon>
            <AssessmentIcon />
          </ListItemIcon>
          <ListItemText primary="Stock Analysis" />
        </ListItem>
        <ListItem 
          button 
          selected={activeView === 'settings'}
          onClick={() => setActiveView('settings')}
        >
          <ListItemIcon>
            <SettingsIcon />
          </ListItemIcon>
          <ListItemText primary="Settings" />
        </ListItem>
      </List>
      <Divider />
      <List>
        <ListItem>
          <ListItemIcon>
            <PersonIcon />
          </ListItemIcon>
          <ListItemText 
            primary={user?.email || 'User'} 
            secondary="Administrator"
          />
        </ListItem>
        <ListItem button onClick={handleLogout}>
          <ListItemIcon>
            <LogoutIcon />
          </ListItemIcon>
          <ListItemText primary="Logout" />
        </ListItem>
      </List>
    </Box>
  );

  const renderContent = () => {
    switch (activeView) {
      case 'dashboard':
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 240 }}>
                <Typography variant="h6" gutterBottom>
                  Quick Stats
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="h4" color="primary">
                        {stats?.length || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Total Stocks
                      </Typography>
                    </Paper>
                  </Grid>
                  {/* Add more stat cards as needed */}
                </Grid>
              </Paper>
            </Grid>
          </Grid>
        );
      case 'analysis':
        return (
          <>
            <StockSelector />
            <StockGraph />
            <StockTable />
          </>
        );
      case 'settings':
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Settings
                </Typography>
                {/* Add settings content here */}
              </Paper>
            </Grid>
          </Grid>
        );
      default:
        return null;
    }
  };

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div">
            Stock Analysis Dashboard
          </Typography>
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        {isMobile ? (
          <Drawer
            variant="temporary"
            open={mobileOpen}
            onClose={handleDrawerToggle}
            ModalProps={{
              keepMounted: true, // Better open performance on mobile.
            }}
            sx={{
              display: { xs: 'block', sm: 'none' },
              '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
            }}
          >
            {drawer}
          </Drawer>
        ) : (
          <Drawer
            variant="permanent"
            sx={{
              display: { xs: 'none', sm: 'block' },
              '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
            }}
            open
          >
            {drawer}
          </Drawer>
        )}
      </Box>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          mt: '64px',
          maxWidth: '100%',
          overflow: 'hidden'
        }}
      >
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        {renderContent()}
      </Box>
    </Box>
  );
};

export default Dashboard; 