import {useState} from 'react';
import Login from './components/Login';
import Profile from './components/Profile';
import {Box, CssBaseline} from '@mui/material';
import TopBar from "./components/TopBar.tsx";

function App() {
  const [token, setToken] = useState<string | null>(localStorage.getItem('authToken'));
  const [userEmail, setUserEmail] = useState<string | null>(localStorage.getItem('userEmail'));

  // This function is called on successful login
  function handleLoginSuccess(newToken: string, email: string) {
    localStorage.setItem('authToken', newToken);
    localStorage.setItem('userEmail', email);
    setToken(newToken);
    setUserEmail(email);
  }

  // This function handles logout
  function handleLogout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userEmail');
    setToken(null);
    setUserEmail(null);
  }

  return (
      <>
        <CssBaseline/>
        {token && userEmail ? (
            // If logged in, show the TopBar and Profile page
            <>
              <TopBar email={userEmail} onLogout={handleLogout}/>
              <Box marginTop={10} marginBottom={10}>
                <Profile token={token}/>
              </Box>
            </>
        ) : (
            // If not logged in, show the Login page
            <Login onLoginSuccess={handleLoginSuccess}/>
        )}
      </>
  );
}

export default App;