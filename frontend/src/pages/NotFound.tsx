import React from 'react';
import { Box, Typography, Button, Container } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { Home, Search } from '@mui/icons-material';

const NotFound: React.FC = () => {
  const navigate = useNavigate();

  const handleGoHome = () => {
    navigate('/');
  };

  return (
    <Container maxWidth="md">
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '60vh',
          textAlign: 'center',
          gap: 3,
        }}
      >
        <Search 
          sx={{ 
            fontSize: 120, 
            color: '#00ffcc', 
            opacity: 0.7 
          }} 
        />
        
        <Box>
          <Typography 
            variant="h1" 
            sx={{ 
              fontSize: '6rem', 
              fontWeight: 700, 
              color: '#00ffcc',
              textShadow: '0 0 20px rgba(0, 255, 204, 0.3)',
              marginBottom: 2 
            }}
          >
            404
          </Typography>
          
          <Typography 
            variant="h4" 
            sx={{ 
              color: '#ffffff', 
              marginBottom: 2,
              fontWeight: 600 
            }}
          >
            Page Not Found
          </Typography>
          
          <Typography 
            variant="body1" 
            sx={{ 
              color: '#94a3b8', 
              marginBottom: 4,
              fontSize: '1.1rem',
              lineHeight: 1.6 
            }}
          >
            The page you're looking for doesn't exist or has been moved.
            <br />
            Let's get you back to the AI Lab dashboard.
          </Typography>
        </Box>

        <Button
          variant="contained"
          startIcon={<Home />}
          onClick={handleGoHome}
          sx={{
            background: 'linear-gradient(135deg, #00ffcc 0%, #00d4aa 100%)',
            color: '#1a1a2e',
            fontWeight: 600,
            fontSize: '1rem',
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
            padding: '0.8rem 2rem',
            borderRadius: '12px',
            boxShadow: '0 4px 20px rgba(0, 255, 204, 0.3)',
            '&:hover': {
              transform: 'translateY(-2px)',
              boxShadow: '0 6px 25px rgba(0, 255, 204, 0.4)',
              background: 'linear-gradient(135deg, #00d4aa 0%, #00b894 100%)',
            },
            transition: 'all 0.2s ease',
          }}
        >
          Go Home
        </Button>
      </Box>
    </Container>
  );
};

export default NotFound; 