---
title: Orkes Conductor — Enterprise Reference
type: reference
status: current
created: 2026-04-21
updated: 2026-04-21
reviewed: 2026-04-21
tags:
  - conductor
  - orkes
  - enterprise
  - cloud
  - schedules
  - secrets
source: https://orkes.io/content/
---

# Orkes Conductor — Enterprise Reference

Orkes is the commercial company behind Conductor OSS. Orkes Conductor is a fully-managed, enterprise-hardened distribution of Conductor with additional features beyond the OSS core.

## OSS vs Orkes Feature Comparison

| Feature | Conductor OSS | Orkes Conductor |
|---------|--------------|-----------------|
| All core task types | ✅ | ✅ |
| LLM/AI tasks (14+ providers) | ✅ | ✅ |
| MCP tool calling | ✅ | ✅ |
| HUMAN task | ✅ | ✅ |
| REST API + CLI | ✅ | ✅ |
| Visual workflow editor (UI) | ✅ | ✅ (enhanced) |
| Self-hosted | ✅ | ✅ (Orkes Private Cloud) |
| Managed cloud | ❌ | ✅ |
| **Schedules** (cron-based workflow triggers) | ❌ | ✅ |
| **Secrets Manager** | ❌ | ✅ |
| **Webhooks** (inbound HTTP triggers) | ❌ | ✅ |
| **RBAC** (fine-grained access control) | Basic | ✅ Full |
| **Audit logs** | Basic | ✅ Full |
| **SSO / SAML / OIDC** | ❌ | ✅ |
| **Multi-tenancy** | ❌ | ✅ |
| **SLA guarantees** | ❌ | ✅ |
| Conductor Skills (agent plugins) | Via CLI | ✅ Enhanced |

## Orkes-Specific CLI Commands

These commands require Orkes Conductor (cloud or private):

```bash
# Schedules — cron-based workflow triggers
conductor schedule list
conductor schedule create schedule.json
conductor schedule pause {name}
conductor schedule resume {name}
conductor schedule delete {name}

# Secrets — encrypted key-value store
conductor secret list
conductor secret get {name}
conductor secret put {name} {value}
conductor secret delete {name}

# Webhooks — inbound HTTP triggers
conductor webhook list
conductor webhook create webhook.json
conductor webhook update webhook.json
conductor webhook delete {name}
```

## Orkes Developer Edition

Orkes provides a **free Developer Edition** at https://developer.orkescloud.com — full Orkes Conductor feature set available for development and testing. This is the recommended sandbox environment for building Conductor workflows before deploying OSS self-hosted.

### Developer Edition Access

1. Sign up at https://orkes.io/free-developer-edition
2. Generate access keys: **Access Control** → **Applications** → **+ Create application**
3. Enable roles: **Worker** (execute tasks), **Metadata API** (create/update definitions)
4. Copy `Key ID`, `Key Secret`, `Server URL`
5. Set environment:
   ```bash
   export CONDUCTOR_SERVER_URL="https://developer.orkescloud.com/api"
   export CONDUCTOR_AUTH_KEY="<Key ID>"
   export CONDUCTOR_AUTH_SECRET="<Key Secret>"
   ```

## Orkes Conductor MCP Server Config

For Orkes cloud endpoint (same package as OSS, different server URL):

```json
{
  "CONDUCTOR_SERVER_URL": "https://developer.orkescloud.com/api",
  "CONDUCTOR_AUTH_KEY": "<YOUR_APPLICATION_AUTH_KEY>",
  "CONDUCTOR_AUTH_SECRET": "<YOUR_APPLICATION_SECRET_KEY>"
}
```

## Conductor Skills (Agent Plugins)

Orkes maintains an official skill set for AI development agents. Available via the Conductor CLI:

```bash
# Install all conductor agent skills
curl -sSL https://conductor-oss.github.io/conductor-skills/install.sh | bash -s -- --all

# Upgrade existing skills
curl -sSL https://conductor-oss.github.io/conductor-skills/install.sh | bash -s -- --all --upgrade

# Claude Code plugin
/plugin marketplace add conductor-oss/conductor-skills
/plugin install conductor@conductor-skills
```

## Anti-Gravity MCP Integration

Anti-Gravity provides an official Conductor MCP server that targets both OSS and Orkes REST APIs:

- URL: https://antigravity.codes/mcp/conductor
- Supports: workflow creation, execution, monitoring, task signaling
- Compatible with: any MCP client (Claude Desktop, Cursor, Anti-Gravity IDE)

## Orkes Documentation

- Main docs: https://orkes.io/content/
- API reference: https://orkes.io/content/apis
- Tutorials: https://orkes.io/content/tutorials
- Blog: https://orkes.io/blog

## Platform Decision

MCP_PLATFORM targets **Conductor OSS** for self-hosted deployment. Orkes Developer Edition is used for development/testing (free tier). Migration to Orkes Private Cloud is evaluated post-gate if the team requires schedules, secrets management, or enhanced RBAC.
