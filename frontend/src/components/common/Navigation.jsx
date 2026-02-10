import { NavLink } from 'react-router-dom';
import './Navigation.css';

function Navigation() {
  return (
    <nav className="bottom-nav">
      <NavLink to="/" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
        <span className="nav-icon">📷</span>
        <span className="nav-label">스캔</span>
      </NavLink>
      <NavLink to="/dashboard" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
        <span className="nav-icon">📊</span>
        <span className="nav-label">대시보드</span>
      </NavLink>
      <NavLink to="/receipts" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
        <span className="nav-icon">🧾</span>
        <span className="nav-label">영수증</span>
      </NavLink>
    </nav>
  );
}

export default Navigation;
