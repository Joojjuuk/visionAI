export default function BoundingBoxes({
  detections,
  activeId,
  hoverId,
  onActivate,
  onHover,
  markingStyle,
  showTags,
}) {
  const computeStatus = (p) => {
    const ok = p.helmet && p.vest;
    const missing = [];
    if (!p.helmet) missing.push("capacete");
    if (!p.vest) missing.push("colete");
    return { ok, missing };
  };

  return (
    <>
      {detections.map((p, idx) => {
        const { ok } = computeStatus(p);
        const cls = [
          "bbox",
          `bbox--${markingStyle}`,
          ok ? "ok" : "bad",
          activeId === p.id ? "is-active" : "",
          activeId != null && activeId !== p.id ? "is-dimmed" : "",
          hoverId === p.id && activeId !== p.id ? "is-hover" : "",
        ]
          .filter(Boolean)
          .join(" ");

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
