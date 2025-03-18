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
import { useDispatch, useSelector } from 'react-redux';
import { login, googleLogin } from '../store/sagas/stockGraphSaga';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();
  const googleButtonRef = useRef(null);
  const dispatch = useDispatch();
  const { isLoggedIn, error } = useSelector(state => state.stockGraph);

  const handleGoogleLogin = useCallback(async (response) => {
    dispatch(googleLogin(response.credential));
  }, [dispatch]);

  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    const handleLoad = () => {
      const clientId = process.env.REACT_APP_GOOGLE_CLIENT_ID;

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
    dispatch(login(username, password));
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
            fullWidth
          >
            Sign In
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