/* global React */
const { useState, useRef, useEffect, useCallback } = React;

/* === Icons (simple inline SVG) === */
const Icon = {
  Upload: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
      <polyline points="17 8 12 3 7 8"/>
      <line x1="12" y1="3" x2="12" y2="15"/>
    </svg>
  ),
  Image: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="18" height="18" rx="2"/>
      <circle cx="9" cy="9" r="2"/>
      <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>
    </svg>
  ),
  Arrow: () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="5" y1="12" x2="19" y2="12"/>
      <polyline points="12 5 19 12 12 19"/>
    </svg>
  ),
  Reload: () => (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 12a9 9 0 0 1 15-6.7L21 8"/>
      <path d="M21 3v5h-5"/>
      <path d="M21 12a9 9 0 0 1-15 6.7L3 16"/>
      <path d="M3 21v-5h5"/>
    </svg>
  ),
  Sun: () => (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="4"/>
      <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/>
    </svg>
  ),
  Moon: () => (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
    </svg>
  ),
  X: () => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="18" y1="6" x2="6" y2="18"/>
      <line x1="6" y1="6" x2="18" y2="18"/>
    </svg>
  ),
  Check: () => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12"/>
    </svg>
  )
};

/* === Brand Mark === */
function BrandMark() {
  return (
    <div className="brand-mark">
      <div className="brand-glyph" aria-hidden="true"></div>
      <span className="brand-name"><b>VisionAI</b> <span>· EPI Detection</span></span>
    </div>
  );
}

/* === Theme Toggle === */
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

/* === Top bar === */
function TopBar({ theme, onToggleTheme, status }) {
  return (
    <header className="topbar">
      <BrandMark />
      <div className="topbar-right">
        <div className="status-chip">
          <span className="pulse-dot" aria-hidden="true"></span>
          <span>{status || "Local · YOLOv8 + LLaVA"}</span>
        </div>
        <ThemeToggle theme={theme} onToggle={onToggleTheme} />
      </div>
    </header>
  );
}

/* === Scene placeholder ===
   A schematic construction-site scene. Workers are positioned to match
   the detection coordinates in scene-data.js so the bounding boxes
   actually land on something visually plausible.
*/
function ScenePlaceholder() {
  const detections = window.DETECTIONS;
  return (
    <div className="scene">
      <div className="scene-grid" aria-hidden="true"></div>
      <div className="scene-overlay" aria-hidden="true"></div>
      <div className="scene-elements" aria-hidden="true">
        <div className="scene-crane"></div>
        <div className="scene-scaffold"></div>
        {detections.map(p => (
          <div
            key={p.id}
            className={`scene-person ${p.helmet ? "has-helmet" : ""} ${p.vest ? "has-vest" : ""}`}
            style={{
              left: `${p.x + p.w * 0.18}%`,
              top: `${p.y + p.h * 0.15}%`,
              width: `${p.w * 0.65}%`,
              height: `${p.h * 0.78}%`,
            }}
          ></div>
        ))}
      </div>
      <div className="scene-label">PLACEHOLDER · canteiro_de_obras.jpg</div>
    </div>
  );
}

/* === Bounding box overlay === */
function BoundingBoxes({ detections, activeId, hoverId, onActivate, onHover, markingStyle, showTags }) {
  return (
    <>
      {detections.map((p, idx) => {
        const { ok } = window.computeStatus(p);
        const cls = [
          "bbox",
          `bbox--${markingStyle}`,
          ok ? "ok" : "bad",
          activeId === p.id ? "is-active" : "",
          activeId != null && activeId !== p.id ? "is-dimmed" : "",
          hoverId === p.id && activeId !== p.id ? "is-hover" : ""
        ].filter(Boolean).join(" ");
        return (
          <button
            key={p.id}
            type="button"
            className={cls}
            style={{
              left: `${p.x}%`,
              top: `${p.y}%`,
              width: `${p.w}%`,
              height: `${p.h}%`,
              animationDelay: `${idx * 80}ms`,
              padding: 0,
              cursor: "pointer",
            }}
            onClick={() => onActivate(p.id === activeId ? null : p.id)}
            onMouseEnter={() => onHover(p.id)}
            onMouseLeave={() => onHover(null)}
            aria-label={`Pessoa ${p.id}`}
          >
            <span className="bbox-badge">{p.id}</span>
            {showTags && (
              <span className="bbox-tag">
                <span>{ok ? "CONFORME" : "SEM EPI"}</span>
                <span className="num">{Math.round(p.confidence * 100)}%</span>
              </span>
            )}
          </button>
        );
      })}
    </>
  );
}

window.Icon = Icon;
window.BrandMark = BrandMark;
window.ThemeToggle = ThemeToggle;
window.TopBar = TopBar;
window.ScenePlaceholder = ScenePlaceholder;
window.BoundingBoxes = BoundingBoxes;
