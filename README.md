# Jira–GitHub Integration

Automatisoitu kaksisuuntainen synkronointi GitHub Issuesin ja Jira-projektin välillä.

---

## ⚠️ Vaaditut Secrets

Ennen kuin mikaan toimii, lisää nämä **GitHub repository secretseihin** (`Settings → Secrets and variables → Actions`):

| Secret | Kuvaus | Esimerkki |
|--------|--------|--------|
| `JIRA_BASE_URL` | Jira Cloud -instanssin URL | `https://uutisseuranta.atlassian.net` |
| `JIRA_EMAIL` | Jira-tilin sähköposti | `nimi@esimerkki.fi` |
| `JIRA_API_TOKEN` | Jira API Token ([luo täällä](https://id.atlassian.com/manage-profile/security/api-tokens)) | `ATATxxxx...` |
| `GH_PAT` | GitHub Personal Access Token (scope: `repo`) | `ghp_xxxx...` |
| `GITHUB_WEBHOOK_SECRET` | Webhook-salaisuus (itsekeksitty merkkijono) | `satunnainenmerkkijono123` |
| `JIRA_WEBHOOK_URL` | Jira Automation Incoming Webhook URL | `https://api-private.atlassian.com/...` |
| `JIRA_WEBHOOK_TOKEN` | Jira Automation Webhook Secret Token | `satunnainenavainabc123...` |

> **HUOM:** Jos `JIRA_BASE_URL` tai `JIRA_WEBHOOK_URL` puuttuu, Actions-workflow tai rele-työkulku epäonnistuu/hyppää yli välittömästi. Nykyiset Jira Cloud -automaatiot vaativat tietoturvasyistä `JIRA_WEBHOOK_TOKEN` -salaisuuden `HTTP 400 (Missing token)` -virheiden välttämiseksi.

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

> **HUOM:** Polku `Jira Settings → System → Automation` ei toimi tässä instanssissa. Käytä aina suoria URL-linkkejä yllä.

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

---

## Rakenne

```
├── saanto-01...09-*.json         # Jira Automation -säännöt (JSON-export)
├── webhook-payload-example.json  # GitHub webhook payload -esimerkki
├── migrate-history.py            # Migraatioskripti: GitHub Issues → Jira
├── .github/workflows/
│   └── migrate-history.yml       # GitHub Actions workflow migraatiolle
├── TECHNICAL_DESIGN.md           # Tekninen suunnittelu ja päätökset
├── DECISION_LOG.csv              # Arkkitehtuuripäätökset
└── CODE_CONVENTIONS.md           # Nimeämis- ja koodaussäännöt
```

---

## Nopea aloitus

1. Lisää secretit (katso taulukko yllä)
2. Tuo JSON-säännöt Jira Automationiin: [https://uutisseuranta.atlassian.net/jira/settings/automation#/import](https://uutisseuranta.atlassian.net/jira/settings/automation#/import)
3. Luo GitHub webhook (`Settings → Webhooks`) osoitteeseen jonka Jira tarjoaa
4. Testaa: luo GitHub issue → tarkista että Jira-issue syntyy

## Migraatio (vanhat issuet)

Käynnistä `Actions → Migrate GitHub Issues to Jira → Run workflow`.
Sama workflow toimii seuraavaan projektiin vaihtamalla `project_key`-parametri. Migraatioskripti ([`migrate-history.py`](migrate-history.py)) lisää automaattisesti `Git:`-etuliitteen tiketteihin.

---

## 🛠️ Toteutushistoria ja arkkitehtuuriratkaisut

Tämä repositorio toimii uutisseuranta-organisaation keskitettynä integraatiohallintana. Kehityskaaren aikana toteutettiin seuraavat arkkitehtuuriratkaisut:

### 1. Kaksisuuntainen otsikkosynkronointi & silmukkaesto

Otsikkosynkronointi on täysin kaksisuuntainen ja perustuu etuliitteisiin **`Git:`** ja **`Jira:`** (ilman hakasulkeita). Alkuperäinen luontipaikka määrittää tiketin master-järjestelmän: jos tiketti luodaan GitHubissa, se saa Jiraan etuliitteen `Git:`. Jira Automation tunnistaa tämän ja skippaa synkronoinnin takaisin GitHubiin, estäen ikuiset päivityssilmukat ilman viiveitä tai monimutkaista aritmetiikkaa (L-002).

### 2. Automaattinen validointi (Test Coverage 100 %)

Kaikki JSON-muotoiset säännöt (`saanto-*.json`) validoidaan automaattisesti jokaisessa PR- ja CI-ajossa Python-testiohjelmalla [`test-rules.py`](test-rules.py). Testit tarkistavat JSON-syntaksin, custom-kenttien käytön (`customfield_10071`–10073`), etuliitteiden oikeellisuuden sekä varmistavat, ettei säännöissä ole kielletttyjä label-poistoja (L-006).

### 3. Keskitetty deployment-automaatio

[**`deploy-integration.yml`**](.github/workflows/deploy-integration.yml) synkronoi ja pushaa `jira-webhook-relay.yml` -välitystiedoston automaattisesti organisaation muihin repositorioihin (`uutisseuranta.github.io`, `patterns`, `bq-activitystreams`, `skills`, `ops`). Tietoturva on varmistettu `insteadOf` URL-uudelleenkirjoituksella, jotta tokenit eivät pääse vuotamaan Actions-virhelokeihin.

### 4. Tietoturvapolitiikka ja koodivastuut

`main`-haara on suojattu kaikissa julkisissa repoissa — vaatii vähintään 1 hyväksytyn katselmoinnin ja Code Owner -hyväksynnän. Koodivastuut on määritelty repositorion juuressa `@jaakkokorhonen` vastuulle.

Lisätietoja: [TECHNICAL_DESIGN.md](TECHNICAL_DESIGN.md) ja [DECISION_LOG.csv](DECISION_LOG.csv)
