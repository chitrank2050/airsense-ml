# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| 0.x.x | ✅ |

## Reporting a Vulnerability

Please do not report security vulnerabilities via public GitHub issues.

Use GitHub's built-in vulnerability reporting:
1. Go to the Security tab on this repository
2. Click "Report a vulnerability"
3. Fill in the details

You will receive a response within 48 hours.

## Scope

This project is a learning/portfolio ML system. Known limitations:

- No authentication on API endpoints — do not deploy with sensitive data
- Rate limiting is basic — not suitable for high-traffic production without additional infrastructure
- Model predictions are probabilistic — not suitable for safety-critical decisions