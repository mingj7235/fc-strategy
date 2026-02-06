import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

console.log('🎯 main.tsx loaded');
console.log('🔍 Looking for root element...');

const rootElement = document.getElementById('root');
console.log('📍 Root element:', rootElement);

if (!rootElement) {
  console.error('❌ Root element not found!');
  document.body.innerHTML = '<div style="padding: 40px; font-family: Arial; background: #fee; color: #c00;"><h1>Error: Root element not found</h1><p>The #root div is missing from the HTML.</p></div>';
} else {
  console.log('✅ Root element found, creating React app...');
  createRoot(rootElement).render(
    <StrictMode>
      <App />
    </StrictMode>,
  );
  console.log('✅ React app rendered');
}
