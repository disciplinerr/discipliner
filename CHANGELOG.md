# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
versionamento conforme [SemVer](https://semver.org/lang/pt-BR/).
Detalhes do fluxo em [docs/releases.md](./docs/releases.md).

## [Unreleased]

## [1.1.0] - 2026-06-15

### Added

- Módulo de controle financeiro: orçamentos, contas, parcelamentos e metas.
- Visão financeira: gasto total do mês, dashboard, projeção e ícones próprios.
- Fluxo de verificação de e-mail no cadastro, com registro anti-enumeration.
- Mailpit como catcher SMTP de desenvolvimento; TLS/auth opcionais no envio.
- Pipeline de CI (pytest backend + lint/build frontend) em todo push e PR.
- Workflow de release tag-driven: publica imagens no GHCR e cria GitHub Release.
- Documentação de versionamento e releases (`docs/releases.md`) e banner do projeto.

### Changed

- Entradas de review e trilha ocultas temporariamente na UI.

### Fixed

- Reenvio do e-mail de verificação ao recadastrar conta ainda não verificada.
- Seed dos itens de sistema da rotina agora idempotente (upsert).
- `NEXT_PUBLIC_API_URL` repassado corretamente ao build do frontend no Docker.

## [1.0.0] - 2026-06-10

### Added

- Versão inicial do Discipliner: auth (JWT + bcrypt), desafio diário,
  rotina, trilha de aprendizado, inglês técnico e challenges com sandbox.
