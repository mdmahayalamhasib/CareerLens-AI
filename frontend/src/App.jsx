import { useState } from 'react';
import { BrowserRouter, Routes, Route, useNavigate, useLocation, Navigate } from 'react-router-dom';
import './App.css';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import ResumeAnalysis from './pages/ResumeAnalysis';
import JobMatcher from './pages/JobMatcher';
import SkillGap from './pages/SkillGap';
import InterviewPrep from './pages/InterviewPrep';
import CoverLetter from './pages/CoverLetter';

const routeMap = {
  'dashboard': '/dashboard',
  'resume': '/resume-analysis',
  'job': '/job-matcher',
  'skills': '/skill-gap',
  'interview': '/interview-prep',
  'cover_letter': '/cover-letter',
  'settings': '/dashboard' // fallback
};

const reverseMap = Object.fromEntries(Object.entries(routeMap).map(([k, v]) => [v, k]));

function AppContent() {
  const navigate = useNavigate();
  const location = useLocation();
  const [isMobileOpen, setMobileOpen] = useState(false);

  // Safe Session Storage Hooks
  const getInitialState = (key, fallback) => {
    try {
      const stored = sessionStorage.getItem(key);
      return stored ? JSON.parse(stored) : fallback;
    } catch {
      return fallback;
    }
  };

  const [globalAtsScore, setGlobalAtsScoreState] = useState(() => getInitialState('atsScore', null));
  const [globalResumeData, setGlobalResumeDataState] = useState(() => getInitialState('resumeData', null));
  const [latestMatchScore, setLatestMatchScoreState] = useState(() => getInitialState('matchScore', null));
  const [globalJobData, setGlobalJobDataState] = useState(() => getInitialState('jobData', null));
  const [globalSkillsToImprove, setGlobalSkillsToImproveState] = useState(() => getInitialState('skillsToImprove', null));

  // Wrappers to update state and storage simultaneously
  const setGlobalAtsScore = (val) => {
    setGlobalAtsScoreState(val);
    try { sessionStorage.setItem('atsScore', JSON.stringify(val)); } catch {}
  };

  const setGlobalResumeData = (val) => {
    setGlobalResumeDataState(val);
    try { sessionStorage.setItem('resumeData', JSON.stringify(val)); } catch {}

    // Wipe stale relational states
    setLatestMatchScoreState(null);
    setGlobalSkillsToImproveState(null);
    try { 
      sessionStorage.removeItem('matchScore'); 
      sessionStorage.removeItem('skillsToImprove'); 
    } catch {}
  };

  const setLatestMatchScore = (val) => {
    setLatestMatchScoreState(val);
    try { sessionStorage.setItem('matchScore', JSON.stringify(val)); } catch {}
  };

  const setGlobalJobData = (val) => {
    setGlobalJobDataState(val);
    try { sessionStorage.setItem('jobData', JSON.stringify(val)); } catch {}
    
    // Wipe stale relational states
    setGlobalSkillsToImproveState(null);
    try { sessionStorage.removeItem('skillsToImprove'); } catch {}
  };

  const setGlobalSkillsToImprove = (val) => {
    setGlobalSkillsToImproveState(val);
    try { sessionStorage.setItem('skillsToImprove', JSON.stringify(val)); } catch {}
  };

  const activeNav = reverseMap[location.pathname] || 'dashboard';

  const setActiveNav = (id) => {
    navigate(routeMap[id] || '/dashboard');
  };

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
        
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard setActiveNav={setActiveNav} atsScore={globalAtsScore} latestMatchScore={latestMatchScore} skillsToImprove={globalSkillsToImprove} />} />
          <Route path="/resume-analysis" element={<ResumeAnalysis setGlobalAtsScore={setGlobalAtsScore} setGlobalResumeData={setGlobalResumeData} />} />
          <Route path="/job-matcher" element={<JobMatcher resumeData={globalResumeData} setLatestMatchScore={setLatestMatchScore} setGlobalJobData={setGlobalJobData} setActiveNav={setActiveNav} />} />
          <Route path="/skill-gap" element={<SkillGap resumeData={globalResumeData} jobData={globalJobData} setGlobalSkillsToImprove={setGlobalSkillsToImprove} setActiveNav={setActiveNav} />} />
          <Route path="/interview-prep" element={<InterviewPrep resumeData={globalResumeData} jobData={globalJobData} setActiveNav={setActiveNav} />} />
          <Route path="/cover-letter" element={<CoverLetter resumeData={globalResumeData} jobData={globalJobData} setActiveNav={setActiveNav} />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}

export default App;
