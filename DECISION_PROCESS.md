# Kehittämisen päätöksentekoprosessi

> Tämä dokumentti kuvaa miten päätökset syntyvät, miten ne kirjataan ja miksi laatu paranee dialogin kautta.

## Prosessin rakenne

Kehittäminen etenee kolmivaiheisessa syklissä:

```
Analyysi (tiketti) → Päätös (DECISION_LOG) → Toteutus (koodi/config)
```

Kaikki kolme vaihetta ovat pakollisia. Tiketti ilman päätöslokimerkintää on keskeneräinen; päätöslokimerkintä ilman tikettikontekstia on jäljittämätön.

## Vaihe 1 — Analyysi tikettinä

Tiketti on ajattelun työtila. Se sisältää:

- **Kontekstin**: mitä ongelmaa ratkaistaan ja miksi se on ongelma
- **Vaihtoehdot**: vähintään kaksi toteutustapaa kustannuksineen ja hyötyineen
- **Kriittiset huomiot**: tekniset rajoitteet, API-käyttäytyminen, reunatapaukset

Tikettiin *ei* kirjata lopullista päätöstä — se kuuluu lokiin. Tiketti saa jäädä messy: se on sen tarkoitus.

## Vaihe 2 — Päätös lokiin

Kun analyysi on riittävä, päätös kirjataan `DECISION_LOG.csv`-tiedostoon. Merkintä sisältää:

| Kenttä | Sisältö |
|---|---|
| `id` | Tunniste: `G-NNN` (globaali) tai `L-NNN` (lokaalitason) |
| `date` | ISO 8601 -päivämäärä |
| `title` | Lyhyt otsikko (max 8 sanaa) |
| `decision` | Mitä tehdään — konkreettinen ja täsmällinen |
| `rationale` | Miksi — perustelee hylätyt vaihtoehdot ja valitun lähestymistavan |
| `affects_issues` | Mihin tiketteihin tai tiedostoihin päätös vaikuttaa |

Tärkeää: `rationale` ei toista `decision`-kenttää. Se vastaa kysymykseen *miksi tämä vaihtoehto muiden joukosta*.

## Vaihe 3 — Toteutus

Toteutus seuraa päätöslokia, ei toisin päin. Jos toteutuksen aikana ilmenee uusi rajoite joka muuttaa päätöstä, palataan vaiheeseen 2 ennen kuin jatketaan.

## Laatu syntyy dialogista

Tärkein oivallus: **tiketit ja päätösloki eivät ole byrokratiaa — ne ovat laadun mekanismi**.

Ilman strukturoitua analyysiä päätökset syntyvät ensimmäisestä toimivasta ideasta. Dialogin pakottaminen — "mitkä ovat vaihtoehdot, mitä ne maksavat, miksi tämä" — nostaa päätöksen laadun systemaattisesti. Tämä projekti on osoittanut sen konkreettisesti:

- Sääntö 13 poistettiin kun analyysi paljasti Free-tier-rajoitteen (L-002)
- Sääntö 15 sai Vaihtoehto A:n kun Vaihtoehto B:n monimutkaisuus arvioitiin suhteessa ongelmaan (L-009)
- Assignee-synkronointi hylättiin kun kartoitusongelma tunnistettiin (L-005)

Kaikki nämä olisivat voineet päätyä huonompaan ratkaisuun ilman eksplisiittistä analyysivaihetta. **Laatu ei tullut lisätyöstä — se tuli kysymyksistä joita dialogi pakotti esittämään.**

## Päätösten hierarkia

Globaalit päätökset (`G-NNN`) koskevat kaikkia repoja ja kirjataan jokaiseen repoon (G-007). Lokaalit päätökset (`L-NNN`) koskevat vain tätä repoa.

Jos lokaalipäätös on ristiriidassa globaalin kanssa, globaali voittaa — paitsi jos lokaalipäätös eksplisiittisesti kumoaa sen ja se hyväksytään organisaatiotasolla.

## Revisiointi

Päätökset eivät ole kiveen hakattuja. Jokainen päätös voidaan avata uudelleen kun:

- Olosuhteet muuttuvat (API-muutos, uusi tier, uusi rajoite)
- Uusi tieto kumoaa aiemman perustelun
- Toteutuksen aikana paljastuu reunatapaus jota analyysi ei kattanut

Revisio kirjataan uutena merkintänä lokiin (ei ylikirjoiteta vanhaa), viitaten aiempaan päätökseen `rationale`-kentässä.
