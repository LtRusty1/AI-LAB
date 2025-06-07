import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  CircularProgress,
  LinearProgress,
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
import { fetchSystemStats } from '../store/slices/systemSlice';

const System: React.FC = () => {
  const theme = useTheme();
  const dispatch = useDispatch();
  const { gpu, loading } = useSelector((state: RootState) => state.system);

  useEffect(() => {
    dispatch(fetchSystemStats());
    const interval = setInterval(() => {
      dispatch(fetchSystemStats());
    }, 5000);
    return () => clearInterval(interval);
  }, [dispatch]);

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        System Status
      </Typography>

      <Grid container spacing={3}>
        {/* GPU Status */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                GPU Status
              </Typography>
              {loading ? (
                <CircularProgress />
              ) : gpu ? (
                <Box>
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Memory Usage
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={(gpu.memory_used / gpu.memory_total) * 100}
                      sx={{ height: 10, borderRadius: 5 }}
                    />
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      {gpu.memory_used}MB / {gpu.memory_total}MB
                    </Typography>
                  </Box>

                  <Box sx={{ mb: 3 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      GPU Utilization
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={gpu.utilization}
                      sx={{ height: 10, borderRadius: 5 }}
                    />
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      {gpu.utilization}%
                    </Typography>
                  </Box>

                  <Box>
                    <Typography variant="subtitle2" gutterBottom>
                      Temperature
                    </Typography>
                    <Typography variant="h4" color="primary">
                      {gpu.temperature}°C
                    </Typography>
                  </Box>
                </Box>
              ) : (
                <Typography color="error">GPU stats unavailable</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Performance Metrics */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Performance Metrics
              </Typography>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={[
                      { time: '00:00', memory: 0, utilization: 0 },
                      { time: '01:00', memory: 20, utilization: 30 },
                      { time: '02:00', memory: 40, utilization: 50 },
                      { time: '03:00', memory: 30, utilization: 40 },
                      { time: '04:00', memory: 50, utilization: 60 },
                    ]}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="memory"
                      name="Memory Usage"
                      stroke={theme.palette.primary.main}
                      activeDot={{ r: 8 }}
                    />
                    <Line
                      type="monotone"
                      dataKey="utilization"
                      name="GPU Utilization"
                      stroke={theme.palette.secondary.main}
                      activeDot={{ r: 8 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* System Information */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Information
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Operating System
                  </Typography>
                  <Typography variant="body1">Windows 10</Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Python Version
                  </Typography>
                  <Typography variant="body1">3.9.0</Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2" color="text.secondary">
                    CUDA Version
                  </Typography>
                  <Typography variant="body1">12.1</Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default System; 