const sharedInitialState = {
  loading: false,
  error: null,
};

const sharedReducer = {
  setLoading: (state, action) => {
    state.loading = action.payload;
  },
  setError: (state, action) => {
    state.error = action.payload;
  },
  clearError: (state) => {
    state.error = null;
  }
}

export { sharedReducer, sharedInitialState };