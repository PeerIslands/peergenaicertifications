# GitHub Actions Workflows

This directory contains CI/CD workflows for the QueryMindAI projects.

## Workflows

### QueryMindAI CI/CD
**File**: `workflows/querymindai-ci.yml`

Automated CI/CD pipeline for the QueryMindAI web application:
- ✅ Linting and type checking
- ✅ Unit tests with coverage
- ✅ Application build
- ✅ Docker image build and push
- ✅ Security scanning
- ✅ Production deployment (on main branch)

### QueryMindIngestion CI/CD
**File**: `workflows/querymindingestion-ci.yml`

Automated CI/CD pipeline for the PDF ingestion tool:
- ✅ Code linting and formatting checks
- ✅ Unit tests (Python 3.9, 3.10, 3.11)
- ✅ Integration tests with MongoDB and Ollama
- ✅ Security scanning
- ✅ Docker image build and push
- ✅ Production deployment (on main branch)

## Quick Start

1. **Set up GitHub Secrets** (see [SETUP.md](./SETUP.md))
2. **Push to main/develop** to trigger workflows
3. **Monitor workflow runs** in the Actions tab

## Documentation

- **[SETUP.md](./SETUP.md)**: Complete setup guide for GitHub Actions
- **[../QueryMindAI/DEPLOYMENT.md](../QueryMindAI/DEPLOYMENT.md)**: Production deployment guide for QueryMindAI
- **[../QueryMindIngestion/DEPLOYMENT.md](../QueryMindIngestion/DEPLOYMENT.md)**: Production deployment guide for QueryMindIngestion

## Workflow Status

View workflow status badges in your README:

```markdown
![CI](https://github.com/your-org/your-repo/workflows/QueryMindAI%20CI%2FCD/badge.svg)
![CI](https://github.com/your-org/your-repo/workflows/QueryMindIngestion%20CI%2FCD/badge.svg)
```

## Support

For issues or questions:
1. Check workflow logs in GitHub Actions
2. Review [SETUP.md](./SETUP.md) for configuration
3. Check deployment guides for environment setup

