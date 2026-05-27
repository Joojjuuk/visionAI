# VisionAI — Detecção de EPI em Obras

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/YOLOv8-Ultralytics-ff6b35?style=flat-square" />
  <img src="https://img.shields.io/badge/LLaVA-Ollama-000000?style=flat-square" />
  <img src="https://img.shields.io/badge/Processamento-100%25%20Local-22c55e?style=flat-square" />
</div>

<br/>

> **MVP de auditoria visual de conformidade de EPIs (Equipamentos de Proteção Individual) para canteiros de obras, rodando 100% em ambiente local — sem nuvem, sem dados saindo da máquina.**

---

## 🎯 O que é o VisionAI?

O VisionAI é uma ferramenta de segurança do trabalho baseada em Inteligência Artificial local. A proposta é simples: o usuário envia uma foto de um ambiente de trabalho e o sistema retorna, de forma visual e interativa, quais trabalhadores estão em conformidade com o uso de EPIs obrigatórios — capacete e colete refletivo — e quais requerem atenção.

Ao contrário de soluções em nuvem, todo o processamento acontece na máquina do usuário. Os modelos de IA rodam localmente, a imagem jamais sai do computador, e não é necessária conexão com a internet após a instalação inicial.

---

## 🧠 Como Funciona — Fluxo Técnico

O sistema é dividido em duas etapas de inferência que se complementam:

```
Imagem enviada pelo usuário
        │
        ▼
┌─────────────────────────────┐
│   YOLOv8 (Ultralytics)      │  ← Detecção de pessoas
│   Detecta ONDE cada pessoa  │    Retorna bounding boxes (%)
│   está na imagem            │    Modelo: yolov8n.pt (local)
└────────────┬────────────────┘
             │ coordenadas de cada pessoa
             ▼
┌─────────────────────────────┐
│   Pillow — Recorte          │  ← Para cada pessoa detectada,
│   Recorta a região de cada  │    recorta a sub-imagem
│   trabalhador individualmente│   correspondente
└────────────┬────────────────┘
             │ recorte individual por pessoa
             ▼
┌─────────────────────────────┐
│   LLaVA via Ollama          │  ← Análise de EPI por pessoa
│   Verifica se a pessoa usa  │    Modelo multimodal local
│   capacete e/ou colete      │    Responde: {helmet, vest}
└────────────┬────────────────┘
             │ status booleano por trabalhador
             ▼
┌─────────────────────────────┐
│   FastAPI — Consolidação    │  ← Monta o JSON de resposta
│   Junta coordenadas + status│    com detecções e estatísticas
│   em uma estrutura única    │
└────────────┬────────────────┘
             │ JSON estruturado
             ▼
┌─────────────────────────────┐
│   Frontend React            │  ← Renderiza a imagem real
│   Sobrepõe bboxes interativas│   com marcações coloridas
│   Painel de estatísticas    │   Verde = conforme / Vermelho = atenção
└─────────────────────────────┘
```

### Por que YOLOv8 + LLaVA?

| Necessidade | Solução | Por quê |
|-------------|---------|---------|
| Localizar pessoas na imagem | **YOLOv8** | Retorna coordenadas precisas de bounding boxes. LLaVA não é projetado para isso. |
| Verificar presença de EPI | **LLaVA** | Entende contexto visual e responde perguntas. YOLOv8 genérico não classifica EPIs sem treinamento específico. |
| Rodar sem internet | **Ollama** | Serve o LLaVA localmente via API HTTP. |
| Renderização interativa | **React** | Bounding boxes dinâmicas no navegador, com hover e painel lateral reativo. |

---

## 🖥️ Interface

A interface é composta por **três telas** com fluxo linear:

### 1. Tela de Upload
- Área de drag-and-drop para arrastar ou selecionar a imagem
- Suporte a JPG, PNG e WebP (até 10MB)
- Prévia da imagem antes de enviar
- Botão "Analisar imagem" habilitado após seleção

### 2. Tela de Processamento (Loading)
- Animação de scan sobre a imagem
- Bounding boxes sendo descobertas progressivamente
- Log do pipeline em tempo real (stderr)
- Etapas: Decodificar → Detectar Pessoas → Analisar EPI → Consolidar

### 3. Tela de Resultados
- Imagem original com bounding boxes coloridas interativas
  - 🟢 **Verde** — trabalhador em conformidade (capacete + colete)
  - 🔴 **Vermelho** — trabalhador sem pelo menos um EPI
- Painel lateral com:
  - Total de pessoas detectadas
  - Conformes vs. Sem EPI
  - Porcentagem geral de conformidade da cena
  - Lista individual com status de cada trabalhador
  - Filtros: Todas / Sem EPI / Conformes
- Botão para analisar nova imagem

---

## 🏗️ Arquitetura do Projeto

```
visionai/
├── backend/                    # Servidor Python FastAPI
│   ├── app/
│   │   ├── main.py             # Ponto de entrada do servidor
│   │   ├── config.py           # Configurações (OLLAMA_URL, modelo, etc.)
│   │   ├── api/
│   │   │   └── router.py       # Rotas: POST /api/analyze, GET /api/status
│   │   └── services/
│   │       ├── yolo_service.py # Wrapper do YOLOv8
│   │       ├── llava_service.py# Wrapper do LLaVA via Ollama
│   │       └── pipeline.py     # Orquestrador da pipeline completa
│   ├── static/                 # Build do frontend servida aqui
│   ├── uploads/                # Imagens enviadas temporariamente
│   └── requirements.txt
└── frontend/                   # Aplicação React + Vite
    ├── src/
    │   ├── App.jsx             # Máquina de estados (upload→loading→results)
    │   ├── components/         # TopBar, BoundingBoxes, TweaksPanel, etc.
    │   └── screens/            # UploadScreen, LoadingScreen, ResultsScreen
    └── vite.config.js          # Proxy para /api → backend em dev
```

---

## ⚙️ Tech Stack

| Camada | Tecnologia | Função |
|--------|-----------|--------|
| Backend | Python 3.10+ + FastAPI | Servidor HTTP assíncrono |
| Detecção | YOLOv8 (ultralytics) | Localização de pessoas |
| Análise EPI | LLaVA 7B via Ollama | Verificação visual de EPIs |
| Processamento | Pillow | Recorte de sub-imagens |
| HTTP Client | HTTPX | Chamadas assíncronas ao Ollama |
| Frontend | React 18 + Vite | Interface reativa e modular |
| Estilo | Vanilla CSS + HSL tokens | Dark/light mode, zero frameworks CSS |

---

## 📋 Limitações do MVP

- Processa **apenas imagens estáticas** (sem suporte a vídeo ou tempo real)
- Analisa apenas **dois EPIs**: capacete e colete refletivo
- Processa **uma imagem por vez**
- O LLaVA é um modelo generalista — pode haver falsos positivos/negativos dependendo do ângulo e qualidade da foto
- O processamento com múltiplas pessoas pode levar **alguns segundos** dependendo do hardware

---

## 📄 Documentação

- 📘 [Guia de Início Rápido](GETTING_STARTED.md) — Como instalar e rodar
- 🗺️ [Plano de Implementação](PLAN-visionai-mvp.md) — Roadmap técnico do desenvolvimento
- 🏛️ [Arquitetura do Sistema](dex-architecture/architecture.md) — Documento arquitetural completo

---

## 👥 Equipe

Desenvolvido como projeto acadêmico na **FATEC**, utilizando YOLOv8 e LLaVA para criar um sistema de auditoria de EPIs local, acessível e visualmente rico.

---

<div align="center">
  <sub>Processamento 100% local · Nenhuma imagem sai do seu computador · VisionAI MVP</sub>
</div>
