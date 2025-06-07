import React, { useState, useRef, useEffect, useCallback } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';
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
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [showThoughtProcess, setShowThoughtProcess] = useState({});
  const messagesEndRef = useRef(null);
  const lastMessageCountRef = useRef(0);
  const [shouldScroll, setShouldScroll] = useState(false);

  // Fit graph to container on mount and when elements change
  useEffect(() => {
    if (cyRef.current) {
      cyRef.current.fit();
    }
  }, [elements]);

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

  // Simple scroll function
  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ 
        behavior: "smooth",
        block: "end"
      });
    }
  };

  // Handle scrolling when flag is set
  useEffect(() => {
    if (shouldScroll) {
      const timeoutId = setTimeout(() => {
        scrollToBottom();
        setShouldScroll(false); // Reset the flag
      }, 100);
      
      return () => clearTimeout(timeoutId);
    }
  }, [shouldScroll]);

  // Animate CEO node when loading (pulsing effect)
  useEffect(() => {
    if (cyRef.current) {
      const ceoNode = cyRef.current.getElementById('ceo');
      if (loading) {
        let pulse = true;
        let pulseInterval = setInterval(() => {
          if (ceoNode) {
            ceoNode.animate({ 
              style: { 
                'background-color': pulse ? '#ffeb3b' : '#00ffcc', 
                'border-width': pulse ? 10 : 3, 
                'border-color': pulse ? '#fff176' : '#fff' 
              } 
            }, { duration: 250 });
            pulse = !pulse;
          }
        }, 300);
        return () => {
          clearInterval(pulseInterval);
          if (ceoNode) ceoNode.animate({ 
            style: { 
              'background-color': '#00ffcc', 
              'border-width': 3, 
              'border-color': '#fff' 
            } 
          }, { duration: 300 });
        };
      } else {
        if (ceoNode) ceoNode.animate({ 
          style: { 
            'background-color': '#00ffcc', 
            'border-width': 3, 
            'border-color': '#fff' 
          } 
        }, { duration: 300 });
      }
    }
  }, [loading]);

  // Generate a new session ID on component mount
  useEffect(() => {
    const newSessionId = Date.now().toString();
    setSessionId(newSessionId);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setLoading(true);

    // Add user message to the chat
    const newUserMessage = { 
      id: Date.now(), 
      role: 'user', 
      content: userMessage 
    };
    
    setMessages(prev => [...prev, newUserMessage]);
    setShouldScroll(true); // Trigger scroll after adding user message

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

      const response = await fetch('http://localhost:8001/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          session_id: sessionId
        }),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.status === 'success') {
        // Add AI response to the chat
        const newAIMessage = {
          id: Date.now() + 1,
          role: 'assistant',
          content: data.response,
          thought_process: data.thought_process
        };
        setMessages(prev => [...prev, newAIMessage]);
        setShouldScroll(true); // Trigger scroll after adding AI message
      } else {
        throw new Error(data.error || 'Failed to get response from AI');
      }
    } catch (error) {
      console.error('Error:', error);
      let errorMessage = 'Sorry, there was an error processing your request.';
      
      if (error.name === 'AbortError') {
        errorMessage = 'Request timed out. Please try again.';
      } else if (error.message.includes('Failed to fetch')) {
        errorMessage = 'Could not connect to the backend server. Please make sure it is running on port 8001.';
      } else if (error.message.includes('HTTP error')) {
        errorMessage = `Server error: ${error.message}. Please check the backend logs.`;
      } else {
        errorMessage = `Error: ${error.message}`;
      }

      const errorMsg = {
        id: Date.now() + 2,
        role: 'error',
        content: errorMessage
      };
      setMessages(prev => [...prev, errorMsg]);
      setShouldScroll(true); // Trigger scroll after adding error message
    } finally {
      setLoading(false);
    }
  };

  const handleNewSession = () => {
    const newSessionId = Date.now().toString();
    setSessionId(newSessionId);
    setMessages([]);
    setShowThoughtProcess({});
    lastMessageCountRef.current = 0;
    setShouldScroll(false); // Reset scroll flag
  };

  const toggleThoughtProcess = (messageId) => {
    setShowThoughtProcess(prev => ({
      ...prev,
      [messageId]: !prev[messageId]
    }));
  };

  const formatThoughtProcess = (thoughtProcess) => {
    if (!thoughtProcess) return null;
    
    return thoughtProcess.split('\n\n').map((section, i) => {
      if (!section.trim()) return null;
      
      const lines = section.split('\n');
      const header = lines[0];
      const content = lines.slice(1).join('\n');
      
      return (
        <div key={i} className="thought-section">
          <h4>{header}</h4>
          <p>{content}</p>
        </div>
      );
    }).filter(Boolean);
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1 className="app-title">AI-Lab Organization Chart & Agent Pipeline</h1>
        <button onClick={handleNewSession} className="new-session-btn">
          New Session
        </button>
      </header>
      
      <div className="main-content">
        <div className="org-chart-section">
          <h2 className="section-title">Organization Chart & Agent Pipeline</h2>
          <div className="chart-container">
            <CytoscapeComponent
              elements={elements}
              style={{ width: '100%', height: '100%', background: 'transparent' }}
              cy={handleCyInit}
              layout={{ name: 'preset' }}
              stylesheet={[
                {
                  selector: 'node',
                  style: {
                    'background-color': '#00ffcc',
                    'label': 'data(label)',
                    'color': '#1a1a2e',
                    'font-size': 16,
                    'font-weight': 'bold',
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'width': 80,
                    'height': 80,
                    'border-width': 3,
                    'border-color': '#fff',
                    'transition-property': 'background-color, border-width, border-color',
                    'transition-duration': '300ms',
                    'box-shadow': '0 4px 12px rgba(0, 255, 204, 0.3)',
                  }
                },
                {
                  selector: 'edge',
                  style: {
                    'width': 3,
                    'line-color': '#64748b',
                    'target-arrow-color': '#00ffcc',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier',
                    'label': 'data(label)',
                    'font-size': 12,
                    'color': '#94a3b8',
                    'text-background-color': '#1e293b',
                    'text-background-opacity': 0.8,
                    'text-background-padding': 4,
                    'transition-property': 'line-color, target-arrow-color, width',
                    'transition-duration': '400ms',
                  }
                }
              ]}
            />
            <p className="chart-help-text">
              Double-click background to add a node. Tap two nodes to create an edge.<br />
              Watch the CEO node pulse when processing your requests!
            </p>
          </div>
        </div>
        
        <div className="chat-section">
          <div className="chat-container">
            <h2 className="section-title">Chat with CEO Agent</h2>
            <div className="chat-messages">
              {messages.length === 0 && (
                <div className="message assistant">
                  <div className="message-content">
                    <strong>AI:</strong>
                    <p>Welcome to AI-Lab! I'm the CEO agent. You can ask me about our organization structure, delegate tasks, or discuss strategy. How can I help you today?</p>
                  </div>
                </div>
              )}
              
              {messages.map((message) => (
                <div key={message.id} className={`message ${message.role}`}>
                  <div className="message-content">
                    <strong>{message.role === 'user' ? 'YOU' : message.role === 'error' ? 'ERROR' : 'AI'}:</strong>
                    <p>{message.content}</p>
                    
                    {message.thought_process && (
                      <div className="thought-process">
                        <button
                          onClick={() => toggleThoughtProcess(message.id)}
                          className="thought-toggle"
                        >
                          {showThoughtProcess[message.id] ? 'Hide' : 'Show'} Thought Process
                        </button>
                        
                        {showThoughtProcess[message.id] && (
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
                    <strong>AI:</strong>
                    <p>Processing your request...</p>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
            
            <form onSubmit={handleSubmit} className="input-form">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about our organization or delegate a task..."
                disabled={loading}
              />
              <button type="submit" disabled={loading || !input.trim()}>
                {loading ? 'Sending...' : 'Send'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
