import React, {useState} from 'react';
import axios from 'axios';
import {Box, Button, Container, TextField, Typography} from '@mui/material';
import { jwtDecode } from 'jwt-decode';

interface DecodedToken {
  user_id: number;
}

interface LoginProps {
  onLoginSuccess: (token: string, email: string) => void;
}


export default function Login({onLoginSuccess}: LoginProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      const response = await axios.post('http://localhost:8000/api/v1/token/', {
        email,
        password,
      });

      // On successful login, store the token and update the app state
      const accessToken = response.data.access;
      localStorage.setItem('authToken', accessToken);

      // Extract user ID from token and store in localStorage
      try {
        const decodedToken: DecodedToken = jwtDecode(accessToken);
        localStorage.setItem("userId", String(decodedToken.user_id));
      } catch (error) {
        console.error("Failed to decode token on login", error);
      }

      onLoginSuccess(accessToken, email);
    } catch (err) {
      setError('Login failed. Please check your credentials.');
      console.error('Login error:', err);
    }
  };

  return (
      <Container maxWidth="xs">
        <Box sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center'
        }}>
          <Typography component="h1" variant="h5">
            Sign in
          </Typography>
          <Box component="form" onSubmit={handleSubmit} sx={{mt: 1}}>
            <TextField
                margin="normal"
                required
                fullWidth
                id="email"
                label="Email Address"
                name="email"
                autoComplete="email"
                autoFocus
                value={email}
                onChange={(e) => setEmail(e.target.value)}
            />
            <TextField
                margin="normal"
                required
                fullWidth
                name="password"
                label="Password"
                type="password"
                id="password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
            />
            {error && (
                <Typography color="error" variant="body2">
                  {error}
                </Typography>
            )}
            <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{mt: 3, mb: 2}}
            >
              Sign In
            </Button>
          </Box>
        </Box>
      </Container>
  );
}