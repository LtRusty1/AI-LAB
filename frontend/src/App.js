import React, { useState, useRef, useEffect } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';
import { Box, Container, Typography, Paper, TextField, Button, CircularProgress, AppBar, Toolbar, CssBaseline, Fade, Backdrop } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import './App.css';

const initialElements = [
  { data: { id: 'ceo', label: 'CEO' }, position: { x: 100, y: 100 } },
  { data: { id: 'worker', label: 'Worker' }, position: { x: 300, y: 200 } },
  { data: { id: 'qa', label: 'QA' }, position: { x: 500, y: 200 } },
  { data: { id: 'ceo_review', label: 'CEO Review' }, position: { x: 700, y: 100 } },
  { data: { id: 'end', label: 'END' }, position: { x: 900, y: 100 } },
  { data: { source: 'ceo', target: 'worker', label: 'delegates' } },
  { data: { source: 'worker', target: 'qa', label: 'submits' } },
  { data: { source: 'qa', target: 'ceo_review', label: 'reviews' } },
  { data: { source: 'ceo_review', target: 'end', label: 'approves' } },
];

function App() {
  const [elements, setElements] = useState(initialElements);
  const cyRef = useRef(null);
  const [chatInput, setChatInput] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [animating, setAnimating] = useState(false);
  const [showOverlay, setShowOverlay] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [showThoughtProcess, setShowThoughtProcess] = useState({});
  const messagesEndRef = useRef(null);

  // Fit graph to container on mount and when elements change
  useEffect(() => {
    if (cyRef.current) {
      cyRef.current.fit();
    }
  }, [elements]);

  // Always fit graph after sending a message
  const fitGraph = () => {
    if (cyRef.current) {
      cyRef.current.fit();
    }
  };

  // Example: Add a node on double click
  const handleCyInit = (cy) => {
    cyRef.current = cy;
    cy.on('dblclick', (evt) => {
      if (evt.target === cy) { // Only trigger on background/core
        const pos = evt.position;
        const newId = `node${elements.length}`;
        setElements((els) => [
          ...els,
          { data: { id: newId, label: `Node ${elements.length}` }, position: pos }
        ]);
      }
    });
    // Example: Add edge on tap two nodes
    let selectedNode = null;
    cy.on('tap', 'node', (evt) => {
      if (!selectedNode) {
        selectedNode = evt.target.id();
      } else {
        if (selectedNode !== evt.target.id()) {
          setElements((els) => [
            ...els,
            { data: { source: selectedNode, target: evt.target.id(), label: 'custom' } }
          ]);
        }
        selectedNode = null;
      }
    });
  };

  // Animate CEO node when loading (pulsing effect)
  useEffect(() => {
    if (cyRef.current) {
      const ceoNode = cyRef.current.getElementById('ceo');
      if (loading) {
        setShowOverlay(true);
        let pulse = true;
        let pulseInterval = setInterval(() => {
          if (ceoNode) {
            ceoNode.animate({ style: { 'background-color': pulse ? '#ffeb3b' : '#00ffcc', 'border-width': pulse ? 10 : 3, 'border-color': pulse ? '#fff176' : '#fff' } }, { duration: 250 });
            pulse = !pulse;
          }
        }, 300);
        return () => {
          clearInterval(pulseInterval);
          if (ceoNode) ceoNode.animate({ style: { 'background-color': '#00ffcc', 'border-width': 3, 'border-color': '#fff' } }, { duration: 300 });
        };
      } else {
        setShowOverlay(false);
        if (ceoNode) ceoNode.animate({ style: { 'background-color': '#00ffcc', 'border-width': 3, 'border-color': '#fff' } }, { duration: 300 });
      }
    }
  }, [loading]);

  // Generate a new session ID on component mount
  useEffect(() => {
    const newSessionId = Date.now().toString();
    setSessionId(newSessionId);
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput('');
    setLoading(true);

    // Add user message to the chat
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          session_id: sessionId
        }),
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        // Add AI response to the chat
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: data.response,
          thought_process: data.thought_process
        }]);
      } else {
        throw new Error(data.error || 'Failed to get response');
      }
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        role: 'error',
        content: 'Sorry, there was an error processing your request.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleNewSession = () => {
    const newSessionId = Date.now().toString();
    setSessionId(newSessionId);
    setMessages([]);
    setShowThoughtProcess({});
  };

  const toggleThoughtProcess = (index) => {
    setShowThoughtProcess(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  const formatThoughtProcess = (thoughtProcess) => {
    if (!thoughtProcess) return null;
    
    return thoughtProcess.split('\n\n').map((section, i) => {
      const [header, ...content] = section.split('\n');
      return (
        <div key={i} className="thought-section">
          <h4>{header}</h4>
          <p>{content.join('\n')}</p>
        </div>
      );
    });
  };

  return (
    <Box sx={{ bgcolor: '#222', minHeight: '100vh' }}>
      <CssBaseline />
      <AppBar position="static" sx={{ bgcolor: '#111' }}>
        <Toolbar>
          <Typography variant="h5" sx={{ flexGrow: 1, color: '#00ffcc', fontWeight: 'bold' }}>
            AI-Lab Organization Chart & Agent Pipeline
          </Typography>
        </Toolbar>
      </AppBar>
      <Container maxWidth="xl" sx={{ pt: 4, pb: 2 }}>
        <Paper elevation={3} sx={{ mb: 4, p: 2, bgcolor: '#181818', borderRadius: 3, position: 'relative' }}>
          {/* Overlay when loading */}
          <Fade in={loading} unmountOnExit>
            <Backdrop open={loading} sx={{ position: 'absolute', zIndex: 10, color: '#ffeb3b', bgcolor: 'rgba(34,34,34,0.5)' }}>
              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <CircularProgress size={48} sx={{ color: '#ffeb3b', mb: 2 }} />
                <Typography variant="h6" sx={{ color: '#ffeb3b' }}>CEO is thinking...</Typography>
              </Box>
            </Backdrop>
          </Fade>
          <CytoscapeComponent
            elements={elements}
            style={{ width: '100%', height: '50vh', background: '#222' }}
            cy={handleCyInit}
            layout={{ name: 'preset' }}
            stylesheet={[
              {
                selector: 'node',
                style: {
                  'background-color': '#00ffcc',
                  'label': 'data(label)',
                  'color': '#222',
                  'font-size': 18,
                  'text-valign': 'center',
                  'text-halign': 'center',
                  'width': 60,
                  'height': 60,
                  'border-width': 3,
                  'border-color': '#fff',
                  'transition-property': 'background-color, border-width, border-color',
                  'transition-duration': '300ms',
                }
              },
              {
                selector: 'edge',
                style: {
                  'width': 4,
                  'line-color': '#888',
                  'target-arrow-color': '#00ffcc',
                  'target-arrow-shape': 'triangle',
                  'curve-style': 'bezier',
                  'label': 'data(label)',
                  'font-size': 14,
                  'color': '#fff',
                  'text-background-color': '#222',
                  'text-background-opacity': 1,
                  'text-background-padding': 2,
                  'transition-property': 'line-color, target-arrow-color, width',
                  'transition-duration': '400ms',
                }
              }
            ]}
          />
          <Typography variant="body2" sx={{ color: '#aaa', textAlign: 'center', mt: 2 }}>
            Double-click background to add a node. Tap two nodes to create an edge.<br />
            Future: Drag, edit, animate, and sync with backend!
          </Typography>
        </Paper>
        <Paper elevation={4} sx={{ maxWidth: 600, mx: 'auto', p: 3, bgcolor: '#111', borderRadius: 3 }}>
          <Typography variant="h6" sx={{ color: '#00ffcc', mb: 2 }}>
            Chat with CEO Agent
          </Typography>
          <Box sx={{ minHeight: 120, maxHeight: 220, overflowY: 'auto', bgcolor: '#222', borderRadius: 2, p: 2, mb: 2 }}>
            {messages.map((message, index) => (
              <div key={index} className={`message ${message.role}`}>
                <div className="message-content">
                  <strong>{message.role === 'user' ? 'You' : 'AI'}:</strong>
                  <p>{message.content}</p>
                  
                  {message.thought_process && (
                    <div className="thought-process">
                      <button
                        onClick={() => toggleThoughtProcess(index)}
                        className="thought-toggle"
                      >
                        {showThoughtProcess[index] ? 'Hide' : 'Show'} Thought Process
                      </button>
                      
                      {showThoughtProcess[index] && (
                        <div className="thought-process-content">
                          {formatThoughtProcess(message.thought_process)}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="message loading">
                <div className="message-content">
                  <p>Thinking...</p>
                </div>
              </div>
            )}
          </Box>
          <form onSubmit={handleSubmit} className="input-form">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              disabled={loading}
            />
            <button type="submit" disabled={loading}>
              Send
            </button>
          </form>
        </Paper>
      </Container>
    </Box>
  );
}

export default App;
