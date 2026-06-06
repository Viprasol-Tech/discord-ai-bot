# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅        |

## Reporting a vulnerability

Please **do not** open a public issue for security vulnerabilities.

Instead, email **[support@viprasol.com](mailto:support@viprasol.com)** with:

- a description of the issue and its impact,
- steps to reproduce (a proof of concept if possible),
- any suggested remediation.

We aim to acknowledge reports within **3 business days** and to provide a fix or
mitigation timeline after triage. We will credit reporters who wish to be named
once a fix is released.

## Handling secrets

This project never stores credentials in source. Bot tokens and API keys must be
provided via environment variables (see `.env.example`) or a secret manager.
`.env`, `*.pem`, `*.key` and `secrets/` are git-ignored — please keep it that way.
