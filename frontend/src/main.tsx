import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

const rootElement = document.getElementById('root');

if (!rootElement) {
  document.body.innerHTML = '<div style="padding: 40px; font-family: Arial; background: #fee; color: #c00;"><h1>Error: Root element not found</h1><p>The #root div is missing from the HTML.</p></div>';
} else {
  createRoot(rootElement).render(
    <StrictMode>
      <App />
    </StrictMode>,
  );
}
