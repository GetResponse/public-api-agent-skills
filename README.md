# GetResponse Public API — AI Skills

**AI agent skills** for the [GetResponse public API](https://apireference.getresponse.com/).

Each skill is a self-contained package — instructions, an AI-optimized API spec, references,
and worked examples — describing how an AI agent can perform operations against the GetResponse
public API safely and reliably, with rate-limit handling and clear usage examples.

All skills follow the [Agent Skills (SKILL.md) standard](https://agentskills.io) and are
compatible with [skills.sh](https://skills.sh), [SkillsMP](https://skillsmp.com), and any
SKILL.md-compatible agent platform.

---

## Table of contents

- [What's in this repo](#whats-in-this-repo)
- [Available skills](#available-skills)
- [Installation](#installation)
- [Authentication](#authentication)

---

## What's in this repo

This repository contains one directory per skill. Each skill is independent and includes
everything an agent needs to use it:

```
.
└── getresponse-newsletter-skill/
    ├── SKILL.md          # Manifest + step-by-step workflow instructions
    ├── openapi.json      # AI-optimized GetResponse API spec
    ├── references/       # Detailed API reference (auth, limits, payloads, errors)
    └── assets/           # Worked examples for the main use cases
```

---

## Available skills

| Skill | What it does |
|---|---|
| [`getresponse-newsletter-skill`](getresponse-newsletter-skill/) | Manage contacts and send HTML newsletters via the GetResponse API v3. Finds or creates campaigns (contact lists) and custom fields, adds contacts (single or bulk import up to 1000 per request), verifies asynchronous imports, and sends HTML newsletters to a whole campaign or to a segment filtered by custom field values — including scheduled sends. Rate-limit aware (honors `X-RateLimit-*` and HTTP 429 `Retry-After`). |

---

## Installation

Pick the method that matches your agent platform.

### Claude / Anthropic
Copy the skill directory into your project's `.claude/skills/` folder:

```bash
cp -r getresponse-newsletter-skill/ /your-project/.claude/skills/
```

### Manual (any SKILL.md-compatible agent)
Copy the skill directory to wherever your agent loads skills from. The agent reads `SKILL.md`
and uses the bundled `openapi.json`, `references/`, and `assets/`.

---

## Authentication

The skills authenticate with a GetResponse API key. Provide your key when the agent prompts for it:

```
X-Auth-Token: api-key YOUR_API_KEY
```

Get your API key from: **GetResponse Dashboard → Account → Integrations → API**.
