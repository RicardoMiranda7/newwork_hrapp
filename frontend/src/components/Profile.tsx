import {type ChangeEvent, useEffect, useState} from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Grid,
  Stack,
  TextField,
  Typography
} from '@mui/material';
import Feedback from "./Feedback.tsx";
import Absence from "./Absence.tsx";
import {isManager, isManagerOrOwner} from "../utils/access.ts";
import {toast} from "sonner";
import apiClient from "../utils/apiClient.ts";
import AccountCircleOutlinedIcon
  from '@mui/icons-material/AccountCircleOutlined';

interface ProfileProps {
  token: string;
}

interface ProfileData {
  [key: string]: any;
}

// --- Fields that are NEVER editable ---
const alwaysDisabledFields = ['id', 'user'];


/**
 * The main component for displaying and editing an employee's profile.
 * It manages its own state for loading, viewing, and editing profile data.
 * It also acts as a container for the Feedback and Absence components.
 *
 * 'profile' holds the original, source-of-truth data from the backend.
 * 'editableProfile' is a temporary copy used only when in edit mode.
 * This prevents UI updates until the user explicitly saves.
 */
export default function Profile({token}: ProfileProps) {
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [editableProfile, setEditableProfile] = useState<ProfileData | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const userId = localStorage.getItem("userId");

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await apiClient.get('/api/v1/profiles/1/', {});
        setProfile(response.data);
      } catch (err) {
        setError('Failed to fetch profile data.');
        console.error('Fetch profile error:', err);
      } finally {
        setIsLoading(false);
      }
    };

    if (token) {
      fetchProfile();
    }
  }, [token]);


  /** Enter edit mode and create a safe, deep copy of the profile to modify. */
  function handleEditClick() {
    setEditableProfile(JSON.parse(JSON.stringify(profile)));
    setIsEditing(true);
  }

  /** Exit edit mode and discard any changes made to the editable profile. */
  function handleCancelClick() {
    setIsEditing(false);
    setEditableProfile(null); // Discard changes
  }

  /** Submit the edited profile data to the backend, if it fails revert to original */
  async function handleSubmitClick() {
    if (!editableProfile || !profile) return;
    try {
      const response = await apiClient.put(`/api/v1/profiles/${profile.id}/`, editableProfile);
      setProfile(response.data); // Update the main profile state with the new data
      setIsEditing(false);

      toast.success("Profile edited successfully");

    } catch (err) {
      console.error("Failed to update profile", err);
      toast.error("Failed to update profile");
      setError("Failed to save changes.");
      setEditableProfile(null);
      setIsEditing(false);
    }
  }

  /** Handle changes in the input fields, updating the editable profile state */
  function handleInputChange(e: ChangeEvent<HTMLInputElement>) {
    const {name, value} = e.target;
    setEditableProfile(prev => prev ? {...prev, [name]: value} : null);
  }

  if (isLoading) {
    return (
        <Box
            sx={{
              position: "fixed",
              inset: 0,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              backdropFilter: "blur(6px)",
              backgroundColor: "rgba(255, 255, 255, 0.3)",
              zIndex: 1300,
              opacity: 1,
              transition: "opacity 0.3s ease",
            }}
        >
          <CircularProgress size={64} thickness={5}/>
        </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  /** Render the Edit/Submit/Cancel buttons based on the current mode and access rights */
  function renderEditActions() {
    // Only users with permission should see any edit-related buttons.
    if (profile && userId && isManagerOrOwner(profile!, userId!)) {
      return (isEditing ? (
          <Stack direction="row" spacing={1}>
            <Button onClick={handleCancelClick} size="small">Cancel</Button>
            <Button onClick={handleSubmitClick} variant="contained"
                    size="small">Submit</Button>
          </Stack>
      ) : (
          <Button onClick={handleEditClick} size="small"
          >Edit</Button>
      ));
    }
    return <></>;
  }

  /**
   * Dynamically renders profile fields as either read-only text or editable text fields.
   * This ensures co-workers who don't receive sensitive data won't see empty fields.
   */
  function renderProfileFields() {
    const sourceData = isEditing ? editableProfile : profile;
    if (!sourceData) return <></>;
    return (
        Object.entries(sourceData).map(([key, value]) => (
            <TextField
                key={key}
                name={key}
                label={key.replace(/_/g, ' ').toUpperCase()}
                value={value || ''}
                onChange={handleInputChange}
                fullWidth
                margin="normal"
                variant="outlined"
                size="small"
                disabled={!(isEditing && !alwaysDisabledFields.includes(key))}
            />
        )))
  }


  return (
      <Box sx={{py: 4, px: 3}}>
        <Typography variant="h4" component="h1" gutterBottom>
          Employee Profile
        </Typography>
        {profile && (
            <Grid container spacing={3} sx={{alignItems: "flex-start"}}>
              <Grid size={{xs: 12, md: 4}}>
                <Card>
                  <CardContent>
                    <Stack direction="row" justifyContent="space-between"
                           alignItems="center">
                      <Stack direction="row" spacing={1} alignItems="center">
                        <AccountCircleOutlinedIcon color="action"/>
                        <Typography variant="h5" sx={{pt: 0.8}}>
                          Details
                        </Typography>
                      </Stack>

                      {/* --- Edit/Submit/Cancel Buttons --- */}
                      {renderEditActions()}
                    </Stack>
                    <Box sx={{
                      maxHeight: '638px',
                      overflowY: 'auto', // Add a vertical scrollbar
                      p: 1
                    }}>
                      {/* --- All profile fields --- */}
                      {renderProfileFields()}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              <Grid size={{xs: 12, md: 4}} sx={{
                maxHeight: '750px'
              }}>
                {/*For demo, always check profile 1*/}
                <Feedback profileId={profile.id || 1} token={token}/>
              </Grid>
              <Grid size={{xs: 12, md: 4}}>
                <Absence token={token}
                         hasAccess={isManagerOrOwner(profile, userId!)}
                         isManager={isManager(profile, userId!)}/>
              </Grid>
            </Grid>
        )}
      </Box>
  );
}