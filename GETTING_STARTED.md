# Guia de Início — VisionAI

> Instale, configure e rode o VisionAI localmente em poucos passos.

---

## Pré-requisitos

| Requisito | Versão Mínima | Link |
|-----------|---------------|------|
| Python | 3.12 | [python.org](https://python.org) |
| Node.js | 20+ | [nodejs.org](https://nodejs.org) |
| Chave de API Gemini | — | [Google AI Studio](https://aistudio.google.com/app/apikey) |

**Hardware:** qualquer máquina recente serve — o trabalho pesado de classificação roda na nuvem (Gemini). GPU acelera a detecção YOLO, mas não é obrigatória.

---

## Passo 1 — Clonar o Repositório

```bash
git clone https://github.com/Joojjuuk/visionAI.git
cd visionAI
```

---

## Passo 2 — Configurar a chave do Google Gemini

Crie o arquivo `backend/.env` com a sua chave do [Google AI Studio](https://aistudio.google.com/app/apikey):

```ini
DETECTION_MODE=gemini
GEMINI_API_KEY=SUA_CHAVE_AQUI
```

> O `.env` está no `.gitignore` e **não** é versionado. Trate a chave como segredo.
> Sem internet/chave, use o **modo offline** (`python run.py --local`), que dispensa o Gemini.

---

## Passo 3 — Backend Python

```bash
cd backend

# (Recomendado) Criar e ativar ambiente virtual
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

> O YOLO-World (`yolov8l-world.pt`, ~91 MB) baixa automaticamente na primeira execução.

---

## Passo 4 — Frontend Node.js

```bash
cd ../frontend
npm install
```

---

## Passo 5 — Rodar a Aplicação

### Modo Produção (servidor único — recomendado)

```bash
# Na raiz do projeto
python run.py            # YOLOv8 + Google Gemini (padrão)
python run.py --local    # offline: YOLOv8 + visão computacional local
python run.py --dev      # pula o rebuild do frontend
```

Acesse: **http://localhost:8000**

### Modo Desenvolvimento (2 terminais)

```bash
# Terminal 1 — Backend
cd backend && uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2 — Frontend
cd frontend && npm run dev
```

Acesse: **http://localhost:5173**

---

## Configuração (`backend/.env` / [config.py](backend/app/config.py))

```ini
DETECTION_MODE=gemini          # "gemini" (nuvem) ou "yolo" (offline)
GEMINI_API_KEY=...             # chave do Google AI Studio
YOLO_MODEL=yolov8l-world.pt
CONFIDENCE_THRESHOLD=0.35
MAX_UPLOAD_SIZE_MB=10
```

---

## Verificar Status

```bash
curl http://localhost:8000/api/status
```

Resposta esperada:
```json
{ "status": "ok", "detection_mode": "gemini", "yolo": "loaded", "yolo_model": "yolov8l-world.pt", "gemini": "configured" }
```

Swagger UI disponível em: **http://localhost:8000/docs**

---

## Solução de Problemas

| Erro | Causa | Solução |
|------|-------|---------|
| Tela branca ao chegar em 100% | bundle antigo em cache | rode `python run.py` (sem `--dev`) e force refresh (Ctrl+F5) |
| 500 "Erro de processamento no Gemini" | chave inválida/ausente ou pico de carga | confira `GEMINI_API_KEY`; o retry cobre picos curtos, tente de novo |
| `gemini: "not_configured"` | `.env` sem `GEMINI_API_KEY` | preencha a chave e reinicie |
| Status `yolo: not_loaded` | modelo não baixou / import | verifique `backend/yolov8l-world.pt`; apague e rode de novo |
| Sem internet / sem chave | modo Gemini indisponível | use `python run.py --local` |
| ImportError ultralytics | dependência faltando | `pip install --upgrade ultralytics` |
| Porta 8000 em uso | outra instância rodando | `Stop-Process -Id <pid>` ou use a instância existente |

---

## Documentação Adicional

- [README.md](README.md) — Visão geral do projeto e como funciona
- [DOCUMENTACAO.md](DOCUMENTACAO.md) — Documentação técnica / especificação completa
- [dex-architecture/architecture.md](dex-architecture/architecture.md) — Arquitetura do sistema

---

<div align="center">
  <sub>VisionAI — YOLOv8 + Google Gemini · FATEC</sub>
</div>
