// Footer with tagline, buddy code link, pass bar and social links.
// Every link and button here redirects to the external SSC CGL page.
import { StubLink, useStub } from '../stub.jsx';
import { CapIcon, InstagramIcon, TelegramIcon } from './Icons.jsx';

export default function Footer() {
  const stub = useStub();
  return (
    <footer className="foot">
      <div className="foot-brand">
        <CapIcon />
        <span className="brand-name">MockCampus by PD</span>
        <span className="tag">
          &middot; CBT mocks for SSC, UPSC, Banking, Railway, NEET &amp; JEE. <b>Practice. Analyze. Excel.</b>
        </span>
      </div>
      <StubLink label="Redeem a buddy code" className="buddy">Redeem a buddy code</StubLink>
      <button className="pass" onClick={() => stub('SSC CGL Pass')}>🔒 SSC CGL Pass · ₹1/day</button>
      <div className="social">
        <StubLink label="Telegram"><TelegramIcon />Telegram</StubLink>
        <StubLink label="Instagram"><InstagramIcon />Instagram</StubLink>
      </div>
      <p className="copy">© 2026 MockCampus by PD (pdcampus.in). All rights reserved. · Made with ❤️ for Indian students.</p>
    </footer>
  );
}
