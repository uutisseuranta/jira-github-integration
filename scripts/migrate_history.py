#!/usr/bin/env python3
"""Historia-miggraatio: hakee GitHub-issuet ja luo ne Jiran work itemeiksi.

Päälogiikka:
1. Hakee kaikki projektin issuet GET /rest/api/3/search (sivutettu, 50 kerrallaan)
2. Per issue: hakee koko muutoshistorian GET /rest/api/3/issue/{key}/changelog
3. Muodostaa jokaisesta changelog-entrystä webhook-payloadin:
   - {{webhookData.issue}}          -- issue-kenttä Automation smart valueja varten
   - {{webhookData.changelog}}      -- author, created, items
   - {{webhookData.originalTimestamp}} -- alkuperäinen aika
   - {{webhookData.migrationMeta}}  -- migraatiomerkintä
4. POST-aa payloadin AUTOMATION_WEBHOOK_URL:iin
5. Kirjoittaa migration_log.jsonl-lokitiedoston

Rate limit: 100 ms viive Jira API -kutsujen välillä, 50 ms webhook-kutsujen välillä.
Retry: 429-vastaus -> odottaa Retry-After-headerin mukaisen ajan.

Tarvittavat ympäristömuuttujat (GitHub Secrets):
  JIRA_BASE_URL          https://uutisseuranta.atlassian.net
  JIRA_EMAIL             Jira-tilin sähköposti
  JIRA_API_TOKEN         Atlassian API token
  AUTOMATION_WEBHOOK_URL Jira Automation incoming webhook URL
  PROJECT_KEY            Jira project key, esim. US
  DRY_RUN                'true' tai 'false'
  MAX_ISSUES             0 = kaikki, muuten maksimimäärä
"""

import json
import os
import time
from datetime import datetime, timezone

import requests
from requests.auth import HTTPBasicAuth

# ---------------------------------------------------------------------------
# Konfiguraatio ympäristömuuttujista
# ---------------------------------------------------------------------------

JIRA_BASE_URL = os.environ["JIRA_BASE_URL"].rstrip("/")
JIRA_EMAIL = os.environ["JIRA_EMAIL"]
JIRA_API_TOKEN = os.environ["JIRA_API_TOKEN"]
AUTOMATION_WEBHOOK_URL = os.environ["AUTOMATION_WEBHOOK_URL"]
PROJECT_KEY = os.environ.get("PROJECT_KEY", "US")
DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"
MAX_ISSUES = int(os.environ.get("MAX_ISSUES", "0"))

JIRA_AUTH = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
JIRA_HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}

LOG_FILE = "migration_log.jsonl"

# ---------------------------------------------------------------------------
# Apufunktiot
# ---------------------------------------------------------------------------


def jira_get(path: str, params: dict | None = None) -> dict:
    """Tekee GET-pyynnön Jira Cloud REST API v3:een. Käsittelee 429-rate limitin."""
    url = f"{JIRA_BASE_URL}/rest/api/3{path}"
    while True:
        resp = requests.get(url, auth=JIRA_AUTH, headers=JIRA_HEADERS, params=params)
        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", "10"))
            print(f"Rate limited (429). Odotetaan {retry_after}s...")
            time.sleep(retry_after)
            continue
        resp.raise_for_status()
        time.sleep(0.1)  # 100 ms viive
        return resp.json()


def post_webhook(payload: dict) -> None:
    """Lähettää webhook-payloadin Jira Automationiin. Käsittelee 429-rate limitin."""
    if DRY_RUN:
        print(f"[DRY RUN] Ei lähetetä: issue {payload['issue']['number']} / {payload['repository']['name']}")
        return
    while True:
        resp = requests.post(AUTOMATION_WEBHOOK_URL, json=payload)
        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", "10"))
            print(f"Rate limited (429). Odotetaan {retry_after}s...")
            time.sleep(retry_after)
            continue
        print(f"  → Webhook HTTP {resp.status_code}")
        time.sleep(0.05)  # 50 ms viive
        return


def log_entry(entry: dict) -> None:
    """Kirjoittaa JSON-rivin migration_log.jsonl-tiedostoon."""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Päälogiikka
# ---------------------------------------------------------------------------


def fetch_all_issues() -> list[dict]:
    """Hakee kaikki projektin issuet sivutettuna (50 kerrallaan)."""
    issues: list[dict] = []
    start_at = 0
    page_size = 50
    while True:
        data = jira_get(
            "/search",
            params={
                "jql": f"project = {PROJECT_KEY} ORDER BY created ASC",
                "startAt": start_at,
                "maxResults": page_size,
                "fields": "summary,description,status,priority,labels,assignee,"
                           "reporter,created,updated,customfield_10071,"
                           "customfield_10072,customfield_10073",
            },
        )
        batch = data.get("issues", [])
        issues.extend(batch)
        print(f"Haettu {len(issues)}/{data['total']} issueta...")
        if len(issues) >= data["total"]:
            break
        if MAX_ISSUES > 0 and len(issues) >= MAX_ISSUES:
            break
        start_at += page_size
    if MAX_ISSUES > 0:
        issues = issues[:MAX_ISSUES]
    return issues


def fetch_changelog(issue_key: str) -> list[dict]:
    """Hakee issuen muutoshistorian kokonaan sivutettuna."""
    entries: list[dict] = []
    start_at = 0
    while True:
        data = jira_get(f"/issue/{issue_key}/changelog", params={"startAt": start_at, "maxResults": 100})
        entries.extend(data.get("values", []))
        if data["isLast"]:
            break
        start_at += len(data["values"])
    return entries


def build_payload(issue: dict, changelog_entry: dict | None = None) -> dict:
    """Muodostaa webhook-payloadin Jira Automation smart valueja varten."""
    fields = issue["fields"]
    source_repo = (fields.get("customfield_10071") or "").strip()
    github_number = fields.get("customfield_10072")
    github_url = fields.get("customfield_10073") or ""

    payload: dict = {
        "action": "migrated",
        "issue": {
            "number": int(github_number) if github_number else None,
            "title": fields.get("summary") or "",
            "body": fields.get("description") or "",
            "html_url": github_url,
            "state": "closed" if fields["status"]["statusCategory"]["key"] == "done" else "open",
            "state_reason": None,
            "labels": [{"name": lbl} for lbl in (fields.get("labels") or [])],
            "assignees": [],
            "assignee": None,
            "milestone": None,
            "user": {"login": ""},
        },
        "repository": {
            "name": source_repo,
            "full_name": f"uutisseuranta/{source_repo}" if source_repo else "",
        },
        "originalTimestamp": fields.get("created") or datetime.now(timezone.utc).isoformat(),
        "migrationMeta": {
            "jiraKey": issue["key"],
            "migratedAt": datetime.now(timezone.utc).isoformat(),
        },
    }

    if changelog_entry:
        payload["changelog"] = {
            "author": changelog_entry.get("author", {}),
            "created": changelog_entry.get("created"),
            "items": changelog_entry.get("items", []),
        }
        payload["originalTimestamp"] = changelog_entry.get("created") or payload["originalTimestamp"]

    return payload


def migrate_issue(issue: dict) -> None:
    """Migroi yhden issuen: lähettää creation-payloadin ja changelog-payloadit."""
    key = issue["key"]
    github_number = issue["fields"].get("customfield_10072")
    source_repo = (issue["fields"].get("customfield_10071") or "").strip()

    print(f"\nKäsitellään {key} (GitHub #{github_number} @ {source_repo})...")

    # Creation payload
    creation_payload = build_payload(issue)
    creation_payload["action"] = "opened"
    log_entry({"type": "creation", "jiraKey": key, "payload": creation_payload})
    post_webhook(creation_payload)

    # Changelog-payloadit
    changelog = fetch_changelog(key)
    print(f"  {len(changelog)} changelog-entryä")
    for entry in changelog:
        cl_payload = build_payload(issue, changelog_entry=entry)
        cl_payload["action"] = "changelog"
        log_entry({"type": "changelog", "jiraKey": key, "payload": cl_payload})
        post_webhook(cl_payload)


def main() -> None:
    print(f"Miggraatio käynnistyy — projekti: {PROJECT_KEY}, dry_run: {DRY_RUN}, max_issues: {MAX_ISSUES}")
    issues = fetch_all_issues()
    print(f"\nYhteensä {len(issues)} issueta miggroitavana.")
    for idx, issue in enumerate(issues, 1):
        print(f"[{idx}/{len(issues)}]", end=" ")
        migrate_issue(issue)
    print("\nValmis.")


if __name__ == "__main__":
    main()
