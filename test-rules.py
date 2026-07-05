#!/usr/bin/env python3
"""Automated validation tests for Jira Automation JSON rules.

Validates:
1. JSON syntax and structure.
2. Custom fields alignment (customfield_10071, 10072, 10073).
3. Removal of label deletion logic (L-006).
4. Correct use of prefix-based master title sync (L-002: Git: and Jira:).
"""

import os
import json
import re
import unittest

class TestJiraRules(unittest.TestCase):
    def get_rule_files(self):
        """Palauttaa kaikki sääntöihin liittyvät JSON-tiedostot."""
        return [f for f in os.listdir('.') if f.startswith('saanto-') and f.endswith('.json')]

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
        """Varmistaa, että käytetään vain organisaatiossa sovittuja ja konfiguroituja custom-kenttiä."""
        allowed_fields = {"customfield_10071", "customfield_10072", "customfield_10073"}
        files = self.get_rule_files()
        for f in files:
            with self.subTest(file=f):
                with open(f, 'r', encoding='utf-8') as fh:
                    content = fh.read()
                
                # Etsitään kaikki viittaukset customfield_XXXXX -muodossa
                found_fields = set(re.findall(r'customfield_\d+', content))
                invalid_fields = found_fields - allowed_fields
                self.assertEqual(
                    len(invalid_fields), 0,
                    f"Tiedostossa {f} käytetään ei-sallittuja custom-kenttiä: {invalid_fields}"
                )

    def test_label_deletion_disabled(self):
        """Varmistaa päätöksen L-006 mukaisesti, ettei säännöissä ole DELETE-kutsuja labeleille."""
        files = self.get_rule_files()
        for f in files:
            # Säännöt 9 ja 12 ovat status/sprint muutoksia
            if f in ['saanto-09-jira-status-changed.json', 'saanto-12-jira-sprint-changed.json']:
                with self.subTest(file=f):
                    with open(f, 'r', encoding='utf-8') as fh:
                        content = fh.read()
                    self.assertNotIn(
                        'DELETE', content,
                        f"Tiedosto {f} sisältää kielletyn DELETE-kutsun labelille (päätös L-006)."
                    )

    # Intentionaalisesti puuttuvat numerot (ks. DECISION_LOG.csv):
    # saanto-06: ei käytössä (assignee-synkronointi poistettu D-005)
    # saanto-10: poistettu (D-005)
    # saanto-11: poistettu (prioriteettisynkronointi poistettu L-011)
    EXPECTED_RULE_COUNT = 12  # 01-05, 07-09, 12-15

    def test_loop_prevention_rule08(self):
        """Varmistaa että saanto-08 sisältää silmukkaestoehdon ([Jira] tai Jira: etuliite)."""
        f = 'saanto-08-github-comment-created.json'
        if os.path.exists(f):
            with open(f, 'r', encoding='utf-8') as fh:
                content = fh.read()
            # Ehdon on löydyttävä joko [Jira] tai Jira: etuliite skip-logiikkana
            has_loop_guard = '[Jira]' in content or 'Jira:' in content
            self.assertTrue(has_loop_guard, f"{f} ei sisällä silmukkaestoehtoa")

    def test_prefix_consistency(self):
        """Varmistaa päätöksen L-002 mukaisesti otsikoiden uudet lyhyet etuliitteet (Git: ja Jira:)."""
        # Sääntö 1 (luonti) ja Sääntö 2 (muokkaus) pitää kirjoittaa "Git: "
        for f in ['saanto-01-github-issue-opened.json', 'saanto-02-github-issue-edited.json']:
            if os.path.exists(f):
                with self.subTest(file=f):
                    with open(f, 'r', encoding='utf-8') as fh:
                        content = fh.read()
                    self.assertIn('Git:', content, f"Tiedosto {f} ei käytä uutta 'Git:' etuliitettä.")
                    self.assertNotIn('[GitHub]', content, f"Tiedosto {f} käyttää vanhentunutta '[GitHub]' etuliitettä.")

        # Sääntö 13 pitää kirjoittaa "Jira: "
        f13 = 'saanto-13-jira-summary-changed.json'
        if os.path.exists(f13):
            with self.subTest(file=f13):
                with open(f13, 'r', encoding='utf-8') as fh:
                    content = fh.read()
                self.assertIn('Jira:', content, f"Tiedosto {f13} ei käytä uutta 'Jira:' etuliitettä.")
                self.assertNotIn('[Jira]', content, f"Tiedosto {f13} käyttää vanhentunutta '[Jira]' etuliitettä.")

if __name__ == '__main__':
    unittest.main()
