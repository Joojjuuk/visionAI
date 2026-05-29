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
    const helmetOk = p.helmet;
    const vestOk = p.vest;
    const glassesOk = p.glasses !== undefined ? p.glasses : true;
    const capAlert = p.cap === true;

    const ok = helmetOk && vestOk && glassesOk && !capAlert;
    const missing = [];
    if (!p.helmet) missing.push("capacete");
    if (!p.vest) missing.push("colete");
    if (p.glasses === false) missing.push("óculos");
    if (p.cap === true) missing.push("boné");
    return { ok, missing, capAlert };
  };

  return (
    <>
      {detections.map((p, idx) => {
        const { ok, capAlert } = computeStatus(p);
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
                <span>{ok ? "CONFORME" : capAlert ? "ALERTA (BONÉ)" : "INCOMPLETO"}</span>
                <span className="num">{Math.round(p.confidence * 100)}%</span>
              </span>
            )}
          </button>
        );
      })}
    </>
  );
}
