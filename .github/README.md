# 🚀 GitHub Actions & Automation

This folder contains GitHub Actions workflows and templates for the Space Debris Risk Assessment project.

## 📂 Structure

```
.github/
├── workflows/
│   ├── ci-cd.yml           # Main CI/CD pipeline
│   ├── cross-platform.yml # Multi-platform testing
│   └── release.yml         # Release automation
├── ISSUE_TEMPLATE/
│   ├── bug_report.md       # Bug report template
│   └── feature_request.md  # Feature request template
├── pull_request_template.md # PR template
├── SECRETS.md              # Secrets configuration guide
└── README.md              # This file
```

## 🔄 Workflows

### 1. 🚀 CI/CD Pipeline (`ci-cd.yml`)
**Triggers:** Push to main/develop, Pull requests, Manual dispatch

**Jobs:**
- **🧪 Test**: Runs comprehensive application tests
- **🏗️ Build**: Creates build artifacts and test reports
- **🌊 Deploy Azure**: Deploys to Azure ML (main branch only)
- **🔒 Security**: Scans dependencies for vulnerabilities
- **⚡ Performance**: Benchmarks application performance

### 2. 🌐 Cross-Platform Testing (`cross-platform.yml`)
**Triggers:** Push, Pull requests, Weekly schedule

**Features:**
- Tests on Ubuntu, Windows, and macOS
- Multiple Python versions (3.9-3.12)
- TLE data validation
- Risk calculation verification
- Performance benchmarking

### 3. 🎯 Release Deployment (`release.yml`)
**Triggers:** GitHub releases, Manual dispatch

**Features:**
- Creates release packages
- Generates comprehensive release notes
- Uploads release assets
- Automated version management

## 🎭 Templates

### 🐛 Bug Reports
Structured template for reporting issues with:
- Environment details
- Reproduction steps
- TLE data context
- Error messages

### 🚀 Feature Requests
Template for suggesting enhancements:
- Problem statement
- Proposed solution
- Space debris context
- Technical considerations

### 📝 Pull Requests
Comprehensive PR template covering:
- Change description
- Testing requirements
- Space debris impact
- Review checklist

## 🔐 Security & Secrets

See [`SECRETS.md`](SECRETS.md) for:
- Required Azure credentials
- Secret configuration steps
- Security best practices
- Troubleshooting guide

## 🎯 Usage Examples

### Running Tests Manually
```bash
# Trigger CI/CD pipeline
gh workflow run ci-cd.yml

# Run cross-platform tests
gh workflow run cross-platform.yml

# Create a release
gh workflow run release.yml -f version=v1.0.0
```

### Creating Issues
Use the issue templates to report bugs or request features with all necessary context.

### Pull Request Workflow
1. Create feature branch
2. Make changes
3. Use PR template
4. Automated tests run
5. Review and merge

## 📊 Monitoring

### Build Status
- ✅ All tests pass before deployment
- 🔒 Security scans completed
- ⚡ Performance benchmarks within limits
- 🌐 Cross-platform compatibility verified

### Deployment Status
- 🌊 Azure ML deployment successful
- 🧪 Endpoint testing completed
- 📊 Performance metrics collected
- 🚨 Alerts configured for failures

## 🛠️ Customization

To modify workflows:
1. Edit YAML files in `workflows/`
2. Test changes on feature branches
3. Monitor workflow runs
4. Update documentation as needed

## 🔍 Troubleshooting

**Common Issues:**
- Missing Azure secrets → See SECRETS.md
- Test failures → Check dependencies and Python version
- Deployment errors → Verify Azure resource access
- Performance issues → Review benchmark thresholds