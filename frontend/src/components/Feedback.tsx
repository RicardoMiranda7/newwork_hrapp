import {type FormEvent, useEffect, useState} from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Divider,
  List,
  ListItem,
  ListItemText,
  TextField,
  Typography
} from '@mui/material';
import apiClient from "../utils/apiClient.ts";

interface FeedbackItem {
  id: number;
  text: string;
  author: number;
  created_at: string;
}

// Interface for the component's props
interface FeedbackProps {
  profileId: number;
  token: string;
}

export default function Feedback({profileId, token}: FeedbackProps) {
  const [feedbackList, setFeedbackList] = useState<FeedbackItem[]>([]);
  const [newFeedback, setNewFeedback] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Fetch feedback when the component mounts or profileId changes
  useEffect(() => {
    if (token && profileId) {
      fetchFeedback();
    }
  }, [profileId, token]);

  //  Fetch feedback from the backend, update the state, handle error and load
  async function fetchFeedback() {
    if (!profileId) {
      setFeedbackList([]);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError('');

      const response = await apiClient.get(`/api/v1/feedback/?profile=${profileId}`);
      setFeedbackList(response.data);
    } catch (err) {
      setError('Could not load feedback.');
      console.error('Fetch feedback error:', err);
    } finally {
      setLoading(false);
    }
  }

  // Handler for submitting new feedback
  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!newFeedback.trim()) return; // Prevent submitting empty feedback

    try {
      await apiClient.post(
          '/api/v1/feedback/',
          {
            text: newFeedback,
            profile: profileId,
          },
      );
      setNewFeedback('');
      await fetchFeedback(); // Refresh the list to show the new feedback
    } catch (err) {
      setError('Failed to submit feedback.');
      console.error('Submit feedback error:', err);
    }
  }

  return (
      <Card sx={{display: 'flex', flexDirection: 'column', height: '100%'}}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Feedback
          </Typography>

          {/* Form for submitting new feedback */}
          <Box component="form" onSubmit={handleSubmit} sx={{mb: 3}}>
            <TextField
                label="Leave new feedback"
                multiline
                rows={3}
                fullWidth
                variant="outlined"
                value={newFeedback}
                onChange={(e) => setNewFeedback(e.target.value)}
            />
            <Button
                type="submit"
                variant="contained"
                sx={{mt: 1}}
            >
              Submit Feedback
            </Button>
          </Box>

          <Divider sx={{my: 2}}/>

          {/* Display feedback list */}
          {loading ? (
              <CircularProgress sx={{mx: 'auto', my: 2}}/>
          ) : error ? (
              <Alert severity="error">{error}</Alert>
          ) : (
              <List sx={{
                maxHeight: '450px',
                overflowY: 'auto', // Add a vertical scrollbar
                p: 2
              }}>
                {feedbackList.length > 0 ? (
                    feedbackList.map((item) => (
                        <ListItem key={item.id} alignItems="flex-start">
                          <ListItemText
                              primary={item.text}
                              secondary={`By User ID: ${item.author} on ${new Date(item.created_at).toLocaleDateString()}`}
                          />
                        </ListItem>
                    ))
                ) : (
                    <Typography>No feedback has been submitted for this profile
                      yet.</Typography>
                )}
              </List>
          )}
        </CardContent>
      </Card>
  );
}