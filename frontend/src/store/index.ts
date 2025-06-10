import { configureStore } from '@reduxjs/toolkit';
import systemReducer from './slices/systemSlice';
import agentReducer from './slices/agentSlice';
import messageReducer from './slices/messageSlice';

export const store = configureStore({
  reducer: {
    system: systemReducer,
    agents: agentReducer,
    messages: messageReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch; 