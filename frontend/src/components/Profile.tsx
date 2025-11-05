import {useEffect, useState} from 'react';
import axios from 'axios';
import {
  Alert,
  Box,
  Card,
  CardContent,
  CircularProgress,
  Grid,
  Typography
} from '@mui/material';
import Feedback from "./Feedback.tsx";

interface ProfileProps {
  token: string;
}

interface ProfileData {
  [key: string]: any;
}

export default function Profile({token}: ProfileProps) {
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [userId] = useState<string | null>(localStorage.getItem("userId"));
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
    return <Box width="100%"> <CircularProgress/></Box>;
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  function isManagerOrOwner(): boolean{
    if (!profile || !userId){
      return false;
    }
    return profile.user?.toString() === userId || profile.manager === userId;
  }

  return (
        <Box sx={{py: 4, px:3}}>
          <Typography variant="h4" component="h1" gutterBottom>
            Employee Profile
          </Typography>
          {profile && (
              <Grid container spacing={3} sx={{alignItems: "flex-start"}}>
                <Grid size={{xs: 12, md: 4}}>
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
                <Grid size={{xs: 12, md: 4}}>
                  {/*For demo, always check profile 1*/}
                  <Feedback profileId={profile.id || 1} token={token}/>
                </Grid>
              </Grid>
          )}
        </Box>
  );
}