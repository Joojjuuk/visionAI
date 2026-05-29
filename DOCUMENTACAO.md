# VisionAI — Documentação Técnica / Especificação

Sistema web de detecção de EPI (Equipamento de Proteção Individual) em fotos de canteiro
de obras. O usuário envia uma imagem pelo navegador; o backend executa um **pipeline
híbrido** — detecção geométrica **local** (YOLOv8 / YOLO-World) seguida de classificação
**na nuvem** (Google Gemini 2.5 Flash) — e devolve a imagem anotada com o status de
conformidade de EPI de cada trabalhador.

> **Arquitetura atual:** `YOLOv8 (local) + Google Gemini 2.5 Flash (nuvem)`.
> A versão anterior usava Ollama/LLaVA 100% local; isso foi substituído (ver §10).

---

## 1. O que o sistema faz

Dada uma foto de canteiro de obras:

1. Detecta **todas as pessoas** na imagem usando **YOLO-World** (open-vocabulary), de forma
   local e instantânea.
2. Para cada pessoa, recorta a região (cabeça + torso) e pede ao **Google Gemini 2.5 Flash**
   uma classificação estruturada de 4 itens:
   - **Capacete** (`helmet`) — EPI obrigatório
   - **Colete refletivo / hi-vis** (`vest`) — EPI obrigatório
   - **Óculos de proteção** (`glasses`) — EPI obrigatório
   - **Boné** (`cap`) — **alerta de risco** (boné sob/no lugar do capacete)
3. Marca cada pessoa na imagem:
   - **Verde (CONFORME)** = capacete **e** colete **e** óculos, **sem** boné
   - **Vermelho (INCOMPLETO)** = falta algum EPI; o sistema lista o que falta
   - **Âmbar (ALERTA · BONÉ)** = uso de boné sinalizado como risco
4. Mostra estatísticas da cena: total de pessoas, conformes, sem EPI, percentual de
   conformidade e confiança média de detecção.

---

## 2. Arquitetura

### 2.1 Camadas

```
┌────────────────────────────┐
│  Frontend (React + Vite)   │  http://localhost:8000
│  - UploadScreen            │
│  - LoadingScreen           │
│  - ResultsScreen           │
└──────────────┬─────────────┘
               │ HTTP POST /api/analyze  (multipart)
               ▼
┌────────────────────────────┐
│  Backend (FastAPI/uvicorn) │  :8000
│  - /api/status             │
│  - /api/analyze            │
│  - /uploads/{file}         │
│  - / (SPA estática)        │
└──────────────┬─────────────┘
               │
               ▼
┌────────────────────────────────────────────────┐
│  Pipeline (pipeline.py)                         │
│                                                  │
│  1. yolo_service  ── LOCAL ──┐                   │
│     detecta pessoas+capacetes│                   │
│                              ▼                    │
│  2. classificador por pessoa (intercambiável):   │
│     ├─ gemini_service  ── NUVEM (padrão) ──►  Google Gemini 2.5 Flash
│     │    crop → Base64 → REST + JSON Schema       (generativelanguage API)
│     └─ local_cv_service ── LOCAL (fallback)       capacete(YOLO)+colete(HSV)
│                                                  │
│  3. consolida → JSON (detections + stats)        │
└──────────────────────────────────────────────────┘
```

### 2.2 Backend — stack

| Tecnologia | Papel |
| ---------- | ----- |
| **Python 3.12** | runtime |
| **FastAPI** + **uvicorn** | API HTTP assíncrona |
| **Ultralytics YOLO-World** (`yolov8l-world.pt`, ~91 MB) | detecção open-vocabulary local de pessoa/capacete |
| **httpx** (async) | chamada REST ao Google Gemini |
| **Pillow** | recorte/encode (Base64 JPEG) da região do trabalhador |
| **OpenCV** + **NumPy** | análise HSV de colete no modo offline (`local_cv_service`) |
| **pydantic-settings** | configuração via `.env` / variáveis de ambiente |

### 2.3 Frontend — stack

- **React 19** + **Vite 8** (SPA buildada e servida pelo próprio FastAPI em `/`)
- 3 telas: **Upload → Loading → Results**
- Bounding boxes posicionadas em **porcentagem** sobre a imagem (independem do tamanho de exibição)
- Painel lateral com lista de trabalhadores (4 chips de EPI) e estatísticas
- Tema claro/escuro e ajustes (estilo de marcação, rótulos) via `TweaksPanel`

### 2.4 Estrutura de pastas

```
visionai/
├─ run.py                       # launcher único: builda frontend + sobe servidor
├─ backend/
│  ├─ requirements.txt
│  ├─ .env                      # DETECTION_MODE + GEMINI_API_KEY (NÃO versionado)
│  ├─ yolov8l-world.pt          # modelo YOLO-World (baixa no 1º run)
│  ├─ uploads/                  # imagens enviadas (runtime)
│  ├─ static/                   # build do frontend servido na raiz
│  └─ app/
│     ├─ main.py                # FastAPI, CORS, mounts, startup (carrega YOLO)
│     ├─ config.py              # Settings (pydantic) — defaults e env
│     ├─ api/router.py          # /api/status e /api/analyze
│     └─ services/
│        ├─ pipeline.py         # orquestra: YOLO → classificador → resposta
│        ├─ yolo_service.py     # YOLO-World (pessoa + capacete)
│        ├─ gemini_service.py   # NUVEM: Gemini 2.5 Flash, JSON Schema, retry
│        └─ local_cv_service.py # OFFLINE: capacete (YOLO) + colete (HSV)
└─ frontend/
   ├─ package.json · vite.config.js
   └─ src/
      ├─ App.jsx
      ├─ screens/{UploadScreen,LoadingScreen,ResultsScreen}.jsx
      └─ components/{BoundingBoxes,Icons,TopBar,TweaksPanel}.jsx
```

---

## 3. Dois modos de classificação

O backend de classificação é escolhido por `DETECTION_MODE` (ou flag no launcher).
A etapa de **detecção de pessoas (YOLO-World)** é sempre local em ambos os modos.

### 3.1 Modo Gemini (PADRÃO)

`DETECTION_MODE=gemini` · `python run.py`

**Como funciona** — para cada pessoa detectada pelo YOLO:
1. `gemini_service._crop_worker_b64` recorta a região com folga (18% nas laterais, 28% acima,
   10% abaixo), normaliza para ≥ 448 px no menor lado e codifica em **Base64 JPEG**.
2. Faz `POST` assíncrono para
   `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent`
   enviando a imagem + um prompt em PT-BR.
3. Usa **Structured Output**: `responseMimeType=application/json` + um `responseSchema`
   (`helmet`, `vest`, `glasses`, `cap` booleanos + `description` string, todos `required`).
   A API é **forçada** a devolver JSON estrito — **sem regex, sem parsing frágil**.

**Pontos fortes**
- **Confiabilidade de formato 100%** (JSON Schema, não texto livre).
- **Sem hardware pesado** — o trabalho do VLM roda na nuvem; qualquer notebook serve.
- **Inicialização instantânea** — nada para baixar/subir localmente além do YOLO.
- **Resiliência** — erros transitórios (`429/500/503` "model overloaded") são repetidos com
  backoff exponencial (até 4 tentativas), então um pico de demanda não derruba a análise.

**Requisitos** — internet + `GEMINI_API_KEY` válida.

### 3.2 Modo local / offline (fallback)

`DETECTION_MODE=yolo` · `python run.py --local`

**Como funciona** — sem nenhuma chamada externa:
- **Capacete**: associa bboxes de capacete do YOLO-World ao topo do bbox da pessoa.
- **Colete**: análise de cor **HSV** no torso (laranja `H 5–22`, amarelo `H 22–45`,
  lime `H 45–75`, alta saturação). Fração > 15% ⇒ colete presente.
- Avalia apenas `helmet` + `vest` (não há `glasses`/`cap` — esses exigem o VLM).

**Quando usar** — sem internet ou sem chave de API; demonstração offline; máquina isolada.

### 3.3 Comparação

| Critério | Gemini (padrão) | Local/offline |
| -------- | --------------- | ------------- |
| EPIs avaliados | capacete, colete, **óculos, boné** | capacete, colete |
| Garantia de formato | ✅ JSON Schema | ✅ (booleans diretos) |
| Dependência externa | internet + chave | nenhuma |
| Custo | tokens da API Gemini | zero |
| Robustez a falhas | retry/backoff embutido | n/a |

---

## 4. Regra de conformidade

Idêntica no backend (`pipeline._build_response`) e no frontend
(`computeStatus` em `ResultsScreen.jsx` e `BoundingBoxes.jsx`):

```
CONFORME  ⇔  helmet  E  vest  E  glasses  E  (NÃO cap)
```

Quando o backend **não avaliou** `glasses`/`cap` (modo offline), esses campos são **omitidos**
do JSON e tratados como "não impeditivos" (`glasses` ⇒ ok, `cap` ⇒ sem alerta), de modo que o
modo offline não marca todos como não-conformes por falta de óculos.

---

## 5. Como rodar

### 5.1 Pré-requisitos
- **Python 3.12** com `pip`
- **Node.js 20+** com `npm` (para buildar o frontend)
- **(modo Gemini)** chave de API do **Google AI Studio**

### 5.2 Instalação
```powershell
cd backend; pip install -r requirements.txt; cd ..
cd frontend; npm install; cd ..
```
O `yolov8l-world.pt` baixa automaticamente no primeiro run.

### 5.3 Configurar a chave (modo Gemini)
Crie `backend/.env`:
```ini
DETECTION_MODE=gemini
GEMINI_API_KEY=SUA_CHAVE_DO_GOOGLE_AI_STUDIO
```

### 5.4 Rodar
```powershell
python run.py            # padrão: YOLOv8 + Google Gemini (builda frontend e sobe servidor)
python run.py --local    # offline: YOLOv8 + visão computacional local
python run.py --dev      # pula o rebuild do frontend (usa o build anterior)
```
Abra **http://localhost:8000** e envie uma foto.

### 5.5 Conferir o modo ativo
```powershell
curl http://localhost:8000/api/status
```
```json
{
  "status": "ok",
  "detection_mode": "gemini",
  "yolo": "loaded",
  "yolo_model": "yolov8l-world.pt",
  "gemini": "configured"
}
```

---

## 6. Configuração

Defaults em [backend/app/config.py](backend/app/config.py); sobrescreva via `.env` ou env vars.

| Variável | Default | O que é |
| -------- | ------- | ------- |
| `DETECTION_MODE` | `gemini` | `gemini` (nuvem) ou `yolo` (offline) |
| `GEMINI_API_KEY` | `""` | chave do Google AI Studio (obrigatória no modo gemini) |
| `YOLO_MODEL` | `yolov8l-world.pt` | modelo YOLO (caminho relativo a `backend/`) |
| `CONFIDENCE_THRESHOLD` | `0.35` | confiança mínima de detecção |
| `MAX_UPLOAD_SIZE_MB` | `10` | tamanho máximo de upload |
| `UPLOAD_DIR` | `uploads` | pasta das imagens enviadas |
| `STATIC_DIR` | `static` | pasta do build do frontend |

> **Segurança:** `.env` está no `.gitignore` e **não** é versionado. Trate a `GEMINI_API_KEY`
> como segredo; se ela vazar (chat, log, screenshot), **rotacione-a** no Google AI Studio.

---

## 7. Endpoints

### `GET /api/status`
Healthcheck: modo ativo, se o YOLO está carregado e se a chave Gemini está configurada.

### `POST /api/analyze`
Recebe imagem (`multipart/form-data`, campo `file`, JPG/PNG/WebP até 10 MB) e devolve:

```json
{
  "detections": [
    {
      "id": 1,
      "x": 33.23, "y": 37.66, "w": 15.21, "h": 30.78,   // % da imagem
      "confidence": 0.958,
      "helmet": true,
      "vest": true,
      "glasses": false,   // presente só no modo Gemini
      "cap": true,        // presente só no modo Gemini
      "role": "Trabalhador 01"
    }
  ],
  "image_width": 960,
  "image_height": 640,
  "stats": { "total": 1, "ok": 0, "bad": 1, "pct": 0, "avg_confidence": 96 },
  "duration_seconds": 4.16,
  "image_url": "/uploads/7986c60e....jpg"
}
```
Coordenadas em **porcentagem** para overlays independentes do tamanho de exibição.

### `GET /uploads/{filename}`
Serve a imagem original enviada (URL retornada em `image_url`).

### `GET /`
Serve a SPA React buildada (`backend/static/`).

---

## 8. Fluxo do usuário

1. Acessa `http://localhost:8000`.
2. **UploadScreen** — arrasta/seleciona a foto; "Analisar imagem" habilita.
3. **LoadingScreen** — anima o pipeline (YOLO local + Google Gemini) e faz `POST /api/analyze`.
   A barra vai a 100% quando o resultado chega.
4. **ResultsScreen** — imagem com bounding boxes (verde/vermelho/âmbar), tooltips com o status
   (CONFORME / INCOMPLETO / ALERTA (BONÉ)) e painel lateral com os 4 chips de EPI por pessoa
   e as estatísticas da cena. "Analisar nova imagem" reinicia o fluxo.

---

## 9. Modelos de IA

### YOLO-World (`yolov8l-world.pt`)
YOLOv8 **open-vocabulary**: recebe classes em linguagem natural (`["helmet", "person"]`) em vez
das 80 classes fixas do COCO. Roda local, ~0.5–1 s por imagem. Faz a detecção geométrica
(bounding boxes) de pessoas e capacetes. Baixa do repositório da Ultralytics no 1º uso.

### Google Gemini 2.5 Flash (`gemini-2.5-flash`)
VLM multimodal da Google acessado pela **Generative Language API** (REST). Recebe o crop de
cada trabalhador + prompt e, via **Structured Output (JSON Schema)**, devolve os 4 booleanos de
EPI + uma descrição. Rápido, sem GPU local, e com **formato garantido** (sem regex).

---

## 10. Decisões de design (Ollama → Gemini)

- **Por que migrar de Ollama/LLaVA para Gemini?** O modo local exigia rodar o serviço Ollama e
  manter um VLM (~4–5 GB VRAM) carregado, parseava texto livre por **regex** (frágil), e a
  inicialização travava checando/baixando o modelo. Gemini elimina o hardware pesado, a
  inicialização lenta e o parsing frágil.
- **Por que Structured Output em vez de regex?** Pedir `responseSchema` força a API a retornar
  JSON estrito e tipado — qualquer variação de redação do modelo deixa de quebrar a leitura.
- **Por que manter YOLO-World local para detecção?** Geometria (onde está cada pessoa) é rápida,
  barata e determinística localmente; mandar a imagem inteira ao VLM só para localizar pessoas
  seria mais lento e caro. O híbrido usa cada ferramenta no que ela é melhor.
- **Por que recortar a pessoa antes de enviar?** Foca o VLM no trabalhador (melhor sinal/ruído),
  reduz tokens de imagem e melhora a precisão da classificação por pessoa.
- **Por que retry com backoff?** O Gemini Flash retorna `503` intermitente sob carga; repetir
  com espera evita que um pico derrube a análise inteira por causa de um único recorte.
- **Por que manter um modo offline (`local_cv_service`)?** Garante demonstração e operação sem
  internet/chave (capacete via YOLO + colete via HSV), mantendo a mesma assinatura de função.

---

## 11. Limitações conhecidas

- **Óculos/boné** dependem do julgamento do VLM; viseiras e bonés sob capacete podem gerar
  classificações discutíveis.
- **Modo offline** não avalia óculos nem boné (só capacete + colete).
- **Coletes não-padrão** (rosa, vermelho puro) podem escapar do HSV no modo offline — adicione
  um range em `local_cv_service._VEST_*`.
- **Cenas escuras / contraluz / pessoas pequenas no fundo** reduzem a precisão de detecção e de
  classificação.
- **Custo/limite de cota** da API Gemini aplica-se ao modo padrão.

---

## 12. Solução de problemas

| Sintoma | Causa provável | Solução |
| ------- | -------------- | ------- |
| **Tela branca ao chegar em 100%** | bundle antigo em cache do navegador | rode `python run.py` (sem `--dev`) para rebuildar e copiar o frontend; force refresh (Ctrl+F5) |
| `/api/analyze` retorna 500 "Erro de processamento no Gemini" | chave inválida/ausente ou `503` persistente | confira `GEMINI_API_KEY` no `.env`; o retry cobre picos curtos — tente de novo |
| `gemini: "not_configured"` no `/api/status` | `.env` sem `GEMINI_API_KEY` | preencha a chave e reinicie o servidor |
| Status `yolo: not_loaded` | modelo não baixou / erro de import | verifique `backend/yolov8l-world.pt`; apague e rode de novo para re-baixar |
| Porta 8000 em uso | outra instância rodando | `Stop-Process -Id <pid>` ou abra a instância existente |
| `UnicodeEncodeError` no terminal Windows | encoding do console | `run.py` já força UTF-8; se persistir, `set PYTHONIOENCODING=utf-8` |
| Sem internet / sem chave | modo Gemini indisponível | use `python run.py --local` (offline) |

---

## 13. Licenças e atribuições

- **Ultralytics YOLOv8 / YOLO-World** — AGPL-3.0
- **Google Gemini API** — Termos do Google AI Studio / Generative Language API
- **FastAPI, React, Vite, OpenCV, Pillow, httpx** — open-source, licenças respectivas
