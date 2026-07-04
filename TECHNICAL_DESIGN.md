# Tekninen suunnittelu — GitHub ↔ Jira -integraatio

> Siirretty [JIRA.md](https://github.com/uutisseuranta/uutisseuranta.github.io/blob/main/JIRA.md):stä 2026-07-04  
> Atlassian Cloud Automation -viitteet: https://support.atlassian.com/cloud-automation/resources/  
> Jira Cloud API -viitteet: https://developer.atlassian.com/cloud/jira/platform/rest/v3/

---

## Arkkitehtuurilinja

**Malli: Jira ensisijaisena, GitHub masterina.**

- **GitHub** on sisällön master: otsikko, body, labelit, milestone, PR:t, source-identiteetti.
- **Jira** on työnhallinnan master: status, prioriteetti, assignee, sprint, workflow.
- Kaikki kolme repositoriota (`uutisseuranta.github.io`, `patterns`, `bq-activitystreams`) ovat lähteitä.
- Sub-issueita ei käytetä. Ristikkäisviittaukset toteutetaan Jira issue link -tyypeillä.
- Natiivi **GitHub for Jira** -app hoitaa kehityspaneelin (branchit, commitit, PR:t, buildit, deploymentit) — sitä ei korvata.
- Issue-synkronointi rakennetaan **Atlassian Automation** -flowien avulla (12 sääntöä).

### GitHub for Jira -integraation linkkityypit

Kun GitHub for Jira -app on asennettu, Jiran issue-näkymässä Development-paneelissa näkyvät natiivit linkit. Nämä ovat Atlassian-puolen vakionimiä:

| Objekti | Atlassian UI -nimi | Mitä sisältää |
|---|---|---|
| GitHub-issue | **GitHub Issue** | Linkitetty GitHub-issue (numero, tila, otsikko) |
| GitHub PR | **GitHub Pull Request** | PR:n tila, branch, reviewit, CI |
| GitHub repo | **Repository** | Repon nimi, URL, connected status |
| Jira → GitHub -linkki | **Link to GitHub** | Manuaalinen tai automaatio-luotu linkki Jira-tiketiltä GitHub-issueen |

> **Huom:** "Link to GitHub" -toiminto löytyy Jira-tiketin **Link**-napista → **Link to GitHub**.  
> Se luo Jira issue link -tyyppisen viittauksen eikä korvaa Development-paneelin natiivia dataa.

### Tekniset arkkitehtuurivalinnat

GitHub org-webhook ei tue custom HTTP-headereita, mutta Jira Automation
vaatii tokenin `X-Automation-Webhook-Token` -headerissa. Siksi käytetään
**GitHub Actions -workflowta** välittäjänä:

```
GitHub Issue event
      ↓
GitHub Actions (jira-webhook-relay.yml)
      ↓  POST + X-Automation-Webhook-Token header
Jira Automation Incoming Webhook trigger
      ↓
Create work item / Transition work item / Comment on work item
```

> **Relay-workflow sijaitsee repossa polulla:**
> ```
> .github/workflows/jira-webhook-relay.yml
> ```

---

## Terminologia (viralliset Atlassian-nimet, 2026)

> **Huom 2026:** Atlassian uudisti terminologiaa vuoden 2025 lopulla.  
> Vanha "rule" = **Flow**. Vanha "issue" = **Work item**. Vanha "project" = **Space**.

| Vanhentunut nimi | Atlassianin virallinen nimi (2026) | Huomio |
|---|---|---|
| Rule / sääntö | **Flow** | Koko automatio-kokonaisuus (trigger + conditions + actions) |
| Issue | **Work item** | Jiran tiketti |
| Project | **Space** | Jiran projekti |
| Transition | **Transition work item** | Action joka siirtää work itemin tilasta toiseen |
| Issue fields condition | **Issue fields condition** | Ei muuttunut; tarkistaa work itemin kentät |
| Lookup issues | **Lookup work items** | Hakee work itemeja JQL-kyselyllä → `{{lookupIssues}}` |
| Edit issue | **Edit work item** | Muokkaa work itemin kenttiä |
| Create issue | **Create work item** | Luo uuden work itemin |
| Comment on issue | **Comment on work item** | Lisää kommentin |
| Send web request | **Send web request** | HTTP-toiminto ulkoiseen järjestelmään; ei uudelleennimetty |
| GitHub for Atlassian | **GitHub for Jira** | Atlassian Marketplace -app (virallinen nykynimi) |
| GitHub issue link | **GitHub Issue** / **Link to GitHub** | Jiran Development-paneelin natiivilinkit GitHubiin |

---

## Tietomalli

### Jira custom -kentät (varmistettu MCP:llä 2026-07-03)

Custom kenttien **display nimet** varmistettu suoraan Jira Cloud -instanssista
(`uutisseuranta.atlassian.net`, projekti `US`):

| customfield ID | Display name (Jirassa) | JQL-syntaksi | Tyyppi | Arvoesimerkki |
|---|---|---|---|---|
| `customfield_10071` | `source_repo` | `cf[10071]` | Text (Single line) | `uutisseuranta.github.io` |
| `customfield_10072` | `github_issue_number` | `cf[10072]` | Number | `45` |
| `customfield_10073` | `github_url` | `cf[10073]` | URL | `https://github.com/uutisseuranta/uutisseuranta.github.io/issues/45` |

> **Idempotenttius-JQL:** `project = US AND cf[10072] = {{webhookData.issue.number}} AND cf[10071] = "{{webhookData.repository.name}}"`  
> **Smart value -syntaksi:** `{{issue.customfield_10071}}` — käytä kenttä-ID:tä, ei display nimeä.

### Kenttäkohtainen synkronointi

| # | Kenttä | GitHub-vastine | Jira-vastine | Auktoriteetti | GitHub → Jira | Jira → GitHub | Konfliktiresoluutio |
|---|---|---|---|---|---|---|---|
| 1 | Otsikko | `title` | `summary` | GitHub | ✅ | ⛔ (D-002) | Yksisuuntainen: GitHub → Jira |
| 2 | Kuvaus | `body` (Markdown) | `description` (plain text) | GitHub | ✅ | ✅ | GitHub voittaa; Markdown säilyy plain textinä Jirassa |
| 3 | Tila | `state` (open/closed) | `status` (workflow) | Jira | ✅ open→To Do, closed→Done | ✅ Done→close, muut→open+label | Jira-status on master |
| 4 | Labelit | `labels[]` | `labels[]` | GitHub | ✅ luo uudet Jiraan | ✅ unioni molempiin | Ei ylikirjoiteta; lisätään puuttuvat |
| 5 | Prioriteetti | label `priority:*` | `priority` | Jira | ✅ label→Jira priority | ✅ Jira priority→GitHub label | Jira voittaa |
| 6 | Milestone | `milestone.title` + `due_on` | `fixVersions` | GitHub | ✅ | ✅ luo tarvittaessa | Nimet identtiset; GitHub on master |
| 7 | Sprint / Iteration | label `sprint:N` | `sprint` (Scrum) | Jira | ⛔ ei lähdettä | ✅ Jira sprint→GitHub label | Jira on ainoa auktoriteetti |
| 8 | Pull Request | PR-numero, branch, status | `development`-kenttä | GitHub | ✅ natiivi GitHub for Jira | ⛔ | Natiivi kattaa |
| 9 | Kommentit | `comments[]` | `comments[]` | Molemmat | ✅ `[GitHub] @user:` -etuliite | ✅ `[Jira] user:` -etuliite | Ei koskaan ylikirjoiteta; aina uusi kommentti |
| 10 | Sulkemisen syy | `state_reason` | `resolution` | Jira | ✅ | ✅ Fixed/Won't Do/Duplicate | Jira voittaa |
| 11 | Source repo | repo-nimi | `customfield_10071` (`source_repo`) | GitHub (vain luku) | ✅ kirjoitetaan luonnissa | ⛔ | Ei muutu koskaan |
| 12 | Source issue # | `number` | `customfield_10072` (`github_issue_number`) | GitHub (vain luku) | ✅ kirjoitetaan luonnissa | ⛔ | Ei muutu koskaan |
| 13 | Source URL | `html_url` | `customfield_10073` (`github_url`) | GitHub (vain luku) | ✅ kirjoitetaan luonnissa | ⛔ | Ei muutu koskaan |
| 14 | Luontiaika | `created_at` | `created` | GitHub | ✅ asetetaan kerran | ⛔ | Ei muutu |
| 15 | Päivitysaika | `updated_at` | `updated` | Molemmat | ✅ käytetään konfliktin ratkaisuun | ✅ | Uudempi voittaa |

> **Huom:** Assignee-synkronointi (aiempi rivi 4) on poistettu — katso [issue #2](https://github.com/uutisseuranta/jira-github-integration/issues/2).

### Issuetype-mapaus

| GitHub-label | Jira work item type |
|---|---|
| `feat`, `enhancement` | Story |
| `bug` | Bug |
| `epic` | Epic |
| `arch`, `sec` | Task |
| `chore`, `docs`, `refactor`, `test` | Task |
| ei labelia | Task (oletus) |

> **Huom:** Päivitetty — katso [issue #5](https://github.com/uutisseuranta/jira-github-integration/issues/5).

---

## Flowien rakenne

Jira Automation -flow koostuu kolmesta osasta järjestyksessä:

```
TRIGGER  →  [CONDITIONS]  →  ACTIONS
```

1. **Trigger** — Käynnistää flowin. Kuuntelee tapahtumia Jirassa tai ulkoisista lähteistä.
2. **Condition** (valinnainen) — Suodatin. Jos ehto ei täyty, flow pysähtyy.
3. **Action** — Tekee jotain (muuttaa kenttiä, lähettää HTTP-pyynnön, siirtää tilan jne.).

### Silmukan esto (kaikki säännöt)

Kommenttisäännöissä tarkistetaan etuliite: ei prosessoida kommenttia joka alkaa `[GitHub]` tai `[Jira]`.

> Katso tarkemmin [issue #1](https://github.com/uutisseuranta/jira-github-integration/issues/1).

---

## GitHub → Jira -flowledet (Säännöt 1–8)

### Sääntö 1: GitHub issue opened → Luo Jira work item ✅

**Tila:** VALMIS — testattu, work item US-7 luotu onnistuneesti 3.7.2026

#### Trigger

| Asetus | Arvo |
|--------|------|
| Tyyppi | **Incoming webhook** |
| Work item criteria | **No work items from the webhook** |

#### Condition: Idempotenttius

```
Action: Lookup work items
  → JQL: project = US AND cf[10072] = {{webhookData.issue.number}}
         AND cf[10071] = "{{webhookData.repository.name}}"

Condition: {{smart values}} condition
  → First value:  {{lookupIssues.size}}
  → Condition:    equals
  → Second value: 0
```

#### Action: Create work item

| Kenttä | Arvo |
|--------|------|
| Space | `Uutisseuranta (US)` |
| Work item type | `Story` |
| Summary | `{{webhookData.issue.title}}` |
| Description | `{{webhookData.issue.body}}` |
| `customfield_10071` | `{{webhookData.repository.name}}` |
| `customfield_10072` | `{{webhookData.issue.number}}` |
| `customfield_10073` | `{{webhookData.issue.html_url}}` |

---

### Sääntö 2: GitHub issue edited → Päivitä Jira work item

**Tila:** JSON v2 valmis, testaamatta

```
Trigger: Incoming webhook
  → webhookData.action == "edited"

Condition: {{smart values}} condition
  → {{webhookData.changes.title}} OR {{webhookData.changes.body}} exists

Action: Lookup work items
  → JQL: project = US AND cf[10072] = {{webhookData.issue.number}}
         AND cf[10071] = "{{webhookData.repository.name}}"

Condition: {{lookupIssues.size}} greater than 0

Action: Edit work item
  → Work item: {{lookupIssues.first.key}}
  → Summary:     {{webhookData.issue.title}}
  → Description: {{webhookData.issue.body}}
```

---

### Sääntö 3: GitHub issue closed → Transition work item → Done

**Tila:** JSON v2 valmis, testaamatta

```
Trigger: Incoming webhook
  → webhookData.action == "closed"

Action: Lookup work items
  → JQL: project = US AND cf[10072] = {{webhookData.issue.number}}
         AND cf[10071] = "{{webhookData.repository.name}}"

Condition: {{lookupIssues.size}} greater than 0

Action: Transition work item
  → Work item: {{lookupIssues.first.key}}
  → To status: Done

Action: Edit work item (resolution)
  → IF {{webhookData.issue.state_reason}} == "completed"   → "Fixed"
  → IF {{webhookData.issue.state_reason}} == "not_planned" → "Won't Do"
  → IF {{webhookData.issue.state_reason}} == "duplicate"   → "Duplicate"
```

> Transition-nimet täsmättävä **Project Settings → Workflows**.  
> US-statukset: `To Do` (10000), `In Progress` (10001), `Done` (10002).

---

### Sääntö 4: GitHub issue reopened → Transition work item → To Do

**Tila:** JSON v2 valmis, testaamatta

```
Trigger: Incoming webhook
  → webhookData.action == "reopened"

Action: Lookup work items
  → JQL: project = US AND cf[10072] = {{webhookData.issue.number}}
         AND cf[10071] = "{{webhookData.repository.name}}"

Condition: {{lookupIssues.size}} greater than 0

Action: Edit work item  (tyhjennä resolution ENNEN transitiota)
  → Field: Resolution → (tyhjä)

Action: Transition work item
  → To status: To Do
```

---

### Sääntö 5: GitHub issue labeled/unlabeled → Edit work item labels

**Tila:** JSON v2 valmis, testattava

```
Trigger: Incoming webhook
  → webhookData.action == "labeled" TAI "unlabeled"

Action: Lookup work items
  → JQL: project = US AND cf[10072] = {{webhookData.issue.number}}
         AND cf[10071] = "{{webhookData.repository.name}}"

Condition: {{lookupIssues.size}} greater than 0

Action: Edit work item
  → Field: Labels
  → IF action == "labeled":   Operation: Add,    Value: {{webhookData.label.name}}
  → IF action == "unlabeled": Operation: Remove, Value: {{webhookData.label.name}}

IF {{webhookData.label.name}} alkaa "priority:":
  Action: Edit work item
    → Field: Priority
    → priority:high    → High
    → priority:medium  → Medium
    → priority:low     → Low
    → priority:lowest  → Lowest
```

---

### Sääntö 6: GitHub issue assigned/unassigned → (poistettu)

> **Poistettu** — assignee-synkronointi ei ole käytössä. Katso [issue #2](https://github.com/uutisseuranta/jira-github-integration/issues/2).

---

### Sääntö 7: GitHub issue milestoned/demilestoned → Päivitä fixVersions

**Tila:** Suunniteltu, ei toteutettu

```
Trigger: Incoming webhook
  → webhookData.action == "milestoned" TAI "demilestoned"

Action: Lookup work items
  → JQL: project = US AND cf[10072] = {{webhookData.issue.number}}
         AND cf[10071] = "{{webhookData.repository.name}}"

Action: Edit work item
  → fixVersions: {{webhookData.issue.milestone.title}}
  Jos versiota ei ole: HTTP POST /rest/api/3/version
    body: {
      "name":        "{{webhookData.issue.milestone.title}}",
      "releaseDate": "{{webhookData.issue.milestone.due_on}}",
      "projectId":   "{{project.id}}"
    }
```

---

### Sääntö 8: GitHub issue comment → Comment on work item

**Tila:** JSON v2 valmis, testaamatta

```
Trigger: Incoming webhook
  → webhookData.action == "created"  (issue_comment event)

Action: Lookup work items
  → JQL: project = US AND cf[10072] = {{webhookData.issue.number}}
         AND cf[10071] = "{{webhookData.repository.name}}"

Condition: {{lookupIssues.size}} greater than 0

Condition: {{webhookData.comment.body}} does not start with "[Jira]"

Action: Comment on work item
  → "[GitHub] @{{webhookData.comment.user.login}}: {{webhookData.comment.body}}"
```

---

## Jira → GitHub -flowledet (Säännöt 9–15)

URL-pohja kaikkiin GitHub API -kutsuihin:

```
https://api.github.com/repos/uutisseuranta/{{issue.customfield_10071}}/issues/{{issue.customfield_10072}}
```

> Käytä `{{issue.customfield_10071}}` ja `{{issue.customfield_10072}}` — **ei** display-nimiä.

Autentikointi kaikissa HTTP-toiminnoissa:
```
Authorization: Bearer {{secrets.GITHUB_TOKEN}}
Content-Type: application/json
```

---

### Sääntö 9: Jira status muuttuu → Päivitä GitHub issue state

**Tila:** Suunniteltu (TODO)

```
Trigger: Work item transitioned

Condition: customfield_10072 is not empty

Action: Send web request
  → Method: PATCH
  → URL: [URL-pohja]
  → Body (jos Done):  {"state": "closed", "state_reason": "completed"}
  → Body (muut):      {"state": "open"}

Action: Send web request  (lisää status-label)
  → Method: POST
  → URL: .../labels
  → Body: {"labels": ["status:{{issue.status.name | toLower}}"]}
```

> **Huom:** Label-poistologiikka poistettu — katso [issue #3](https://github.com/uutisseuranta/jira-github-integration/issues/3).

---

### Sääntö 10: Jira assignee muuttuu → (poistettu)

> **Poistettu** — katso [issue #2](https://github.com/uutisseuranta/jira-github-integration/issues/2).

---

### Sääntö 11: Jira prioriteetti muuttuu → Päivitä GitHub label

**Tila:** Suunniteltu (TODO)

```
Trigger: Field value changed → Field: Priority

Condition: customfield_10072 is not empty

Action: Send web request  (lisää uusi priority-label)
  → Method: POST
  → URL: .../labels
  → Body: {"labels": ["priority:{{issue.priority.name | toLower}}"]}
```

> **Huom:** Label-poistologiikka poistettu — katso [issue #3](https://github.com/uutisseuranta/jira-github-integration/issues/3).

---

### Sääntö 12: Jira sprint → GitHub label

**Tila:** Suunniteltu (TODO)

```
Trigger: Field value changed → Field: Sprint

Condition: customfield_10072 is not empty

Action: Send web request  (lisää sprint-label)
  → Method: POST
  → URL: .../labels
  → Body: {"labels": ["sprint:{{issue.sprint.name}}"]}
```

> **Huom:** Label-poistologiikka poistettu — katso [issue #3](https://github.com/uutisseuranta/jira-github-integration/issues/3).

---

### Sääntö 13: Jira summary muuttuu → GitHub otsikko (poistettu)

> **Poistettu** — Free-tierillä silmukkaesto ei ole teknisesti toteutettavissa (D-002).  
> Otsikkosynkronointi on yksisuuntainen: GitHub → Jira.  
> Katso [issue #1](https://github.com/uutisseuranta/jira-github-integration/issues/1) ja [issue #7](https://github.com/uutisseuranta/jira-github-integration/issues/7).

---

### Sääntö 14: Uusi Jira kommentti → Lisää GitHub issue comment

**Tila:** Suunniteltu (TODO)

```
Trigger: Comment added

Condition: customfield_10072 is not empty

Condition: {{comment.body}} does not start with "[GitHub]"

Action: Send web request
  → Method: POST
  → URL: .../comments
  → Body: {"body": "[Jira] {{comment.author.displayName}}: {{comment.body}}"}
```

---

### Sääntö 15: fixVersions muuttuu → Päivitä GitHub milestone

**Tila:** Suunniteltu (TODO)

```
Trigger: Field value changed → Field: Fix versions

Condition: customfield_10072 is not empty

Action: Send web request  (hae milestone-numero)
  → Method: GET
  → URL: https://api.github.com/repos/uutisseuranta/{{issue.customfield_10071}}/milestones

Action: Send web request  (päivitä tai luo)
  → Jos milestone löytyy nimellä {{issue.fixVersions[0].name}}:
      Method: PATCH, body: {"milestone": <numero>}
  → Jos ei löydy:
      Method: POST .../milestones, body: {"title": "{{issue.fixVersions[0].name}}"}
```

---

## GitHub Actions Workflows

### 1. Relay: `jira-webhook-relay.yml`

Välittää live GitHub-issueeventsit Jira Automation -webhookiin.

```yaml
name: Jira Webhook Relay

on:
  issues:
    types: [opened, edited, closed, reopened, labeled, unlabeled,
            milestoned, demilestoned]
  issue_comment:
    types: [created]

jobs:
  relay:
    runs-on: ubuntu-latest
    steps:
      - name: Send to Jira Automation
        env:
          JIRA_WEBHOOK_TOKEN: ${{ secrets.JIRA_WEBHOOK_TOKEN }}
          JIRA_WEBHOOK_URL: ${{ secrets.JIRA_WEBHOOK_URL }}
        run: |
          echo '${{ toJson(github.event) }}' | \
          curl -s -X POST \
            "$JIRA_WEBHOOK_URL" \
            -H "Content-Type: application/json" \
            -H "X-Automation-Webhook-Token: $JIRA_WEBHOOK_TOKEN" \
            --data-binary @- \
            -w "\nHTTP %{http_code}\n"
```

---

## Conditions (Ehdot)

### Issue fields condition

Tarkistaa work itemin kentän arvon suoraan.

```
Condition: Issue fields condition
  → Field:      Status
  → Condition:  equals
  → Value:      Done
```

### {{smart values}} condition

Vertaa kahta smart value -arvoa keskenään.

```
Condition: {{smart values}} condition
  → First value:  {{lookupIssues.size}}
  → Condition:    greater than
  → Second value: 0
```

### If/else block

```
IF:      {{webhookData.action}} equals "closed"
           → Transition work item → Done
ELSE IF: {{webhookData.action}} equals "reopened"
           → Transition work item → To Do
```

> **Tärkeä:** Vanhentunut `jira.condition.webhook.compare` ei enää toimi JSON-importissa.  
> Korvaa aina `jira.condition.if` (If/else block) -ehdolla.

---

## Smart Values -syntaksi

Virallinen dokumentaatio: https://support.atlassian.com/cloud-automation/docs/what-are-smart-values/

| Smart value | Palauttaa |
|---|---|
| `{{webhookData.action}}` | GitHub-eventin tyyppi (`opened`, `closed`, `labeled`...) |
| `{{webhookData.issue.number}}` | GitHub issue -numero |
| `{{webhookData.issue.title}}` | GitHub issue -otsikko |
| `{{webhookData.issue.body}}` | GitHub issue -kuvaus (Markdown plain textinä) |
| `{{webhookData.issue.html_url}}` | GitHub issue -URL |
| `{{webhookData.issue.state}}` | Issue state (`open`/`closed`) |
| `{{webhookData.issue.state_reason}}` | Sulkemisen syy (`completed`, `not_planned`, `duplicate`) |
| `{{webhookData.issue.labels[*].name}}` | Kaikkien labelien nimet listana |
| `{{webhookData.issue.milestone.title}}` | Milestonen nimi |
| `{{webhookData.issue.milestone.due_on}}` | Milestonen eräpäivä (ISO 8601) |
| `{{webhookData.label.name}}` | Lisätyn/poistetun labelin nimi (labeled/unlabeled) |
| `{{webhookData.comment.body}}` | Kommentin sisältö (issue_comment) |
| `{{webhookData.comment.user.login}}` | Kommentoijan GitHub-tunnus |
| `{{webhookData.repository.name}}` | Repositorion nimi (ilman organia) |
| `{{lookupIssues}}` | Lookup work items -actionin tulos |
| `{{lookupIssues.first.key}}` | Ensimmäisen tuloksen avain (esim. `US-7`) |
| `{{lookupIssues.size}}` | Tulosten lukumäärä |
| `{{issue.key}}` | Nykyisen work itemin avain |
| `{{issue.summary}}` | Nykyisen work itemin otsikko |
| `{{issue.status.name}}` | Nykyisen tilan nimi |
| `{{issue.priority.name}}` | Prioriteetin nimi |
| `{{issue.sprint.name}}` | Aktiivisen sprintin nimi (vain Scrum) |
| `{{issue.customfield_10071}}` | `source_repo` -kentän arvo |
| `{{issue.customfield_10072}}` | `github_issue_number` -kentän arvo |
| `{{issue.customfield_10073}}` | `github_url` -kentän arvo |
| `{{issue.updated.epochMillis}}` | Viimeinen päivitysaika ms |
| `{{now.epochMillis}}` | Nykyinen aika ms |
| `{{comment.body}}` | Jira-kommentin teksti (Jira→GitHub -säännöissä) |
| `{{comment.author.displayName}}` | Jira-kommentoijan näyttönimi |

### Oletusarvo (fallback)

```
{{issue.assignee.displayName | "Ei vastuuhenkilöä"}}
```

### Listoja läpi käyminen

```
{{#lookupIssues}}
  * {{key}}: {{summary}}
{{/}}
```

### Merkkijonon muunnokset

```
{{issue.priority.name | toLower}}
{{issue.priority.name | toUpper}}
{{issue.summary | substring(0,50)}}
```

---

## Webhook-data-rakenne (`{{webhookData}}`)

```json
{
  "action": "opened",
  "issue": {
    "number": 42,
    "title": "Fix login bug",
    "body": "Description...",
    "html_url": "https://github.com/uutisseuranta/uutisseuranta.github.io/issues/42",
    "state": "open",
    "state_reason": null,
    "labels": [{"name": "bug"}],
    "milestone": {
      "title": "v1.0",
      "due_on": "2026-08-01T00:00:00Z",
      "number": 1
    },
    "user": {"login": "username"}
  },
  "comment": {
    "id": 123456,
    "body": "Comment text",
    "user": {"login": "commenter"}
  },
  "label": {"name": "bug"},
  "repository": {
    "name": "uutisseuranta.github.io",
    "full_name": "uutisseuranta/uutisseuranta.github.io"
  },
  "sender": {"login": "triggering-user"}
}
```

---

## JSON Import -huomiot

### Tunnettu vanhentunut komponentti

```text
IllegalStateException: Component for type ComponentTypeKey{
  component=CONDITION, type='jira.condition.webhook.compare'
} no longer exists.
```

**Korjaus:** Korvaa `jira.condition.if` (If/else block) -ehdolla.

---

## Debuggaus

### Curl-testi manuaalisesti

```bash
curl -s -X POST \
  "${JIRA_WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -H "X-Automation-Webhook-Token: ${JIRA_WEBHOOK_TOKEN}" \
  -d '{"action":"opened","issue":{"number":999,"title":"Test","body":"Test body","html_url":"https://github.com/uutisseuranta/uutisseuranta.github.io/issues/999"},"repository":{"name":"uutisseuranta.github.io"}}' \
  -w "\nHTTP %{http_code}\n"
```

### Yleisimmät virheet

| Virhe | Syy | Korjaus |
|-------|-----|--------|
| `Missing token` (400) | Token query-parametrina eikä headerissa | Käytä `X-Automation-Webhook-Token` headeria |
| `No work items from the webhook` | Trigger-asetus väärä | Vaihda **No work items from the webhook** |
| `The project or issue type wasn't set` | Space/work item type "Copy from trigger" | Aseta kiinteät arvot dropdownista |
| `Fields ignored: customfield_10071` | Kenttä ei ole projektissa | Lisää kenttä **Project settings → Fields** |
| `Component ... no longer exists` | JSON sisältää vanhan komponenttityypin | Käytä `jira.condition.if` |
| Transition not found | Transition-nimi väärä | Tarkista **Project Settings → Workflows** |
| `{{lookupIssues}}` tyhjä | JQL ei löydä work itemejä | Tarkista `cf[10072]` ja `cf[10071]` |
| `{{issue.customfield_10071}}` tyhjä | Väärä smart value -syntaksi | Käytä kenttä-ID:tä, ei display-nimeä |
| HTTP 422 GitHub API | Assignee-login ei ole GitHub-käyttäjä | Assignee-synkronointi poistettu (issue #2) |
| Resolution estää transition (Sääntö 4) | Resolution asetettu ennen transitiota | Tyhjennä Resolution **ennen** Transition-actionia |
| `JIRA_BASE_URL` undefined | Secret puuttuu | Lisää `JIRA_BASE_URL` = `https://uutisseuranta.atlassian.net` |

### Automation-lokit

**Jira Settings → Automation → Audit log** — filter work item keylla tai ajanjaksolla.

---

## Rajoitukset ja hyväksytyt kompromissit

| Rajoitus | Päätös |
|---|---|
| Markdown → ADF-konversio | Hyväksytty: body tallennetaan Jiraan plain textinä |
| Sub-issues | Kielletty; ristikkäisviittaukset Jira issue link -tyypeillä |
| Sprint → GitHub natiivikäsite | Hyväksytty: sprint näkyy GitHubissa vain labelina `sprint:N` |
| Konfliktiresoluutio | Yksinkertainen sääntö: uudempi `updated_at` voittaa |
| Assignee-synkronointi | Poistettu — katso [issue #2](https://github.com/uutisseuranta/jira-github-integration/issues/2) |
| Otsikkosynkronointi Jira→GitHub | Poistettu — katso D-002 ja [issue #7](https://github.com/uutisseuranta/jira-github-integration/issues/7) |
| Label-akkumuloituminen | Hyväksytty — katso D-006 ja [issue #3](https://github.com/uutisseuranta/jira-github-integration/issues/3) |
| Automation-kutsumäärä | Jira Automation Free: 500 kutsua/kk |
| Historiallinen backfill | Ei toteuteta — katso D-004 |

---

## Linkit

- [Cloud Automation — resources](https://support.atlassian.com/cloud-automation/resources/)
- [Jira Automation triggers](https://support.atlassian.com/cloud-automation/docs/jira-automation-triggers/)
- [Jira Automation actions](https://support.atlassian.com/cloud-automation/docs/jira-automation-actions/)
- [Jira Automation conditions](https://support.atlassian.com/cloud-automation/docs/jira-automation-conditions/)
- [Smart values — overview](https://support.atlassian.com/cloud-automation/docs/what-are-smart-values/)
- [Smart values — issues](https://support.atlassian.com/cloud-automation/docs/smart-values-issues/)
- [Jira Cloud REST API v3](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [GitHub Issues API](https://docs.github.com/en/rest/issues/issues)
- [GitHub for Jira — Atlassian Marketplace](https://marketplace.atlassian.com/apps/1219592/github-for-jira)
