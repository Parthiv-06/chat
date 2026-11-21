// Gradient hero with breadcrumb, headline, CTA and search box.
// Registers a global "/" key listener that focuses the search input.
import { useEffect, useRef } from 'react';
import { StubLink, useStub } from '../stub.jsx';
import { SearchIcon } from './Icons.jsx';

export default function Hero() {
  const stub = useStub();
  const inputRef = useRef(null);

  // "/" focuses the search box, as the hint in the UI suggests.
  useEffect(() => {
    const onKey = (e) => {
      if (e.key === '/' && document.activeElement !== inputRef.current) {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, []);

  return (
    <section className="hero">
      <div className="wrap">
        <div className="crumbs">
          <StubLink label="Breadcrumb: Home">Home</StubLink><span>&rsaquo;</span>
          <StubLink label="Breadcrumb: SSC">SSC</StubLink><span>&rsaquo;</span>
          <b>SSC CGL</b>
        </div>
        <p className="eyebrow">SSC &middot; Combined Graduate Level</p>
        <h1>SSC CGL Mock Tests for Tier 1 and Tier 2</h1>
        <p className="lead">
          Practise for SSC CGL Tier-I and Tier-II with full mocks, previous-year papers,{' '}<br />
          2026 PYQs and chapter-wise tests.
        </p>
        <div className="cta-row">
          <button className="btn-gold" onClick={() => stub('Explore 2026 PYQs')}>Explore 2026 PYQs &rarr;</button>
          <span className="cta-note">Browse by date and shift &middot; English / हिंदी</span>
        </div>
      </div>
      <div className="search">
        <SearchIcon />
        <input
          ref={inputRef}
          type="text"
          placeholder="Search 1000+ mocks — topic, chapter, mock number..."
          onKeyDown={(e) => e.key === 'Enter' && stub('Search')}
        />
        <kbd>/</kbd>
      </div>
    </section>
  );
}
