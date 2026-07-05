# DESIGN_GUIDELINES.md

> Tämä dokumentti koskee vain `jira-github-integration`-repositoriota.
> Globaalit käytännöt: [CODE_CONVENTIONS.md](https://github.com/uutisseuranta/jira-github-integration/blob/main/CODE_CONVENTIONS.md)
> Päätökset: [DECISION_LOG.csv](https://github.com/uutisseuranta/jira-github-integration/blob/main/DECISION_LOG.csv)
> Päätöksentekoprosessi: [DECISION_PROCESS.md](https://github.com/uutisseuranta/jira-github-integration/blob/main/DECISION_PROCESS.md)

---

## Kehittämisen päätöksentekoprosessi

Kehittäminen etenee kolmivaiheisessa syklissä jossa jokainen vaihe on pakollinen:

```
Analyysi (tiketti) → Päätös (DECISION_LOG) → Toteutus (koodi / config)
```

Vaiheita ei voi ohittaa eikä järjestystä vaihtaa. Tiketti ilman päätöslokimerkintää on keskeneräinen. Päätöslokimerkintä ilman tikettikontekstia on jäljittämätön. Toteutus ilman lokia on oikosulku joka korjataan joka kerta erikseen.

### Vaihe 1 — Analyysi tikettiin

Tiketti on ajattelun työtila — ei tehtävälistaus. Se sisältää vähintään:

- **Konteksti**: mitä ongelmaa ratkaistaan ja miksi se on ongelma
- **Vaihtoehdot**: vähintään kaksi toteutustapaa kustannuksineen ja hyötyineen
- **Kriittiset huomiot**: API-käyttäytyminen, tekniset rajoitteet, reunatapaukset

Tiketti saa olla epäsiisti — se on sen tarkoitus. Lopullinen päätös kirjataan lokiin, ei tikettiin.

### Vaihe 2 — Päätös lokiin

Kun analyysi on riittävä, kirjataan `DECISION_LOG.csv`-merkintä:

| Kenttä | Sisältö |
|---|---|
| `id` | `G-NNN` (globaali) tai `L-NNN` (repokohtainen) |
| `date` | ISO 8601 |
| `title` | Lyhyt otsikko, max 8 sanaa |
| `decision` | Mitä tehdään — konkreettinen ja täsmällinen |
| `rationale` | Miksi tämä vaihtoehto — perustelee myös hylätyt |
| `affects_issues` | Tiketit ja tiedostot joihin päätös vaikuttaa |

`rationale` ei toista `decision`-kenttää. Se vastaa kysymykseen *miksi tämä vaihtoehto muiden joukosta*.

### Vaihe 3 — Toteutus seuraa lokia

Toteutus seuraa päätöslokia, ei toisin päin. Jos toteutuksen aikana ilmenee uusi rajoite joka muuttaa päätöstä, palataan vaiheeseen 2 ennen kuin jatketaan. Revisiot kirjataan aina uusina lokimerkintöinä — vanhoja ei ylikirjoiteta.

### Päätösten hierarkia

Globaalit päätökset (`G-NNN`) koskevat kaikkia repoja ja kirjataan jokaiseen repoon (ks. G-007). Repokohtaiset päätökset (`L-NNN`) koskevat vain tätä repoa. Jos lokaalipäätös on ristiriidassa globaalin kanssa, globaali voittaa — paitsi jos lokaalipäätös eksplisiittisesti kumoaa sen.

---

## Miksi dialogi on laadun mekanismi

Tiketit ja päätösloki eivät ole byrokratiaa — ne ovat mekanismi jolla laatu paranee systemaattisesti.

Ilman strukturoitua analyysia päätökset syntyvät ensimmäisestä toimivasta ideasta. Dialogi — "mitkä ovat vaihtoehdot, mitä ne maksavat, miksi tämä" — pakottaa esittämään kysymyksen joka muuten jää esittämättä. **Laatu ei tule lisätyöstä — se tulee kysymyksistä.**

Tämä projekti on osoittanut sen konkreettisesti:

- **L-002**: Sääntö 13 poistettiin kun analyysi paljasti Free-tier-rajoitteen *ennen* toteutusta — ilman dialogia rajoite olisi paljastunut tuotannossa
- **L-005**: Assignee-synkronointi hylättiin kun kartoitusongelma tunnistettiin analyysivaiheessa — ilman dialogia se olisi koodattu valmiiksi ennen ongelman löytymistä
- **L-009**: Vaihtoehto B (GitHub Actions -välikerros) esti kun monimutkaisuus arvioitiin suhteessa ongelman kokoon — ilman dialogia se olisi toteutettu ylimitoitettuna ratkaisuna

Kaikki kolme päätystä olisivat voineet päätyä huonompaan ratkaisuun ilman eksplisiittistä analyysivaihetta. Loki tekee tämän näkyväksi: se ei ole pelkkä muisti — se on todiste siitä että dialogi toimii.

Perustelu: [DECISION_LOG.csv](https://github.com/uutisseuranta/jira-github-integration/blob/main/DECISION_LOG.csv) → G-008, G-009

---

## Poikkeukset

Jos tekninen syy pakottaa poikkeamaan tästä dokumentista, sovelletaan samaa periaatetta kuin CODE_CONVENTIONS.md:ssä: kirjaa poikkeus `DECISION_LOG.csv`-tiedostoon, merkitse syy ja laajuus `rationale`-kenttään. Dokumentoimaton poikkeus on rikkomus — dokumentoitu poikkeus on tietoinen päätös.

## Persistointiperiaate

Integraatio ei käytä erillistä state storea eikä integraatiotietokantaa. Jira ja
GitHub ovat kanonisia totuuslähteitä — avoimet standardit tarjoavat kaiken
tarvittavan tilan suoraan APIn kautta.

Webhook-duplikaatit ja retryt ovat teoreettinen ongelma jonka todennäköisyys on
häviävän pieni. Jos ongelma joskus ilmenee, siitä avataan ops-bugi aikanaan.
Kompleksiteettia ei lisätä spekulatiivisia ongelmia varten. Ks. päätösloki **G-010**.

