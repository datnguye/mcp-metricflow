# Security Policy

## Table of Contents

- [Security Policy](#security-policy)
  - [Table of Contents](#table-of-contents)
  - [Supported Versions](#supported-versions)
  - [Reporting a Vulnerability](#reporting-a-vulnerability)
    - [1. Do NOT create a public issue](#1-do-not-create-a-public-issue)
    - [2. Report privately](#2-report-privately)
    - [3. Include detailed information](#3-include-detailed-information)
    - [4. Response timeline](#4-response-timeline)
  - [Security Best Practices](#security-best-practices)
    - [API Key Security](#api-key-security)
    - [Environment Configuration](#environment-configuration)
    - [Network Security](#network-security)
    - [Data Protection](#data-protection)
  - [Known Security Considerations](#known-security-considerations)
    - [SSE Server](#sse-server)
    - [MetricFlow Integration](#metricflow-integration)
    - [Dependencies](#dependencies)
  - [Security Updates](#security-updates)
    - [How we handle security updates](#how-we-handle-security-updates)
    - [Staying informed](#staying-informed)
  - [Responsible Disclosure](#responsible-disclosure)
    - [Hall of Fame](#hall-of-fame)

## Supported Versions

We actively support security updates for the following versions of `mcp-metricflow`:

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |
| < Latest| :x:                |

We recommend always using the latest version to ensure you have the most recent security updates.

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability, please follow these steps:

### 1. Do NOT create a public issue

Please do not report security vulnerabilities through public GitHub issues, discussions, or pull requests.

### 2. Report privately

Instead, please report the vulnerability by:

- **Email**: Send details to [datnguyen.it09@gmail.com](mailto:datnguyen.it09@gmail.com)
- **Subject Line**: Include "SECURITY VULNERABILITY - mcp-metricflow" in the subject
- **GitHub Security Advisories**: Use GitHub's private vulnerability reporting feature (preferred)

### 3. Include detailed information

Please include as much information as possible:

- Type of vulnerability (e.g., authentication bypass, code injection, etc.)
- Step-by-step instructions to reproduce the issue
- Potential impact and attack scenarios
- Any suggested fixes or mitigations
- Your contact information for follow-up questions

### 4. Response timeline

We will acknowledge receipt of your vulnerability report within **48 hours** and provide a more detailed response within **7 days** indicating the next steps in handling your report.

## Security Best Practices

When using `mcp-metricflow`, please follow these security best practices:

### API Key Security
- **Never commit API keys** to version control
- **Use environment variables** for sensitive configuration
- **Rotate API keys regularly**
- **Use strong, unique API keys** for production environments
- **Limit API key permissions** to the minimum required scope

### Environment Configuration
- **Secure your `.env` files** and never commit them to version control
- **Use different API keys** for development, staging, and production
- **Implement proper access controls** for your dbt projects and data warehouse
- **Regularly audit your environment variables** and remove unused keys

### Network Security
- **Use HTTPS** for all SSE server communications
- **Implement proper firewall rules** when exposing the SSE server
- **Consider using a reverse proxy** with additional security features
- **Monitor server logs** for suspicious activity

### Data Protection
- **Validate all inputs** to MetricFlow commands
- **Implement proper authentication** for SSE mode when required
- **Use least privilege principles** for database connections
- **Regular security audits** of your dbt project permissions

## Known Security Considerations

### SSE Server
- The SSE server can be run with or without authentication
- When `MCP_REQUIRE_AUTH=false`, the server accepts all connections
- API keys are transmitted in HTTP headers - ensure HTTPS is used
- The `/health` endpoint is always accessible without authentication

### MetricFlow Integration
- Commands are executed with the permissions of the running user
- Database credentials are inherited from dbt profiles
- Query results may contain sensitive business data

### Dependencies
- Regular dependency updates are performed to address security vulnerabilities
- We use `bandit` for static security analysis
- Pre-commit hooks help prevent common security issues

## Security Updates

### How we handle security updates

1. **Assessment**: We evaluate the severity and impact of reported vulnerabilities
2. **Development**: We develop and test fixes in private repositories
3. **Coordination**: For significant vulnerabilities, we may coordinate with other projects
4. **Release**: We release security updates as quickly as possible
5. **Disclosure**: We publish security advisories after fixes are available

### Staying informed

- **Watch this repository** to receive notifications about security updates
- **Check releases regularly** for security-related updates
- **Subscribe to our security advisories** through GitHub

## Responsible Disclosure

We follow responsible disclosure practices:

- **Coordination**: We work with security researchers to understand and fix vulnerabilities
- **Timeline**: We aim to fix critical vulnerabilities within 30 days
- **Credit**: We provide appropriate credit to security researchers (with their permission)
- **Transparency**: We publish security advisories for significant vulnerabilities

### Hall of Fame

We thank the following security researchers for their responsible disclosure:

<!-- This section will be updated as we receive security reports -->
*No security vulnerabilities have been reported yet.*

---

Thank you for helping keep `mcp-metricflow` and the community safe!
