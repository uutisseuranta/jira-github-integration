# GITHUB_JIRA_SYNC.md

## Mikä tämä on

`github_jira_sync.py` on Python-skripti, joka hakee avoimet GitHub-issuet REST
API:n kautta ja synkronoi ne Jiran work itemeihin. Skripti **täydentää**
Jira Automation -floweja — se ei korvaa niitä. Automation hoitaa
reaaliaikaiset tapahtumat (luonti, kommentti, status-muutos), skripti hoitaa
bulk-synkronoinnin ja historiallisen datan siirron.

---

## Arkkitehtuurinen rooli

| Tilanne | Käytä tätä |
|---|---|
| Uusi GitHub-issue luodaan → Jiraan automaattisesti | **Jira Automation** (saanto-01) |
| Olemassa olevan issuen status muuttuu | **Jira Automation** |
| Haluat siirtää kymmeniä vanhoja issueita kerralla | **Tämä skripti** |
| Alkusetupin yhteydessä tai uuden repon lisäämisen jälkeen | **Tämä skripti** |
| Cron-pohjainen yöllinen täsmäytys | **Tämä skripti** |

Arkkitehtuurilinja noudattaa `TECHNICAL_DESIGN.md`:n periaatteita.

---

## Asennusohjeet

### Riippuvuudet

```bash
pip install requests
```

> **Huom:** Skripti käyttää ainoastaan Python-standardikirjastoja sekä
> `requests`-kirjastoa. Muita ulkoisia riippuvuuksia ei ole.

### Ympäristömuuttujat

| Muuttuja | Pakollinen | Kuvaus | Esimerkki |
|---|---|---|---|
| `GITHUB_TOKEN` | ✅ | GitHub Personal Access Token (repo scope) | `ghp_xxxx` |
| `GITHUB_OWNER` | ✅ | GitHub-organisaatio tai käyttäjä | `uutisseuranta` |
| `GITHUB_REPOS` | ✅ | Pilkulla erotettu lista repoista | `uutisseuranta.github.io,patterns` |
| `JIRA_BASE_URL` | ✅ | Jira-instanssin URL (ei trailing slash) | `https://uutisseuranta.atlassian.net` |
| `JIRA_EMAIL` | ✅ | Jira-käyttäjän sähköposti | `admin@example.com` |
| `JIRA_API_TOKEN` | ✅ | Jira API token | `ATATTxxx` |
| `JIRA_PROJECT_KEY` | ✅ | Jira-projektin avain | `US` |
| `DRY_RUN` | ➖ | `true` = vain tulostus, `false` = kirjoittaa Jiraan. **Oletus: `true`** | `false` |

Aseta muuttujat ennen ajoa, esimerkiksi `.env`-tiedostona tai shellin `export`-komennoilla.

---

## Käyttö

### 1. Dry-run (suositeltava ensimmäiseksi)

```bash
export GITHUB_TOKEN="ghp_xxxx"
export GITHUB_OWNER="uutisseuranta"
export GITHUB_REPOS="uutisseuranta.github.io,patterns,bq-activitystreams"
export JIRA_BASE_URL="https://uutisseuranta.atlassian.net"
export JIRA_EMAIL="admin@example.com"
export JIRA_API_TOKEN="ATATTxxx"
export JIRA_PROJECT_KEY="US"
export DRY_RUN="true"  # oletusarvo, voi jättää pois

python github_jira_sync.py
```

Tarkista lokista, mitä skripti tekisi. Kun tulos näyttää oikealta:

### 2. Todellinen ajo

```bash
export DRY_RUN="false"
python github_jira_sync.py
```

### 3. Cron-ajo (esimerkki)

```cron
0 3 * * * cd /app && DRY_RUN=false python github_jira_sync.py >> /var/log/jira_sync.log 2>&1
```

---

## Kenttämappaus GitHub → Jira

| GitHub-kenttä | Jira-kenttä | Huomio |
|---|---|---|
| `title` | `summary` | Etuliite `"Git: "` silmukan estoksi (L-002) |
| `body` | `description` | Markdown-muoto säilyy (Atlassian Document Format) |
| `labels[].name` | `labels` | Lista label-nimistä sellaisenaan |
| Repo nimi (string) | `customfield_10071` | source_repo — idempotenttisuuden avain |
| `number` (int) | `customfield_10072` | github_number — idempotenttisuuden avain |
| `html_url` | `customfield_10073` | github_url — suora linkki issueen |

---

## Issuetype-logiikka

Skripti päättelee Jiran work item -tyypin GitHub-labeleista:

| GitHub-label | Jira issuetype |
|---|---|
| `epic` | Epic |
| `feat` tai `enhancement` | Story |
| `bug` | Bug |
| Ei em. labeleja | Task |

Jos issuella on useita labeleja, prioriteetti on: `epic` > `feat`/`enhancement` > `bug` > `Task`.

---

## Silmukan esto (L-002)

Jira Automation -sääntö **saanto-13** (`jira-summary-changed`) kirjoittaa
Jiran work itemin muutokset takaisin GitHubiin. Jos GitHub-issuen otsikko
`title` siirrettäisiin suoraan Jiran `summary`-kenttään, saanto-13 tulkitsisi
myöhemmän synkronoinnin muutokseksi ja päivittäisi GitHub-issuen — josta
taas seuraa uusi päivitys Jiraan, ja syntyy silmukka.

**Ratkaisu:** Kaikki skriptin kirjoittamat `summary`-arvot saavat etuliitteen
`"Git: "`. Saanto-13 on konfiguroitu ohittamaan work itemit, joiden summary
alkaa `"Git: "`. Älä poista tai muuta tätä etuliitettä.

> Päätös kirjattu `DECISION_LOG.csv`:ssä kohdassa **L-002**.

---

## Idempotenttisuus

Skripti tunnistaa jo olemassa olevat Jira work itemit kahden custom fieldin
yhdistelmällä:

- `customfield_10071` (source_repo) — repo nimi
- `customfield_10072` (github_number) — issuen numero

JQL-kysely: `project = US AND cf[10072] = {number} AND cf[10071] = "{repo}"`

Jos osuma löytyy, skripti **päivittää** (update). Jos ei löydy, skripti
**luo** (create). Skriptin voi ajaa useita kertoja turvallisesti — se ei
luo duplikaatteja.

---

## Rajoitukset

Skripti **ei** synkronoi seuraavia kenttiä Jiraan (ne ovat Jiran master-data):

- **Status** (Open/In Progress/Done) — hallitaan Jirassa ja Jira Automationilla
- **Prioriteetti** — asetetaan Jirassa manuaalisesti
- **Sprintti** — kuuluu Jira-releasesuunnitteluun
- **Assignee** — Jiran henkilömappaukset eroavat GitHubista
- **Kommentit** — yksittäisiä kommentteja ei synkronoida
- **Suljetut issuet** — skripti käsittelee vain `state=open` -issuet

---

## Vianetsintä

### `400 Bad Request` Jiraa kirjoitettaessa

Customfield-numerot (`10071`, `10072`, `10073`) eivät täsmää Jira-instanssiin.
Tarkista oikeat numerot:

```bash
curl -u $JIRA_EMAIL:$JIRA_API_TOKEN \
  "$JIRA_BASE_URL/rest/api/3/field" | python -m json.tool | grep -A2 '"source_repo\|github_number\|github_url"'
```

Päivitä skriptin `CF_*`-vakiot vastaamaan löydettyjä kenttiä.

### `401 Unauthorized` GitHub-haussa

`GITHUB_TOKEN` puuttuu tai on vanhentunut. Luo uusi token osoitteessa
[github.com/settings/tokens](https://github.com/settings/tokens) ja varmista
`repo`-scope.

### `401 Unauthorized` Jira-haussa

`JIRA_EMAIL` tai `JIRA_API_TOKEN` on väärä. Varmista, että email vastaa
Atlassian-tiliä ja token on luotu osoitteessa
[id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens).

### JQL-kysely ei löydä issueita vaikka ne ovat Jirassa

Customfieldien arvot eivät välttämättä ole indeksoituneet. Odota muutama
minuutti tai suorita haku ensin Jiran käyttöliittymässä aktivoidaksesi indeksin.

### Dry-run näyttää "Would create" jokaiselle issuella

Normaalia, jos Jirassa ei vielä ole yhteensopivilla custom fieldeillä
varustettuja work itemeja. Aja skripti `DRY_RUN=false` ja tarkista tulos.
