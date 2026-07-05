# Jira–GitHub-integraatio

> **Huom:** Tämä tiedosto on operatiivinen ohjedokumentti. Arkkitehtuuripäätökset ja tekniset speksit löytyvät [TECHNICAL_DESIGN.md](https://github.com/uutisseuranta/jira-github-integration/blob/main/TECHNICAL_DESIGN.md):stä ja [DECISION_LOG.csv](https://github.com/uutisseuranta/jira-github-integration/blob/main/DECISION_LOG.csv):stä.

---

## GitHub Secrets

Tarvittavat secrets GitHub Actions -workflowlle:

| Secret | Arvo | Tila |
|---|---|---|
| `JIRA_BASE_URL` | `https://uutisseuranta.atlassian.net` | [⚠️ lisättävä ennen ajoa](https://github.com/uutisseuranta/uutisseuranta.github.io/settings/secrets/actions) |
| `JIRA_API_TOKEN` | Jira API token | [⚠️ lisättävä ennen ajoa](https://github.com/uutisseuranta/uutisseuranta.github.io/settings/secrets/actions) |
| `JIRA_USER_EMAIL` | Jira-tilin sähköposti | [⚠️ lisättävä ennen ajoa](https://github.com/uutisseuranta/uutisseuranta.github.io/settings/secrets/actions) |

---

## Issuetype-mapaus

GitHub-label määrittää Jira work item -tyypin:

| GitHub-label | Jira work item type |
|---|---|
| `feat`, `enhancement` | Story |
| `bug` | Bug |
| `epic` | Epic |
| `arch`, `sec` | Task |
| `chore`, `docs`, `refactor`, `test` | Task |
| ei labelia | Task (oletus) |

---

## Automation-sääntöjen hallinta

### Importoi sääntö

Avaa suoraan: **[https://uutisseuranta.atlassian.net/jira/settings/automation#/import](https://uutisseuranta.atlassian.net/jira/settings/automation#/import)**

1. Lataa JSON-tiedosto reposta (ks. Tiedostot-taulukko alla)
2. Klikkaa **Import** / **Import flow**
3. Valitse projektiksi `US` (Uutisseuranta)
4. Tallenna ja aktivoi

### Audit log (vianetsintä)

Avaa suoraan: **[https://uutisseuranta.atlassian.net/jira/settings/automation#/audit-log](https://uutisseuranta.atlassian.net/jira/settings/automation#/audit-log)**

> **Huom:** Polku `Jira Settings → System → Automation` ei toimi tässä instanssissa.
> Käytä aina suoria URL-linkkejä yllä.

---

## Tiedostot

| Tiedosto | Tarkoitus |
|---|---|
| [`saanto-01-github-issue-opened.json`](https://github.com/uutisseuranta/jira-github-integration/blob/main/saanto-01-github-issue-opened.json) | GitHub issue opened → luo Jira work item |
| [`saanto-02-github-issue-edited.json`](https://github.com/uutisseuranta/jira-github-integration/blob/main/saanto-02-github-issue-edited.json) | GitHub issue edited → päivitä Jira summary + description |
| [`saanto-03-github-issue-closed.json`](https://github.com/uutisseuranta/jira-github-integration/blob/main/saanto-03-github-issue-closed.json) | GitHub issue closed → transition Jira → Done |
| [`saanto-04-github-issue-reopened.json`](https://github.com/uutisseuranta/jira-github-integration/blob/main/saanto-04-github-issue-reopened.json) | GitHub issue reopened → transition Jira → To Do |
| [`saanto-05-github-issue-labeled.json`](https://github.com/uutisseuranta/jira-github-integration/blob/main/saanto-05-github-issue-labeled.json) | GitHub issue labeled/unlabeled → päivitä Jira labels + priority |
| [`saanto-07-github-issue-milestoned.json`](https://github.com/uutisseuranta/jira-github-integration/blob/main/saanto-07-github-issue-milestoned.json) | GitHub milestone → päivitä Jira fixVersions |
| [`saanto-08-github-comment-created.json`](https://github.com/uutisseuranta/jira-github-integration/blob/main/saanto-08-github-comment-created.json) | GitHub comment → kommentti Jiraan (silmukkaesto: skip jos alkaa `[Jira]`) |
| [`saanto-09-jira-status-changed.json`](https://github.com/uutisseuranta/jira-github-integration/blob/main/saanto-09-jira-status-changed.json) | Jira status changed → päivitä GitHub issue state |
| [`test-webhook.sh`](https://github.com/uutisseuranta/jira-github-integration/blob/main/test-webhook.sh) | Manuaalinen curl-testi — aja paikallisesti webhookin testaamiseen |
| [`webhook-payload-example.json`](https://github.com/uutisseuranta/jira-github-integration/blob/main/webhook-payload-example.json) | Esimerkki webhook-payloadista — käytä testauksen pohjana |
