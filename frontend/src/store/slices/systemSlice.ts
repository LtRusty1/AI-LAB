import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

interface GPUStats {
  memory_used: number;
  memory_total: number;
  utilization: number;
  temperature: number;
}

interface SystemState {
  gpu: GPUStats | null;
  loading: boolean;
  error: string | null;
}

const initialState: SystemState = {
  gpu: null,
  loading: false,
  error: null,
};

export const fetchSystemStats = createAsyncThunk(
  'system/fetchStats',
  async () => {
    const response = await axios.get('/api/system/stats');
    return response.data;
  }
);

const systemSlice = createSlice({
  name: 'system',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchSystemStats.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchSystemStats.fulfilled, (state, action) => {
        state.loading = false;
        state.gpu = action.payload.gpu;
      })
      .addCase(fetchSystemStats.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch system stats';
      });
  },
});

export default systemSlice.reducer; 