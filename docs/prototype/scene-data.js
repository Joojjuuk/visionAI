// Detection data — fake YOLOv8 + LLaVA output for the demo construction site placeholder.
// Coordinates are in % of scene container (top-left origin).

window.DETECTIONS = [
  {
    id: 1,
    x: 11,  y: 51, w: 9,  h: 32,
    helmet: true,  vest: true,
    confidence: 0.94,
    role: "Trabalhador 01"
  },
  {
    id: 2,
    x: 24,  y: 48, w: 8,  h: 36,
    helmet: false, vest: true,
    confidence: 0.89,
    role: "Trabalhador 02"
  },
  {
    id: 3,
    x: 37,  y: 46, w: 10, h: 39,
    helmet: true,  vest: true,
    confidence: 0.97,
    role: "Trabalhador 03"
  },
  {
    id: 4,
    x: 52,  y: 52, w: 8,  h: 32,
    helmet: true,  vest: false,
    confidence: 0.86,
    role: "Trabalhador 04"
  },
  {
    id: 5,
    x: 65,  y: 49, w: 9,  h: 35,
    helmet: true,  vest: true,
    confidence: 0.92,
    role: "Trabalhador 05"
  },
  {
    id: 6,
    x: 79,  y: 53, w: 8,  h: 30,
    helmet: true,  vest: true,
    confidence: 0.91,
    role: "Trabalhador 06"
  }
];

window.computeStatus = function(p) {
  const ok = p.helmet && p.vest;
  const missing = [];
  if (!p.helmet) missing.push("capacete");
  if (!p.vest)   missing.push("colete");
  return { ok, missing };
};
