// Top navigation bar with brand, links, Logout and theme buttons.
// Every item redirects to the external site except the theme button, which opens the secret screen.
import { StubLink, useStub } from '../stub.jsx';
import { CapIcon, ChevronIcon, GridIcon, HomeIcon, MenuIcon, TagIcon } from './Icons.jsx';

export default function Navbar({ onThemeToggle }) {
  const stub = useStub();
  return (
    <header className="nav">
      <div className="nav-inner">
        <StubLink label="Logo" className="brand">
          <CapIcon />
          <span className="brand-name">MockCampus <small>by</small> PD</span>
        </StubLink>
        <nav className="links">
          <StubLink label="Home"><HomeIcon />Home</StubLink>
          <StubLink label="MockCampus">MockCampus</StubLink>
          <StubLink label="KnowledgeHub">KnowledgeHub</StubLink>
          <StubLink label="SkillCampus">SkillCampus</StubLink>
          <StubLink label="Exams">Exams <ChevronIcon /></StubLink>
          <StubLink label="Pricing"><TagIcon />Pricing</StubLink>
          <StubLink label="Dashboard"><GridIcon />Dashboard</StubLink>
          <button className="menu-btn" aria-label="Menu" onClick={() => stub('Menu')}><MenuIcon /></button>
          <button className="btn-logout" onClick={() => stub('Logout')}>Logout</button>
          <button className="btn-theme" aria-label="Theme" onClick={onThemeToggle}>&#9790;</button>
        </nav>
      </div>
    </header>
  );
}
