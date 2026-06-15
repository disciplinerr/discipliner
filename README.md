<div align="center">

<img src="frontend/app/icon.svg" width="88" alt="Discipliner logo" />

# Discipliner

**A personal discipline and study tracker. Not a friendly productivity app — a training ground.**

<a href="#portugues"><img src="https://img.shields.io/badge/🇧🇷_Português-fafafa?style=for-the-badge&logoColor=0a0a0a" alt="Português" /></a>
&nbsp;
<a href="#english"><img src="https://img.shields.io/badge/🇺🇸_English-1d1d1d?style=for-the-badge" alt="English" /></a>

<sub>Clique no idioma · Click a language — or use the collapsible sections below.</sub>

</div>

---

<a id="portugues"></a>
<details open>
<summary><strong>🇧🇷 Português (BR) — clique para abrir/fechar</strong></summary>

<br/>

Todo dia o app gera **um** desafio (problema de matemática/física + tarefa de programação), exige uma rotina diária rígida e acompanha o progresso em uma trilha linear de Backend + DevOps. A IA nunca explica soluções: a avaliação é PASSOU / FALHOU / PARCIAL + uma frase, nada mais.

A dinâmica de aprendizado usa as duas únicas técnicas classificadas como "high utility" pela pesquisa (Dunlosky et al., 2013): **repetição espaçada** e **recall ativo** — os tópicos da trilha viram cartas de revisão agendadas por um algoritmo SM-2-lite — além de **explicações Feynman** para concluir fases e um timer **Pomodoro** embutido. Veja [docs/learning-method.md](docs/learning-method.md).

### Stack

| Camada | Tecnologia |
|---|---|
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind CSS, i18n pt-BR/en |
| Backend | FastAPI (Python 3.12), SQLAlchemy 2, Alembic |
| Banco | PostgreSQL 16 |
| Auth | JWT (python-jose) + bcrypt |
| IA | Claude API (`claude-fable-5`) — só geração e avaliação de desafios |
| Sandbox | Pyodide (Python no navegador) + JS — roda 100% no cliente |
| Infra | Docker Compose (+ Nginx em produção) |

### Como rodar

```bash
cp .env.example .env   # preencha ANTHROPIC_API_KEY, DB_PASSWORD, SECRET_KEY
docker compose up --build
```

- Frontend: http://localhost:3000
- API: http://localhost:8000 (Swagger em /docs)

Instruções completas: [docs/setup.md](docs/setup.md)

### Regras inegociáveis

1. Nenhuma IA explica a solução. Avaliação = PASSOU/FALHOU/PARCIAL + uma frase.
2. Itens de rotina não somem. PULADO fica registrado para sempre.
3. Sem pular fases da trilha. A API rejeita conclusões fora de ordem.
4. O desafio é o mesmo o dia inteiro. Sem botão de regenerar.
5. A derivação matemática é obrigatória (mínimo 50 caracteres).
6. Editor de código é textarea pura. Sem highlight, sem autocomplete, sem IA.

### Documentação

- [Arquitetura](docs/architecture.md) — visão geral + diagramas de sequência
- [Método de aprendizado](docs/learning-method.md) — a evidência e o mapa técnica→funcionalidade
- [Frontend](docs/frontend.md) — i18n, configurações, sandbox de código no navegador
- [Referência da API](docs/api.md)
- [Trilha de aprendizado](docs/trail.md) — as 6 fases
- [Setup](docs/setup.md) — dev local + produção
- [SMTP / e-mail](docs/smtp-setup.md) — testar e-mail local com Mailpit + provedores de produção

</details>

<a id="english"></a>
<details>
<summary><strong>🇺🇸 English — click to expand/collapse</strong></summary>

<br/>

Every day it generates **one** challenge (math/physics problem + programming task), enforces a strict routine checklist, and tracks progress through a linear Backend + DevOps learning trail. AI never explains solutions: evaluation is PASS / FAIL / PARTIAL plus one sentence, nothing more.

The learning dynamic is built on the only two techniques rated "high utility" by the research (Dunlosky et al., 2013): **spaced repetition** and **active recall** — trail topics automatically become review cards scheduled by an SM-2-lite algorithm — plus **Feynman explanations** to complete phases and a built-in **Pomodoro** timer. See [docs/learning-method.md](docs/learning-method.md).

### Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind CSS, pt-BR/en i18n |
| Backend | FastAPI (Python 3.12), SQLAlchemy 2, Alembic |
| Database | PostgreSQL 16 |
| Auth | JWT (python-jose) + bcrypt |
| AI | Claude API (`claude-fable-5`) — challenge generation + evaluation only |
| Sandbox | Pyodide (Python in the browser) + JS — runs 100% client-side |
| Infra | Docker Compose (+ Nginx in production) |

### Quick start

```bash
cp .env.example .env   # fill in ANTHROPIC_API_KEY, DB_PASSWORD, SECRET_KEY
docker compose up --build
```

- Frontend: http://localhost:3000
- API: http://localhost:8000 (Swagger at /docs)

Full instructions: [docs/setup.md](docs/setup.md)

### Non-negotiable rules

1. No AI explains the solution. Evaluation = PASS/FAIL/PARTIAL + one sentence.
2. No erasing routine items. SKIPPED is permanently logged.
3. No skipping trail phases. The API rejects out-of-order completions.
4. The challenge is the same challenge all day. No regeneration button.
5. The math derivation is required (minimum 50 characters).
6. Plain textarea code editor. No syntax highlighting, no autocomplete, no AI.

### Documentation

- [Architecture](docs/architecture.md) — system overview + sequence diagrams
- [Learning method](docs/learning-method.md) — the evidence and how each technique maps to features
- [Frontend](docs/frontend.md) — i18n (pt-BR/en), settings, in-browser code sandbox
- [API reference](docs/api.md)
- [Learning trail](docs/trail.md) — the 6 phases
- [Setup](docs/setup.md) — local dev + production
- [SMTP / email](docs/smtp-setup.md) — test email locally with Mailpit + production providers

</details>

---

<div align="center">
<sub>Built to train discipline, not to feel good. · Feito para treinar disciplina, não para agradar.</sub>
</div>
