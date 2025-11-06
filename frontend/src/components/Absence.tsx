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
  Stack,
  TextField,
  Typography
} from '@mui/material';
import apiClient from "../utils/apiClient.ts";
import CalendarMonthOutlinedIcon
  from '@mui/icons-material/CalendarMonthOutlined';
import {toast} from "sonner";

interface AbsenceItem {
  id: number;
  start_date: string;
  end_date: string;
  reason: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
}

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

/** Helper to determine the color of the status chip */
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

/**
 * Absence component for managing and displaying employee absences.
 * Users can submit new absence requests, and view their absence history.
 * Managers can update the status of absence requests.
 * @param token Authentication token required for API requests.
 * @param hasAccess Flag indicating if the user has access to submit absence requests.
 * @param isManager Flag indicating if the user has managerial privileges.
 * @constructor
 */
export default function Absence({token, hasAccess, isManager}: AbsenceProps) {
  const [absenceList, setAbsenceList] = useState<AbsenceItem[]>([]);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [reason, setReason] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [submitError, setSubmitError] = useState("");

  // Fetch data when the component mounts
  useEffect(() => {
    fetchAbsences();
  }, [token]);


  /**  Fetch absences from the backend, update the state, handle error and load */
  async function fetchAbsences() {
    try {
      const response = await apiClient.get("/api/v1/absences/");
      setAbsenceList(response.data);
    } catch (err) {
      setError("Could not load absence history.");
      console.error("Fetch absences error:", err);
    } finally {
      setIsLoading(false);
    }
  }

  /** Handler for updating the status of an absence request */
  async function handleStatusUpdate(absenceId: number, currentStatus: AbsenceItem['status']) {
    const nextStatus = statusCycle[currentStatus];
    try {
      await apiClient.patch(`/api/v1/absences/${absenceId}/`, {status: nextStatus});
      fetchAbsences(); // Refresh the list to show the new status
    } catch (err) {
      console.error("Failed to update status", err);
    }
  }

  /** Handler for submitting a new absence request */
  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setSubmitError(""); // Clear previous errors

    try {
      await apiClient.post(
          "/api/v1/absences/",
          {start_date: startDate, end_date: endDate, reason},
      );
      // Clear form and refresh the list
      setStartDate("");
      setEndDate("");
      setReason("");
      fetchAbsences();
      toast.success("Absence request submitted successfully.");
    } catch (err) {
      setSubmitError("Failed to submit request. Please check the dates and reason.");
      console.error("Submit absence error:", err);
    }
  }

  return (
      <Card sx={{display: 'flex', flexDirection: 'column', height: '100%'}}>
        <CardContent>
          <Stack direction="row" spacing={1} alignItems="center" sx={{mb: 2}}>
            <CalendarMonthOutlinedIcon color="action"/>
            <Typography variant="h5" sx={{pt: 0.8}}>
              Absences
            </Typography>
          </Stack>

          {/* Form for new request if hasAccess*/}
          {hasAccess && (
              <Box component="form" onSubmit={handleSubmit} sx={{mb: 3}}>
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

                <Box sx={{display: 'flex', justifyContent: 'flex-end', mt: 2}}>
                  <Button type="submit" variant="contained">
                    Request Absence
                  </Button>
                </Box>
              </Box>
          )}

          <Divider sx={{my: 2}}/>

          {/* List of past absences */}
          <Typography variant="h6" sx={{mb: 2}}>Your Absences</Typography>
          {isLoading ? (
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