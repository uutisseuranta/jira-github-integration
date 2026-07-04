# Toteutuksen tila

Päivitetty: 2026-07-04

## Säännöt

| # | Sääntö | Suunta | Tila |
|---|--------|--------|------|
| 1 | GitHub issue opened → Luo Jira-issue | GH→Jira | ✅ Valmis |
| 2 | GitHub issue closed → Sulje Jira-issue | GH→Jira | ✅ Valmis |
| 3 | GitHub issue reopened → Avaa Jira-issue | GH→Jira | ✅ Valmis |
| 4 | GitHub issue labeled → Lisää label Jiraan | GH→Jira | ✅ Valmis |
| 5 | GitHub comment → Lisää kommentti Jiraan | GH→Jira | ✅ Valmis |
| 6 | ~~GitHub issue assigned → Päivitä assignee~~ | ~~GH→Jira~~ | ❌ Poistettu (D-005) |
| 7 | Jira-issue created → Luo GitHub issue | Jira→GH | ✅ Valmis |
| 8 | Jira comment → Lisää kommentti GitHubiin | Jira→GH | ✅ Valmis |
| 9 | Jira status muuttuu → Päivitä GitHub state | Jira→GH | 📋 Suunniteltu |
| 10 | ~~Jira assignee muuttuu → Päivitä GitHub assignee~~ | ~~Jira→GH~~ | ❌ Poistettu (D-005) |
| 11 | Jira priority muuttuu → Päivitä GitHub label | Jira→GH | 📋 Suunniteltu |
| 12 | GitHub milestone → Päivitä Jira sprint | GH→Jira | 🔄 Osittain |
| 13 | Jira sprint → Päivitä GitHub milestone | Jira→GH | 🔄 Osittain |
| 14 | GitHub issue deleted → Sulje Jira-issue | GH→Jira | ✅ Valmis |
| 15 | Jira-issue deleted → Sulje GitHub issue | Jira→GH | 📋 Suunniteltu |

**Selitykset:** ✅ Valmis &nbsp;|&nbsp; 🔄 Osittain &nbsp;|&nbsp; 📋 Suunniteltu &nbsp;|&nbsp; ❌ Poistettu

## Migraatio

| Tehtävä | Tila |
|---------|------|
| `migrate-history.py` skripti | ✅ Valmis |
| GitHub Actions workflow | ✅ Valmis |
| Tuotantomigraatio ajettu | 📋 Tekemättä |

## Tunnetut rajoitukset

- `migrate-history.py` luo issuet Jira-tyyppinä "Task" — muuta `issuetype`-kenttää tarvittaessa.
