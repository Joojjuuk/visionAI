# Deploy — Frontend no Vercel + Backend separado

O VisionAI tem duas partes com necessidades diferentes:

| Parte | O que é | Onde hospedar |
| ----- | ------- | ------------- |
| **Frontend** | SPA React/Vite (estático) | **Vercel** |
| **Backend** | FastAPI + YOLO (torch) + Gemini, servidor longo que grava em disco | **NÃO** no Vercel — use Render / Railway / Fly.io / VPS |

> O backend não roda em serverless (Vercel) por causa do tamanho do `torch`/`ultralytics`,
> do modelo YOLO de 91 MB carregado em memória e da gravação em `uploads/`.

O frontend (Vercel) chama o backend pela URL definida em `VITE_API_URL`.

---

## 1. Backend — hospede num serviço com container/processo longo

Exemplo com **Render** (Web Service):

- **Root Directory:** `backend`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Environment:**
  | Variável | Valor |
  | -------- | ----- |
  | `DETECTION_MODE` | `gemini` |
  | `GEMINI_API_KEY` | sua chave do Google AI Studio |
  | `CORS_ORIGINS` | `https://SEU-PROJETO.vercel.app` (a URL do frontend no Vercel) |

Anote a URL pública gerada, ex.: `https://visionai-api.onrender.com`.

> Dica: instância pequena/free pode ficar lenta no YOLO em CPU. Se faltar internet/cota
> do Gemini, o backend cai automaticamente para o modo de visão computacional local
> (capacete + colete). Para forçar offline: `DETECTION_MODE=yolo`.

---

## 2. Frontend — Vercel

Importe o repositório no Vercel. O [vercel.json](vercel.json) já configura o build:

- **Build:** `cd frontend && npm run build`
- **Output:** `frontend/dist`

Em **Project Settings → Environment Variables**, adicione (antes do build, pois o Vite
embute as variáveis em tempo de build):

| Variável | Valor |
| -------- | ----- |
| `VITE_API_URL` | a URL pública do backend, ex.: `https://visionai-api.onrender.com` |

Faça o deploy. O frontend passará a chamar `${VITE_API_URL}/api/analyze` e a carregar as
imagens de `${VITE_API_URL}/uploads/...`.

---

## 3. Ligando os dois

1. Suba o backend primeiro e pegue a URL pública.
2. No backend, defina `CORS_ORIGINS` com a URL do Vercel.
3. No Vercel, defina `VITE_API_URL` com a URL do backend e refaça o deploy.

Se a `VITE_API_URL` ficar vazia (ex.: rodando tudo local via `python run.py`), o frontend
usa caminhos relativos (mesma origem) e tudo continua funcionando.

---

## Checklist

- [ ] Backend no ar com `GEMINI_API_KEY` e `CORS_ORIGINS` configurados
- [ ] `GET https://SEU-BACKEND/api/status` retorna `detection_mode: gemini`
- [ ] `VITE_API_URL` setado no Vercel apontando para o backend
- [ ] Deploy do Vercel refeito após setar a env
- [ ] Upload de imagem funciona ponta a ponta no domínio do Vercel
