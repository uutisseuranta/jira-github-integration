# Jira–GitHub Integration

Automatisoitu kaksisuuntainen synkronointi GitHub Issuesin ja Jira-projektin välillä.

## ⚠️ Vaaditut Secrets

Ennen kuin mikään toimii, lisää nämä **GitHub repository secretseihin** (`Settings → Secrets and variables → Actions`):

| Secret | Kuvaus | Esimerkki |
|--------|--------|--------|
| `JIRA_BASE_URL` | Jira Cloud -instanssin URL | `https://oma-org.atlassian.net` |
| `JIRA_EMAIL` | Jira-tilin sähköposti | `nimi@esimerkki.fi` |
| `JIRA_API_TOKEN` | Jira API Token ([luo täällä](https://id.atlassian.com/manage-profile/security/api-tokens)) | `ATATxxxx...` |
| `GH_PAT` | GitHub Personal Access Token (scope: `repo`) | `ghp_xxxx...` |
| `GITHUB_WEBHOOK_SECRET` | Webhook-salaisuus (itsekeksitty merkkijono) | `satunnainenmerkkijono123` |

> **HUOM:** Jos `JIRA_BASE_URL` puuttuu, Actions-workflow epäonnistuu välittömästi.

## Rakenne

```
├── saanto-01...09-*.json         # Jira Automation -säännöt (JSON-export)
├── webhook-payload-example.json  # GitHub webhook payload -esimerkki
├── migrate-history.py            # Migraatioskripti: GitHub Issues → Jira
├── .github/workflows/
│   └── migrate-history.yml       # GitHub Actions workflow migraatiolle
├── TECHNICAL_DESIGN.md           # Tekninen suunnittelu ja päätökset
├── DECISION_LOG.csv              # Arkkitehtuuripäätökset
└── STATUS.md                     # Toteutuksen tila
```

## Nopea aloitus

1. Lisää secretit (katso taulukko yllä)
2. Tuo JSON-säännöt Jira Automationiin
3. Luo GitHub webhook (`Settings → Webhooks`) osoitteeseen jonka Jira tarjoaa
4. Testaa: luo GitHub issue → tarkista että Jira-issue syntyy

## Migraatio (vanhat issuet)

Käynnistä `Actions → Migrate GitHub Issues to Jira → Run workflow`.
Sama workflow toimii seuraavaan projektiin vaihtamalla `project_key`-parametri. Migraatioskripti ([`migrate-history.py`](migrate-history.py)) lisää automaattisesti `Git:`-etuliitteen tiketteihin.

---

## 🛠️ Toteutushistoria ja arkkitehtuuriratkaisut

Tämä repositorio toimii uutisseuranta-organisaation keskitettynä integraatiohallintana. Kehityskaaren aikana toteutettiin seuraavat arkkitehtuuriratkaisut:

### 1. Kaksisuuntainen otsikkosynkronointi & silmukkaesto
*   Otsikkosynkronointi on täysin kaksisuuntainen ja perustuu etuliitteisiin **`Git:`** ja **`Jira:`** (ilman hakasulkeita).
*   Alkuperäinen luontipaikka määrittää tiketin master-järjestelmän: jos tiketti luodaan GitHubissa, se saa Jiraan etuliitteen `Git:`. Jira Automation tunnistaa tämän ja skippaa synkronoinnin takaisin GitHubiin, estäen ikuiset päivityssilmukat ilman viiveitä tai monimutkaista aritmetiikkaa (L-002).

### 2. Automaattinen validointi (Test Coverage 100 %)
*   Kaikki JSON-muotoiset säännöt (`saanto-*.json`) validoidaan automaattisesti jokaisessa PR- ja CI-ajossa Python-testiohjelmalla [`test-rules.py`](test-rules.py).
*   Testit tarkistavat JSON-syntaksin, custom-kenttien käytön (`customfield_10071`–`10073`), etuliitteiden oikeellisuuden sekä varmistavat, ettei säännöissä ole kiellettyjä label-poistoja (L-006).

### 3. Keskitetty deployment-automaatio
*   [**`deploy-integration.yml`**](.github/workflows/deploy-integration.yml) synkronoi ja pushaa `jira-webhook-relay.yml` -välitystiedoston automaattisesti organisaation muihin repositorioihin:
    *   `uutisseuranta.github.io`
    *   `patterns`
    *   `bq-activitystreams`
    *   `skills`
    *   `ops` (Uusi valvonta- ja orkestrointirepo)
*   Tietoturva on varmistettu `insteadOf` URL-uudelleenkirjoituksella, jotta tokenit eivät pääse vuotamaan Actions-virhelokeihin.

### 4. Tietoturvapolitiikka ja koodivastuut (Issue #16)
*   **Haaransuojaukset (Branch Protection)**: `main`-haara on suojattu kaikissa julkisissa repoissa. Se vaatii vähintään 1 hyväksytyn katselmoinnin ja Code Owner -hyväksynnän.
*   **CODEOWNERS**: Koodivastuut on määritelty ja jaettu repositorion juuressa `@jaakkokorhonen` vastuulle.

Lisätietoja: [TECHNICAL_DESIGN.md](TECHNICAL_DESIGN.md) ja [DECISION_LOG.csv](DECISION_LOG.csv)
