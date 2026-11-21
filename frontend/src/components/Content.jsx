// Tabs, stats strip and the four mock-type cards, rendered from the constants below.
// The tabs don't switch content yet; Tier-I is always shown as active.
import { StubLink, useStub } from '../stub.jsx';

const TABS = [
  { id: 'tier1', name: 'Tier-I', sub: 'Prelims' },
  { id: 'tier2', name: 'Tier-II', sub: 'Mains' },
  { id: 'notes', name: 'Notes', sub: 'Free', icon: '✎ ' },
];

const STATS = [
  { value: 128, label: 'Full Mocks' },
  { value: 213, label: 'PYQ Papers' },
  { value: 753, label: 'Chapter-wise' },
  { value: 300, label: 'Sectional' },
];

const CARDS = [
  { icon: '📋', title: 'Full Mocks', text: 'Full-length Tier-I CBT mocks on the latest exam pattern.',
    chips: ['100 Q · 4 sections', '60 min'], gold: 'Bilingual', cta: 'Open Full Mocks' },
  { icon: '🕐', title: 'Previous Year Papers', text: 'Year-wise SSC CGL papers, including 53 papers from 2026, with timed practice and answer review.',
    chips: ['Year-wise', '2026 PYQs', 'Answer review'], gold: 'English / हिंदी', cta: 'Open PYQ' },
  { icon: '📚', title: 'Chapter-wise Mocks', text: 'Topic-by-topic practice across Quant, Reasoning, English & GK.',
    chips: ['All 4 subjects', 'Instant scoring'], gold: 'Bilingual', cta: 'Open Chapter-wise' },
  { icon: '📝', title: 'Sectional Mocks', text: 'Single-subject tests on the real SSC CGL exam pattern.',
    chips: ['All 4 subjects', 'Exam pattern'], gold: 'Bilingual', cta: 'Open Subject Mocks' },
];

export default function Content() {
  const stub = useStub();
  return (
    <main className="wrap main">
      <div className="tabs">
        {TABS.map((t, i) => (
          <button key={t.id} className={`tab${i === 0 ? ' active' : ''}`} onClick={() => stub(`${t.name} tab`)}>
            {t.icon}{t.name} <small>&middot; {t.sub}</small>
          </button>
        ))}
      </div>

      <div className="stats">
        {STATS.map((s) => (
          <div className="stat" key={s.label}><strong>{s.value}</strong><i /><span>{s.label}</span></div>
        ))}
        <div className="stat bi"><b>2-in-1</b><span>EN &amp; हिंदी</span></div>
      </div>

      <div className="cards">
        {CARDS.map((c) => (
          <article className="card" key={c.title} onClick={() => stub(c.title)}>
            <div className="ci">{c.icon}</div>
            <h3>{c.title}</h3>
            <p>{c.text}</p>
            <div className="chips">
              {c.chips.map((chip) => <em key={chip}>{chip}</em>)}
              <em className="g">{c.gold}</em>
            </div>
            <StubLink label={c.cta} className="open">
              {c.cta} &rarr;
            </StubLink>
          </article>
        ))}
      </div>
    </main>
  );
}
