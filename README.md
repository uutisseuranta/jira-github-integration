# Jira–GitHub Integration

Automatisoitu kaksisuuntainen synkronointi GitHub Issuesin ja Jira-projektin välillä.

---

## ⚠️ Vaaditut Secrets

Ennen kuin mikään toimii, lisää nämä **GitHub repository secretseihin** (`Settings → Secrets and variables → Actions`).

GitHub Secretsejä **ei voi hallita Atlassian Rovo MCP Serverin kautta** — Rovo MCP on Atlassian-ekosysteemin työkalu (Jira, Confluence, Bitbucket), eikä sillä ole pääsyä GitHub-repositorion asetuksiin. Secrets-hallintaan käytetään joko **GitHub-käyttöliittymää** tai **GitHub CLI:tä**.

| Secret | Kuvaus | Esimerkki |
|--------|--------|--------|
| `JIRA_BASE_URL` | Jira Cloud -instanssin URL | `https://uutisseuranta.atlassian.net` |
| `JIRA_EMAIL` | Jira-tilin sähköposti | `nimi@esimerkki.fi` |
| `JIRA_API_TOKEN` | Jira API Token ([luo täällä](https://id.atlassian.com/manage-profile/security/api-tokens)) | `ATATxxxx...` |
| `GH_PAT` | GitHub Personal Access Token (scope: `repo`) | `ghp_xxxx...` |
| `GITHUB_WEBHOOK_SECRET` | Webhook-salaisuus (itsekeksitty merkkijono) | `satunnainenmerkkijono123` |
| `JIRA_WEBHOOK_URL` | Jira Automation Incoming Webhook URL | `https://api-private.atlassian.com/...` |
| `JIRA_WEBHOOK_TOKEN` | Jira Automation Webhook Secret Token | `satunnainenavainabc123...` |

> **HUOM:** Jos `JIRA_BASE_URL` tai `JIRA_WEBHOOK_URL` puuttuu, Actions-workflow tai rele-työkulu epäonnistuu/hyppää yli välittömästi. Nykyiset Jira Cloud -automaatiot vaativat tietoturvasyistä `JIRA_WEBHOOK_TOKEN` -salaisuuden `HTTP 400 (Missing token)` -virheiden välttämiseksi.

---

## Secrets-hallinta GitHub CLI:llä

Secretsejä voi lisätä ja päivittää paikallisesti [GitHub CLI:llä](https://cli.github.com/) ilman selainarvon näkymistä näytöllä.

GitHub CLI vaatii kirjautumisen:

```bash
gh auth login
```

Aseta tai päivitä secret interaktiivisesti (arvo ei jää shellin historiaan):

```bash
gh secret set JIRA_API_TOKEN --repo uutisseuranta/jira-github-integration
# CLI pyytää arvon interaktiivisesti
```

Tai suoraan (varo shellin historiaa):

```bash
gh secret set JIRA_API_TOKEN --repo uutisseuranta/jira-github-integration --body "ATATxxxx..."
```

Lista repon secretseistä (nimet näkyvät, arvot piilotettu):

```bash
gh secret list --repo uutisseuranta/jira-github-integration
```

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

## Automation flows -hallinta

### Tuo flow (import)

Import tapahtuu **globaalin** Automation-näkymän kautta — ei projektikohtaisesta näkymästä.

1. Avaa **Jira settings → System → Automation flows**
   (suora linkki: [https://uutisseuranta.atlassian.net/jira/settings/automation](https://uutisseuranta.atlassian.net/jira/settings/automation))
2. Paina oikeasta yläkulmasta **… (More actions) → Import flows**
3. Valitse JSON-tiedosto reposta (ks. Tiedostot-taulukko alla)
4. Valitse projektikohdistukseksi `US` (Uutisseuranta) ja haluamasi flowt
5. Paina **Let's do this**
6. **Aktivoi tuodut flowt manuaalisesti** — kaikki tuodut flowt tulevat disabled-tilassa

> **HUOM:** Jos samanniminen flow on jo olemassa, tuodun nimi muuttuu automaattisesti muotoon `Copy of [nimi]`. Tarkista duplikaatit ja poista vanhentunut versio.

### Audit log (vianetsintä)

1. Avaa **Jira settings → System → Automation flows**
2. Paina **Audit log** vasemman sivupalkin alaosasta

---

## Tiedostot

| Tiedosto | Tarkoitus |
|---|---|
| [`saanto-01-github-issue-opened.json`](saanto-01-github-issue-opened.json) | GitHub issue opened → luo Jira work item |
| [`saanto-02-github-issue-edited.json`](saanto-02-github-issue-edited.json) | GitHub issue edited → päivitä Jira summary + description |
| [`saanto-03-github-issue-closed.json`](saanto-03-github-issue-closed.json) | GitHub issue closed → transition Jira → Done |
| [`saanto-04-github-issue-reopened.json`](saanto-04-github-issue-reopened.json) | GitHub issue reopened → transition Jira → To Do |
| [`saanto-05-github-issue-labeled.json`](saanto-05-github-issue-labeled.json) | GitHub issue labeled/unlabeled → päivitä Jira labels + priority |
| [`saanto-07-github-issue-milestoned.json`](saanto-07-github-issue-milestoned.json) | GitHub milestone → päivitä Jira fixVersions |
| [`saanto-08-github-comment-created.json`](saanto-08-github-comment-created.json) | GitHub comment → kommentti Jiraan (silmukkaesto: skip jos alkaa `[Jira]`) |
| [`saanto-09-jira-status-changed.json`](saanto-09-jira-status-changed.json) | Jira status changed → päivitä GitHub issue state |
| [`test-webhook.sh`](test-webhook.sh) | Manuaalinen curl-testi — aja paikallisesti webhookin testaamiseen |
| [`webhook-payload-example.json`](webhook-payload-example.json) | Esimerkki webhook-payloadista — käytä testauksen pohjana |
| [`.github/workflows/deploy-integration.yml`](.github/workflows/deploy-integration.yml) | Synkronoi `jira-webhook-relay.yml` automaattisesti organisaation repoihin (`uutisseuranta.github.io`, `patterns`, `bq-activitystreams`, `skills`, `ops`) |
| [`.github/workflows/jira-webhook-relay.yml`](.github/workflows/jira-webhook-relay.yml) | GitHub Actions -rele: välittää GitHub-webhook-pyynnöt Jira Automation Incoming Webhook -osoitteeseen |
| [`.github/workflows/lint-filenames.yml`](.github/workflows/lint-filenames.yml) | CI-tarkistus: varmistaa tiedostonimien yhdenmukaisuuden CODE_CONVENTIONS.md-säännöillä |
| [`migrate-history.py`](migrate-history.py) | Migraatioskripti: siirtää vanhat GitHub Issues → Jira, lisää `Git:`-etuliitteen tiketteihin |

---

## Rakenne

```
├── saanto-01...09-*.json         # Jira Automation flows (JSON-export)
├── webhook-payload-example.json  # GitHub webhook payload -esimerkki
├── migrate-history.py            # Migraatioskripti: GitHub Issues → Jira
├── .github/workflows/
│   ├── deploy-integration.yml    # Synkronoi jira-webhook-relay.yml organisaation muihin repoihin
│   ├── jira-webhook-relay.yml    # Rele: GitHub webhook → Jira Automation
│   ├── lint-filenames.yml        # CI: tiedostonimitarkistus
│   └── migrate-history.yml       # GitHub Actions workflow migraatiolle
├── TECHNICAL_DESIGN.md           # Tekninen suunnittelu ja päätökset
├── DECISION_LOG.csv              # Arkkitehtuuripäätökset
└── CODE_CONVENTIONS.md           # Nimeämis- ja koodaussäännöt
```

---

## Nopea aloitus

1. Lisää secretit (katso taulukko yllä) — GitHub UI:lla tai `gh secret set` -komennolla
2. Tuo JSON-flowt: **Jira settings → System → Automation flows → … → Import flows**
3. Aktivoi tuodut flowt manuaalisesti (tulevat disabled-tilassa)
4. Luo GitHub webhook: `Settings → Webhooks → Add webhook`
   - **Payload URL:** `JIRA_WEBHOOK_URL`-secretin arvo (Jira Automation → saanto-01 → Incoming Webhook -osoite)
   - **Content type:** `application/json`
   - **Secret:** `GITHUB_WEBHOOK_SECRET`-secretin arvo
   - **Events:** _Issues_ ja _Issue comments_
5. Testaa: luo GitHub issue → tarkista että Jira-issue syntyy

## Migraatio (vanhat issuet)

Käynnistä `Actions → Migrate GitHub Issues to Jira → Run workflow`.
Sama workflow toimii seuraavaan projektiin vaihtamalla `project_key`-parametri. Migraatioskripti ([`migrate-history.py`](migrate-history.py)) lisää automaattisesti `Git:`-etuliitteen tiketteihin.

---

## Mitä Atlassian Rovo MCP Server tekee (ja mitä ei)

**Rovo MCP Server** (`https://mcp.atlassian.com/v1/sse`) on Atlassianin virallinen remote MCP -palvelin, joka yhdistää Claude Coden, Cursorin tai VS Coden Atlassian-ekosysteemiin. Se autentikoidaan OAuth 2.1:llä tai API-tokenilla.

**Rovo MCP voi:**
- Lukea ja kirjoittaa **Jira-issuet** (getJiraIssue, createJiraIssue, editJiraIssue, transitionJiraIssue, searchJiraIssuesUsingJql)
- Lukea ja kirjoittaa **Confluence-sivut** (getConfluencePage, createConfluencePage, updateConfluencePage)
- Hakea tietoa **Bitbucket-repositorioista** (pull requestit, commitit, pipelinit)
- Hallita **Compass-komponentteja**
- Hakea yhteyksiä Teamwork Graphista (Jira ↔ Confluence ↔ PR:t ↔ deploymentit)

**Rovo MCP EI voi:**
- Hallita GitHub repository secretsejä
- Muuttaa GitHub Actions -konfiguraatioita
- Kirjoittaa tiedostoja GitHub-repositorioon (se onnistuu vain GitHub MCP Serverillä tai GitHub CLI:llä)

Claude Coden yhdistäminen Atlassian Rovo MCP:hen:

```bash
claude mcp add --scope user --transport sse atlassian https://mcp.atlassian.com/v1/sse
```

Tämän jälkeen Claude Code avaa OAuth-kirjautumisikkunan selaimessa ja pyytää hyväksymään Jira/Confluence-oikeudet.

---

## 🛠️ Toteutushistoria ja arkkitehtuuriratkaisut

Tämä repositorio toimii uutisseuranta-organisaation keskitettynä integraatiohallintana. Kehityskaaren aikana toteutettiin seuraavat arkkitehtuuriratkaisut:

### 1. Kaksisuuntainen otsikkosynkronointi & silmukkaesto

Otsikkosynkronointi on täysin kaksisuuntainen ja perustuu etuliitteisiin **`Git:`** ja **`Jira:`** (ilman hakasulkeita). Alkuperäinen luontipaikka määrittää tiketin master-järjestelmän: jos tiketti luodaan GitHubissa, se saa Jiraan etuliitteen `Git:`. Jira Automation tunnistaa tämän ja skippaa synkronoinnin takaisin GitHubiin, estäen ikuiset päivityssilmukat ilman viiveitä tai monimutkaista aritmetiikkaa (L-002).

### 2. Automaattinen validointi (Test Coverage 100 %)

Kaikki JSON-muotoiset flowt (`saanto-*.json`) validoidaan automaattisesti jokaisessa PR- ja CI-ajossa Python-testiohjelmalla [`test-rules.py`](test-rules.py). Testit tarkistavat JSON-syntaksin, custom-kenttien käytön (`customfield_10071`–10073), etuliitteiden oikeellisuuden sekä silmukkaeston logiikan toimivuuden.
