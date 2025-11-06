import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f4f6f8',
      paper: '#ffffff',
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    // Override the default styles for the Card component
    MuiCard: {
      styleOverrides: {
        root: {
          // Use a more subtle shadow for a modern look
          boxShadow: 'rgba(145, 158, 171, 0.2) 0px 0px 2px 0px, rgba(145, 158, 171, 0.12) 0px 12px 24px -4px',
          // Ensure cards have a consistent height in flex containers
          height: '100%',
        },
      },
    },
    // Override the default styles for the Button component
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none', // Remove uppercase transformation on buttons
        },
      },
    },
  },
});

export default theme;