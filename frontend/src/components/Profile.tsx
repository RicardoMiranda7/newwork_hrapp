import {useEffect, useState} from 'react';
import axios from 'axios';
import {
  Alert,
  Box,
  Card,
  CardContent,
  CircularProgress,
  Container,
  Grid,
  Typography
} from '@mui/material';
import Feedback from "./Feedback.tsx";

// Define the props interface, expecting the auth token
interface ProfileProps {
  token: string;
}

// Define a flexible interface for the profile data
interface ProfileData {
  [key: string]: any;
}

export default function Profile({token}: ProfileProps) {
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/v1/profiles/1/', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setProfile(response.data);
      } catch (err) {
        setError('Failed to fetch profile data.');
        console.error('Fetch profile error:', err);
      } finally {
        setLoading(false);
      }
    };

    if (token) {
      fetchProfile();
    }
  }, [token]);

  if (loading) {
    return <CircularProgress/>;
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  return (
      <Container maxWidth="lg">
        <Box sx={{my: 4}}>
          <Typography variant="h4" component="h1" gutterBottom>
            Employee Profile
          </Typography>
          {profile && (
              <Grid container spacing={3} sx={{alignItems: "flex-start"}}>
                <Grid size={{xs: 12, md: 6}}>
                  <Card>
                    <CardContent>
                      <Typography variant="h5" gutterBottom>
                        Details
                      </Typography>

                      {Object.entries(profile).map(([key, value]) => (
                          <Typography key={key} variant="body1">
                            <strong>{key.replace(/_/g, ' ').toUpperCase()}:</strong> {String(value)}
                          </Typography>
                      ))}
                    </CardContent>
                  </Card>
                </Grid>
                <Grid size={{xs: 12, md: 6}}>
                  <Feedback profileId={profile.id} token={token}/>
                </Grid>
              </Grid>
          )}
        </Box>
      </Container>
  );
}