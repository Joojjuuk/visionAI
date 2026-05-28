# VisionAI — Documentação Técnica

Sistema web local de detecção de EPI (Equipamento de Proteção Individual) em fotos de obra. O usuário envia uma imagem pelo navegador, o backend processa com IA rodando 100% local, e retorna a imagem anotada com o status de conformidade de cada trabalhador.

---

## 1. O que o projeto faz

Dada uma foto de canteiro de obras:

1. Detecta **todas as pessoas** na imagem usando YOLO-World.
2. Para cada pessoa, verifica se ela está usando:
   - **Capacete de segurança** (qualquer cor)
   - **Colete refletivo / hi-vis** (laranja, amarelo, lime)
3. Retorna a imagem original com cada pessoa marcada:
   - **Verde** = EPI completo (capacete + colete)
   - **Vermelho** = EPI incompleto, com descrição do que falta
4. Mostra estatísticas: total de pessoas, em conformidade, sem EPI, percentual de conformidade da cena.

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
               │ HTTP POST /api/analyze
               ▼
┌────────────────────────────┐
│  Backend (FastAPI)         │  uvicorn :8000
│  - /api/status             │
│  - /api/analyze            │
│  - /uploads/{file}         │
│  - / (static frontend)     │
└──────────────┬─────────────┘
               │
               ▼
┌────────────────────────────┐
│  Pipeline                  │
│  yolo_service              │
│   ├─ detecta pessoas       │
│   └─ detecta capacetes     │
│  llava_service OR          │
│  ollama_service            │
│   └─ classifica EPI/pessoa │
└────────────────────────────┘
```

### 2.2 Backend — stack

- **Python 3.12+**
- **FastAPI** + **uvicorn** — API HTTP
- **Ultralytics YOLO-World** — detecção open-vocabulary (`yolov8l-world.pt`, 91 MB)
- **OpenCV** + **NumPy** — análise HSV para coletes hi-vis
- **Pillow** — manipulação de imagem
- **httpx** — chamadas ao Ollama (modo opcional)
- **Ollama** + **gemma3:4b** — modelo de visão local (modo opcional)

### 2.3 Frontend — stack

- **React 19** + **Vite 8**
- 3 telas: Upload → Loading → Results
- Bounding boxes desenhadas via SVG sobre a imagem
- Painel lateral com lista de trabalhadores e estatísticas

### 2.4 Estrutura de pastas

```
visionai/
├─ run.py                     # launcher único: checa deps, builda frontend, sobe servidor
├─ backend/
│  ├─ requirements.txt
│  ├─ yolov8l-world.pt        # modelo YOLO-World (baixado no primeiro run)
│  ├─ uploads/                # imagens enviadas (geradas em runtime)
│  ├─ static/                 # build do frontend servido na raiz
│  └─ app/
│     ├─ main.py              # FastAPI app, CORS, mounts estáticos
│     ├─ config.py            # pydantic_settings com env vars
│     ├─ api/
│     │  └─ router.py         # endpoints /api/status e /api/analyze
│     └─ services/
│        ├─ pipeline.py       # orquestra: YOLO → classificador → resposta
│        ├─ yolo_service.py   # YOLO-World detection (pessoa + capacete)
│        ├─ llava_service.py  # modo YOLO: helmet via YOLO-World + vest via HSV
│        └─ ollama_service.py # modo Ollama: VLM gemma3:4b por trabalhador
└─ frontend/
   ├─ package.json
   ├─ vite.config.js
   └─ src/
      ├─ App.jsx
      ├─ screens/UploadScreen.jsx
      ├─ screens/LoadingScreen.jsx
      ├─ screens/ResultsScreen.jsx
      └─ components/BoundingBoxes.jsx, TopBar.jsx, ...
```

---

## 3. Dois modos de detecção

O projeto entrega dois backends de classificação intercambiáveis, escolhidos pela variável `DETECTION_MODE` (ou flag `--ollama` no launcher).

### 3.1 Modo YOLO (default — recomendado)

**Como funciona**

1. YOLO-World é prompted com as classes `["helmet", "person"]` e roda **uma única vez** sobre a imagem inteira.
2. Para cada pessoa detectada:
   - **Helmet** = `True` se algum bbox de capacete do YOLO-World tem seu centro dentro da zona da cabeça da pessoa (topo do bbox da pessoa + folga).
   - **Vest** = análise de cor HSV no torso. Conta a fração de pixels em ranges hi-vis (laranja `H 5-22`, amarelo `H 22-45`, lime `H 45-75`) com alta saturação. Se total > 15%, considera colete presente.

**Performance**

- ~1 segundo por imagem (independente do número de pessoas)
- 100% acerto em fotos de teste com EPIs hi-vis padrão
- Não precisa de Ollama rodando

**Limitações**

- Coletes não-padrão (rosa, vermelho puro) podem não ser detectados — adicionar range HSV se necessário
- Capacetes muito apagados em fundo neutro podem ter conf baixa do YOLO-World

### 3.2 Modo Ollama (alternativo)

**Como funciona**

1. YOLO-World detecta pessoas (sem usar a classe helmet).
2. Para cada pessoa, recorta o bbox com folga (cabeça + torso) e envia ao modelo `gemma3:4b` via `/api/chat` do Ollama com um prompt descritivo:
   > "Describe this construction worker in 2-3 short sentences, focused on what they wear on their head and on their torso. Be specific about colors. If they have no hat or no vest, say so explicitly."
3. A descrição em texto é parseada por regex de keywords:
   - `helmet`: detecta `hard hat`, `helmet`, etc., negado por `no [...] hat/helmet`, `bare head`, etc.
   - `vest`: detecta `safety vest`, `hi-vis vest`, `[color] vest`, negado por `no [...] vest`, etc.

**Performance**

- ~10 segundos **por trabalhador** (~80s para 8 pessoas)
- ~75-80% de acurácia em fotos de teste
- Requer Ollama rodando + `gemma3:4b` baixado (~3.3 GB)

**Limitações**

- LLMs pequenos têm viés de "trabalhador de obra = tem EPI" e ocasionalmente alucinam capacete/colete inexistente
- Pelo contrário, capacetes brancos em fundo branco/céu às vezes não são vistos

### 3.3 Quando usar cada um

| Critério                   | YOLO              | Ollama            |
| -------------------------- | ----------------- | ----------------- |
| Velocidade                 | ✅ ~1s            | ⚠️ ~80s           |
| Acurácia (fotos testadas)  | ✅ ~100%          | ~75-80%           |
| Dependência externa        | nenhuma           | Ollama rodando    |
| Uso de GPU                 | 1-2 GB VRAM       | 4.3 GB VRAM       |
| Descrição textual          | ❌                | ✅ (futura feature) |

**Use Ollama** apenas se for evoluir o produto para gerar relatórios em linguagem natural ou explicar visualmente os achados. Caso contrário, mantenha o **YOLO**.

---

## 4. Como rodar

### 4.1 Pré-requisitos

- **Python 3.12+** com `pip`
- **Node.js 20+** com `npm` (para buildar o frontend)
- **GPU NVIDIA com ≥ 4 GB VRAM** recomendado (CPU funciona mas é lento)
- **(Apenas modo Ollama)** [Ollama](https://ollama.com/) instalado e disponível no PATH

### 4.2 Instalação inicial

```powershell
# Backend
cd backend
pip install -r requirements.txt
cd ..

# Frontend
cd frontend
npm install
cd ..
```

O modelo YOLO-World (`yolov8l-world.pt`, 91 MB) baixa automaticamente no primeiro run.

### 4.3 Rodar (modo YOLO — default)

```powershell
python run.py
```

O launcher:
1. Mostra "Detection mode: YOLO-World (default)"
2. Pula checagens de Ollama (não é necessário)
3. Builda o frontend com `npm run build`
4. Copia o build para `backend/static/`
5. Sobe o servidor com uvicorn em `http://localhost:8000`

Abra o navegador em **http://localhost:8000** e suba uma foto.

### 4.4 Rodar (modo Ollama)

```powershell
python run.py --ollama
```

O launcher:
1. Mostra "Detection mode: OLLAMA (gemma3:4b)"
2. Inicia o Ollama em background se não estiver rodando
3. Baixa `gemma3:4b` se ainda não existir (~3.3 GB, demora alguns minutos na primeira vez)
4. Builda o frontend e sobe o servidor

Alternativamente, defina a variável de ambiente:

```powershell
$env:DETECTION_MODE = "ollama"
python run.py
```

### 4.5 Flags úteis

```powershell
python run.py --dev          # pula o build do frontend (usa o build anterior)
python run.py --ollama --dev # ambos
```

### 4.6 Verificar o modo ativo

```powershell
curl http://localhost:8000/api/status
```

Retorna algo como:
```json
{
  "status": "ok",
  "detection_mode": "yolo",
  "yolo": "loaded",
  "yolo_model": "yolov8l-world.pt",
  "ollama": "unused",
  "ollama_model": null
}
```

No modo Ollama, `ollama` será `connected` e `ollama_model` mostra o modelo.

---

## 5. Configuração

Tudo configurável via variáveis de ambiente ou arquivo `.env` em `backend/`. Defaults em [backend/app/config.py](backend/app/config.py).

| Variável                | Default              | O que é |
| ----------------------- | -------------------- | ------- |
| `DETECTION_MODE`        | `yolo`               | `yolo` ou `ollama` |
| `OLLAMA_URL`            | `http://localhost:11434` | Endpoint do Ollama |
| `OLLAMA_MODEL`          | `gemma3:4b`          | Modelo VLM usado no modo Ollama |
| `YOLO_MODEL`            | `yolov8l-world.pt`   | Modelo YOLO (caminho relativo a `backend/`) |
| `CONFIDENCE_THRESHOLD`  | `0.35`               | Confiança mínima de detecção |
| `MAX_UPLOAD_SIZE_MB`    | `10`                 | Tamanho máximo de upload |
| `UPLOAD_DIR`            | `uploads`            | Pasta de imagens enviadas |
| `STATIC_DIR`            | `static`             | Pasta do build do frontend |

Exemplo de `backend/.env`:

```ini
DETECTION_MODE=ollama
OLLAMA_MODEL=gemma3:4b
CONFIDENCE_THRESHOLD=0.40
```

---

## 6. Endpoints

### `GET /api/status`

Healthcheck. Retorna modo ativo, status do YOLO e (no modo Ollama) status do Ollama.

### `POST /api/analyze`

Recebe uma imagem (multipart/form-data, campo `file`, JPG/PNG/WebP até 10 MB) e devolve um JSON:

```json
{
  "detections": [
    {
      "id": 1,
      "x": 19.4,         // % esquerda
      "y": 23.2,         // % topo
      "w": 12.2,         // % largura
      "h": 70.5,         // % altura
      "confidence": 0.96,
      "helmet": true,
      "vest": true,
      "role": "Trabalhador 01"
    }
  ],
  "image_width": 2816,
  "image_height": 1536,
  "image_url": "/uploads/abc...png",
  "stats": {
    "total": 8,
    "ok": 3,
    "bad": 5,
    "pct": 38,
    "avg_confidence": 72
  },
  "duration_seconds": 1.32
}
```

Coordenadas vêm em **porcentagem da imagem** para que o frontend possa desenhar overlays independente do tamanho de exibição.

### `GET /uploads/{filename}`

Serve a imagem original enviada. URL retornada em `image_url`.

### `GET /`

Serve o frontend buildado (React SPA).

---

## 7. Fluxo do usuário

1. Acessa `http://localhost:8000`.
2. **UploadScreen** — arrasta ou seleciona uma foto de obra. Botão "Analisar imagem" habilita.
3. **LoadingScreen** — animação enquanto roda o pipeline. Faz `POST /api/analyze`.
4. **ResultsScreen** — exibe a imagem com bounding boxes coloridas:
   - **Verde**: trabalhador em conformidade
   - **Vermelho**: trabalhador sem EPI completo
   Painel lateral lista cada trabalhador (`Trabalhador 01`, `02`, ...) com o que falta. Botão "Analisar nova imagem" reseta o fluxo.

---

## 8. Modelos de IA

### YOLO-World (`yolov8l-world.pt`)

Modelo open-vocabulary baseado em YOLOv8 — recebe **prompts em linguagem natural** como classes ao invés das 80 classes fixas do COCO. Usado com `["helmet", "person"]` como classes ativas. 91 MB, roda em GPU em ~0.5-1s por imagem. Baixa automaticamente do GitHub da Ultralytics no primeiro uso.

### Gemma 3 (`gemma3:4b`) — apenas no modo Ollama

Modelo de visão da Google. 3.3 GB em disco, ocupa ~4.3 GB VRAM, cabe 100% em GPUs de 6 GB+. Acessado via Ollama na porta 11434. Recebe um crop de cada trabalhador e devolve descrição em texto livre que é parseada por regex.

---

## 9. Decisões de design e histórico

Este projeto passou por iterações relevantes. As decisões abaixo são propositais.

- **Por que YOLO-World e não YOLOv8 padrão?** O YOLO padrão só detecta as 80 classes do COCO ("person" sim, mas nada de "helmet" ou "vest"). YOLO-World permite prompts customizados, dispensando treinamento de dataset.

- **Por que análise HSV para colete e não LLM?** Coletes hi-vis são *projetados* para serem cromaticamente distintos (alta saturação em hues específicos). HSV acerta com alta precisão em milissegundos. LLMs pequenos confundem coletes com camisas coloridas.

- **Por que não usar LLM para capacete também?** Os capacetes têm formas e texturas variadas. YOLO-World tem feature de detecção de objetos forte para isso, enquanto LLMs pequenos alucinam capacetes em qualquer foto de obra.

- **Por que Ollama mode existe se YOLO é melhor?** Existe como segunda opção para futuros casos onde se queira **descrição em linguagem natural** do que cada trabalhador veste — útil para gerar relatórios automáticos ou validação humana.

- **Por que `gemma3:4b` e não `llava:13b`/`llama3.2-vision:11b`?** Modelos > 6 GB em uma GPU de 6 GB VRAM caem para offload CPU/GPU e o vision encoder quebra (saída vira lixo de tokens). Gemma 3 (4B) cabe 100% na GPU e funciona.

---

## 10. Limitações conhecidas

- **Coletes não-tradicionais** (rosa, vermelho puro, sem listras refletivas): não detectados no modo YOLO. Adicione um range HSV em `llava_service._VEST_*` se aparecer no dataset real.
- **Cenas muito escuras ou contraluz**: tanto YOLO-World quanto Gemma perdem precisão.
- **Pessoas muito pequenas no fundo**: detectadas pelo YOLO mas EPI pouco confiável (baixa resolução do crop).
- **Modo Ollama** alucina ~20% dos casos em LLMs pequenos. Para produção confiável, treinar um YOLO específico para EPI no dataset alvo.

---

## 11. Evoluções futuras sugeridas

1. **Modelo YOLO treinado em PPE** — coletar/anotar 500-1000 imagens de obra e treinar `yolov8n.pt` com classes `["helmet", "vest", "person"]`. Substitui ambos os modos atuais e elimina os pontos fracos.
2. **Suporte a vídeo** (atualmente só imagens estáticas).
3. **Mais EPIs**: luvas, óculos, máscara, botina.
4. **Relatório PDF** com print da cena anotada + estatísticas + descrição em linguagem natural (aqui o modo Ollama vira útil).
5. **Multi-imagem em batch** com filtro de "não conformes apenas".
6. **Webcam ao vivo** com detecção em tempo real (depende do item 1).

---

## 12. Solução de problemas

| Sintoma                                              | Causa provável                                    | Solução |
| ---------------------------------------------------- | ------------------------------------------------- | ------- |
| `ConnectError: Ollama não está rodando`              | Modo Ollama mas serviço offline                   | `ollama serve` ou rode com `python run.py` (sem `--ollama`) |
| Status mostra `yolo: not_loaded`                     | YOLO não baixou ou erro de import                 | Verifique `backend/yolov8l-world.pt`. Apague e rode de novo para re-baixar. |
| Modelo Ollama carrega em `100% CPU` em vez de GPU    | Modelo maior que sua VRAM                         | Use `gemma3:4b` (cabe em 6 GB), evite `llava:13b` ou `llama3.2-vision:11b` em GPUs pequenas. |
| Frontend quebrado / tela branca                       | Build desatualizado                               | `python run.py` (sem `--dev`) para forçar rebuild |
| Erro `UnicodeEncodeError` no terminal Windows         | Encoding console                                  | `run.py` já força UTF-8; se persistir, `set PYTHONIOENCODING=utf-8` |
| Porta 8000 em uso                                     | Outra instância rodando                           | `Stop-Process -Id <pid>` ou abra a já existente |
| Acurácia ruim em fotos específicas                    | Limitações do modelo / coletes não-padrão         | Modo YOLO + adicione ranges HSV; ou treine modelo PPE-específico |

---

## 13. Licença e atribuições

- **Ultralytics YOLOv8 / YOLO-World** — licença AGPL-3.0
- **Ollama + Gemma 3** — licenças dos respectivos modelos (consultar Ollama)
- **FastAPI, React, Vite, OpenCV, Pillow** — open-source nas suas respectivas licenças
