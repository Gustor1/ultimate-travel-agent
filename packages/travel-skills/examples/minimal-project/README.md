# Minimal Project Example

This directory demonstrates a minimal Antigravity-compatible workspace before or after installing `travel-skills`.

## Structure

```text
minimal-project/
├── .agents/
│   └── skills/
│       └── custom-logging/       <-- Pre-existing project skill
│           └── SKILL.md
└── README.md
```

## Installing Travel Skills into this Project

From the root of `ultimate-travel-agent`:

```bash
# Using CLI
ultimate-travel-agent install-skills --target ./packages/travel-skills/examples/minimal-project

# Or using the installer script directly
python packages/travel-skills/install.py --target ./packages/travel-skills/examples/minimal-project
```

The installer copies the 6 travel skills into `.agents/skills/` without touching `custom-logging`.
