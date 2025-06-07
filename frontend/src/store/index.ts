import { configureStore } from '@reduxjs/toolkit';
import systemReducer from './slices/systemSlice';

export const store = configureStore({
  reducer: {
    system: systemReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch; 