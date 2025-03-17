import React, { useState, useEffect, useCallback } from 'react';
import { 
  Box, 
  Container, 
  Paper, 
  TextField, 
  Button, 
  Typography, 
  Alert,
  Divider
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_ENDPOINTS } from '../config';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faGoogle } from '@fortawesome/free-brands-svg-icons';

// Configure axios to include credentials
axios.defaults.withCredentials = true;
axios.defaults.headers.common['Content-Type'] = 'application/json';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleGoogleLogin = useCallback(async (response) => {
    try {
      const googleResponse = await axios.post(API_ENDPOINTS.googleLogin, {
        token: response.credential
      });

      if (googleResponse.data.success) {
        localStorage.setItem('token', googleResponse.data.token);
        localStorage.setItem('isLoggedIn', 'true');
        axios.defaults.headers.common['Authorization'] = `Bearer ${googleResponse.data.token}`;
        navigate('/');
      } else {
        setError(googleResponse.data.message || 'Google login failed');
      }
    } catch (err) {
      console.error('Google login error:', err);
      setError('Failed to login with Google');
    }
  }, [navigate]);

  const initializeGoogleAuth = useCallback(() => {
    if (window.google) {
      window.google.accounts.id.initialize({
        client_id: process.env.REACT_APP_GOOGLE_CLIENT_ID,
        callback: handleGoogleLogin
      });
    }
  }, [handleGoogleLogin]);

  useEffect(() => {
    // Load Google API
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    
    const handleLoad = () => {
      initializeGoogleAuth();
    };

    script.addEventListener('load', handleLoad);
    document.head.appendChild(script);

    return () => {
      script.removeEventListener('load', handleLoad);
      if (document.head.contains(script)) {
        document.head.removeChild(script);
      }
    };
  }, [initializeGoogleAuth]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const response = await axios.post(API_ENDPOINTS.login, {
        username,
        password
      });
      
      if (response.data.success) {
        localStorage.setItem('token', response.data.token);
        localStorage.setItem('isLoggedIn', 'true');
        axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.token}`;
        navigate('/');
      } else {
        setError(response.data.message || 'Login failed');
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to login');
    }
  };

  const initiateGoogleLogin = useCallback(() => {
    if (window.google) {
      window.google.accounts.id.prompt();
    }
  }, []);

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 8 }}>
        <Paper sx={{ p: 4 }}>
          <Typography variant="h5" component="h1" gutterBottom align="center">
            Login
          </Typography>
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              margin="normal"
              required
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              color="primary"
              sx={{ mt: 3, mb: 2 }}
            >
              Login
            </Button>
          </form>

          <Divider sx={{ my: 2 }}>OR</Divider>

          <Button
            fullWidth
            variant="outlined"
            onClick={initiateGoogleLogin}
            sx={{
              mt: 2,
              mb: 2,
              color: '#757575',
              borderColor: '#757575',
              '&:hover': {
                borderColor: '#616161',
                backgroundColor: 'rgba(0, 0, 0, 0.04)'
              },
              textTransform: 'none',
              fontSize: '1rem'
            }}
            startIcon={<FontAwesomeIcon icon={faGoogle} style={{ color: '#4285F4' }} />}
          >
            Continue with Google
          </Button>
        </Paper>
      </Box>
    </Container>
  );
};

export default Login; 