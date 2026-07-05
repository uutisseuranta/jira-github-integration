#!/usr/bin/env python3
"""Jira Automation JSON -sääntöjen automaattiset validointitestit.

Validoi:
1. JSON-syntaksin ja -rakenteen.
2. Custom-kenttien yhdenmukaisuuden (customfield_10071, 10072, 10073).
3. Label-poistologiikan poistamisen (päätös L-006).
4. Etuliitepohjaisen otsikkosynkronoinnin oikean käytön (päätös L-002: Git: ja Jira:).

Ajo: python -m pytest test-rules.py -v
Viite: DECISION_LOG.csv, TECHNICAL_DESIGN.md
"""

import os
import json
import re
import unittest

class TestJiraRules(unittest.TestCase):
    # Päivitä kun sääntöjä lisätään tai poistetaan — kirjaa myös DECISION_LOG.csv
    # Intentionaalisesti puuttuvat numerot:
    # saanto-06: ei käytössä (assignee-synkronointi poistettu, D-005)
    # saanto-10: poistettu (D-005)
    # saanto-11: poistettu (prioriteettisynkronointi poistettu, L-011)
    EXPECTED_RULE_COUNT = 12  # 01-05, 07-09, 12-15

    def get_rule_files(self):
        """Palauttaa kaikki sääntöihin liittyvät JSON-tiedostot hakemistosta."""
        return [f for f in os.listdir('.') if f.startswith('saanto-') and f.endswith('.json')]

    def test_rule_count(self):
        """Varmistaa, että löydettyjen sääntötiedostojen määrä vastaa EXPECTED_RULE_COUNT-vakiota.

        Testi epäonnistuu jos sääntötiedostoja lisätään tai poistetaan ilman vakion päivitystä.
        Tämä on regression guard -mekanismi konfiguraatiomuutoksille.
        """
        files = self.get_rule_files()
        self.assertEqual(
            len(files),
            self.EXPECTED_RULE_COUNT,
            f"Odotettiin {self.EXPECTED_RULE_COUNT} sääntöä, löytyi {len(files)}. "
            f"Päivitä EXPECTED_RULE_COUNT tai tarkista puuttuvat/ylimääräiset tiedostot. "
            f"Kirjaa myös muutos DECISION_LOG.csv:hen."
        )

    def test_json_validity(self):
        """Varmistaa, että kaikki sääntötiedostot ovat valideja JSON-tiedostoja ja sisältävät perustiedot."""
        files = self.get_rule_files()
        self.assertGreater(len(files), 0, "Yhtään saanto-*.json tiedostoa ei löytynyt.")
        for f in files:
            with self.subTest(file=f):
                try:
                    with open(f, 'r', encoding='utf-8') as fh:
                        data = json.load(fh)
                    self.assertIn('name', data)
                    self.assertIn('state', data)
                    self.assertIn('trigger', data)
                    self.assertIn('components', data)
                except Exception as e:
                    self.fail(f"Tiedoston {f} lataus epäonnistui: {e}")

    def test_custom_fields_consistency(self):
        """Varmistaa, että käytetään vain organisaatiossa sovittuja ja konfiguroituja custom-kenttiä.

        Sallitut kentät on listattu TECHNICAL_DESIGN.md:ssä. Lisää sallittu kenttä allowed_fields
        -joukkoon JA kirjaa päätös DECISION_LOG.csv:hen ennen kuin käytät uutta customfield-arvoa.
        """
        allowed_fields = {"customfield_10071", "customfield_10072", "customfield_10073"}
        files = self.get_rule_files()
        for f in files:
            with self.subTest(file=f):
                with open(f, 'r', encoding='utf-8') as fh:
                    content = fh.read()
                found_fields = set(re.findall(r'customfield_\d+', content))
                invalid_fields = found_fields - allowed_fields
                self.assertEqual(
                    len(invalid_fields), 0,
                    f"Tiedostossa {f} käytetään ei-sallittuja custom-kenttiä: {invalid_fields}"
                )

    def test_label_deletion_disabled(self):
        """Varmistaa päätöksen L-006 mukaisesti, ettei säännöissä ole DELETE-kutsuja labeleille.

        Vain status- ja sprint-muutossäännöt (09, 12) tarkistetaan, koska ne olivat
        aiemmin virheellisesti käyttäneet DELETE-kutsua labelien poistoon.
        """
        files = self.get_rule_files()
        for f in files:
            # Tarkistetaan vain tiedostot joissa on aiemmin ollut DELETE-kutsuja
            if f in ['saanto-09-jira-status-changed.json', 'saanto-12-jira-sprint-changed.json']:
                with self.subTest(file=f):
                    with open(f, 'r', encoding='utf-8') as fh:
                        content = fh.read()
                    self.assertNotIn(
                        'DELETE', content,
                        f"Tiedosto {f} sisältää kielletyn DELETE-kutsun labelille (päätös L-006)."
                    )

    def test_loop_prevention_comments(self):
        """Varmistaa että saanto-08 ja saanto-14 kommenttisäännöt sisältävät yhteensopivat silmukkaestot.

        Päätös L-002: saanto-08 käyttää etuliitettä 'Jira:' GitHub→Jira-suunnassa,
        saanto-14 käyttää etuliitettä 'Git:' Jira→GitHub-suunnassa.
        Ilman näitä tarkistuksia kommenttisynkronointi looppaisi loputtomasti.
        """
        f8 = 'saanto-08-github-comment-created.json'
        if os.path.exists(f8):
            with open(f8, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
            conditions = [c for c in data['components'] if c['component'] == 'CONDITION']
            has_loop_guard = False
            for cond in conditions:
                for sub_c in cond['value'].get('conditions', []):
                    if sub_c.get('first') == '{{webhookData.comment.body}}' and sub_c.get('second') == 'Jira:':
                        has_loop_guard = True
            self.assertTrue(has_loop_guard, f"{f8} ei sisällä silmukkaestoehtoa 'Jira:'")

        f14 = 'saanto-14-jira-comment-added.json'
        if os.path.exists(f14):
            with open(f14, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
            conditions = [c for c in data['components'] if c['component'] == 'CONDITION']
            has_loop_guard = False
            for cond in conditions:
                for sub_c in cond['value'].get('conditions', []):
                    if sub_c.get('first') == '{{comment.body}}' and sub_c.get('second') == 'Git:':
                        has_loop_guard = True
            self.assertTrue(has_loop_guard, f"{f14} ei sisällä silmukkaestoehtoa 'Git:'")

    def test_prefix_consistency(self):
        """Varmistaa päätöksen L-002 mukaisesti otsikoiden uudet lyhyet etuliitteet (Git: ja Jira:).

        Vanhat etuliitteet '[GitHub]' ja '[Jira]' on korvattu lyhyemmillä muodoilla
        jotta Jira Summary -kentän 255 merkin raja ei täyty (ks. DECISION_LOG.csv, L-002).
        """
        for f in ['saanto-01-github-issue-opened.json', 'saanto-02-github-issue-edited.json']:
            if os.path.exists(f):
                with self.subTest(file=f):
                    with open(f, 'r', encoding='utf-8') as fh:
                        content = fh.read()
                    self.assertIn('Git:', content, f"Tiedosto {f} ei käytä uutta 'Git:' etuliitettä.")
                    self.assertNotIn('[GitHub]', content, f"Tiedosto {f} käyttää vanhentunutta '[GitHub]' etuliitettä.")

        f13 = 'saanto-13-jira-summary-changed.json'
        if os.path.exists(f13):
            with self.subTest(file=f13):
                with open(f13, 'r', encoding='utf-8') as fh:
                    content = fh.read()
                self.assertIn('Jira:', content, f"Tiedosto {f13} ei käytä uutta 'Jira:' etuliitettä.")
                self.assertNotIn('[Jira]', content, f"Tiedosto {f13} käyttää vanhentunutta '[Jira]' etuliitettä.")

if __name__ == '__main__':
    unittest.main()
