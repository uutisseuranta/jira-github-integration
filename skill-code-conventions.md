# MML Skill — uutisseuranta/jira-github-integration

> Tämä tiedosto latautuu automaattisesti MML-kontekstiin kun teet muutoksia
> `uutisseuranta/jira-github-integration`-repoon.
> Määritelty: https://github.com/uutisseuranta/jira-github-integration/issues/13

---

## Automaattiset säännöt

### 1. Tiedostorakenne

Kaikki tiedostot luodaan **repositorion juureen**. Alikansioita ei käytetä.

Poikkeus: `.github/` on **vain GitHubin omaa infrastruktuuria** varten (Actions-workflowt,
issue-templatet, Dependabot). Sinne ei sijoiteta repon omia tiedostoja.

Jos käyttäjä pyytää tiedostoa alikansioon (esim. `docs/foo.md`, `scripts/bar.py`),
luo se juureen ilman kansiota (`foo.md`, `bar.py`).

### 2. Tiedostojen nimeäminen

| Tyyppi | Konventio | Esimerkki |
|---|---|---|
| Normatiiviset sopimusdokumentit | `SCREAMING_SNAKE_CASE.md` | `TECHNICAL_DESIGN.md`, `DECISION_LOG.csv` |
| Kaikki muut tiedostot (sh, py, yml, json, js) | `kebab-case` | `test-webhook.sh`, `migrate-history.py` |
| README ja LICENSE | Isolla | `README.md`, `LICENSE` |

- ❌ Ei `snake_case` (esim. `migrate_history.py` → `migrate-history.py`)
- ❌ Ei `camelCase` tai `PascalCase` tavallisille tiedostoille

### 3. Päätösloki

Ennen kuin teet arkkitehtuuripäätöksen, kirjaa se
[`DECISION_LOG.csv`](https://github.com/uutisseuranta/jira-github-integration/blob/main/DECISION_LOG.csv):ään:

```
id,date,title,decision,rationale,affects_issues
```

### 4. Cross-repo-linkit

Käytä aina **absoluuttisia GitHub-URL:eja**:

```markdown
<!-- ✅ Oikein -->
[TECHNICAL_DESIGN.md](https://github.com/uutisseuranta/jira-github-integration/blob/main/TECHNICAL_DESIGN.md)

<!-- ❌ Väärin -->
[TECHNICAL_DESIGN.md](../jira-github-integration/TECHNICAL_DESIGN.md)
```

### 5. Koodin kommentointi

Kommentit selittävät **miksi**, eivät **mitä**.

| Kieli | Syntaksi |
|---|---|
| JS | `//` yksiriviset, `/** */` JSDoc vain julkisille API-funktioille |
| CSS | `/* */` |
| HTML | `<!-- -->` |
| Bash | `#`, skriptin yläosassa käyttöohje |
| YAML | `#`, selitä miksi step on olemassa |
| Python | `#`, docstring julkisille funktioille |

### 6. Versionumerointi

SemVer muodossa `vX.Y.Z`. Git-tagit ja GitHub Releases käyttävät samaa muotoa.

---

## Muistisäännöt ennen jokaista toimenpidettä

1. **Tiedoston nimi** — `kebab-case` vai `SCREAMING_SNAKE_CASE`?
2. **Kansio** — älä luo. Kaikki juureen.
3. **Arkkitehtuuripäätös** — kirjaa `DECISION_LOG.csv`:hen ensin.
4. **Toisen repon viittaus** — absoluuttinen GitHub-URL.

---

## Nykyinen tiedostoluettelo (juuri)

| Tiedosto | Kuvaus |
|---|---|
| `.github/workflows/*.yml` | GitHub Actions -workflowt |
| `CODE_CONVENTIONS.md` | Koodauskäytännöt (yhteinen kaikille uutisseuranta-repoille) |
| `DECISION_LOG.csv` | Arkkitehtuuripäätökset |
| `LICENSE` | Lisenssi |
| `mml-skill.md` | Tämä tiedosto — MML-skill-konfiguraatio |
| `README.md` | Lyhyt kuvaus |
| `TECHNICAL_DESIGN.md` | Tekninen suunnittelu |
| `saanto-NN-*.json` | Jira Automation -sääntömäärittelyt |
| `webhook-payload-example.json` | Webhook-payload-esimerkki |
| `test-webhook.sh` | Manuaalinen curl-testi |
| `migrate-history.py` | Historia-migraatioskripti |
