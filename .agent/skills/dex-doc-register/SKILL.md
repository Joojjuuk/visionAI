---
name: dex-doc-register
description: Sistema Oficial de Documentação de decisões arquiteturais do DEX. Registra ADRs, Soluções, Mudanças e Padrões, sempre distinguindo a contribuição da IA da do Humano.
---

# dex-doc-register

Sistema de registro formal de decisões técnicas, mudanças de arquitetura e soluções de problemas.
A rastreabilidade e o histórico são fundamentais no **DEX Flow Kit**. Todo registro DEVE distinguir explicitamente o raciocínio gerado pela **IA** e o contexto de negócio fornecido pelo **Humano**.

---

## QUANDO USAR

- Após tomar uma decisão arquitetural significativa ou mudar a stack (ADR).
- Ao resolver um problema não-trivial (bug cabeludo ou problema de performance).
- Ao realizar refatorações ou mudanças sistêmicas de grande impacto.
- Ao definir padrões de código e convenções para o projeto inteiro.
- Automaticamente chamado por outros agentes (Theo, Viktor, Kai, etc.) quando finalizam uma ação estrutural.

---

## FLUXO RIGOROSO DE REGISTRO

### Passo 1 — Identificar o tipo de documento
Inspecione o contexto ou pergunte ao usuário o que estamos registrando:
- **ADR (Architecture Decision Record):** Quando escolhemos tecnologias ou designs.
- **SOL (Solução de Problema):** Como um erro grave foi diagnosticado e consertado.
- **CHG (Mudança de Sistema):** Atualização ou alteração de comportamento.
- **STD (Padrão de Projeto):** Convenções, regras de linter corporativas, etc.

### Passo 2 — Coletar o Contexto da IA (Seu raciocínio)
Documente:
- O que foi analisado sistematicamente.
- Solução/Proposta gerada.
- Trade-offs e alternativas descartadas.
- Riscos intrínsecos mantidos.

### Passo 3 — Coletar o Contexto do Humano (O Porquê do Negócio)
Pergunte e capture rigorosamente as restrições humanas:
- "Qual foi a restrição de negócio, prazo ou preferência que nos guiou aqui?"
- "Qual o problema inicial sob a sua perspectiva?"
*Nota: Se o usuário já informou tudo isso durante a sessão, apenas sintetize sem perguntar novamente.*

### Passo 4 — Geração e Armazenamento do Documento
Os arquivos devem ser salvos nas pastas abaixo e formatados de acordo:
- ADR: `dex-architecture/decisions/ADR-[numero]-[titulo-kebab-case].md`
- SOL: `dex-architecture/solutions/SOL-[YYYYMMDD]-[titulo-kebab-case].md`
- CHG: `dex-architecture/changes/CHG-[YYYYMMDD]-[componente].md` *(auto-criado pelo hook PostToolUse — você apenas enriquece)*
- STD: `dex-architecture/standards/STD-[titulo-kebab-case].md`

### 🔄 Integração com o Auto-Trigger (PostToolUse hook)
O hook `.agent/scripts/auto_change_register.py` cria/atualiza CHGs automaticamente sempre que qualquer agente faz Edit/Write. Você (`dex-doc-register`) é invocado para:

1. **Enriquecer CHGs abertos** com `needs_review: true` — adicionar contexto do humano, decidir se vira ADR, fechar (`status: closed`).
2. **Sweep diário**: ao final de uma sessão grande, varrer `dex-architecture/changes/` agrupando CHGs do dia em um único ADR/SOL se aplicável.
3. **Promover CHG → ADR** quando o usuário valida uma decisão estrutural (mover registro de `changes/` para `decisions/`).

---

## TEMPLATES OBRIGATÓRIOS

### TEMPLATE — ADR (Architecture Decision Record)

```markdown
# ADR-[numero]: [Título da Decisão]

**Data:** [YYYY-MM-DD]
**Status:** [Proposto | Aceito | Depreciado | Substituído por ADR-X]
**Autores:** [IA: Agente] & [Humano: Nome/Username]

---

## 1. Contexto & Problema
[Descrição clara do problema sendo resolvido e por que uma decisão é necessária agora]

### 🧠 Contribuição da IA
[Análise técnica da IA, levantamento do ecossistema e avaliação das constraints]

### 👤 Contribuição do Humano
[Contexto de negócio trazido pelo humano, restrições financeiras/prazo]

---

## 2. Decisão
[A decisão definitiva descrita em forma afirmativa e clara]

---

## 3. Opções Consideradas

| Opção | Prós | Contras | Motivo da Rejeição / Escolha |
|-------|------|---------|-----------------------------|
| [Opção A] | ... | ... | [Escolhida] |
| [Opção B] | ... | ... | [Rejeitada por X] |

---

## 4. Consequências e Mitigações

**Positivas:** [O que a arquitetura ganha]
**Negativas / Riscos:** [A dívida técnica ou o risco que estamos assumindo]
**Mitigações:** [Como o time vai lidar com o risco]
```

### TEMPLATE — SOLUÇÃO DE PROBLEMA

```markdown
# SOL-[YYYYMMDD]-[titulo]

**Data:** [YYYY-MM-DD]
**Ambiente:** [Dev | Staging | Prod]
**Severidade:** [Critical | High | Medium | Low]

---

## 1. O Problema
### 👤 Relato do Humano
[Sintomas do erro e o que o usuário tentou inicialmente]
### 🧠 Diagnóstico da IA
[Investigação forense e causa raiz isolada]

**Causa Raiz Definitiva:** [Uma frase identificando o erro exato]

---

## 2. A Solução
### 🧠 Ação da IA
[Código ou configuração alterada - snippets de Antes e Depois]
### 👤 Ação do Humano
[Validação e ajustes de contorno]

---

## 3. Prevenção Futura
[Como garantir que isso não volte a ocorrer? Adicionar testes, monitoria, etc]
```

---

## REGRAS DE EXECUÇÃO

- Após escrever o arquivo no disco, ofereça atualizar automaticamente o `dex-architecture/INDEX.md` listando todos os documentos para fácil navegação.
- NUNCA invente declarações do Humano. Se algo não foi dito, escreva `[Não Informado pelo Usuário]`.
- Mantenha a integridade da numeração cronológica dos ADRs verificando a pasta `dex-architecture/decisions/` antes de criar o arquivo.
- Comunique sempre com sucesso a rota de arquivo salva.

