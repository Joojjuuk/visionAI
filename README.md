# VisionAI — Detecção de EPI em Obras

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/YOLOv8-Ultralytics-ff6b35?style=flat-square" />
  <img src="https://img.shields.io/badge/Google%20Gemini-2.5%20Flash-4285F4?style=flat-square&logo=google&logoColor=white" />
</div>

<br/>

> **Auditoria visual de conformidade de EPIs (Equipamentos de Proteção Individual) para canteiros de obras, com pipeline híbrido: detecção local (YOLOv8) + classificação na nuvem (Google Gemini 2.5 Flash).**

---

## 🎯 O que é o VisionAI?

O VisionAI é uma ferramenta de segurança do trabalho baseada em IA. O usuário envia uma foto de um ambiente de trabalho e o sistema retorna, de forma visual e interativa, quais trabalhadores estão em conformidade com os EPIs obrigatórios — **capacete, colete refletivo e óculos de proteção** — sinalizando ainda o uso de **boné** como risco, e quais requerem atenção.

A **detecção de pessoas** roda localmente (rápida e leve); a **classificação de EPI** usa o Google Gemini 2.5 Flash na nuvem. Há também um **modo offline** (`--local`) que dispensa internet e chave de API (avalia capacete + colete via visão computacional local).

---

## 🧠 Como Funciona — Fluxo Técnico

```
Imagem enviada pelo usuário
        │
        ▼
┌─────────────────────────────┐
│   YOLOv8 / YOLO-World       │  ← Detecção de pessoas (LOCAL)
│   Detecta ONDE cada pessoa  │    Retorna bounding boxes (%)
│   está na imagem            │    Modelo: yolov8l-world.pt
└────────────┬────────────────┘
             │ coordenadas de cada pessoa
             ▼
┌─────────────────────────────┐
│   Pillow — Recorte          │  ← Recorta a região (cabeça+torso)
│   de cada trabalhador       │    e codifica em Base64
└────────────┬────────────────┘
             │ recorte individual por pessoa
             ▼
┌─────────────────────────────┐
│   Google Gemini 2.5 Flash   │  ← Análise de EPI por pessoa (NUVEM)
│   Structured Output (JSON)  │    Responde: {helmet, vest,
│   forçado por JSON Schema   │              glasses, cap, description}
└────────────┬────────────────┘
             │ status booleano por trabalhador
             ▼
┌─────────────────────────────┐
│   FastAPI — Consolidação    │  ← Monta o JSON de resposta
│   coordenadas + status      │    com detecções e estatísticas
└────────────┬────────────────┘
             │ JSON estruturado
             ▼
┌─────────────────────────────┐
│   Frontend React            │  ← Renderiza a imagem real com
│   bboxes interativas +      │    marcações coloridas
│   painel de estatísticas    │    Verde=conforme / Vermelho=atenção / Âmbar=boné
└─────────────────────────────┘
```

### Por que YOLOv8 + Google Gemini?

| Necessidade | Solução | Por quê |
|-------------|---------|---------|
| Localizar pessoas na imagem | **YOLOv8 / YOLO-World** | Retorna coordenadas precisas de bounding boxes, local e rápido. |
| Verificar presença de EPI | **Google Gemini 2.5 Flash** | VLM multimodal que entende contexto visual; classifica 4 EPIs por pessoa. |
| Garantir resposta confiável | **Structured Output (JSON Schema)** | A API é forçada a devolver JSON estrito — elimina parsing por regex. |
| Renderização interativa | **React** | Bounding boxes dinâmicas no navegador, com hover e painel reativo. |

---

## 🖥️ Interface

Três telas com fluxo linear:

1. **Upload** — drag-and-drop (JPG/PNG/WebP até 10 MB), prévia e botão "Analisar imagem".
2. **Processamento** — animação de scan + log do pipeline (YOLO local + Google Gemini).
3. **Resultados** — imagem com bounding boxes interativas:
   - 🟢 **Verde** — conforme (capacete + colete + óculos, sem boné)
   - 🔴 **Vermelho** — falta pelo menos um EPI
   - 🟠 **Âmbar** — alerta de boné
   - Painel lateral: total, conformes vs. sem EPI, % de conformidade, lista por trabalhador com os 4 chips de EPI e filtros (Todas / Sem EPI / Conformes).

---

## 🏗️ Arquitetura do Projeto

```
visionai/
├── backend/                       # Servidor Python FastAPI
│   ├── app/
│   │   ├── main.py                # Entrada do servidor (carrega YOLO no startup)
│   │   ├── config.py              # Settings (DETECTION_MODE, GEMINI_API_KEY, ...)
│   │   ├── api/router.py          # Rotas: POST /api/analyze, GET /api/status
│   │   └── services/
│   │       ├── yolo_service.py        # Wrapper do YOLO-World (pessoa + capacete)
│   │       ├── gemini_service.py      # Classificação via Google Gemini (nuvem)
│   │       ├── local_cv_service.py    # Fallback offline (capacete + colete via HSV)
│   │       └── pipeline.py            # Orquestrador da pipeline completa
│   ├── .env                       # DETECTION_MODE + GEMINI_API_KEY (não versionado)
│   ├── static/                    # Build do frontend servido aqui
│   ├── uploads/                   # Imagens enviadas temporariamente
│   └── requirements.txt
└── frontend/                      # Aplicação React + Vite
    ├── src/
    │   ├── App.jsx                # Máquina de estados (upload→loading→results)
    │   ├── components/            # TopBar, BoundingBoxes, Icons, TweaksPanel
    │   └── screens/               # UploadScreen, LoadingScreen, ResultsScreen
    └── vite.config.js
```

---

## ⚙️ Tech Stack

| Camada | Tecnologia | Função |
|--------|-----------|--------|
| Backend | Python 3.12 + FastAPI | Servidor HTTP assíncrono |
| Detecção | YOLOv8 / YOLO-World (Ultralytics) | Localização de pessoas (local) |
| Análise EPI (padrão) | Google Gemini 2.5 Flash | Classificação visual de 4 EPIs (nuvem) |
| Análise EPI (offline) | OpenCV + NumPy | Capacete (YOLO) + colete (HSV) sem internet |
| Processamento | Pillow | Recorte/encode das sub-imagens |
| HTTP Client | HTTPX | Chamadas assíncronas ao Gemini |
| Frontend | React 19 + Vite 8 | Interface reativa e modular |
| Estilo | Vanilla CSS + tokens | Dark/light mode, zero frameworks CSS |

---

## 📋 Limitações do MVP

- Processa **apenas imagens estáticas** (sem vídeo/tempo real) e **uma imagem por vez**.
- O modo padrão depende de **internet + chave de API** do Google AI Studio.
- O modo **offline** avalia apenas **capacete e colete** (óculos/boné exigem o VLM).
- Óculos e boné dependem do julgamento do VLM; viseiras e bonés sob capacete podem gerar classificações discutíveis.

---

## 📄 Documentação

- 📘 [Guia de Início Rápido](GETTING_STARTED.md) — Como instalar e rodar
- 📗 [Documentação Técnica / Especificação](DOCUMENTACAO.md) — Arquitetura, decisões e detalhes
- 🏛️ [Arquitetura do Sistema](dex-architecture/architecture.md) — Documento arquitetural

---

## 👥 Equipe

Desenvolvido como projeto acadêmico na **FATEC**, utilizando **YOLOv8 + Google Gemini 2.5 Flash** para uma auditoria de EPIs acessível e visualmente rica.

---

<div align="center">
  <sub>Detecção local (YOLOv8) + classificação na nuvem (Google Gemini) · VisionAI</sub>
</div>
