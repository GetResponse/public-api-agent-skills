# GetResponse Public API — AI Skills

[![Agent Skills standard](https://img.shields.io/badge/standard-SKILL.md-blue)](https://agentskills.io)
[![GetResponse API](https://img.shields.io/badge/API-GetResponse%20v3-00baff)](https://apireference.getresponse.com/)

**AI agent skills** for the [GetResponse public API](https://apireference.getresponse.com/).

Each skill is a self-contained package — instructions, an AI-optimized API spec, references,
and worked examples — describing how an AI agent can perform operations against the GetResponse
public API safely and reliably, with rate-limit handling and clear usage examples.

All skills follow the [Agent Skills (SKILL.md) standard](https://agentskills.io) and are
compatible with [skills.sh](https://skills.sh) and any SKILL.md-compatible agent platform.

---

## Table of contents

- [What's in this repo](#whats-in-this-repo)
- [Available skills](#available-skills)
- [Installation](#installation)
    - [Install via skills.sh](#install-via-skillssh)
    - [Claude / Anthropic](#claude--anthropic)
    - [Manual (any SKILL.md-compatible agent)](#manual-any-skillmd-compatible-agent)
- [Usage examples](#usage-examples)
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

### Install via skills.sh

The easiest way is the [skills.sh](https://skills.sh) CLI, which installs skills directly from
this GitHub repository into 70+ agents (Claude Code, Codex, Cursor, OpenCode, Gemini CLI,
GitHub Copilot, and more):

```bash
# install all skills from this repo (interactive picker)
npx skills add GetResponse/public-api-agent-skills

# install a specific skill
npx skills add GetResponse/public-api-agent-skills --skill getresponse-newsletter-skill

# preview the skills in this repo without installing
npx skills add GetResponse/public-api-agent-skills --list
```

### Claude / Anthropic
Copy the skill directory into your project's `.claude/skills/` folder:

```bash
cp -r getresponse-newsletter-skill/ /your-project/.claude/skills/
```

### Manual (any SKILL.md-compatible agent)
Copy the skill directory to wherever your agent loads skills from. The agent reads `SKILL.md`
and uses the bundled `openapi.json`, `references/`, and `assets/`.

---

## Usage examples

Once the skill is installed and your API key is configured, you can talk to the agent in plain language. Below are example prompts you can use.

**Add contacts and send a newsletter to a whole campaign:**
> Add these contacts to my "Q2-Leads" campaign. Each has a "department" field. Then send them an HTML newsletter with subject "Welcome to Q2".

**Send a newsletter only to a filtered segment:**
> Send a newsletter to all contacts in the "Engineering" department. HTML content: `<h1>Tech Update</h1><p>See what's new.</p>`

**Import a large list of contacts (2500+):**
> Import the attached list of 2500 contacts into my "Newsletter" campaign.

**Schedule a newsletter for a future date:**
> Send a monthly newsletter to the "June-2026" campaign on June 1st at 9:00 AM Warsaw time. Use this HTML: `<h1>Monthly Update</h1><p>Here's what happened this month.</p>`

**Create a new campaign:**
> Create a new contact list called "Product-Updates" and add john@example.com to it.

**Check sending limits before a bulk send:**
> What are my current sending limits before I send a newsletter to 50 000 contacts?

---

## Authentication

The skills authenticate with a GetResponse API key. Provide your key when the agent prompts for it:

```
X-Auth-Token: api-key YOUR_API_KEY
```

Get your API key from: **GetResponse Dashboard → Account → Integrations → API**.
