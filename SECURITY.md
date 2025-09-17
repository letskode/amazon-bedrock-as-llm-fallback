# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly:

1. **Do NOT open a public issue** for security vulnerabilities
2. **Email the maintainer** directly with details
3. **Include** steps to reproduce the vulnerability
4. **Provide** your assessment of the impact

## Security Best Practices

When using this project:

### API Key Management
- **Never commit API keys** to version control
- **Use environment variables** for all credentials
- **Rotate API keys** regularly
- **Use IAM roles** instead of access keys when possible (for AWS)

### AWS Security
- **Enable CloudTrail** for audit logging
- **Use VPC endpoints** for Bedrock access when possible
- **Follow principle of least privilege** for IAM permissions
- **Monitor API usage** and set up billing alerts

### Production Deployment
- **Use secrets management** services (AWS Secrets Manager, etc.)
- **Enable request logging** for monitoring
- **Set up rate limiting** to prevent abuse
- **Monitor for unusual usage patterns**
- **Keep dependencies updated**

## Required IAM Permissions

Minimum required permissions for Bedrock access:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": [
                "arn:aws:bedrock:*::foundation-model/anthropic.claude*",
                "arn:aws:bedrock:*::foundation-model/meta.llama*",
                "arn:aws:bedrock:*::foundation-model/us.anthropic.claude*",
                "arn:aws:bedrock:*::foundation-model/us.meta.llama*"
            ]
        }
    ]
}
```

## Known Security Considerations

1. **API Rate Limits**: Respect provider rate limits to avoid service disruption
2. **Error Logging**: Be careful not to log sensitive data in error messages
3. **Network Security**: Use HTTPS for all API communications (handled by SDKs)
4. **Input Validation**: Validate user inputs before sending to AI models
5. **Response Filtering**: Consider filtering AI responses for sensitive content

## Updates

This security policy will be updated as needed. Check back regularly for updates.