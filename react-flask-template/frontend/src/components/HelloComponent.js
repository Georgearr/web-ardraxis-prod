import React, { useState, useEffect } from 'react';
import './HelloComponent.css';

const HelloComponent = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch data from Flask backend
    const fetchData = async () => {
      try {
        setLoading(true);
        // Using proxy from package.json, so we can use relative path
        const response = await fetch('/api/hello');
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        setData(result);
        setError(null);
      } catch (err) {
        setError(err.message);
        console.error('Error fetching data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleRefresh = () => {
    window.location.reload();
  };

  return (
    <div className="hello-component">
      <div className="card">
        <h2>Flask API Response</h2>
        
        {loading && (
          <div className="loading">
            <p>Loading...</p>
          </div>
        )}
        
        {error && (
          <div className="error">
            <p>Error: {error}</p>
            <p className="error-hint">
              Make sure Flask backend is running on port 5000
            </p>
          </div>
        )}
        
        {data && !loading && !error && (
          <div className="success">
            <div className="response-box">
              <p className="message">{data.message}</p>
              <p className="status">Status: {data.status}</p>
            </div>
            <button onClick={handleRefresh} className="refresh-btn">
              Refresh
            </button>
          </div>
        )}
      </div>
      
      <div className="info-box">
        <h3>How it works:</h3>
        <ol>
          <li>React frontend (port 3000) makes a request to Flask backend</li>
          <li>Flask backend (port 5000) responds with JSON data</li>
          <li>React displays the response in the UI</li>
        </ol>
      </div>
    </div>
  );
};

export default HelloComponent;

