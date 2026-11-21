// Inline stroke icons used across the page, so there's no icon library dependency.
// Size and color come from the .ico classes in styles.css.
const Svg = ({ className = 'ico', children }) => (
  <svg className={className} viewBox="0 0 24 24">{children}</svg>
);

export const CapIcon = () => (
  <Svg className="ico gold">
    <path d="M2 9l10-5 10 5-10 5L2 9z" /><path d="M6 11.5V16c0 1.5 2.7 3 6 3s6-1.5 6-3v-4.5" /><path d="M22 9v6" />
  </Svg>
);
export const HomeIcon = () => <Svg><path d="M3 11l9-8 9 8" /><path d="M5 10v10h5v-6h4v6h5V10" /></Svg>;
export const ChevronIcon = () => <Svg className="ico sm"><path d="M6 9l6 6 6-6" /></Svg>;
export const TagIcon = () => <Svg><path d="M3 12V4h8l10 10-8 8L3 12z" /><circle cx="7.5" cy="8.5" r="1" /></Svg>;
export const GridIcon = () => (
  <Svg>
    <rect x="3" y="3" width="7" height="7" rx="1" /><rect x="14" y="3" width="7" height="7" rx="1" />
    <rect x="3" y="14" width="7" height="7" rx="1" /><rect x="14" y="14" width="7" height="7" rx="1" />
  </Svg>
);
export const MenuIcon = () => <Svg><path d="M4 7h16M4 12h16M4 17h16" /></Svg>;
export const SearchIcon =() => <Svg><circle cx="10" cy="10" r="6" /><path d="M15 15l6 6" /></Svg>;
export const TelegramIcon = () => <Svg><path d="M21 3L3 11l6 2 2 7 3-5 5 3 2-15z" /></Svg>;
export const InstagramIcon = () => (
  <Svg><rect x="3" y="3" width="18" height="18" rx="5" /><circle cx="12" cy="12" r="4" /><circle cx="17.5" cy="6.5" r=".8" /></Svg>
);
