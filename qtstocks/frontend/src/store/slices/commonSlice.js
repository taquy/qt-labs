const commonSlice = {
  setError: (state, action) => {
    state.error = action.payload;
  },
  setLoading: (state, action) => {
    state.loading = action.payload;
  },
  clearError: (state) => {
    state.error = null;
  },
}

const commonState = {
  error: null,
  loading: false,
};

export { commonState, commonSlice };
