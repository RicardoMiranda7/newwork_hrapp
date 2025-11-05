import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';

interface TopBarProps {
  email: string;
  onLogout: () => void;
}

export default function TopBar({ email, onLogout }:TopBarProps) {
  return (
      <>
        <AppBar position="fixed">
          <Toolbar>
            <IconButton
                size="large"
                edge="start"
                color="inherit"
                aria-label="menu"
                sx={{ mr: 2 }}
            >
            </IconButton>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              NewWork HR | Logged in as: {email}
            </Typography>
            <Button variant="contained" color="error" onClick={onLogout} >Logout</Button>
          </Toolbar>
        </AppBar>
      </>
  );
}
