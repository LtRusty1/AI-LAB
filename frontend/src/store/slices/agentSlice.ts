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

export const startAgent = createAsyncThunk(
  'agents/startAgent',
  async (agentId: string) => {
    const response = await axios.post(`/api/agents/${agentId}/start`);
    return response.data;
  }
);

export const stopAgent = createAsyncThunk(
  'agents/stopAgent',
  async (agentId: string) => {
    const response = await axios.post(`/api/agents/${agentId}/stop`);
    return response.data;
  }
);

export const restartAgent = createAsyncThunk(
  'agents/restartAgent',
  async (agentId: string) => {
    const response = await axios.post(`/api/agents/${agentId}/restart`);
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
      })
      .addCase(startAgent.fulfilled, (state, action) => {
        const idx = state.agents.findIndex(a => a.id === action.payload.id);
        if (idx !== -1) {
          state.agents[idx] = { ...state.agents[idx], ...action.payload, status: action.payload.state } as Agent;
        }
        if (state.selectedAgent && state.selectedAgent.id === action.payload.id) {
          state.selectedAgent = { ...state.selectedAgent, ...action.payload, status: action.payload.state } as Agent;
        }
      })
      .addCase(stopAgent.fulfilled, (state, action) => {
        const idx = state.agents.findIndex(a => a.id === action.payload.id);
        if (idx !== -1) {
          state.agents[idx] = { ...state.agents[idx], ...action.payload, status: action.payload.state } as Agent;
        }
        if (state.selectedAgent && state.selectedAgent.id === action.payload.id) {
          state.selectedAgent = { ...state.selectedAgent, ...action.payload, status: action.payload.state } as Agent;
        }
      })
      .addCase(restartAgent.fulfilled, (state, action) => {
        const idx = state.agents.findIndex(a => a.id === action.payload.id);
        if (idx !== -1) {
          state.agents[idx] = { ...state.agents[idx], ...action.payload, status: action.payload.state } as Agent;
        }
        if (state.selectedAgent && state.selectedAgent.id === action.payload.id) {
          state.selectedAgent = { ...state.selectedAgent, ...action.payload, status: action.payload.state } as Agent;
        }
      });
  },
});

export const { setSelectedAgent, clearSelectedAgent } = agentSlice.actions;
export default agentSlice.reducer; 