# ForgeWeb CI/CD Templates

This directory contains GitHub Actions workflow templates for ForgeWeb deployments and operations.

## Workflow Files

### 🚀 `github-pages-deploy.yml`
**Purpose**: Deploy ForgeWeb sites to GitHub Pages
**Trigger**: Push to main branch, manual dispatch
**Features**:
- Validates site structure and configuration
- Handles fresh setups with placeholder content
- Deploys static content to GitHub Pages
- Configures Pages environment automatically

**Usage**:
```bash
# Copy to your repository
cp ci/github-pages-deploy.yml .github/workflows/deploy.yml
git add .github/workflows/deploy.yml
git commit -m "Add GitHub Pages deployment"
git push
```

### 🐳 `docker-build.yml`  
**Purpose**: Build and publish ForgeWeb Docker images
**Trigger**: Push to main, tags, pull requests
**Features**:
- Multi-platform Docker builds
- Publishes to GitHub Container Registry
- Generates Software Bill of Materials (SBOM)
- Semantic versioning support

**Usage**:
```bash
# Copy for Docker deployments
cp ci/docker-build.yml .github/workflows/docker.yml
```

### 🧪 `test-and-qa.yml`
**Purpose**: Comprehensive testing and quality assurance
**Trigger**: Push, pull requests
**Features**:
- Multi-version Python testing (3.8-3.11)
- Code quality checks (flake8, black, isort)
- Security scanning (safety, bandit, trufflehog)
- Accessibility testing with axe-core
- Performance and compatibility checks

**Usage**:
```bash
# Copy for quality assurance
cp ci/test-and-qa.yml .github/workflows/test.yml
```

## Setup Instructions

### For Site Deployment (GitHub Pages)

1. **Enable GitHub Pages**
   ```bash
   # In your repository settings:
   # Settings → Pages → Source: GitHub Actions
   ```

2. **Copy Workflow**
   ```bash
   mkdir -p .github/workflows
   cp ci/github-pages-deploy.yml .github/workflows/deploy.yml
   ```

3. **Configure Site**
   - Edit `admin/site-config.json` with your site details
   - Create content using ForgeWeb admin interface
   - Commit and push changes

### For Docker Deployment

1. **Copy Docker Workflow**
   ```bash
   cp ci/docker-build.yml .github/workflows/docker.yml
   ```

2. **Configure Container Registry**
   - GitHub Container Registry is used by default
   - Images published to `ghcr.io/username/repository`
   - Requires no additional configuration

### For Quality Assurance

1. **Copy QA Workflow**
   ```bash
   cp ci/test-and-qa.yml .github/workflows/test.yml
   ```

2. **Optional: Add Additional Tools**
   - Configure additional security scanners
   - Add performance benchmarks
   - Customize accessibility tests

## Workflow Customization

### Environment Variables
```yaml
env:
  FORGEWEB_CONFIG: custom-config.json  # Custom configuration file
  PYTHON_VERSION: "3.11"              # Default Python version
  NODE_VERSION: "18"                  # Node.js version for tools
```

### Site Configuration
```yaml
- name: Validate site configuration
  run: |
    # Add custom validation rules
    python scripts/validate-config.py
```

### Custom Deployment Targets
```yaml
- name: Deploy to custom hosting
  run: |
    # Add deployment to other platforms
    rsync -av ./ user@host:/path/to/site/
```

## Advanced Configurations

### Multi-Environment Deployment
```yaml
strategy:
  matrix:
    environment: [staging, production]
    include:
      - environment: staging
        url: https://staging.example.com
      - environment: production
        url: https://example.com
```

### Scheduled Builds
```yaml
on:
  schedule:
    # Rebuild every day at 2 AM UTC
    - cron: '0 2 * * *'
```

### Dependency Caching
```yaml
- name: Cache dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

## Security Considerations

### Secret Management
- Use GitHub Secrets for API keys
- Never commit sensitive information
- Use environment-specific configurations

```yaml
env:
  AI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  CUSTOM_DOMAIN: ${{ secrets.PRODUCTION_DOMAIN }}
```

### Permission Management
```yaml
permissions:
  contents: read      # Read repository content
  pages: write       # Deploy to GitHub Pages
  id-token: write    # OIDC token for authentication
  packages: write    # Publish to registries
```

## Monitoring and Notifications

### Slack Notifications
```yaml
- name: Notify Slack
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: failure
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Email Notifications
```yaml
- name: Send email notification
  if: success()
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: "ForgeWeb deployed successfully"
    body: "Site deployed to ${{ steps.deployment.outputs.page_url }}"
```

## Troubleshooting

### Common Issues

**Deployment fails with permission error**
```bash
# Check repository permissions
# Settings → Actions → General → Workflow permissions
# Select "Read and write permissions"
```

**Docker build fails**
```bash
# Check Dockerfile path in workflow
# Ensure ops/Dockerfile exists
# Verify base image availability
```

**Tests fail on Python version**
```bash
# Check Python compatibility
# Update requirements.txt for specific versions
# Use version-specific conditionals in tests
```

### Debug Mode
```yaml
- name: Debug information
  run: |
    echo "Runner OS: ${{ runner.os }}"
    echo "GitHub Actor: ${{ github.actor }}"
    echo "Repository: ${{ github.repository }}"
    echo "Event: ${{ github.event_name }}"
    ls -la
    env | sort
```

## Best Practices

1. **Version Control**
   - Tag releases with semantic versioning
   - Use branch protection rules
   - Require status checks before merging

2. **Testing Strategy**
   - Run tests on multiple Python versions
   - Test in clean environments
   - Validate configuration files

3. **Security**
   - Scan for vulnerabilities regularly
   - Keep dependencies updated
   - Use minimal container images

4. **Performance**
   - Optimize build times with caching
   - Use parallel jobs when possible
   - Monitor resource usage

---

**Need help with CI/CD?** Check the [GitHub Actions documentation](https://docs.github.com/actions) or get [support](https://buildly.io/support).