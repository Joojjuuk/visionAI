import { Icon } from "./Icons.jsx";

function BrandMark() {
  return (
    <div className="brand-mark">
      <div className="brand-glyph" aria-hidden="true" />
      <span className="brand-name">
        <b>VisionAI</b> <span>· EPI Detection</span>
      </span>
    </div>
  );
}

function ThemeToggle({ theme, onToggle }) {
  return (
    <button
      className="theme-toggle"
      onClick={onToggle}
      title={theme === "dark" ? "Modo claro" : "Modo escuro"}
      aria-label="Alternar tema"
    >
      <span className="theme-toggle-thumb">
        {theme === "dark" ? <Icon.Moon /> : <Icon.Sun />}
      </span>
    </button>
  );
}

export default function TopBar({ theme, onToggleTheme, status }) {
  return (
    <header className="topbar">
      <BrandMark />
      <div className="topbar-right">
        <div className="status-chip">
          <span className="pulse-dot" aria-hidden="true" />
          <span>{status || "Local · YOLOv8 + LLaVA"}</span>
        </div>
        <ThemeToggle theme={theme} onToggle={onToggleTheme} />
      </div>
    </header>
  );
}
