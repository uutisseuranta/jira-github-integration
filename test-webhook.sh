#!/usr/bin/env bash
# test-webhook.sh — manuaalinen curl-testi Jira Automation -webhookin testaamiseen.
# Käyttö: JIRA_WEBHOOK_URL=... JIRA_WEBHOOK_TOKEN=... bash test-webhook.sh
#
# HUOM: Tämä lähettää saanto-01 (issue opened) -triggerin testipayloadilla.
# GitHub toimittaa webhookit at-least-once — sama event voidaan lähettää kahdesti.
# Katso issue #29: tarkista luodaanko Jiraan duplikaattitiketti toistuvalla ajolla.

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
