import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  useTheme,
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { RootState } from '../store';
import { fetchAgents } from '../store/slices/agentSlice';
import { fetchSystemStats } from '../store/slices/systemSlice';

const Dashboard: React.FC = () => {
  const theme = useTheme();
  const dispatch = useDispatch();
  const { agents, loading: agentsLoading } = useSelector(
    (state: RootState) => state.agents
  );
  const { gpu, loading: systemLoading } = useSelector(
    (state: RootState) => state.system
  );

  useEffect(() => {
    dispatch(fetchAgents());
    dispatch(fetchSystemStats());
    const interval = setInterval(() => {
      dispatch(fetchSystemStats());
    }, 5000);
    return () => clearInterval(interval);
  }, [dispatch]);

  const activeAgents = agents.filter((agent) => agent.status === 'active').length;
  const totalAgents = agents.length;

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      <Grid container spacing={3}>
        {/* Agent Status */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Agent Status
              </Typography>
              {agentsLoading ? (
                <CircularProgress />
              ) : (
                <Box sx={{ textAlign: 'center', py: 2 }}>
                  <Typography variant="h3" color="primary">
                    {activeAgents}/{totalAgents}
                  </Typography>
                  <Typography variant="subtitle1" color="text.secondary">
                    Active Agents
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* GPU Usage */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                GPU Usage
              </Typography>
              {systemLoading ? (
                <CircularProgress />
              ) : gpu ? (
                <Box sx={{ textAlign: 'center', py: 2 }}>
                  <Typography variant="h3" color="primary">
                    {gpu.utilization}%
                  </Typography>
                  <Typography variant="subtitle1" color="text.secondary">
                    GPU Utilization
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Memory: {gpu.memory_used}MB / {gpu.memory_total}MB
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Temperature: {gpu.temperature}°C
                  </Typography>
                </Box>
              ) : (
                <Typography color="error">GPU stats unavailable</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* System Metrics Chart */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Metrics
              </Typography>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={[
                      { time: '00:00', value: 0 },
                      { time: '01:00', value: 20 },
                      { time: '02:00', value: 40 },
                      { time: '03:00', value: 30 },
                      { time: '04:00', value: 50 },
                    ]}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="value"
                      stroke={theme.palette.primary.main}
                      activeDot={{ r: 8 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard; 