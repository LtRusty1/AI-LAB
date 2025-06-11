import React, { useState, useEffect } from 'react';
import './APIKeyManager.css';

const APIKeyManager = () => {
  const [apiKeys, setApiKeys] = useState({});
  const [newKey, setNewKey] = useState({ service: '', key: '' });
  const [supportedServices, setSupportedServices] = useState([]);
  const [loading, setLoading] = useState(false);
  const [testing, setTesting] = useState({});
  const [confirmDelete, setConfirmDelete] = useState(null);

  useEffect(() => {
    fetchApiKeys();
  }, []);

  const fetchApiKeys = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8001/api-keys');
      const data = await response.json();
      
      // Convert the configured_services array to an object for easier handling
      const configuredServicesArray = data.configured_services || [];
      const configuredServicesObject = {};
      configuredServicesArray.forEach(service => {
        configuredServicesObject[service] = true;
      });
      
      setApiKeys(configuredServicesObject);
      
      // Ensure supportedServices is always an array
      const services = data.supported_services || [];
      setSupportedServices(Array.isArray(services) ? services : Object.keys(services));
    } catch (error) {
      console.error('Failed to fetch API keys:', error);
      // Set fallback supported services if API fails
      setSupportedServices(['openai', 'anthropic', 'google', 'azure', 'cohere', 'huggingface', 'ollama']);
    }
  };

  const handleAddKey = async () => {
    if (!newKey.service || !newKey.key) return;
    
    setLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:8001/api-keys', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          service_name: newKey.service,
          api_key: newKey.key
        })
      });
      
      const result = await response.json();
      if (result.success) {
        setNewKey({ service: '', key: '' });
        fetchApiKeys();
      } else {
        alert(`Failed to add API key: ${result.message}`);
      }
    } catch (error) {
      alert(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleTestKey = async (service) => {
    setTesting(prev => ({ ...prev, [service]: true }));
    try {
      const response = await fetch(`http://127.0.0.1:8001/api-keys/${service}/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      const result = await response.json();
      alert(result.success ? 'API key is valid!' : `API key test failed: ${result.message}`);
    } catch (error) {
      alert(`Test failed: ${error.message}`);
    } finally {
      setTesting(prev => ({ ...prev, [service]: false }));
    }
  };

  const handleRemoveKey = async (service) => {
    try {
      const response = await fetch(`http://127.0.0.1:8001/api-keys/${service}`, {
        method: 'DELETE'
      });
      
      const result = await response.json();
      if (result.success) {
        fetchApiKeys();
      } else {
        alert(`Failed to remove API key: ${result.message}`);
      }
    } catch (error) {
      alert(`Error: ${error.message}`);
    }
    setConfirmDelete(null);
  };

  return (
    <div className="api-key-manager">
      <h3>API Key Management</h3>
      
      <div className="add-key-section">
        <h4>Add New API Key</h4>
        <div className="add-key-form">
          <select 
            value={newKey.service} 
            onChange={(e) => setNewKey(prev => ({ ...prev, service: e.target.value }))}
          >
            <option value="">Select Service</option>
            {supportedServices && supportedServices.length > 0 ? (
              supportedServices.map(service => (
                <option key={service} value={service}>{service}</option>
              ))
            ) : (
              <option disabled>Loading services...</option>
            )}
          </select>
          
          <input
            type="password"
            placeholder="API Key"
            value={newKey.key}
            onChange={(e) => setNewKey(prev => ({ ...prev, key: e.target.value }))}
          />
          
          <button 
            onClick={handleAddKey} 
            disabled={loading || !newKey.service || !newKey.key}
          >
            {loading ? 'Adding...' : 'Add Key'}
          </button>
        </div>
      </div>

      <div className="configured-keys">
        <h4>Configured API Keys</h4>
        {Object.keys(apiKeys).length === 0 ? (
          <p>No API keys configured yet.</p>
        ) : (
          <div className="key-list">
            {Object.keys(apiKeys).map(service => (
              <div key={service} className="key-item">
                <span className="service-name">{service}</span>
                <div className="key-actions">
                  <button 
                    onClick={() => handleTestKey(service)}
                    disabled={testing[service]}
                  >
                    {testing[service] ? 'Testing...' : 'Test'}
                  </button>
                  <button 
                    onClick={() => setConfirmDelete(service)}
                    className="remove-btn"
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {confirmDelete && (
        <div className="confirmation-overlay">
          <div className="confirmation-dialog">
            <h4>Confirm Deletion</h4>
            <p>Are you sure you want to remove the API key for {confirmDelete}?</p>
            <div className="confirmation-actions">
              <button 
                onClick={() => handleRemoveKey(confirmDelete)}
                className="confirm-btn"
              >
                Yes, Remove
              </button>
              <button 
                onClick={() => setConfirmDelete(null)}
                className="cancel-btn"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default APIKeyManager; 