# PLAN-fix-epi-logic.md

## Goal
Melhorar a organização dos arquivos do projeto (limpeza da raiz) e corrigir o erro de falso-negativo na detecção de EPI (LLaVA não reconhecendo capacete/colete corretamente).

## Tarefas

- [ ] Task 1: Limpeza da Estrutura Raiz → Verify: Arquivos `*.jsx`, `*.js`, `*.css` e `*.html` do protótipo movidos para `docs/prototype/`. A raiz deve conter apenas `backend/`, `frontend/`, `docs/`, `run.py` e arquivos de configuração.
- [ ] Task 2: Melhorar o recorte (crop) das imagens → Verify: Aumentar o `padding` no `llava_service.py` de 5% para 20%. Isso garante que o LLaVA veja a cabeça inteira (capacete) e o tronco (colete) com contexto.
- [ ] Task 3: Forçar modo JSON no Ollama e otimizar prompt → Verify: Adicionar `"format": "json"` no payload da API do Ollama no `llava_service.py` e ajustar o prompt para ser mais explícito.
- [ ] Task 4: Ajustar lógica de fallback e keywords → Verify: Adicionar suporte a palavras em português no parser caso o modelo traduza (ex: "capacete", "colete").

## Done When
- [ ] A raiz do projeto está limpa, contendo apenas o essencial.
- [ ] O backend usa `"format": "json"` nativo do Ollama.
- [ ] O padding do recorte permite ao modelo de visão analisar melhor as extremidades do corpo.
- [ ] Teste visual confirma que os trabalhadores da imagem agora são detectados corretamente como "Conformes".
