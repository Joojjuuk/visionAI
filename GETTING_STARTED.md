# Guia de Início — VisionAI

> Instale, configure e rode o VisionAI localmente em 5 passos.

---

## Pré-requisitos

| Requisito | Versão Mínima | Link |
|-----------|---------------|------|
| Python | 3.10+ | [python.org](https://python.org) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org) |
| Ollama | Última | [ollama.ai](https://ollama.ai) |

**Hardware:** 16 GB RAM recomendados (mínimo 8 GB). GPU acelera significativamente.

---

## Passo 1 — Clonar o Repositório

```bash
git clone https://github.com/Joojjuuk/visionAI.git
cd visionAI
```

---

## Passo 2 — Configurar o Ollama (LLaVA)

```bash
# Baixar o modelo LLaVA (~4.7 GB) — necessário apenas uma vez
ollama pull llava:7b

# Iniciar o servidor Ollama (manter rodando em background)
ollama serve
```

> O Ollama estará disponível em `http://localhost:11434`.

---

## Passo 3 — Backend Python

```bash
cd backend

# (Recomendado) Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

> O YOLOv8 baixará o modelo `yolov8n.pt` (~6.7 MB) automaticamente na primeira execução.

---

## Passo 4 — Frontend Node.js

```bash
cd ../frontend
npm install
```

---

## Passo 5 — Rodar a Aplicação

### Modo Desenvolvimento (2 terminais)

```bash
# Terminal 1 — Backend
cd backend && uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2 — Frontend
cd frontend && npm run dev
```

Acesse: **http://localhost:5173**

### Modo Produção (servidor único)

```bash
# Na raiz do projeto
python run.py
```

Acesse: **http://localhost:8000**

---

## Configuração (`backend/app/config.py`)

```python
OLLAMA_URL = "http://localhost:11434"
LLAVA_MODEL = "llava:7b"       # Trocar por llava:13b para mais precisão
YOLO_MODEL = "yolov8n.pt"
CONFIDENCE_THRESHOLD = 0.50
```

---

## Verificar Status

```bash
curl http://localhost:8000/api/status
```

Resposta esperada:
```json
{ "status": "ok", "yolo": "loaded", "ollama": "connected", "model": "llava:7b" }
```

Swagger UI disponível em: **http://localhost:8000/docs**

---

## Solução de Problemas

| Erro | Causa | Solução |
|------|-------|---------|
| `ConnectionRefusedError` | Ollama não está rodando | Execute `ollama serve` |
| Modelo não encontrado | LLaVA não baixado | Execute `ollama pull llava:7b` |
| ImportError ultralytics | Dependência faltando | `pip install --upgrade ultralytics` |
| Frontend não conecta | Backend offline | Verifique porta 8000 ativa |
| Processamento lento | Sem GPU | Normal em CPU; evite imagens com muitas pessoas |

---

## Documentação Adicional

- [README.md](README.md) — Visão geral do projeto e como funciona
- [PLAN-visionai-mvp.md](PLAN-visionai-mvp.md) — Roadmap técnico
- [dex-architecture/architecture.md](dex-architecture/architecture.md) — Arquitetura do sistema

---

<div align="center">
  <sub>VisionAI — Processamento 100% Local · FATEC</sub>
</div>
