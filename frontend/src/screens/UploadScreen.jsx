import { useState, useRef, useCallback } from "react";
import { Icon } from "../components/Icons.jsx";

export default function UploadScreen({ onAnalyze }) {
  const [dragging, setDragging] = useState(false);
  const [file, setFile] = useState(null); // real File object
  const [preview, setPreview] = useState(null); // object URL
  const inputRef = useRef(null);

  const handleFile = useCallback((f) => {
    if (!f) return;
    if (preview) URL.revokeObjectURL(preview);
    setFile(f);
    setPreview(URL.createObjectURL(f));
  }, [preview]);

  const onDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files?.[0];
    if (f) handleFile(f);
  };

  const onPick = (e) => {
    const f = e.target.files?.[0];
    if (f) handleFile(f);
  };

  const fmtSize = (b) => {
    if (b < 1024) return `${b} B`;
    if (b < 1024 * 1024) return `${(b / 1024).toFixed(0)} KB`;
    return `${(b / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <section className="upload-screen fade-in">
      <div className="upload-hero">
        <div className="eyebrow">
          <span style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--brand)", display: "inline-block" }} />
          MVP · processamento 100% local
        </div>
        <h1>
          Detecção de <em>EPI</em> em imagens de obra.
        </h1>
        <p>
          Envie uma foto do ambiente de trabalho. O VisionAI identifica cada
          pessoa na cena e indica quem está em conformidade com capacete e
          colete refletivo.
        </p>
      </div>

      <div
        className={`dropzone ${dragging ? "is-dragging" : ""} ${file ? "has-file" : ""}`}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
      >
        {!file ? (
          <>
            <div className="dropzone-icon">
              <Icon.Upload />
            </div>
            <h3>
              Arraste uma foto ou{" "}
              <button className="file-link" onClick={() => inputRef.current?.click()}>
                selecione do computador
              </button>
            </h3>
            <p className="dz-sub">JPG, PNG ou WebP até 10MB · uma imagem por vez</p>
            <div className="dz-meta">
              <span>FORMATOS: JPG · PNG · WEBP</span>
              <span>MAX: 10MB</span>
              <span>RESOLUÇÃO: até 4096px</span>
            </div>
            <input
              ref={inputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              style={{ display: "none" }}
              onChange={onPick}
            />
          </>
        ) : (
          <div className="preview-row">
            <div className="preview-thumb">
              <img src={preview} alt="Pré-visualização" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
            </div>
            <div className="preview-meta">
              <div className="name">{file.name}</div>
              <div className="size">{fmtSize(file.size)} · pronto para análise</div>
            </div>
            <button
              className="btn-icon"
              onClick={() => { setFile(null); setPreview(null); }}
              title="Remover"
            >
              <Icon.X />
            </button>
          </div>
        )}
      </div>

      <div className="upload-cta">
        <button
          className="btn btn-primary"
          disabled={!file}
          onClick={() => file && onAnalyze(file)}
        >
          Analisar imagem
          <Icon.Arrow />
        </button>
      </div>

      <div className="feature-row">
        {[
          { num: "01", label: "Detecção de pessoas", desc: "YOLOv8 identifica todas as pessoas presentes e isola cada região da cena." },
          { num: "02", label: "Análise por pessoa", desc: "Google Gemini verifica individualmente capacete, colete, óculos e boné de cada trabalhador." },
          { num: "03", label: "Visualização imediata", desc: "Sobreposição colorida com painel resumo e descrição do que está faltando." },
        ].map((f) => (
          <div className="feature" key={f.num}>
            <span className="num">{f.num}</span>
            <span className="label">{f.label}</span>
            <span className="desc">{f.desc}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
