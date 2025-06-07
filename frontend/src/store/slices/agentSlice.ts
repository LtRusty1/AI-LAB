import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

interface Agent {
  id: string;
  name: string;
  status: string;
  capabilities: string[];
  current_task: string;
}

interface AgentState {
  agents: Agent[];
  selectedAgent: Agent | null;
  loading: boolean;
  error: string | null;
}

const initialState: AgentState = {
  agents: [],
  selectedAgent: null,
  loading: false,
  error: null,
};

export const fetchAgents = createAsyncThunk(
  'agents/fetchAgents',
  async () => {
    const response = await axios.get('/api/agents');
    return response.data.agents;
  }
);

export const fetchAgent = createAsyncThunk(
  'agents/fetchAgent',
  async (agentId: string) => {
    const response = await axios.get(`/api/agents/${agentId}`);
    return response.data;
  }
);

const agentSlice = createSlice({
  name: 'agents',
  initialState,
  reducers: {
    setSelectedAgent: (state, action) => {
      state.selectedAgent = action.payload;
    },
    clearSelectedAgent: (state) => {
      state.selectedAgent = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchAgents.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAgents.fulfilled, (state, action) => {
        state.loading = false;
        state.agents = action.payload;
      })
      .addCase(fetchAgents.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch agents';
      })
      .addCase(fetchAgent.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAgent.fulfilled, (state, action) => {
        state.loading = false;
        state.selectedAgent = action.payload;
      })
      .addCase(fetchAgent.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch agent';
      });
  },
});

export const { setSelectedAgent, clearSelectedAgent } = agentSlice.actions;
export default agentSlice.reducer; 