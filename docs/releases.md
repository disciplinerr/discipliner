# Versionamento & Releases

O Discipliner segue [SemVer](https://semver.org/lang/pt-BR/): `MAJOR.MINOR.PATCH`.

| Parte     | Quando incrementar                                        |
| --------- | --------------------------------------------------------- |
| **MAJOR** | Mudança incompatível (quebra API, schema, contrato)       |
| **MINOR** | Nova funcionalidade compatível com versões anteriores     |
| **PATCH** | Correção de bug compatível                                 |

Pré-releases usam sufixo: `1.3.0-rc.1`, `1.3.0-beta.2`.

## Nivelamento — qual número subir

Cada release sobe **exatamente um** nível. Ao subir um nível, os de menor
ordem voltam a zero (`1.4.2` → MINOR → `1.5.0`, não `1.5.2`).

| Mudança                                  | Nível | Exemplo de salto      |
| ---------------------------------------- | ----- | --------------------- |
| Corrige bug, sem mudar comportamento     | PATCH | `1.2.0` → `1.2.1`     |
| Adiciona feature, nada quebra            | MINOR | `1.2.1` → `1.3.0`     |
| Quebra API/schema/contrato existente     | MAJOR | `1.3.0` → `2.0.0`     |

### Antes do 1.0.0 (fase `0.x`)

Enquanto o produto é instável, fica em `0.MINOR.PATCH` e a regra muda:

| Mudança                          | Nível | Exemplo            |
| -------------------------------- | ----- | ------------------ |
| Primeiro código publicável       | —     | `0.1.0`            |
| Correção de bug em `0.x`         | PATCH | `0.1.0` → `0.1.1`  |
| Feature nova **ou** breaking     | MINOR | `0.1.1` → `0.2.0`  |
| Considerado estável p/ produção  | MAJOR | `0.x` → `1.0.0`    |

- **`v0.0.1`** — primeiro patch experimental, nada garantido (raro usar de início).
- **`v0.1.0`** — primeira versão funcional em desenvolvimento; em `0.x` qualquer
  breaking sobe só o MINOR, porque tudo antes do `1.0.0` é "pode mudar".
- **`v1.0.0`** — API pública estável e comprometida; a partir daqui breaking = MAJOR.

> Regra prática: enquanto não promete estabilidade a terceiros, fique em `0.x`.
> O `1.0.0` é uma promessa, não um marco de "ficou bonito".

## Fluxo de release (tag-driven)

A release é disparada empurrando uma tag Git `vX.Y.Z`. Nada é publicado sem tag.

```bash
# 1. Garanta que master está atualizado e o CI verde
git checkout master
git pull

# 2. Atualize o CHANGELOG (mova "Unreleased" para a nova versão)
# 3. Crie a tag anotada
git tag -a v1.3.0 -m "Release 1.3.0"

# 4. Empurre a tag — isso dispara o workflow de release
git push origin v1.3.0
```

O workflow `.github/workflows/release.yml` então:

1. Builda e publica as imagens no **GHCR**:
   - `ghcr.io/fernandohaeser/discipliner-backend:1.3.0` (+ `1.3`, `latest`)
   - `ghcr.io/fernandohaeser/discipliner-frontend:1.3.0` (+ `1.3`, `latest`)
2. Cria a **GitHub Release** com notas geradas automaticamente a partir
   dos commits/PRs desde a última tag.

Tags com sufixo (`-rc`, `-beta`) são marcadas como **pré-release** e **não**
recebem a tag `latest`.

## CI (toda branch / todo PR)

O workflow `.github/workflows/ci.yml` roda em **todo push e todo PR**:

- **backend**: `pytest` contra um PostgreSQL efêmero (service container)
- **frontend**: `npm run lint` + `npm run build`

Cada commit precisa passar no CI antes de virar release.

## Convenção de commits

Recomendado [Conventional Commits](https://www.conventionalcommits.org/) —
melhora as notas de release automáticas:

```
feat(finance): ...     # → MINOR
fix(auth): ...         # → PATCH
feat!: ... / BREAKING  # → MAJOR
```

## Configuração necessária no GitHub

- **Variável de repo** `NEXT_PUBLIC_API_URL` (Settings → Variables): URL
  pública da API, baked no build do frontend.
- GHCR usa o `GITHUB_TOKEN` automático — nenhum secret extra é necessário.
