import { Box, CircularProgress } from '@mui/material';

const PageLoader = () => {
  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        width: '100%',
        backgroundColor: 'background.default'
      }}
    >
      <CircularProgress size={60} />
    </Box>
  );
};

export default PageLoader;
