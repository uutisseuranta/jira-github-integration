#!/usr/bin/env bash
# Manuaalinen curl-testi Jira Automation -webhookin testaamiseen.
# Käyttö: JIRA_WEBHOOK_URL=... JIRA_WEBHOOK_TOKEN=... bash docs/curl-test.sh

curl -s -X POST \
  "${JIRA_WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -H "X-Automation-Webhook-Token: ${JIRA_WEBHOOK_TOKEN}" \
  -d '{
    "action": "opened",
    "issue": {
      "number": 999,
      "title": "Test",
      "body": "Test body",
      "html_url": "https://github.com/uutisseuranta/uutisseuranta.github.io/issues/999"
    },
    "repository": {
      "name": "uutisseuranta.github.io"
    }
  }' \
  -w "\nHTTP %{http_code}\n"
