import React, { useEffect, useRef, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  Divider,
  CircularProgress,
  Paper,
} from '@mui/material';
import { Send as SendIcon } from '@mui/icons-material';
import { RootState } from '../store';
import { fetchMessages, sendMessage } from '../store/slices/messageSlice';
import { fetchAgents } from '../store/slices/agentSlice';

const Messages: React.FC = () => {
  const dispatch = useDispatch();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [newMessage, setNewMessage] = useState('');

  const { messages, loading: messagesLoading } = useSelector(
    (state: RootState) => state.messages
  );
  const { agents, loading: agentsLoading } = useSelector(
    (state: RootState) => state.agents
  );

  useEffect(() => {
    dispatch(fetchAgents());
  }, [dispatch]);

  useEffect(() => {
    if (selectedAgent) {
      dispatch(fetchMessages(selectedAgent));
    }
  }, [dispatch, selectedAgent]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = () => {
    if (newMessage.trim() && selectedAgent) {
      dispatch(
        sendMessage({
          sender_id: 'user',
          receiver_id: selectedAgent,
          content: newMessage.trim(),
          message_type: 'text',
        })
      );
      setNewMessage('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <Box sx={{ display: 'flex', gap: 3, height: 'calc(100vh - 200px)' }}>
      {/* Agent List */}
      <Card sx={{ width: 250, flexShrink: 0 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Agents
          </Typography>
          <List>
            {agents.map((agent) => (
              <React.Fragment key={agent.id}>
                <ListItem
                  button
                  selected={selectedAgent === agent.id}
                  onClick={() => setSelectedAgent(agent.id)}
                >
                  <ListItemText
                    primary={agent.name}
                    secondary={agent.status}
                  />
                </ListItem>
                <Divider />
              </React.Fragment>
            ))}
          </List>
        </CardContent>
      </Card>

      {/* Message Area */}
      <Card sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <CardContent sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          {selectedAgent ? (
            <>
              <Typography variant="h6" gutterBottom>
                Messages
              </Typography>
              <Paper
                sx={{
                  flex: 1,
                  overflow: 'auto',
                  p: 2,
                  mb: 2,
                  bgcolor: 'background.default',
                }}
              >
                {messagesLoading ? (
                  <CircularProgress />
                ) : (
                  <List>
                    {messages.map((message) => (
                      <ListItem
                        key={message.id}
                        sx={{
                          justifyContent:
                            message.sender_id === 'user'
                              ? 'flex-end'
                              : 'flex-start',
                        }}
                      >
                        <Paper
                          sx={{
                            p: 2,
                            maxWidth: '70%',
                            bgcolor:
                              message.sender_id === 'user'
                                ? 'primary.main'
                                : 'background.paper',
                            color:
                              message.sender_id === 'user'
                                ? 'primary.contrastText'
                                : 'text.primary',
                          }}
                        >
                          <Typography variant="body1">
                            {message.content}
                          </Typography>
                          <Typography
                            variant="caption"
                            color="text.secondary"
                            sx={{ display: 'block', mt: 1 }}
                          >
                            {new Date(message.timestamp).toLocaleString()}
                          </Typography>
                        </Paper>
                      </ListItem>
                    ))}
                    <div ref={messagesEndRef} />
                  </List>
                )}
              </Paper>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <TextField
                  fullWidth
                  multiline
                  maxRows={4}
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type a message..."
                  variant="outlined"
                />
                <Button
                  variant="contained"
                  endIcon={<SendIcon />}
                  onClick={handleSendMessage}
                  disabled={!newMessage.trim()}
                >
                  Send
                </Button>
              </Box>
            </>
          ) : (
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                height: '100%',
              }}
            >
              <Typography color="text.secondary">
                Select an agent to start messaging
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default Messages; 