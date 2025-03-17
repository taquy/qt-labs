import React, { useState, useEffect, useCallback, useRef } from 'react';
import { 
  Box, 
  Paper, 
  TextField, 
  Button, 
  Typography, 
  Alert,
  Divider,
  Link as RouterLink
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_ENDPOINTS } from '../config';

// Configure axios to include credentials
axios.defaults.withCredentials = true;
axios.defaults.headers.common['Content-Type'] = 'application/json';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const googleButtonRef = useRef(null);
  const [loading, setLoading] = useState(false);

  const handleGoogleLogin = useCallback(async (response) => {
    try {
      if (!response || !response.credential) {
        setError('Failed to get Google credentials');
        return;
      }

      const result = await fetch(API_ENDPOINTS.googleLogin, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({ token: response.credential }),
      });

      if (!result.ok) {
        const errorData = await result.json().catch(() => ({ message: 'Failed to authenticate with Google' }));
        throw new Error(errorData.message || 'Failed to authenticate with Google');
      }

      const data = await result.json();
      if (data.token) {
        localStorage.setItem('token', data.token);
        localStorage.setItem('isLoggedIn', 'true');
        // Set the token for future axios requests
        axios.defaults.headers.common['Authorization'] = `Bearer ${data.token}`;
        navigate('/');
      } else {
        throw new Error('No token received from server');
      }
    } catch (err) {
      console.error('Google login error:', err);
      setError(err.message || 'Failed to login with Google');
    }
  }, [navigate]);

  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    
    const handleLoad = () => {
      const clientId = process.env.REACT_APP_GOOGLE_CLIENT_ID;
      if (!clientId) {
        console.error('Google Client ID is not configured');
        setError('Google Sign-In is not properly configured');
        return;
      }

      try {
        window.google.accounts.id.initialize({
          client_id: clientId,
          callback: handleGoogleLogin,
          auto_select: false,
          cancel_on_tap_outside: true
        });

        // Render the Google Sign-In button
        window.google.accounts.id.renderButton(
          googleButtonRef.current,
          {
            type: 'standard',
            theme: 'outline',
            size: 'large',
            text: 'continue_with',
            width: '100%',
            logo_alignment: 'left'
          }
        );
      } catch (err) {
        console.error('Error initializing Google Sign-In:', err);
        setError('Failed to initialize Google Sign-In');
      }
    };

    script.addEventListener('load', handleLoad);
    document.head.appendChild(script);

    return () => {
      script.removeEventListener('load', handleLoad);
      if (document.head.contains(script)) {
        document.head.removeChild(script);
      }
    };
  }, [handleGoogleLogin]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

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
      console.error('Login error:', err);
      setError(err.response?.data?.message || 'Failed to login. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '80vh'
      }}
    >
      <Paper
        elevation={3}
        sx={{
          p: 4,
          width: '100%',
          maxWidth: 400,
          display: 'flex',
          flexDirection: 'column',
          gap: 2
        }}
      >
        <Typography variant="h5" component="h1" gutterBottom align="center">
          Login
        </Typography>
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <TextField
            label="Username"
            name="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            fullWidth
          />
          <TextField
            label="Password"
            name="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            fullWidth
          />
          <Button
            type="submit"
            variant="contained"
            color="primary"
            size="large"
            disabled={loading}
            fullWidth
          >
            {loading ? 'Logging in...' : 'Login'}
          </Button>
        </form>

        <Divider sx={{ my: 2 }}>OR</Divider>

        <Box 
          ref={googleButtonRef}
          sx={{
            mt: 2,
            mb: 2,
            display: 'flex',
            justifyContent: 'center',
            '& > div': {
              width: '100% !important'
            }
          }}
        />

        <Typography variant="body2" align="center" sx={{ mt: 2 }}>
          Don't have an account?{' '}
          <RouterLink to="/register">
            Register here
          </RouterLink>
        </Typography>
      </Paper>
    </Box>
  );
};

export default Login; 