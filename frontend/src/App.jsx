import { useState } from 'react';
import './App.css';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import ResumeAnalysis from './pages/ResumeAnalysis';

function App() {
  const [activeNav, setActiveNav] = useState('dashboard');
  const [isMobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="app-layout">
      <Sidebar 
        activeNav={activeNav} 
        setActiveNav={setActiveNav} 
        isMobileOpen={isMobileOpen}
        setMobileOpen={setMobileOpen}
      />
      
      <main className="main-area">
        <Header setMobileOpen={setMobileOpen} />
        
        {activeNav === 'dashboard' ? (
          <Dashboard setActiveNav={setActiveNav} />
        ) : activeNav === 'resume' ? (
          <ResumeAnalysis />
        ) : (
          <div className="placeholder-content">
            <h2>{activeNav.charAt(0).toUpperCase() + activeNav.slice(1).replace('_', ' ')}</h2>
            <p>This module will be implemented in a future phase.</p>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
