---
name: dex-code-review
description: Unified code review skill — DEX 6-dimension review (Correção, Segurança, Performance, Clean Code, Testes, Arquitetura) + Antigravity checklist (rules, severity, fix examples).
---

# dex-code-review — Unified Code Review

Processo cirúrgico de Code Review do DEX Flow Kit.
Sem persona. Avaliação sistêmica, fria, metódica e orientada a elevar o padrão de engenharia.

> **Merged from:** `dex-code-review` (DEX 6-dim) + `code-review-checklist` (Antigravity rule-by-rule checklist).
> **See also:** [code-review-checklist.md](code-review-checklist.md) — granular checklist with severities and fix examples.

## ATIVAÇÃO E CONTEXTO

Ao ser invocado, solicite as seguintes informações (se não estiverem presentes):
1. O snippet, Pull Request diff, ou arquivo que precisa de revisão.
2. O framework ou linguagem alvo.
3. O objetivo de negócio ou Critério de Aceite que o código tenta resolver.
4. Áreas de insegurança do desenvolvedor (ex: "estou em dúvida se essa query escala").

## AS 6 DIMENSÕES DO REVIEW

Para cada dimensão avaliada, atribua uma das flags:
**✅ Approved / ⚠️ Warning (Necessita Fix) / ❌ Critical (Blocker)**

### 1. Correção Lógica (Correctness)
- O código atende de fato ao requisito de negócio?
- Lida corretamente com off-by-one errors, null pointers ou lógicas assíncronas invertidas?

### 2. Segurança (Security - OWASP Focado)
- Entradas de usuários estão sendo rigorosamente sanitizadas ou validadas?
- O ORM/SQL impede Injections?
- Há PII (Personal Identifiable Information) vazando em logs ou traces?
- Verificações de Authorization (Não apenas Authentication) estão presentes no backend?

### 3. Performance & Eficiência
- O Big-O notation das funções principais faz sentido?
- Há N+1 Queries ocorrendo mascaradas por ORMs?
- Alocações em loops que causam degradação do Garbage Collector/Memory Leaks?
- Faltam índices ou estratégias básicas de memoization/caching?

### 4. Legibilidade & Clean Code
- Nomenclatura é universal e descreve a intenção? (Evite variáveis `temp`, `data`, `x`).
- Funções possuem responsabilidade única (SRP)?
- Complexidade ciclomática alta? Níveis de indentação extremos?
- Uso exagerado de "Magic Strings/Numbers"?

### 5. Cobertura de Testes
- As branches vitais do código recém adicionado possuem asserções de teste automatizado?
- Os testes avaliam cenários de falha e edge cases, ou apenas o "caminho feliz"?
- São testes frágeis (acoplados a implementações internas invés de comportamento)?

### 6. Integridade Arquitetural
- O código desrespeita camadas da arquitetura do projeto (ex: Controller acessando DB diretamente ignorando services/repositories)?
- Aumenta perigosamente o acoplamento ou a dívida técnica global?

## FORMATO DE OUTPUT (TEMPLATE)

```markdown
## DEX Code Review — [Resumo da Feature ou Arquivo]

### Visão Geral
[Parágrafo sintético: "Código funcional, mas exige ajustes críticos na camada de segurança e na nomenclatura."]

### Dashboard de Avaliação
| Dimensão | Status | Feedback Rápido |
|----------|--------|-----------------|
| Correção | ✅/⚠️/❌ | ... |
| Segurança | ✅/⚠️/❌ | ... |
| Performance| ✅/⚠️/❌ | ... |
| Clean Code| ✅/⚠️/❌ | ... |
| Testes | ✅/⚠️/❌ | ... |
| Arquitetura| ✅/⚠️/❌ | ... |

### Aprofundamento e Remediações

#### ❌ BLOCKERS CRÍTICOS
- **[Segurança] Linha X:** [Detalhe do erro].
  - *Sugerido:* `[Snippet do código corrigido]`

#### ⚠️ WARNINGS IMPORTANTES
- **[Performance] Linha Y:** [Detalhe do problema].
  - *Sugerido:* Refatorar para usar Map/Set para O(1) lookup em vez de O(n) array filter.

#### 💡 Sugestões de Excelência (Non-blocking)
- Melhorias sintáticas ou abstrações elegantes menores.

### Veredito Final
`[ ] Aprovado (LGTM)` | `[ ] Aprovado Condicionalmente` | `[ ] Solicitar Alterações Críticas`
```

Sempre encerre perguntando se o usuário quer documentar essas decisões de design no `dex-doc-register`.

