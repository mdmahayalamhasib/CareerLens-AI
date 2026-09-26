import { useState } from 'react';
import './App.css';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import ResumeAnalysis from './pages/ResumeAnalysis';
import JobMatcher from './pages/JobMatcher';

function App() {
  const [activeNav, setActiveNav] = useState('dashboard');
  const [isMobileOpen, setMobileOpen] = useState(false);
  const [globalAtsScore, setGlobalAtsScore] = useState(null);
  const [globalResumeData, setGlobalResumeData] = useState(null);
  const [latestMatchScore, setLatestMatchScore] = useState(null);

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
          <Dashboard setActiveNav={setActiveNav} atsScore={globalAtsScore} latestMatchScore={latestMatchScore} />
        ) : activeNav === 'resume' ? (
          <ResumeAnalysis setGlobalAtsScore={setGlobalAtsScore} setGlobalResumeData={setGlobalResumeData} />
        ) : activeNav === 'job' ? (
          <JobMatcher resumeData={globalResumeData} setLatestMatchScore={setLatestMatchScore} setActiveNav={setActiveNav} />
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
