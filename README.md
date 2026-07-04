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
├── saanto-01...15-*.json      # Jira Automation -säännöt (JSON-export)
├── webhook-payload-example.json  # GitHub webhook payload -esimerkki
├── scripts/
│   └── migrate-history.py     # Migraatioskripti: GitHub Issues → Jira
├── .github/workflows/
│   └── migrate-history.yml    # GitHub Actions workflow migraatiolle
└── TECHNICAL_DESIGN.md        # Tekninen suunnittelu ja päätökset
```

## Nopea aloitus

1. Lisää secretit (katso taulukko yllä)
2. Tuo JSON-säännöt Jira Automationiin
3. Luo GitHub webhook (`Settings → Webhooks`) osoitteeseen jonka Jira tarjoaa
4. Testaa: luo GitHub issue → tarkista että Jira-issue syntyy

## Migraatio (vanhat issuet)

Käynnistä `Actions → Migrate GitHub Issues to Jira → Run workflow`.
Sama workflow toimii seuraavaan projektiin vaihtamalla `project_key`-parametri.

Lisätietoja: [TECHNICAL_DESIGN.md](TECHNICAL_DESIGN.md)
