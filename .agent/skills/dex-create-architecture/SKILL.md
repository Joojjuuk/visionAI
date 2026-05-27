---
name: dex-create-architecture
description: Criação guiada da Arquitetura de Sistemas do DEX. Baseado no modelo C4, mapeando contexto, containers, segurança e infraestrutura.
---

# dex-create-architecture

Design avançado e padronizado de Arquitetura de Sistemas.
Focado no alinhamento da engenharia de software de alta performance, clareza visual em Mermaid.js, e documentação pragmática sem academicismos excessivos.

## ATIVAÇÃO E INSTRUÇÕES

"Olá. Este processo estruturará o esqueleto técnico da sua aplicação. Quais são os Requisitos Não Funcionais (NFRs) prioritários hoje? (Escalabilidade, Segurança Extrema, Custo Mínimo, Tempo de Resposta)?"

Siga pelas seções estruturalmente. Aplique **HALT** após o rascunho de cada bloco para validar as decisões com o humano.

## ESTRUTURA DO DOCUMENTO ARQUITETURAL (AD)

### Seção 1: Contexto Executivo & Goals Técnicos
- O que o sistema faz de modo sistêmico.
- Trade-offs primários fixados (ex: Consistência Forte ao invés de Eventual).
- **HALT** para calibração.

### Seção 2: Visão C4 Level 1 — System Context
- Diagrama gerado em syntax `mermaid` (C4Context).
- Identifica os atores externos, o sistema core em design, e as APIs/Sistemas de Terceiros que ele consome.
- **HALT** para validar integrações.

### Seção 3: Visão C4 Level 2 — Container Level
- O miolo técnico: Quais são as aplicações web, SPAs, APIs (Go/Node/Python), Bancos de Dados (Relacional, NoSQL), e Filas?
- Diagrama em `mermaid` demonstrando o fluxo de rede/protocolos (REST, gRPC, WSS).
- **HALT** para validar a Stack e Containers escolhidos.

### Seção 4: Fluxo e Arquitetura de Dados (Data Flow)
- Como os dados nascem, tramitam e são persistidos.
- Políticas de consistência de banco (ACID, transações distribuídas, Event Sourcing, CAP Theorem).
- **HALT**

### Seção 5: Security Architecture & Auth
- Onde moram as chaves criptográficas.
- O fluxo de autenticação e revogação de sessão.
- Comunicação de rede (VPC, TLS).
- **HALT**

### Seção 6: Deploy, CI/CD e Observabilidade
- A esteira de deploy (Containers Docker, Kubernetes, Serverless).
- Estratégia de monitoria (Logs estruturados, tracing e APM).
- Políticas de Escalabilidade (Auto-Scaling, Rate Limits).

### Seção 7: Registro Inicial de Decisões (ADRs Iniciais)
- Tabela compacta listando decisões tomadas durante este brainstorming que virarão ADRs (Ex: "Escolha do PostgreSQL invés do MongoDB para transações").

## OUTPUT E ENCERRAMENTO

1. Compile o documento massivo em Markdown de altíssima fidelidade.
2. Salve o artefato como `architecture/architecture.md` (ou crie um sub-diretório de arquiteturas/se for evolutivo).
3. Se houverem ADRs cruciais extraídos dessa conversa, instigue o uso do `dex-doc-register` para arquivá-los separadamente em `architecture/decisions/`.

## REGRAS
- Utilize o standard C4-PlantUML/Mermaid (`graph TD` ou C4 plugins disponíveis) para criar diagramas inteligíveis no VSCode ou GitHub.
- Aponte riscos em escolhas muito "hype" ou over-engineered.
- Sempre responda no idioma do usuário.

