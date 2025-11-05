import {type FormEvent, useEffect, useState} from 'react';
import axios from 'axios';
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

interface AbsenceItem {
  id: number;
  start_date: string;
  end_date: string;
  reason: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
}

// Interface for the component's props
interface AbsenceProps {
  token: string;
  hasAccess: boolean;
  isManager: boolean;
}

const statusCycle = {
  'PENDING': 'APPROVED',
  'APPROVED': 'REJECTED',
  'REJECTED': 'PENDING',
};


export default function Absence({token, hasAccess, isManager}: AbsenceProps) {
  const [absenceList, setAbsenceList] = useState<AbsenceItem[]>([]);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [reason, setReason] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [submitError, setSubmitError] = useState("");

  // Fetch data when the component mounts
  useEffect(() => {
    fetchAbsences();
  }, [token]);


  // Fetch the user's absences, set state, handle errors and loading
  async function fetchAbsences() {
    try {
      const response = await axios.get("http://localhost:8000/api/v1/absences/", {
        headers: {Authorization: `Bearer ${token}`},
      });
      setAbsenceList(response.data);
    } catch (err) {
      setError("Could not load absence history.");
      console.error("Fetch absences error:", err);
    } finally {
      setLoading(false);
    }
  }

  async function handleStatusUpdate(absenceId: number, currentStatus: AbsenceItem['status']) {
    const nextStatus = statusCycle[currentStatus];
    try {
      await axios.patch(`http://localhost:8000/api/v1/absences/${absenceId}/`, {status: nextStatus}, {
        headers: {Authorization: `Bearer ${token}`},
      });
      fetchAbsences(); // Refresh the list to show the new status
    } catch (err) {
      console.error("Failed to update status", err);
    }
  }

  // Handler for submitting a new absence request
  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setSubmitError(""); // Clear previous errors

    try {
      await axios.post(
          "http://localhost:8000/api/v1/absences/",
          {start_date: startDate, end_date: endDate, reason},
          {headers: {Authorization: `Bearer ${token}`}}
      );
      // Clear form and refresh the list
      setStartDate("");
      setEndDate("");
      setReason("");
      fetchAbsences();
    } catch (err) {
      setSubmitError("Failed to submit request. Please check the dates and reason.");
      console.error("Submit absence error:", err);
    }
  }

  // Helper to determine the color of the status chip
  function getStatusChipColor(status: AbsenceItem["status"]) {
    switch (status) {
      case "APPROVED":
        return "success";
      case "REJECTED":
        return "error";
      default:
        return "warning";
    }
  }

  return (
      <Card sx={{display: 'flex', flexDirection: 'column', height: '100%'}}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Absence Requests
          </Typography>

          {/* Form for new request if hasAccess*/}
          {hasAccess && (
              <Box component="form" onSubmit={handleSubmit} sx={{mb: 3}}>
                <Typography variant="h6" sx={{mb: 2}}>Request New
                  Absence</Typography>
                <Box sx={{display: 'flex', gap: 2, mb: 2}}>
                  <TextField
                      label="Start Date"
                      type="date"
                      slotProps={{inputLabel: {shrink: true}}}
                      fullWidth
                      value={startDate}
                      onChange={(e) => setStartDate(e.target.value)}
                      required
                  />
                  <TextField
                      label="End Date"
                      type="date"
                      slotProps={{inputLabel: {shrink: true}}}
                      fullWidth
                      value={endDate}
                      onChange={(e) => setEndDate(e.target.value)}
                      required
                  />
                </Box>
                <TextField
                    label="Reason"
                    multiline
                    rows={2}
                    fullWidth
                    variant="outlined"
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                    required
                />
                {submitError &&
                    <Alert severity="error" sx={{mt: 2}}>{submitError}</Alert>}
                <Button type="submit" variant="contained" sx={{mt: 2}}>
                  Submit Request
                </Button>
              </Box>
          )}

          <Divider sx={{my: 2}}/>

          {/* List of past absences */}
          <Typography variant="h6" sx={{mb: 2}}>Your Absences</Typography>
          {loading ? (
              <CircularProgress/>
          ) : error ? (
              <Alert severity="error">{error}</Alert>
          ) : (
              <List sx={{maxHeight: '300px', overflowY: 'auto'}}>
                {absenceList.length > 0 ? (
                    absenceList.map((item) => (
                        <ListItem key={item.id} divider>
                          <ListItemText
                              primary={item.reason}
                              secondary={`From: ${item.start_date} To: ${item.end_date}`}
                          />
                          {/* --- Status Button --- */}
                          <Button
                              variant="contained"
                              size="small"
                              color={getStatusChipColor(item.status)}
                              // Only managers can click the button
                              disabled={!isManager}
                              onClick={() => handleStatusUpdate(item.id, item.status)}
                              sx={{
                                '&.Mui-disabled': {
                                  backgroundColor: (theme) => theme.palette[getStatusChipColor(item.status)].main,
                                  color: (theme) => theme.palette[getStatusChipColor(item.status)].contrastText,
                                  opacity: 1,
                                },
                              }}
                          >
                            {item.status}
                          </Button>
                        </ListItem>
                    ))
                ) : (
                    <Typography> You have no absence requests.</Typography>
                )}
              </List>
          )}
        </CardContent>
      </Card>
  );
}