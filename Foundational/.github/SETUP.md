# GitHub Actions Setup Guide

This guide explains how to configure GitHub Actions workflows for both QueryMindAI and QueryMindIngestion projects.

## Overview

The repository includes two CI/CD workflows:
- **QueryMindAI CI/CD** (`.github/workflows/querymindai-ci.yml`)
- **QueryMindIngestion CI/CD** (`.github/workflows/querymindingestion-ci.yml`)

## Required GitHub Secrets

To enable full CI/CD functionality, you need to configure the following secrets in your GitHub repository:

### Repository Secrets

Go to: **Settings → Secrets and variables → Actions → New repository secret**

#### Docker Registry Secrets (Required for Docker builds)

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `DOCKER_USERNAME` | Docker Hub or registry username | `yourusername` |
| `DOCKER_PASSWORD` | Docker Hub or registry password/token | `dckr_pat_...` |
| `DOCKER_REGISTRY` | Docker registry URL (optional, defaults to Docker Hub) | `docker.io` or `ghcr.io` |

#### Production Deployment Secrets (Required for auto-deployment)

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `PRODUCTION_HOST` | Production server hostname or IP | `example.com` or `192.168.1.100` |
| `PRODUCTION_USER` | SSH username for production server | `deploy` |
| `PRODUCTION_SSH_KEY` | Private SSH key for production server | `-----BEGIN RSA PRIVATE KEY-----...` |
| `PRODUCTION_PATH` | Path to application on production server | `/var/www/querymindai` |
| `PRODUCTION_URL` | Production application URL | `https://app.example.com` |
| `INGESTION_PRODUCTION_PATH` | Path to ingestion tool on production server | `/var/www/querymindingestion` |
| `INGESTION_PRODUCTION_URL` | Production ingestion service URL (if applicable) | `https://ingestion.example.com` |

#### Testing Secrets (Optional, for integration tests)

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `TEST_MONGODB_URI` | MongoDB URI for testing | `mongodb://localhost:27017/test` |

#### Monitoring/Notification Secrets (Optional)

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `SNYK_TOKEN` | Snyk API token for security scanning | `snyk_token_here` |
| `SLACK_WEBHOOK_URL` | Slack webhook URL for notifications | `https://hooks.slack.com/services/...` |

## Setting Up Secrets

### 1. Docker Registry Setup

**For Docker Hub:**
1. Go to Docker Hub → Account Settings → Security
2. Generate an access token
3. Add as `DOCKER_PASSWORD` secret

**For GitHub Container Registry:**
1. Use `ghcr.io` as registry
2. Use GitHub Personal Access Token with `write:packages` permission
3. Username is your GitHub username

### 2. Production Server SSH Setup

**Generate SSH Key Pair:**
```bash
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions
```

**Add Public Key to Production Server:**
```bash
ssh-copy-id -i ~/.ssh/github_actions.pub user@production-server
```

**Add Private Key to GitHub Secrets:**
```bash
cat ~/.ssh/github_actions
# Copy the entire output including -----BEGIN and -----END lines
# Paste as PRODUCTION_SSH_KEY secret
```

### 3. Snyk Security Scanning (Optional)

1. Sign up at [snyk.io](https://snyk.io)
2. Go to Settings → API Token
3. Copy token and add as `SNYK_TOKEN` secret

### 4. Slack Notifications (Optional)

1. Go to Slack → Apps → Incoming Webhooks
2. Create webhook for your channel
3. Copy webhook URL and add as `SLACK_WEBHOOK_URL` secret

## Workflow Features

### QueryMindAI Workflow

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Only runs when files in `QueryMindAI/` change

**Jobs:**
1. **Lint**: ESLint and TypeScript type checking
2. **Test**: Run test suite with coverage
3. **Build**: Build application
4. **Docker Build**: Build and push Docker image (on push to main/develop)
5. **Security Scan**: npm audit and Snyk scanning
6. **Deploy**: Deploy to production (only on push to main)

### QueryMindIngestion Workflow

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual workflow dispatch
- Only runs when files in `QueryMindIngestion/` change

**Jobs:**
1. **Lint**: flake8, black, isort checks
2. **Test**: Run tests on Python 3.9, 3.10, 3.11
3. **Integration Test**: Test with MongoDB and Ollama services
4. **Security Scan**: Safety and Bandit scanning
5. **Docker Build**: Build and push Docker image (on push to main/develop)
6. **Deploy**: Deploy to production (only on push to main)

## Workflow Customization

### Disable Auto-Deployment

If you don't want automatic deployment, you can:

1. **Remove the deploy job** from workflows
2. **Comment out the deploy step** in the workflow file
3. **Use manual workflow dispatch** for deployment

### Change Deployment Target

Edit the workflow files and update:
- `PRODUCTION_HOST` secret reference
- Deployment commands in the deploy job
- Environment URLs

### Add Additional Environments

Create environment-specific workflows or add environments:

```yaml
environment:
  name: staging
  url: ${{ secrets.STAGING_URL }}
```

Then add corresponding secrets:
- `STAGING_HOST`
- `STAGING_USER`
- `STAGING_SSH_KEY`
- etc.

## Testing Workflows Locally

### Using act (GitHub Actions locally)

```bash
# Install act
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Run workflow locally
act -j lint
act -j test
```

### Manual Testing

Test individual workflow steps:

```bash
# Lint
cd QueryMindAI && npm run lint

# Test
cd QueryMindAI && npm test

# Build
cd QueryMindAI && npm run build
```

## Troubleshooting

### Workflow Not Running

1. Check if files changed are in the correct paths
2. Verify branch names match workflow triggers
3. Check workflow file syntax (YAML)

### Docker Build Fails

1. Verify Docker secrets are set correctly
2. Check Docker registry permissions
3. Verify Dockerfile exists and is correct

### Deployment Fails

1. Verify SSH key is correct
2. Check server accessibility
3. Verify deployment path exists
4. Check server permissions

### Tests Fail

1. Check test environment setup
2. Verify test dependencies
3. Review test logs in workflow output

## Best Practices

1. **Use Environment Secrets**: For production, use environment-specific secrets
2. **Rotate Secrets Regularly**: Update passwords and tokens periodically
3. **Limit Secret Access**: Only grant necessary permissions
4. **Monitor Workflow Runs**: Set up notifications for failures
5. **Review Workflow Logs**: Regularly check for issues
6. **Test Before Merging**: Ensure workflows pass on feature branches

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Hub Documentation](https://docs.docker.com/docker-hub/)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)

---

**Note**: Keep secrets secure and never commit them to the repository. Always use GitHub Secrets for sensitive information.

