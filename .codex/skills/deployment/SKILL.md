---
name: deployment
description: Use for preparing safe deployment to Vercel/Sites or other hosting, with environment checks and no secret leakage.
---

# Deployment Skill

Use this skill when preparing a web report, dashboard, or API for deployment.

## Rules

1. Deployment must have a plan first.
2. Never commit secrets or tokens.
3. Check environment variables, build command, output directory, and rollback path.
4. Use Vercel only after login is confirmed.
5. Do not publish sensitive trading data unless explicitly approved.

## Output

- Deployment target
- Required secrets
- Build command
- Rollback method
- Confirmation needed
