#!/usr/bin/env python3
"""Migrate GitHub Issues → Jira.

Migroi GitHub-repon avoimet issuet Jiraan ja tallentaa linkit
custom fieldeihin (GitHub Issue Number = 10072, GitHub Repo = 10071).

Käyttö: Ajettavissa suoraan tai GitHub Actions -workflown kautta
(.github/workflows/migrate-history.yml).

Vaaditut ympäristömuuttujat:
  GITHUB_TOKEN      - GitHub Personal Access Token (repo scope)
  JIRA_BASE_URL     - Jira Cloud URL (esim. https://oma-org.atlassian.net)
  JIRA_EMAIL        - Jira-tilin sähköposti
  JIRA_API_TOKEN    - Jira API Token
  JIRA_PROJECT_KEY  - Kohde-projektin avain (esim. US)
  GITHUB_REPO       - Lähde-repo (esim. uutisseuranta.github.io)
  DRY_RUN           - 'true' = ei luo issueja, vain listaa (oletus: false)
"""

import os
import sys
import requests
from requests.auth import HTTPBasicAuth

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
JIRA_BASE_URL = os.environ["JIRA_BASE_URL"].rstrip("/")
JIRA_EMAIL = os.environ["JIRA_EMAIL"]
JIRA_API_TOKEN = os.environ["JIRA_API_TOKEN"]
JIRA_PROJECT_KEY = os.environ["JIRA_PROJECT_KEY"]
GITHUB_REPO = os.environ["GITHUB_REPO"]
DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"
GITHUB_OWNER = "uutisseuranta"

# Jira custom field IDs
CF_GITHUB_NUMBER = "customfield_10072"
CF_GITHUB_REPO = "customfield_10071"

def get_github_issues():
    """Hae kaikki avoimet issuet GitHubista (paginointi)."""
    issues = []
    page = 1
    while True:
        resp = requests.get(
            f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/issues",
            headers={"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"},
            params={"state": "open", "per_page": 100, "page": page},
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        # Suodata pull requestit pois
        issues.extend([i for i in batch if "pull_request" not in i])
        page += 1
    return issues


def create_jira_issue(gh_issue):
    """Luo yksi Jira-issue GitHub-issuen pohjalta."""
    payload = {
        "fields": {
            "project": {"key": JIRA_PROJECT_KEY},
            "summary": f"Git: {gh_issue['title']}",
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": gh_issue.get("body") or ""}],
                    },
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": f"Alkuperäinen GitHub issue: {gh_issue['html_url']}"}],
                    },
                ],
            },
            "issuetype": {"name": "Task"},
            CF_GITHUB_NUMBER: str(gh_issue["number"]),
            CF_GITHUB_REPO: GITHUB_REPO,
        }
    }
    resp = requests.post(
        f"{JIRA_BASE_URL}/rest/api/3/issue",
        auth=HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN),
        json=payload,
        headers={"Content-Type": "application/json"},
    )
    if not resp.ok:
        print(f"  VIRHE ({resp.status_code}): {resp.text}")
        return None
    return resp.json()["key"]


def main():
    print(f"Migroidaan {GITHUB_OWNER}/{GITHUB_REPO} → Jira {JIRA_PROJECT_KEY}")
    if DRY_RUN:
        print("*** DRY RUN - ei luoda Jira-issueja ***")

    issues = get_github_issues()
    print(f"Löydettiin {len(issues)} avointa GitHub-issuea")

    ok, fail = 0, 0
    for gh in issues:
        if DRY_RUN:
            print(f"  [DRY] #{gh['number']} {gh['title']}")
            ok += 1
            continue
        jira_key = create_jira_issue(gh)
        if jira_key:
            print(f"  OK: #{gh['number']} → {jira_key}")
            ok += 1
        else:
            fail += 1

    print(f"\nValmis: {ok} onnistui, {fail} epäonnistui")
    if fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
