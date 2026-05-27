---
name: dex-quick-dev
description: Fluxo ninja de desenvolvimento rápido do DEX: Clarify → Plan → Build → Review → Present.
---

# dex-quick-dev

O fluxo tático e unificado de desenvolvimento super-rápido do DEX.
Sem persona atribuída. Foco absoluto em precisão, velocidade e qualidade de código. Ideal para tarefas curtas a médias onde instanciar um agente completo é desnecessário.

## WORKFLOW RIGOROSO (Executar estritamente em sequência)

Este fluxo possui HALTs obrigatórios. Você **NUNCA** deve pular as validações do humano antes de codar.

### Passo 1 — Clarify (Clarificação)
- Infira ou extraia ativamente o problema: O que vamos construir?
- Quais são os Critérios de Aceite (ACs)?
- Existem limitações de lib ou dependências?
- Se as instruções do usuário já estiverem 100% detalhadas, faça um resumo relâmpago de 1 linha e siga para o Passo 2.
- **HALT Opcional:** Só pare se faltar contexto crítico.

### Passo 2 — Plan (Plano de Voo)
Apresente o blueprint tático ANTES de modificar arquivos:
- Lista exata dos arquivos criados/modificados.
- Lógica de implementação em bullets diretos.
- Riscos colaterais mapeados.
- **HALT OBRIGATÓRIO:** Pare a execução de texto e pergunte ativamente: "Este plano está aprovado para iniciar a codificação?" Aguarde o SIM.

### Passo 3 — Implement (Construção)
Ao receber autorização:
- Desenvolva o código completo e 100% funcional.
- **PROIBIDO O USO DE PLACEHOLDERS** (ex: `// resto do código aqui` ou `...`). Retorne o código modular e montado.
- Siga estritamente as convenções de lint e padrões existentes no projeto.
- Crie ou atualize os testes relativos a essa modificação em conjunto (Shift-left test).

### Passo 4 — Self-Review (Autocrítica)
Faça uma varredura instantânea sobre seu próprio output:
- Todos os ACs foram de fato englobados no código?
- Há vazamentos de estado, variáveis não inicializadas ou concorrência mal controlada?
- Performance O(n) e Legibilidade.
- *Corrija proativamente qualquer falha sem precisar que o usuário aponte.*

### Passo 5 — Present (Entrega e Handoff)
Exiba o pacote entregue de forma limpa:
- Resumo conciso do que foi alterado.
- Instruções de teste manual (ex: curl local, cliques no UI).
- Pergunte obrigatoriamente: "Quer que eu registre esta alteração oficialmente via `dex-doc-register`?"

## REGRAS INEGOCIÁVEIS

- Sem aprovação do Plano, **NÃO** escreva código. Reduz retrabalho.
- Códigos fraturados (com placeholders) são bloqueantes e proibidos.
- Responda de forma ágil, técnica e no idioma do usuário.
- Utilize artefatos e diffs limpos para mostrar mudanças em arquivos grandes.

