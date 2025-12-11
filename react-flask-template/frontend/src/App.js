import React, { useState, useEffect } from 'react';
import './App.css';
import HelloComponent from './components/HelloComponent';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>React + Flask Full-Stack App</h1>
        <p>Frontend (React) - Port 3000</p>
        <p>Backend (Flask) - Port 5000</p>
      </header>
      <main className="App-main">
        <HelloComponent />
      </main>
    </div>
  );
}

export default App;

