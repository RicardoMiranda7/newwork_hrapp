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
  ListItemText, Stack,
  TextField,
  Tooltip,
  Typography
} from '@mui/material';
import apiClient from "../utils/apiClient.ts";
import {toast} from "sonner";
import IconButton from "@mui/material/IconButton";
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import ChatBubbleOutlineIcon from '@mui/icons-material/ChatBubbleOutline';

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
  const [isLoading, setIsLoading] = useState(true);
  const [isPolishing, setIsPolishing] = useState(false);
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
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      setError('');

      const response = await apiClient.get(`/api/v1/feedback/?profile=${profileId}`);
      setFeedbackList(response.data);
    } catch (err) {
      setError('Could not load feedback.');
      console.error('Fetch feedback error:', err);
    } finally {
      setIsLoading(false);
    }
  }

  // Handler for polishing feedback using AI
  async function handlePolishClick() {
    if (!newFeedback.trim()) {
      toast.info("Please write some feedback before polishing.");
      return;
    }

    setIsPolishing(true);
    try {
      const response = await apiClient.post('/api/v1/feedback/polish/', {text: newFeedback});
      setNewFeedback(response.data.polished_text);
      toast.success("Feedback polished with AI!");
    } catch (err) {
      console.error("Failed to polish feedback", err);
      toast.error("AI polisher is currently unavailable.");
    } finally {
      setIsPolishing(false);
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
          <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
            <ChatBubbleOutlineIcon color="action" />
            <Typography variant="h5" sx={{ pt: 0.8 }}>
              Feedback
            </Typography>
          </Stack>

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
                disabled={isPolishing}
            />

            {/* --- Request AI polish / submit Feedback action buttons --- */}
            <Box sx={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              mt: 1
            }}>
              <Tooltip title="Polish with AI">
                {/* Disable button while polishing */}
                <span>
                <IconButton onClick={handlePolishClick}
                            disabled={isPolishing || !newFeedback.trim()}>
                  {/* Show a spinner when polishing */}
                  {isPolishing ? <CircularProgress size={24}/> :
                      <AutoFixHighIcon/>}
                </IconButton>
              </span>
              </Tooltip>
              <Button
                  type="submit"
                  variant="contained"
                  disabled={isPolishing}
              >
                Submit Feedback
              </Button>
            </Box>
          </Box>

          <Divider sx={{my: 2}}/>

          {/* Display feedback list */}
          {isLoading ? (
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
                    <Box sx={{ textAlign: 'center', py: 4 }}>
                      <Typography variant="body2" color="text.secondary">
                        No feedback has been submitted for this profile yet.
                      </Typography>
                    </Box>
                )}
              </List>
          )}
        </CardContent>
      </Card>
  )
      ;
}