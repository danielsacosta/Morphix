import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './app/App';
import './app/styles/globals.css';
import { loadRuntimeConfig } from './shared/config/env';

const rootElement = document.getElementById('root');

if (!rootElement) {
  throw new Error('Root element not found.');
}

document.documentElement.classList.add('dark');

void loadRuntimeConfig().finally(() => {
  ReactDOM.createRoot(rootElement).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>,
  );
});
