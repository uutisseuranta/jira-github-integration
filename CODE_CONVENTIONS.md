# CODE_CONVENTIONS.md

> Tämä dokumentti on yhteinen kaikille uutisseuranta-repositorioille.
> Sama tiedosto sijaitsee jokaisen repon juuressa.
>
> **Repos:**
> - [uutisseuranta/uutisseuranta.github.io](https://github.com/uutisseuranta/uutisseuranta.github.io)
> - [uutisseuranta/patterns](https://github.com/uutisseuranta/patterns)
> - [uutisseuranta/jira-github-integration](https://github.com/uutisseuranta/jira-github-integration)
> - [uutisseuranta/bq-activitystreams](https://github.com/uutisseuranta/bq-activitystreams)
> - [uutisseuranta/skills](https://github.com/uutisseuranta/skills)

---

## Dokumentin rakenne ja soveltaminen

Tämä ohjeisto jakautuu kolmeen pääosaan:
1. **Kanoniset (yhteiset) käytännöt** (Tiedostorakenne, nimeäminen, linkit, versionhallinta, commitit) — koskevat kaikkia organisaation repositorioita.
2. **Repokohtaiset käytännöt** (Kommentointi, linttaustyökalut) — sovelletaan kunkin repon käyttämän teknologiapinon mukaan.
3. **AI-agentin käyttäytymissäännöt** — ohjeet Perplexity-agentille ja muille AI-assistenteille, jotka työskentelevät tässä repossa. Nämä säännöt ovat sitovia agentin toiminnalle samalla tavalla kuin koodikonventiot ovat sitovia ihmiskehittäjille.

Jokainen repositorio ylläpitää omaa paikallista `DESIGN_GUIDELINES.md` ja `STANDARDS.md` -ohjeistoaan, jotka kuvaavat vain kyseisen palvelun omia käyttöliittymä-, asettelu- ja teknologiapinostandardeja (katso [DECISION_LOG.csv](https://github.com/uutisseuranta/jira-github-integration/blob/main/DECISION_LOG.csv) -> G-004).

---

## 1. Kanoniset (yhteiset) käytännöt

### Tiedostorakenne

**Kaikki tiedostot sijaitsevat repositorion juuressa. Alikansioita ei käytetä.**

Sallitut poikkeukset kaikissa repoissa:

- `.github/` — GitHubin omaa infrastruktuuria varten (Actions-workflowt, issue-templatet, Dependabot-konfiguraatio jne.). `.github/` ei ole tarkoitettu repon omille tiedostoille — sinne ei sijoiteta dokumentaatiota, skriptejä, konfiguraatioita eikä muita projektin tiedostoja.
- `skill-*/` — **vain `skills`-repossa**: Perplexity-agenttiskillit hakemistorakenteella `skill-<nimi>/SKILL.md`. Muissa repoissa ei käytetä `skill-*/`-hakemistoja.

```
repo/
├── .github/               ← VAIN GitHub-infrastruktuuri (Actions, issue-templatet)
│   └── workflows/
│       └── *.yml
├── skill-<nimi>/          ← VAIN skills-repossa: Perplexity-skill-hakemistot
│   └── SKILL.md
├── skill-(käyttötarkoitus).yml  ← MML/ops-konfiguraatiot, juuressa (kaikki repot)
├── SOPIMUSDOKUMENTTI.md   ← SCREAMING_SNAKE_CASE-dokumentit juuressa
├── tiedosto.ext           ← muu kebab-case-lähdekoodisto juuressa
└── ...
```

Perustelu (katso [DECISION_LOG.csv](https://github.com/uutisseuranta/jira-github-integration/blob/main/DECISION_LOG.csv) -> G-001): Projekteissa on vähän tiedostoja. Hakemistorakenne ei tuo lisäarvoa — se lisää navigaatiokulua ilman hyötyä. Kaikki tiedostot löytyvät yhdestä paikasta. `skill-*/`-poikkeus on skills-repokohtainen ja perusteltu: Perplexity-skillit ovat itsenäisiä dokumentaatioyksikköjä, jotka tarvitsevat oman hakemiston `load_skill`-mekanismin vuoksi.

---

## Tiedostojen nimeäminen

### Sopimusdokumentit — `SCREAMING_SNAKE_CASE.md`

Kaikki normatiiviset sopimusdokumentit nimetään `SCREAMING_SNAKE_CASE`-muodossa:

```
TECHNICAL_DESIGN.md
DECISION_LOG.csv
CODE_CONVENTIONS.md
STANDARDS.md
DESIGN_GUIDELINES.md
PATTERNS_CATALOG.md
USER_PATHS.md
```

Perustelu (katso [DECISION_LOG.csv](https://github.com/uutisseuranta/jira-github-integration/blob/main/DECISION_LOG.csv) -> G-002): Erottaa sopimukset ja normatiiviset dokumentit ops-tiedostoista ja lähdekoodista. Yhtenäinen nimeäminen kaikkien repojen välillä.

### Skill-tiedostot — kaksi formaattia

Organisaatiossa on kaksi erillisistä käyttötarkoituksesta johtuvaa skill-formaattia:

**Formaatti A — MML/ops-konfiguraatiot (kaikki repot)**

MML-skill-konfiguraatiot nimetään muodossa `skill-(käyttötarkoitus).yml` ja sijoitetaan **repositorion juureen**.

```
skill-decision-log.yml
skill-jira-sync.yml
skill-label-manager.yml
```

Nimeämissäännöt:
- Prefix `skill-` on aina läsnä — erottaa skill-tiedostot muusta konfiguraatiosta
- Käyttötarkoitusosa: `lowercase`, sanojen välissä väliviiva (`kebab-case`)
- Vain pienet kirjaimet ja väliviivoilla — ei alaviivoja, välilyöntejä eikä erikoismerkkejä
- Enintään 64 merkkiä (koko tiedostonimi)
- Formaatti: `.yml` (ei `.yaml`)

Perustelu: Claudelint-spesifikaation skill-nimikäytäntö (lowercase-with-hyphens, max 64 merkkiä) sovellettuna tähän projektiin. `skill-`-prefix tekee tiedostot tunnistettaviksi hakemistolistauksessa ilman hakemistorakennetta. Skillit ovat repokohtaisia YAML-konfiguraatioita, eivät sopimusdokumentteja — siksi ne eivät käytä `SCREAMING_SNAKE_CASE`-muotoa.

**Formaatti B — Perplexity-agenttiskillit (vain `skills`-repo)**

Perplexity-agentin `load_skill`-kutsulla ladattavat skillit sijaitsevat `skills`-repossa hakemistorakenteella `skill-<nimi>/SKILL.md`.

```
skill-code-conventions/
└── SKILL.md
skill-decision-log/
└── SKILL.md
```

Hakemiston nimi (`<nimi>`) on se tunniste, jolla skill ladataan: `load_skill(skill_names=["<nimi>"])`. Nimi noudattaa samaa `kebab-case`-käytäntöä kuin Formaatti A.

`SKILL.md` sisältää YAML front matterin ja markdown-rungon:

```markdown
---
name: <nimi>
description: Lyhyt kuvaus skillin tarkoituksesta
version: 1.0.0
---

# Skillin otsikko

Skillin sisältö markdown-muodossa.
```

Nimeämissäännöt:
- Hakemisto: `skill-<nimi>/` — `kebab-case`, prefix `skill-` pakollinen
- Tiedosto hakemiston sisällä: aina `SKILL.md` (`SCREAMING_SNAKE_CASE`, koska normatiivinen sopimusdokumentti)
- YAML front matter: `name`, `description`, `version` ovat pakollisia kenttiä
- Formaatti: `.md`

Perustelu: Perplexity-agentin `load_skill`-mekanismi tunnistaa skillit hakemistonimen perusteella. `SKILL.md`-tiedosto on sekä ihmis- että agenttiluettava dokumentaatio, joka eroaa konekäyttöisestä YAML-konfiguraatiosta (Formaatti A) — siksi eri rakenne on perusteltu.

### Lähdekooditiedostot — `kebab-case`

Kaikki muut tiedostot (HTML, CSS, JS, JSON, Bash): `kebab-case`.

```
index.html
style.css
app.js
prefs.js
profile.js
patterns.js
live-smoke-test.sh
firebase.json
jira-webhook-relay.yml
mock-article-wayback-machine.json
```

Fontit ja binäärit noudattavat samaa konventiota:
```
satoshi-regular.woff2
cabinet-grotesk-bold.woff2
```

### README ja LICENSE — standardi

`README.md` ja `LICENSE` kirjoitetaan isolla — GitHub-konventio.

---

## Cross-repo-linkit

Kaikki viittaukset toisiin repositorioihin kirjoitetaan **absoluuttisina GitHub-URL:eina**.

```markdown
<!-- ✅ Oikein -->
[TECHNICAL_DESIGN.md](https://github.com/uutisseuranta/jira-github-integration/blob/main/TECHNICAL_DESIGN.md)

<!-- ❌ Väärin -->
[TECHNICAL_DESIGN.md](../jira-github-integration/TECHNICAL_DESIGN.md)
```

Perustelu (katso [DECISION_LOG.csv](https://github.com/uutisseuranta/jira-github-integration/blob/main/DECISION_LOG.csv) -> G-002): Relatiiviset polut eivät toimi GitHubissa cross-repo-viittauksissa.

---

## Versionumerointi

Kaikki repositoriot käyttävät **SemVer**-versionumerointia muodossa `vX.Y.Z`.

```
v1.0.0   ← ensimmäinen vakaa julkaisu
v1.2.3   ← patch
v2.0.0   ← breaking change
```

Git-tagit luodaan tällä muodolla. GitHub Releases käyttää samaa tunnistetta.

| Muutos | SemVer | Kuvaus |
|--------|--------|--------|
| Bugikorjaus, dokumentaatio | `vX.Y.Z+1` | patch — ei breaking changeja |
| Uusi toiminnallisuus, taaksepäin yhteensopiva | `vX.Y+1.0` | minor |
| Breaking change, API-muutos | `vX+1.0.0` | major |

Perustelu (katso [DECISION_LOG.csv](https://github.com/uutisseuranta/jira-github-integration/blob/main/DECISION_LOG.csv) -> G-002): Yhtenäiset julkaisukäytännöt kaikkien repojen välillä.

---

## Commit-viestit

Kaikki commit-viestit noudattavat **Conventional Commits** -muotoa:

```
<type>(<scope>): <kuvaus>
```

`type`-arvot:

| type | Käyttö |
|------|--------|
| `feat` | Uusi toiminnallisuus |
| `fix` | Bugikorjaus |
| `docs` | Dokumentaatio |
| `chore` | Ylläpito, riippuvuudet, konfiguraatio |
| `refactor` | Koodirakenne ilman toiminnallista muutosta |
| `test` | Testit |
| `ci` | GitHub Actions -muutokset |

`scope` on valinnainen ja viittaa repo-nimeen tai komponenttiin:

```
feat(patterns): lisää regex-pattern uutisotsikoille
fix(jira-sync): korjaa webhook-duplikaatti
docs: päivitä CODE_CONVENTIONS versionumerointiohje
chore(deps): päivitä firebase 10.x → 11.x
ci: lisää yamllint-tarkistus workflowhin
```

Perustelu (katso [DECISION_LOG.csv](https://github.com/uutisseuranta/jira-github-integration/blob/main/DECISION_LOG.csv) -> G-003): Yhdenmukainen commit-historia mahdollistaa automaattisen CHANGELOG-generoinnin ja helpottaa `git log`-selailua. Kytkeytyy suoraan DECISION_LOG-merkintöihin.

---

## 2. Repokohtaiset käytännöt

### Koodin kommentointi

### Periaate

Kommentit selittävät **miksi**, eivät **mitä**. Koodi selittää itse mitä se tekee — hyvä kommentti kertoo päätöksen taustan tai ei-ilmeisen reunaehdon.

```js
// ❌ Turha — koodi sanoo saman
const user = getUser(); // haetaan käyttäjä

// ✅ Hyödyllinen — kertoo miksi
// Firebase palauttaa null ennen auth-tilan latautumista;
// näytetään skeleton eikä login-näkymää välttääksemme vilkkumisen
if (user === null) return renderSkeleton();
```

### JavaScript

```js
// Yksiriviset kommentit: //
// Monirivinen selitys:
// Rivi 1
// Rivi 2

// Funktiotason JSDoc vain julkisille API-funktioille:
/**
 * Palauttaa käyttäjän preferenssit tai oletukset jos ei ole tallennettu.
 * @returns {Object}
 */
export function getPrefs() { ... }
```

### CSS

```css
/* Yksiriviset: */
.component { color: var(--color-text); }

/* Osion otsikko: */
/* =============================================================
   Typografia
   ============================================================= */

/* Selitys miksi, ei mitä: */
/* clamp() estää tekstin skaalautumisen alle 12px — iOS-zoom-esto */
font-size: clamp(0.75rem, ...);
```

### HTML

```html
<!-- Yksiriviset: -->
<!-- Monirivinen:
  Tässä on käytetty aria-live koska screen reader
  ei muuten huomaa dynaamista päivitystä.
-->
```

### Bash

```bash
# Yksiriviset: #
# Skriptin yläosan kuvaus:
# live-smoke-test.sh — testaa deployatun sivuston HTTP-vastaukset
# Käyttö: ./live-smoke-test.sh https://uutisseuranta.fi
```

### YAML (GitHub Actions & muut konfiguraatiot)

```yaml
# Yksiriviset: #
# Selitä miksi step on olemassa, ei mitä se tekee:
# toJson() muuntaa GitHub event -objektin merkkijonoksi;
# curl lukee sen stdin:stä --data-binary @- välttääkseen
# shellin erikoismerkkien tulkinnan
```

### Python

```python
# Yksiriviset: #
# Funktiotason docstring julkisille funktioille — kielivalinta: suomi (päätös L-007):
def get_prefs(uid: str) -> dict:
    """Palauttaa käyttäjän preferenssit tai oletusarvot."""
    ...
```

---

## Automaattinen tarkistus

Konventioiden automaattinen tarkistus on **repokohtaista** — jokainen repo määrittelee `.github/workflows/`-hakemistossaan omat tarkistuksensa sen mukaan, mitä kieliä ja formaatteja se käyttää. Tarkistustyökalut ja konfiguraatiot eivät kuulu tähän kanoniseen dokumenttiin.

Suositeltavat työkalut repokohtaiseen harkintaan:

| Kieli / formaatti | Työkalu | Huomio |
|-------------------|---------|--------|
| JavaScript | `eslint` | `.eslintrc.json` repokohtainen |
| Bash | `shellcheck` | ei erillistä konfiguraatiota |
| YAML | `yamllint` | `.yamllint` repokohtainen |
| Markdown | `markdownlint` | `.markdownlint.json` repokohtainen |

Perustelu: Repojen kielivalikoima vaihtelee — `bq-activitystreams` tarvitsee eri tarkistukset kuin `uutisseuranta.github.io`. Pakollinen yhteinen tooling-lista vanhentuisi nopeasti ja rajoittaisi repojen kehitystä tarpeettomasti. Enforcement-periaate (konventiot tarkistetaan CI:ssä) on kuitenkin yhteinen.

---

## Päätösloki

Kaikki arkkitehtuuripäätökset kirjataan repokohtaiseen [DECISION_LOG.csv](https://github.com/uutisseuranta/jira-github-integration/blob/main/DECISION_LOG.csv) -tiedostoon.

Esimerkki uutisseuranta.github.io -repositorion päätöksistä:
```csv
id,date,title,decision,rationale,affects_issues
G-002,2026-07-04,Cross-repo links,Use absolute GitHub URLs for cross-repository links,Relative paths do not resolve correctly across different GitHub repositories,CODE_CONVENTIONS.md
G-001,2026-07-04,Flat directory structure,Keep all project files in the repository root directory with minimal exceptions (.github/ and skill-*/),Flat structures reduce navigation overhead and simplify path management in small projects,CODE_CONVENTIONS.md;DESIGN_GUIDELINES.md
```

Jira-integraation päätösloki:
[jira-github-integration / DECISION_LOG.csv](https://github.com/uutisseuranta/jira-github-integration/blob/main/DECISION_LOG.csv)

---

## Poikkeukset konventiosta

Jos tekninen syy (esim. kolmannen osapuolen kirjaston nimikonventiokonflikti tai tooling-rajoite) pakottaa poikkeamaan tästä dokumentista:

1. Kirjaa poikkeus repokohtaiseen `DECISION_LOG.csv`-tiedostoon erillisellä `D-xxx`-merkinnällä
2. Merkitse `rationale`-kenttään syy ja poikkeuksen laajuus
3. Lisää `affects_issues`-kenttään tieto siitä, mihin konventioon poikkeus kohdistuu
4. Poikkeuksella on revisiopäivä: palaa arvioimaan poikkeuksen tarpeellisuutta seuraavan major-version yhteydessä

Poikkeusta ei saa tehdä hiljaa — dokumentoimaton poikkeus on rikkomus, dokumentoitu poikkeus on tietoinen päätös.

---

## 3. AI-agentin käyttäytymissäännöt

> Tämä osio on tarkoitettu Perplexity-agentille ja muille AI-assistenteille, jotka työskentelevät tässä repossa. Säännöt ovat sitovia agentin toiminnalle — ne ohjaavat miten agentti lukee repon kontekstin, tekee päätöksiä ja kirjaa muutokset.
>
> **Miksi tässä tiedostossa?** Repon skill-konfiguraatiot (`skill-*.yml`) lataavat tämän dokumentin automaattisesti kontekstiksi. AI-spesifiset säännöt kuuluvat tänne eikä erilliseen issue-konfiguraatioon, koska tiedosto on versionhallinnassa, muutoshistoria näkyy, ja se on sekä ihmis- että agenttiluettava.

---

### Ennen muutosten tekemistä — lukujärjestys

Agentti lukee aina seuraavat tiedostot **ennen kuin tekee yhtään muutosta**:

1. [`DECISION_LOG.csv`](https://github.com/uutisseuranta/jira-github-integration/blob/main/DECISION_LOG.csv) — mitä päätöksiä on jo tehty; estää vanhojen päätösten uudelleenkysymisen
2. [`TECHNICAL_DESIGN.md`](https://github.com/uutisseuranta/jira-github-integration/blob/main/TECHNICAL_DESIGN.md) — arkkitehtuurin rajaukset ja tekninen konteksti
3. [`CODE_CONVENTIONS.md`](https://github.com/uutisseuranta/jira-github-integration/blob/main/CODE_CONVENTIONS.md) — tämä tiedosto
4. Avoimet issuet (`gh issue list --state open`) — mitä työtä on kesken
5. Relevantti lähdekoodi (sääntötiedostot, testit) — ennen kuin kommentoi tai muuttaa

Jos agentti ei ole lukenut näitä, sen suositukset voivat olla ristiriidassa jo tehtyjen päätösten kanssa.

---

### Tiedostorakenne (AI-spesifinen)

- **Älä koskaan luo alikansioita.** Kaikki tiedostot menevät repositorion juureen. Jos käyttäjä pyytää luomaan tiedoston polkuun `docs/foo.md` tai `scripts/bar.py`, luo se juureen (`foo.md`, `bar.py`) ja kerro mitä teit.
- **Tarkista tiedostonimi ennen luomista**: `kebab-case` vai `SCREAMING_SNAKE_CASE`? Katso nimeämistaulukko luvusta 1.
- **Älä luo tiedostoa `.github/`-hakemistoon** muuhun kuin GitHub Actions -workflowhin tai issue-templateihin.

---

### Päätösloki (AI-spesifinen)

- **Kirjaa päätös ennen toimenpidettä** — ei jälkikäteen. Jos agentti tekee arkkitehtuurivalinnan (esim. valitsee toteutustavan tai poistaa ominaisuuden), merkintä `DECISION_LOG.csv`:hen tehdään ensin.
- Formaatti on täsmälleen: `id,date,title,decision,rationale,affects_issues`
- `id` noudattaa olemassa olevaa juoksevaa numerointia (G-xxx globaalit, L-xxx lokaaliset, D-xxx poikkeukset). Katso suurin olemassa oleva numero ennen kuin lisäät uuden.
- Älä keksi päätös-ID:tä ilman tarkistusta — se voi törmätä olemassa olevaan.

---

### Issue-käytännöt (AI-spesifinen)

- **Ennen uuden issuen avaamista**: tarkista onko vastaava jo olemassa (`gh issue list --state all --search "<avainsanat>"`). Duplikaatti-issuet haittaavat seurantaa.
- **Issue-rakenne**: jokaisessa issuessa tulee olla: Ongelma / Konteksti, Ratkaisu / Ehdotus, Acceptance criteria (tarkistuslistamuodossa), Business-arvo (yhden virkkeen kuvaus mitä käyttäjä tai kehittäjä hyötyy).
- **Business-arvo on pakollinen kenttä** — "Miksi tämä muutos on tärkeä?" tulee olla vastattuna issuen rungossa.
- **Kirjallisuusviitteet ovat suositeltavia** kun issue liittyy integraatiomalleihin, testausstrategiaan tai arkkitehtuuriin (esim. Hohpe & Woolf *Enterprise Integration Patterns*, Meszaros *xUnit Test Patterns*).
- **Älä sulje issueta** jota käytetään pysyvänä konfiguraatiotiedostona (esim. MML-skill-issuet). Tarkista issue #13 —se on tarkoitettu pysymään auki. **Huomio**: Issue #13:n sisältö on nyt siirretty tähän tiedostoon. Issue #13 voidaan sulkea kun tämä dokumentti on käytössä.

---

### Koodikommentointi (AI-spesifinen)

- **Noudattaa luvun 2 periaatteita**: kommentit selittävät miksi, eivät mitä.
- **Docstringien kieli**: suomi (päätös L-007). Moduulitason docstringit, luokkien docstringit ja metodien docstringit kirjoitetaan suomeksi.
- **Älä lisää kommenttia joka toistaa koodin** — se on kohinaa, ei dokumentaatiota.
- **Lisää kommentti kun**: käytetään ei-ilmeistä kiertotapaa, viitataan ulkoiseen päätökseen (esim. `# päätös L-006`), tai reunaehto ei käy ilmi koodista.
- **Testikoodissa**: `EXPECTED_RULE_COUNT`-muuttujan kaltaiset vakiot kommentoidaan aina viittauksella `DECISION_LOG.csv`:hen, jotta arvo ei vaikuta maagiselta numerolta.

---

### Tiedostoluettelo (tämä repo)

| Tiedosto | Kuvaus |
|---|---|
| `.github/workflows/*.yml` | GitHub Actions -workflowt |
| `CODE_CONVENTIONS.md` | Tämä sopimusdokumentti (sisältää myös AI-agentin säännöt) |
| `DECISION_LOG.csv` | Arkkitehtuuripäätökset |
| `LICENSE` | Lisenssi |
| `README.md` | Lyhyt kuvaus |
| `TECHNICAL_DESIGN.md` | Tekninen suunnittelu |
| `saanto-NN-*.json` | Jira Automation -sääntömäärittelyt (12 kpl: 01-05, 07-09, 12-15) |
| `webhook-payload-example.json` | Webhook-payload-esimerkki |
| `test-webhook.sh` | Manuaalinen curl-testi |
| `test-rules.py` | Automaattiset validointitestit sääntötiedostoille |
| `migrate-history.py` | Historia-migraatioskripti |

---

### Muistisäännöt AI-agentille

1. **Ennen kuin luot tiedoston:** tarkista nimi — `kebab-case` vai `SCREAMING_SNAKE_CASE`?
2. **Ennen kuin luot kansion:** älä luo. Kaikki menee juureen.
3. **Ennen kuin teet arkkitehtuuripäätöksen:** kirjaa se `DECISION_LOG.csv`:hen. Lue ensin suurin olemassa oleva ID.
4. **Ennen kuin viittaat toiseen repoon:** käytä absoluuttista GitHub-URL:ia.
5. **Ennen kuin avaat uuden issuen:** tarkista ettei vastaava ole jo auki tai kiinni.
6. **Ennen kuin kommentoit issueen:** lue koko issue ja sen kommentit — älä toista jo sanottua.
7. **Docstringit kirjoitetaan suomeksi** (päätös L-007).
8. **Business-arvo jokaiseen issueen** — miksi muutos on tärkeä kehittäjälle tai loppukäyttäjälle?
