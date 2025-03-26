import React from 'react';
import { Box, Paper, Typography, Grid } from '@mui/material';

const Settings = () => {
  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Settings
            </Typography>
            {/* Add settings content here */}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Settings; 