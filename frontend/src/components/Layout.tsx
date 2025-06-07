import React from 'react';
import { Box, Container, useTheme } from '@mui/material';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const theme = useTheme();

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        bgcolor: theme.palette.background.default,
        overflow: 'hidden',
      }}
    >
      <Container
        maxWidth="xl"
        sx={{
          flex: 1,
          py: 4,
          display: 'flex',
          flexDirection: 'column',
          gap: 4,
          overflow: 'auto',
          height: '100%',
        }}
      >
        {children}
      </Container>
    </Box>
  );
};

export default Layout; 