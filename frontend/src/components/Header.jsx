export default function Header({ setMobileOpen }) {
  return (
    <header className="top-header">
      <div className="header-left">
        <button className="mobile-menu-btn" onClick={() => setMobileOpen(true)} aria-label="Open Menu">
          ☰
        </button>
        <div>
          <h1 className="header-title">Dashboard</h1>
          <p className="header-subtitle">Your career preparation workspace</p>
        </div>
      </div>
      <div className="header-right">
        <div className="avatar">MA</div>
      </div>
    </header>
  );
}
