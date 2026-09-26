export default function Sidebar({ activeNav, setActiveNav, isMobileOpen, setMobileOpen }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'resume', label: 'Resume Analysis' },
    { id: 'job', label: 'Job Matcher' },
    { id: 'skills', label: 'Skill Gap' },
    { id: 'interview', label: 'Interview Prep' },
    { id: 'cover_letter', label: 'Cover Letter' },
  ];

  return (
    <>
      {/* Mobile overlay */}
      {isMobileOpen && <div className="sidebar-overlay" onClick={() => setMobileOpen(false)}></div>}
      
      <aside className={`sidebar ${isMobileOpen ? 'open' : ''}`}>
        <div className="sidebar-brand">
          <h2>CareerLens AI</h2>
        </div>
        
        <nav className="sidebar-nav">
          <ul>
            {navItems.map(item => (
              <li key={item.id}>
                <button 
                  className={`nav-btn ${activeNav === item.id ? 'active' : ''}`}
                  onClick={() => { setActiveNav(item.id); setMobileOpen(false); }}
                >
                  {item.label}
                </button>
              </li>
            ))}
          </ul>
          
          <div className="sidebar-divider"></div>
          
          <ul>
            <li>
              <button 
                className={`nav-btn ${activeNav === 'settings' ? 'active' : ''}`}
                onClick={() => { setActiveNav('settings'); setMobileOpen(false); }}
              >
                Settings
              </button>
            </li>
          </ul>
        </nav>
      </aside>
    </>
  );
}
