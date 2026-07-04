# JIRA.md — Jira–GitHub-integraation käyttöohje

Tämä dokumentti kuvaa `uutisseuranta/jira-github-integration`-repon Jira-konfiguraation: issuetype-mapaukset, secrets-taulukot sekä migrate-history-tiedostopolut.

---

## Issuetype-mapaus

GitHub-labelit mapautuvat Jira work item -tyyppeihin seuraavasti:

| GitHub-label | Jira work item type |
|---|---|
| `feat`, `enhancement` | Story |
| `bug` | Bug |
| `epic` | Epic |
| `arch`, `sec` | Task |
| `chore`, `docs`, `refactor`, `test` | Task |
| ei labelia | Task (oletus) |

---

## GitHub Secrets

Seuraavat secrets täytyy asettaa repoon ennen Jira Automation -sääntöjen käyttöönottoa:

| Secret | Arvo | Tila |
|---|---|---|
| `JIRA_BASE_URL` | `https://uutisseuranta.atlassian.net` | [⚠️ lisättävä ennen ajoa](https://github.com/uutisseuranta/uutisseuranta.github.io/settings/secrets/actions) |
| `JIRA_API_TOKEN` | Atlassian API token | [⚠️ lisättävä ennen ajoa](https://github.com/uutisseuranta/uutisseuranta.github.io/settings/secrets/actions) |
| `JIRA_USER_EMAIL` | Atlassian-tilin sähköposti | [⚠️ lisättävä ennen ajoa](https://github.com/uutisseuranta/uutisseuranta.github.io/settings/secrets/actions) |

---

## Migrate-history — tiedostopolut

| Tiedosto | Tarkoitus |
|---|---|
| `.github/workflows/migrate-history.yml` | GitHub Actions workflow — käynnistetään manuaalisesti (`workflow_dispatch`) |
| `migrate-history.py` | Python-skripti joka hakee GitHub-issuet sivuttain ja luo ne Jiran work itemeiksi |

---

## Viitteet

- [TECHNICAL_DESIGN.md](https://github.com/uutisseuranta/jira-github-integration/blob/main/TECHNICAL_DESIGN.md)
- [DECISION_LOG.csv](https://github.com/uutisseuranta/jira-github-integration/blob/main/DECISION_LOG.csv)
- [CODE_CONVENTIONS.md](https://github.com/uutisseuranta/jira-github-integration/blob/main/CODE_CONVENTIONS.md)
