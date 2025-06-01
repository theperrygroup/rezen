# Security Policy

## Supported Versions

We actively support and provide security updates for the following versions of the ReZEN Python client:

| Version | Supported          |
| ------- | ------------------ |
| 1.1.x   | :white_check_mark: |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability in the ReZEN Python client, please follow these steps:

### 1. Do Not Create a Public Issue

Please **do not** create a GitHub issue for security vulnerabilities. This helps ensure that the vulnerability is not exploited before a fix is available.

### 2. Report via Email

Send a detailed report to: **security@theperrygroup.com**

Include the following information:
- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact of the vulnerability
- Any suggested fixes or mitigations
- Your contact information for follow-up

### 3. Response Timeline

We commit to responding to security reports according to the following timeline:

- **Initial Response**: Within 48 hours of receiving the report
- **Assessment**: Within 5 business days, we'll provide an assessment of the vulnerability
- **Fix Development**: Critical vulnerabilities will be addressed within 7 business days
- **Disclosure**: After a fix is available, we'll coordinate disclosure with the reporter

### 4. Disclosure Process

1. We'll work with you to understand and validate the vulnerability
2. We'll develop and test a fix
3. We'll prepare a security advisory
4. We'll release the fix in a new version
5. We'll publish the security advisory with appropriate credits

## Security Best Practices

When using the ReZEN Python client:

### API Key Security
- **Never commit API keys** to version control
- Use environment variables or secure configuration management
- Rotate API keys regularly
- Use the minimum required permissions

### Network Security
- Always use HTTPS endpoints
- Validate SSL/TLS certificates
- Consider using VPN or private networks for sensitive operations

### Data Handling
- Follow data minimization principles
- Encrypt sensitive data at rest and in transit
- Implement proper access controls
- Regular security audits of your implementation

## Dependencies

We regularly monitor our dependencies for security vulnerabilities using:
- GitHub Security Advisories
- Safety (Python package vulnerability scanner)
- Dependabot for automated security updates

## Security Testing

Our CI pipeline includes:
- Static analysis with flake8 and mypy
- Dependency vulnerability scanning with safety
- Automated testing across multiple Python versions

## Contact

For security-related questions or concerns:
- Email: security@theperrygroup.com
- For general issues: https://github.com/theperrygroup/rezen/issues

## Acknowledgments

We appreciate the security community's efforts in responsible disclosure. Security researchers who responsibly report vulnerabilities will be acknowledged in our security advisories (with permission).
