import { createSlice } from '@reduxjs/toolkit';
const initialState = {
  users: [],
  error: "",
};

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    setUsers: (state, action) => {
      state.users = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
  },
});

export const {
  setUsers,
  setError,
} = userSlice.actions;
export default userSlice.reducer;
