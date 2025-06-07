import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  CircularProgress,
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  Refresh,
  Add as AddIcon,
} from '@mui/icons-material';
import { RootState } from '../store';
import { fetchAgents } from '../store/slices/agentSlice';

const Agents: React.FC = () => {
  const dispatch = useDispatch();
  const { agents, loading } = useSelector((state: RootState) => state.agents);
  const [openDialog, setOpenDialog] = React.useState(false);
  const [newAgentName, setNewAgentName] = React.useState('');

  useEffect(() => {
    dispatch(fetchAgents());
  }, [dispatch]);

  const handleStartAgent = (agentId: string) => {
    // TODO: Implement agent start
    console.log('Start agent:', agentId);
  };

  const handleStopAgent = (agentId: string) => {
    // TODO: Implement agent stop
    console.log('Stop agent:', agentId);
  };

  const handleRestartAgent = (agentId: string) => {
    // TODO: Implement agent restart
    console.log('Restart agent:', agentId);
  };

  const handleCreateAgent = () => {
    // TODO: Implement agent creation
    console.log('Create agent:', newAgentName);
    setOpenDialog(false);
    setNewAgentName('');
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Agents</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
        >
          New Agent
        </Button>
      </Box>

      {loading ? (
        <CircularProgress />
      ) : (
        <Grid container spacing={3}>
          {agents.map((agent) => (
            <Grid item xs={12} md={6} lg={4} key={agent.id}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="h6">{agent.name}</Typography>
                    <Chip
                      label={agent.status}
                      color={agent.status === 'active' ? 'success' : 'default'}
                      size="small"
                    />
                  </Box>

                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Current Task: {agent.current_task || 'Idle'}
                  </Typography>

                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Capabilities:
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {agent.capabilities.map((capability) => (
                        <Chip
                          key={capability}
                          label={capability}
                          size="small"
                          variant="outlined"
                        />
                      ))}
                    </Box>
                  </Box>

                  <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                    <IconButton
                      color="primary"
                      onClick={() => handleStartAgent(agent.id)}
                      disabled={agent.status === 'active'}
                    >
                      <PlayArrow />
                    </IconButton>
                    <IconButton
                      color="error"
                      onClick={() => handleStopAgent(agent.id)}
                      disabled={agent.status !== 'active'}
                    >
                      <Stop />
                    </IconButton>
                    <IconButton
                      color="info"
                      onClick={() => handleRestartAgent(agent.id)}
                    >
                      <Refresh />
                    </IconButton>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)}>
        <DialogTitle>Create New Agent</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Agent Name"
            fullWidth
            value={newAgentName}
            onChange={(e) => setNewAgentName(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateAgent} variant="contained">
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Agents; 