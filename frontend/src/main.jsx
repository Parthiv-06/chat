// React entry point: mounts <App /> into #root and loads global styles.
// StrictMode double-runs effects in dev, so effects must clean up after themselves.
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';
import './index.css';
import './styles.css';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>
);
