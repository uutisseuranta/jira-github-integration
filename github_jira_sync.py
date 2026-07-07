#!/usr/bin/env python3
"""
github_jira_sync.py — Bulk sync GitHub issues to Jira work items.

Logic:
  1. Fetch open issues from each configured GitHub repo (REST API).
  2. For each issue, search Jira by customfield_10071 (repo) + customfield_10072 (issue number).
  3. If found  → update summary / description / labels.
  4. If not found → create new work item.
  5. DRY_RUN=true (default) only prints what would be done.

See GITHUB_JIRA_SYNC.md for full documentation.
"""

import os
import sys
import time
import json
import logging
from urllib import request, parse, error as urllib_error
from base64 import b64encode
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration (read from environment)
# ---------------------------------------------------------------------------

GITHUB_TOKEN  = os.environ.get("GITHUB_TOKEN", "")
GITHUB_OWNER  = os.environ.get("GITHUB_OWNER", "uutisseuranta")
GITHUB_REPOS  = [
    r.strip()
    for r in os.environ.get("GITHUB_REPOS", "").split(",")
    if r.strip()
]

JIRA_BASE_URL   = os.environ.get("JIRA_BASE_URL", "").rstrip("/")
JIRA_EMAIL      = os.environ.get("JIRA_EMAIL", "")
JIRA_API_TOKEN  = os.environ.get("JIRA_API_TOKEN", "")
JIRA_PROJECT    = os.environ.get("JIRA_PROJECT_KEY", "US")

DRY_RUN = os.environ.get("DRY_RUN", "true").lower() != "false"

RATE_LIMIT_DELAY = 0.2  # seconds between API calls

# Jira custom field IDs
CF_SOURCE_REPO     = "customfield_10071"  # string: repo name
CF_GITHUB_NUMBER   = "customfield_10072"  # number: issue number
CF_GITHUB_URL      = "customfield_10073"  # string: html_url

# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def _auth_header_github() -> dict:
    return {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}


def _auth_header_jira() -> dict:
    token = b64encode(f"{JIRA_EMAIL}:{JIRA_API_TOKEN}".encode()).decode()
    return {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _http(method: str, url: str, headers: dict, body: Optional[dict] = None) -> dict:
    """Minimal HTTP wrapper using stdlib only."""
    data = json.dumps(body).encode() if body else None
    req = request.Request(url, data=data, headers=headers, method=method)
    try:
        with request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib_error.HTTPError as exc:
        raw = exc.read().decode(errors="replace")
        raise RuntimeError(f"HTTP {exc.code} {method} {url}: {raw}") from exc
    finally:
        time.sleep(RATE_LIMIT_DELAY)


# ---------------------------------------------------------------------------
# GitHub helpers
# ---------------------------------------------------------------------------

def fetch_open_issues(owner: str, repo: str) -> list[dict]:
    """Return all open issues for owner/repo (follows pagination)."""
    issues: list[dict] = []
    page = 1
    while True:
        url = (
            f"https://api.github.com/repos/{owner}/{repo}/issues"
            f"?state=open&per_page=100&page={page}"
        )
        batch = _http("GET", url, _auth_header_github())
        if not batch:
            break
        # Filter out pull requests (GitHub returns PRs in the issues endpoint)
        issues.extend(i for i in batch if "pull_request" not in i)
        if len(batch) < 100:
            break
        page += 1
    return issues


# ---------------------------------------------------------------------------
# Issuetype logic
# ---------------------------------------------------------------------------

def _issuetype_from_labels(labels: list[str]) -> str:
    label_set = {l.lower() for l in labels}
    if label_set & {"epic"}:
        return "Epic"
    if label_set & {"feat", "enhancement"}:
        return "Story"
    if label_set & {"bug"}:
        return "Bug"
    return "Task"


# ---------------------------------------------------------------------------
# Jira helpers
# ---------------------------------------------------------------------------

def search_jira_issue(repo_name: str, github_number: int) -> Optional[dict]:
    """Return the first matching Jira issue or None."""
    jql = (
        f'project = {JIRA_PROJECT} '
        f'AND cf[10072] = {github_number} '
        f'AND cf[10071] = "{repo_name}"'
    )
    url = f"{JIRA_BASE_URL}/rest/api/3/search?jql={parse.quote(jql)}&maxResults=1"
    result = _http("GET", url, _auth_header_jira())
    issues = result.get("issues", [])
    return issues[0] if issues else None


def _build_jira_fields(gh_issue: dict, repo_name: str, issuetype: str) -> dict:
    label_names = [lbl["name"] for lbl in gh_issue.get("labels", [])]
    return {
        "project":    {"key": JIRA_PROJECT},
        "issuetype":  {"name": issuetype},
        # L-002: "Git: " prefix prevents Jira Automation saanto-13 loop-back
        "summary":    f"Git: {gh_issue['title']}",
        "description": {
            "version": 1,
            "type":    "doc",
            "content": [
                {
                    "type":    "paragraph",
                    "content": [{"type": "text", "text": gh_issue.get("body") or ""}],
                }
            ],
        },
        "labels": label_names,
        CF_SOURCE_REPO:   repo_name,
        CF_GITHUB_NUMBER: gh_issue["number"],
        CF_GITHUB_URL:    gh_issue["html_url"],
    }


def create_jira_issue(fields: dict) -> str:
    """Create a Jira issue and return its key (e.g. US-42)."""
    result = _http("POST", f"{JIRA_BASE_URL}/rest/api/3/issue", _auth_header_jira(), {"fields": fields})
    return result["key"]


def update_jira_issue(issue_key: str, fields: dict) -> None:
    """Update summary, description, and labels on an existing Jira issue."""
    update_fields = {
        k: fields[k]
        for k in ("summary", "description", "labels")
        if k in fields
    }
    _http("PUT", f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}", _auth_header_jira(), {"fields": update_fields})


# ---------------------------------------------------------------------------
# Main sync loop
# ---------------------------------------------------------------------------

def sync_repo(repo: str, counters: dict) -> None:
    log.info("Fetching issues from %s/%s …", GITHUB_OWNER, repo)
    try:
        issues = fetch_open_issues(GITHUB_OWNER, repo)
    except Exception as exc:
        log.error("Failed to fetch issues for %s: %s", repo, exc)
        counters["errors"] += 1
        return

    log.info("  → %d open issues found", len(issues))

    for issue in issues:
        number     = issue["number"]
        title      = issue["title"]
        label_names = [lbl["name"] for lbl in issue.get("labels", [])]
        issuetype  = _issuetype_from_labels(label_names)

        try:
            existing = search_jira_issue(repo, number)
            fields   = _build_jira_fields(issue, repo, issuetype)

            if existing:
                jira_key = existing["key"]
                if DRY_RUN:
                    log.info("[DRY-RUN] Would update %s ← GH#%d %s", jira_key, number, title)
                else:
                    update_jira_issue(jira_key, fields)
                    log.info("Updated %s ← GH#%d %s", jira_key, number, title)
                counters["updated"] += 1
            else:
                if DRY_RUN:
                    log.info("[DRY-RUN] Would create %s issue ← GH#%d %s", issuetype, number, title)
                else:
                    jira_key = create_jira_issue(fields)
                    log.info("Created %s ← GH#%d %s", jira_key, number, title)
                counters["created"] += 1

        except Exception as exc:
            log.error("Error processing GH#%d (%s): %s", number, title, exc)
            counters["errors"] += 1


def main() -> None:
    # Validate required config
    missing = [k for k, v in {
        "GITHUB_TOKEN": GITHUB_TOKEN,
        "JIRA_BASE_URL": JIRA_BASE_URL,
        "JIRA_EMAIL": JIRA_EMAIL,
        "JIRA_API_TOKEN": JIRA_API_TOKEN,
    }.items() if not v]
    if missing:
        log.error("Missing required environment variables: %s", ", ".join(missing))
        sys.exit(1)

    if not GITHUB_REPOS:
        log.error("GITHUB_REPOS is empty. Set it to a comma-separated list of repo names.")
        sys.exit(1)

    mode = "DRY-RUN" if DRY_RUN else "LIVE"
    log.info("=== github_jira_sync.py starting [%s] ===", mode)
    log.info("Repos: %s", ", ".join(GITHUB_REPOS))
    log.info("Jira project: %s", JIRA_PROJECT)

    counters = {"created": 0, "updated": 0, "skipped": 0, "errors": 0}

    for repo in GITHUB_REPOS:
        sync_repo(repo, counters)

    log.info(
        "=== Done === Created: %d | Updated: %d | Skipped: %d | Errors: %d ===",
        counters["created"], counters["updated"], counters["skipped"], counters["errors"],
    )

    if counters["errors"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
