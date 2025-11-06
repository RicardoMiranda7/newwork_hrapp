import {type FormEvent, useState} from 'react';
import {Avatar, Box, Button, TextField, Typography} from '@mui/material';
import {jwtDecode} from 'jwt-decode';
import LogInContainer from "./LogInContainer.tsx";
import {toast} from "sonner";
import apiClient from "../utils/apiClient.ts";
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';

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

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    try {
      const response = await apiClient.post('/api/v1/token/', {
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
      toast.success("Login successful");
    } catch (err) {
      setError('Login failed. Please check your credentials.');
      console.error('Login error:', err);
    }
  };

  return (
      <LogInContainer animation={"slide"}>
        <Box sx={{
          marginTop: 2,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center'
        }}>
          <Avatar sx={{ m: 1, bgcolor: 'secondary.main' }}>
            <LockOutlinedIcon />
          </Avatar>
          <Typography component="h1" variant="h5">
            Sign in
          </Typography>
          {/* Login form with email, password and submit button */}
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
      </LogInContainer>
  );
}