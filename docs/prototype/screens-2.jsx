/* global React, Icon, ScenePlaceholder, BoundingBoxes */
const { useState: useState_r, useEffect: useEffect_r, useMemo: useMemo_r, useRef: useRef_r } = React;

/* ====================================================================
 * Results Screen
 * ==================================================================== */
function ResultsScreen({ file, onReset, markingStyle, showTags }) {
  const detections = window.DETECTIONS;
  const [activeId, setActiveId] = useState_r(null);
  const [hoverId, setHoverId] = useState_r(null);
  const [filter, setFilter] = useState_r("all"); // all | ok | bad

  // Stats
  const stats = useMemo_r(() => {
    const total = detections.length;
    const okCount = detections.filter(p => window.computeStatus(p).ok).length;
    const badCount = total - okCount;
    const pct = total === 0 ? 0 : Math.round((okCount / total) * 100);
    return { total, okCount, badCount, pct };
  }, [detections]);

  const filtered = useMemo_r(() => {
    if (filter === "all") return detections;
    if (filter === "ok")  return detections.filter(p => window.computeStatus(p).ok);
    return detections.filter(p => !window.computeStatus(p).ok);
  }, [detections, filter]);

  // close on Esc
  useEffect_r(() => {
    const onKey = (e) => { if (e.key === "Escape") setActiveId(null); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <section className="results-screen fade-in">
      <div className="results-header">
        <div>
          <div className="breadcrumbs">
            <span>Análises</span>
            <span className="sep">/</span>
            <span className="current">{file?.name || "canteiro_obras_demo.jpg"}</span>
          </div>
          <h1 style={{ marginTop: 6 }}>Resultado da análise</h1>
        </div>
        <div className="header-actions">
          <button className="btn btn-ghost" onClick={onReset}>
            <Icon.Reload /> Analisar nova imagem
          </button>
        </div>
      </div>

      <div className="image-panel">
        <div className="image-toolbar">
          <div className="left">
            <span className="file">{file?.name || "canteiro_obras_demo.jpg"}</span>
            <span>1920 × 1200</span>
            <span>processado em 4.8s</span>
          </div>
          <div className="legend">
            <span className="legend-item"><span className="legend-dot ok"></span> Conforme</span>
            <span className="legend-item"><span className="legend-dot bad"></span> Sem EPI completo</span>
          </div>
        </div>
        <div className="image-stage">
          <div style={{ position: "relative", aspectRatio: "16 / 10", width: "calc(100% - 32px)", maxHeight: "calc(100% - 32px)" }}>
            <ScenePlaceholder />
            <BoundingBoxes
              detections={detections}
              activeId={activeId}
              hoverId={hoverId}
              onActivate={setActiveId}
              onHover={setHoverId}
              markingStyle={markingStyle}
              showTags={showTags}
            />
          </div>
        </div>
      </div>

      <aside className="sidebar">
        <div className="card">
          <div className="eyebrow" style={{ marginBottom: 14 }}>Resumo</div>
          <div className="stats-grid">
            <div className="stat">
              <span className="label">Total</span>
              <span className="value">{String(stats.total).padStart(2, "0")}</span>
            </div>
            <div className="stat ok">
              <span className="label">Conformes</span>
              <span className="value">{String(stats.okCount).padStart(2, "0")}</span>
            </div>
            <div className="stat bad">
              <span className="label">Sem EPI</span>
              <span className="value">{String(stats.badCount).padStart(2, "0")}</span>
            </div>
            <div className="stat">
              <span className="label">Avg. confidence</span>
              <span className="value">
                {Math.round(detections.reduce((a, p) => a + p.confidence, 0) / detections.length * 100)}
                <span style={{ fontSize: 14, color: "var(--text-muted)" }}>%</span>
              </span>
            </div>
          </div>

          <div className="compliance-bar">
            <div className="top">
              <h4>Conformidade da cena</h4>
              <span className="pct">{stats.pct}%</span>
            </div>
            <div className="bar-track">
              <div className="bar-seg ok" style={{ width: `${stats.pct}%` }}></div>
              <div className="bar-seg bad" style={{ width: `${100 - stats.pct}%` }}></div>
            </div>
            <div className="bar-meta">
              <span>{stats.okCount} conforme</span>
              <span>{stats.badCount} requerem atenção</span>
            </div>
          </div>
        </div>

        <div className="card persons-card">
          <div className="card-head">
            <h3>Pessoas detectadas</h3>
            <span className="count">{filtered.length} de {detections.length}</span>
          </div>

          <div className="filter-tabs" role="tablist">
            {[
              { key: "all", label: "Todas", count: stats.total },
              { key: "bad", label: "Sem EPI", count: stats.badCount },
              { key: "ok",  label: "Conformes", count: stats.okCount },
            ].map(t => (
              <button
                key={t.key}
                className={`filter-tab ${filter === t.key ? "active" : ""}`}
                onClick={() => setFilter(t.key)}
              >
                {t.label}<span className="filter-count">{t.count}</span>
              </button>
            ))}
          </div>

          <ul className="person-list">
            {filtered.map(p => {
              const { ok, missing } = window.computeStatus(p);
              const isActive = activeId === p.id;
              return (
                <li key={p.id}>
                  <button
                    className={`person ${isActive ? "is-active" : ""} ${ok ? "ok-state" : "bad-state"}`}
                    onClick={() => setActiveId(p.id === activeId ? null : p.id)}
                    onMouseEnter={() => setHoverId(p.id)}
                    onMouseLeave={() => setHoverId(null)}
                  >
                    <span className={`person-num ${ok ? "ok" : "bad"}`}>{p.id}</span>
                    <span className="person-body">
                      <span className="person-title">
                        {p.role}
                        <span className="eyebrow" style={{ fontSize: 10 }}>
                          {ok ? "CONFORME" : "ATENÇÃO"}
                        </span>
                      </span>
                      <span className="person-desc">
                        <span className={`epi-chip ${p.helmet ? "ok" : "bad"}`}>capacete</span>
                        <span className={`epi-chip ${p.vest ? "ok" : "bad"}`}>colete</span>
                        {!ok && (
                          <span style={{ color: "var(--danger)", fontSize: 11.5 }}>
                            sem {missing.join(" e ")}
                          </span>
                        )}
                      </span>
                    </span>
                    <span className="person-conf">{Math.round(p.confidence * 100)}%</span>
                  </button>
                </li>
              );
            })}
            {filtered.length === 0 && (
              <li style={{
                padding: "32px 16px", textAlign: "center",
                color: "var(--text-faint)", fontSize: 13
              }}>
                Nenhuma pessoa neste filtro.
              </li>
            )}
          </ul>
        </div>
      </aside>
    </section>
  );
}

window.ResultsScreen = ResultsScreen;
