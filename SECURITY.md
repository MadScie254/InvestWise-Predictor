# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

The InvestWise Predictor team takes security bugs seriously. We appreciate your efforts to responsibly disclose your findings, and will make every effort to acknowledge your contributions.

### How to Report a Security Vulnerability

1. **Do not open an issue** for security-related concerns
2. Email the security team directly at: **security@investwise.com** (or repository maintainer if this email doesn't exist)
3. Include the following information:
   - Description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact
   - Any suggested fixes (if available)

### What to Expect

- **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 48 hours
- **Updates**: We will provide regular updates on our progress every 5-7 days
- **Resolution**: We aim to resolve critical vulnerabilities within 30 days

## Security Best Practices

### Environment Variables and Secrets

1. **Never commit secrets to version control**
   - Use `.env.example` as a template
   - Copy to `.env` and populate with real values
   - Ensure `.env` is in `.gitignore`

2. **Required Environment Variables**
   ```bash
   # Django Security
   DJANGO_SECRET_KEY=your-super-secret-key-minimum-50-chars
   DJANGO_DEBUG=False  # Always False in production
   
   # Database
   DJANGO_DATABASE_URL=postgres://user:password@host:port/database
   
   # Security Keys
   DATA_ENCRYPTION_KEY=your-encryption-key
   ```

3. **Secret Key Requirements**
   - Minimum 50 characters
   - Use cryptographically random values
   - Rotate keys regularly (quarterly recommended)
   - Different keys for each environment

### Key Rotation Procedures

1. **Django Secret Key Rotation**
   ```bash
   # Generate new secret key
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   
   # Update environment variable
   export DJANGO_SECRET_KEY="new-secret-key"
   
   # Restart application
   ```

2. **Database Password Rotation**
   - Update password in database system
   - Update `DJANGO_DATABASE_URL` environment variable
   - Restart application gracefully

3. **API Key Rotation**
   - Generate new keys from service providers
   - Update environment variables
   - Test API connectivity
   - Revoke old keys after verification

### Production Security Checklist

- [ ] `DEBUG = False` in production
- [ ] Strong, unique `SECRET_KEY` (minimum 50 characters)
- [ ] HTTPS enforced (`SECURE_SSL_REDIRECT = True`)
- [ ] Secure cookies (`SESSION_COOKIE_SECURE = True`, `CSRF_COOKIE_SECURE = True`)
- [ ] Database credentials secured and rotated
- [ ] All API keys stored in environment variables
- [ ] Error reporting configured (but not exposing sensitive data)
- [ ] Regular security updates applied
- [ ] Rate limiting implemented
- [ ] Input validation on all endpoints
- [ ] SQL injection protection (using Django ORM)
- [ ] CSRF protection enabled
- [ ] CORS properly configured

### Database Security

1. **Connection Security**
   - Use SSL connections for databases
   - Restrict database access by IP
   - Use connection pooling
   - Regular backup encryption

2. **Data Protection**
   - Encrypt sensitive data at rest
   - Use Django's built-in password hashing
   - Implement data retention policies
   - Regular security audits

### API Security

1. **Authentication**
   - JWT tokens with short expiration
   - Secure token storage on client side
   - Token rotation mechanisms
   - Rate limiting on auth endpoints

2. **Authorization**
   - Principle of least privilege
   - Resource-level permissions
   - Regular permission audits

### Deployment Security

1. **Environment Separation**
   - Separate environments (dev, staging, prod)
   - Different credentials for each environment
   - Network isolation

2. **Monitoring**
   - Security event logging
   - Failed authentication monitoring
   - Unusual activity detection
   - Regular security scans

### Dependencies

1. **Regular Updates**
   - Monthly dependency updates
   - Security patch priority
   - Automated vulnerability scanning

2. **Vulnerability Management**
   ```bash
   # Check for vulnerabilities
   pip-audit
   safety check
   bandit -r .
   ```

## Security Headers

Ensure the following security headers are configured:

```python
# In production settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

## Incident Response

1. **Immediate Response**
   - Assess the scope of the security incident
   - Contain the issue (disable affected systems if necessary)
   - Document the incident

2. **Investigation**
   - Determine root cause
   - Assess data impact
   - Check for related vulnerabilities

3. **Recovery**
   - Apply security patches
   - Restore from clean backups if necessary
   - Update security measures

4. **Post-Incident**
   - Conduct post-mortem
   - Update security procedures
   - Communicate with stakeholders

## Contact Information

- Security Team: security@investwise.com
- Emergency Contact: +1-XXX-XXX-XXXX
- PGP Key: [Link to public key if available]

## Acknowledgments

We thank the following researchers for their responsible disclosure:

- [List of researchers who reported vulnerabilities]

---

**Last Updated**: [Current Date]
**Version**: 1.0