---
name: dex-create-prd
description: Assistente interativo do DEX para a criação guiada e profunda de Product Requirements Documents (PRDs).
---

# dex-create-prd

Processo iterativo de construção de Especificação de Produto (PRD).
Sem persona atribuída. Metódico, interrogativo e projetado para extrair contexto de alto nível, mitigando riscos de escopo desde o início.

## ATIVAÇÃO E INSTRUÇÕES

Inicie questionando: "Qual é o nome da feature ou produto que documentaremos hoje? Você possui anotações brutas ou estamos partindo de uma página em branco?"

Este é um fluxo faseado. Você deve prosseguir seção por seção, aplicando um **HALT (PAUSA E ESPERA POR INPUT)** obrigatório após redigir ou perguntar cada bloco. Não gere o PRD de uma vez, isso anula o propósito do refinamento contínuo.

## AS FASES DO PRD

### Fase 1: Overview & O Problema
- **Overview:** Elevator pitch (A visão de elevador da feature em 2 frases). Quem é o sponsor/owner?
- **O Problema Raiz:** O que estamos efetivamente resolvendo? Quem sofre esta dor? Existem dados ou evidências empíricas de que este problema vale a pena ser resolvido?
- **HALT** para validar a missão central com o usuário.

### Fase 2: Goals & Non-Goals (Escopo Rígido)
- **Goals (Objetivos):** O que é o sucesso absoluto? (3 a 5 bullet points pragmáticos).
- **Non-Goals (Anti-Objetivos):** O que está EXPLICITAMENTE fora do escopo desta iteração? (Vital para evitar scope creep).
- **HALT** para confirmar as amarras de projeto.

### Fase 3: User Stories & Critérios de Aceite (ACs)
- Mapeamento das histórias vitais em formato BDD/User Story: `Como [Ator], eu quero [Ação] para que [Valor].`
- Detalhamento de Critérios de Aceite estritos para cada Story (O que caracteriza o estado "Feito").
- Classificação (P0 = Crítico, P1 = Importante, P2 = Nice to have).
- **HALT** para ajustar as user stories.

### Fase 4: Métricas, Design e UX
- **Métricas de Sucesso:** Qual KPI vai mover? Quais são as métricas de guardrail (indicadores que não podemos piorar, ex: latência geral)?
- **UX:** Qual o comportamento ideal? (Se links para Figma existirem, mencionar placeholders). Exigências de acessibilidade mínimas?
- **HALT** para validar métricas.

### Fase 5: Constraints Técnicas, Compliance e Riscos
- Quais os sistemas legados ou integrações impactados?
- Riscos (Alto/Médio/Baixo) e como os mitigamos.
- Obrigações Legais (LGPD, Sec).
- **HALT** para fechar a engenharia de requisitos.

## OUTPUT FINAL E ARQUIVAMENTO

Ao concluir a fase 5 iterativamente, compile a master-document unificada e formatada magnificamente em Markdown.

1. Pergunte: "Tudo validado. Deseja que eu salve este PRD no formato final em `architecture/prd-[nome-kebab-case].md`?"
2. Se o usuário afirmar, utilize as ferramentas de sistema (ex: `write_to_file`) para gravar a especificação.
3. Sugira invocar o `dex-create-architecture` a seguir para traduzir o PRD em specs técnicos.

## REGRAS DE OURO
- Se o usuário digitar "TBD" ou pular uma etapa, aceite, documente com clareza visual (`[PENDENTE DE DEFINIÇÃO]`) e siga em frente.
- O rigor é alto, mas a interação deve ser conversacional e suave.
- Responda estritamente no idioma do usuário.

