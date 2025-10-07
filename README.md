# Security Auto Scan Action

<div align="center">

![Security](https://img.shields.io/badge/security-auto--scan-red?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.11-blue?style=for-the-badge)
[![License](https://img.shields.io/github/license/h7ml/security-auto-scan?style=for-the-badge)](LICENSE)
[![GitHub release](https://img.shields.io/github/v/release/h7ml/security-auto-scan?style=for-the-badge)](https://github.com/h7ml/security-auto-scan/releases)
[![GitHub Marketplace](https://img.shields.io/badge/Marketplace-Security%20Auto%20Scan-blue?style=for-the-badge&logo=github)](https://github.com/marketplace/actions/security-auto-scan)

[![GitHub stars](https://img.shields.io/github/stars/h7ml/security-auto-scan?style=social)](https://github.com/h7ml/security-auto-scan/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/h7ml/security-auto-scan?style=social)](https://github.com/h7ml/security-auto-scan/network/members)
[![GitHub watchers](https://img.shields.io/github/watchers/h7ml/security-auto-scan?style=social)](https://github.com/h7ml/security-auto-scan/watchers)
[![GitHub issues](https://img.shields.io/github/issues/h7ml/security-auto-scan)](https://github.com/h7ml/security-auto-scan/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/h7ml/security-auto-scan)](https://github.com/h7ml/security-auto-scan/pulls)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/h7ml/security-auto-scan/test.yml?branch=main&label=tests)](https://github.com/h7ml/security-auto-scan/actions)

**Automatically scan and clean malicious workflow files in GitHub Actions**

[English](./README.md) | [简体中文](./README_zh-CN.md)

</div>

## 📖 Introduction

Security Auto Scan is a GitHub Action that automatically detects and removes malicious workflow files. Features:

- 🔍 **Auto Scan** all your repositories (personal + organizations)
- 🧹 **Auto Clean** detected malicious files
- 🔐 **Log Masking** automatically hide sensitive information using GitHub Actions `::add-mask::`
- 📊 **Generate Reports** detailed scan and cleanup reports
- 🚨 **Create Issues** automatically create alerts when threats are found
- 📢 **Webhook Notifications** support Slack/Discord/Teams/DingTalk/Feishu, etc.
- 💾 **Cache Optimization** avoid duplicate cloning, improve performance by 50-80%
- 🛡️ **Security First** won't delete important files, won't disable itself

## 🎯 Use Cases

### Supply Chain Attack Response

If your GitHub account is compromised, attackers might:

1. Inject malicious workflow files
2. Steal your GitHub Secrets
3. Exfiltrate data through domains like `*.oast.fun`

**This Action helps you clean all infected repositories with one click!**

### Regular Security Scanning

Even without an attack, regular scanning is recommended:

- Auto scan daily (cron: '0 3 * * *')
- Immediate alert on suspicious files
- Protect your code and Secrets

## 🚀 Quick Start

### 1. Create Workflow File

Create `.github/workflows/security-scan.yml` in your repository:

```yaml
name: Security Scan

on:
  # Auto scan daily at 3 AM
  schedule:
    - cron: '0 3 * * *'

  # Manual trigger
  workflow_dispatch:
    inputs:
      keyword:
        description: 'Search keyword'
        required: false
        default: '.oast.fun'
      dry_run:
        description: 'Scan only (true/false)'
        required: false
        default: 'false'

jobs:
  security-scan:
    runs-on: ubuntu-latest

    permissions:
      contents: write
      actions: write
      issues: write

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Security Auto Scan
        uses: h7ml/security-auto-scan@v1
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          keyword: ${{ github.event.inputs.keyword || '.oast.fun' }}
          dry-run: ${{ github.event.inputs.dry_run || 'false' }}
          create-issue: 'true'
          mask-sensitive-data: 'true'
```

### 2. Configure Token

**Option A: Use default GITHUB_TOKEN (Recommended)**

The default `GITHUB_TOKEN` can only access the current repository. To scan all repositories, use Option B.

**Option B: Use Personal Access Token**

1. Visit https://github.com/settings/tokens/new
2. Create Token with permissions:
   - ✅ `repo` - Full repository access
   - ✅ `workflow` - Workflow permission
3. Add Token to repository Secrets:
   - Settings → Secrets → Actions → New repository secret
   - Name: `SECURITY_SCAN_TOKEN`
   - Value: Paste your Token

4. Update workflow:
   ```yaml
   with:
     github-token: ${{ secrets.SECURITY_SCAN_TOKEN }}
   ```

### 3. Run Scan

**Auto Run**: Executes daily at 3 AM

**Manual Run**:
1. Go to Actions tab
2. Select "Security Scan"
3. Click "Run workflow"
4. Configure parameters and run

## 📋 Input Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `github-token` | ✅ | - | GitHub Token (requires `repo` and `workflow` permissions) |
| `keyword` | ❌ | `.oast.fun` | Search keyword (malicious signature) |
| `dry-run` | ❌ | `false` | Scan-only mode (no cleanup) |
| `create-issue` | ❌ | `true` | Create Issue when threats found |
| `disable-workflows` | ❌ | `false` | Disable workflows in infected repositories |
| `mask-sensitive-data` | ❌ | `true` | Log masking (auto-hide sensitive info) |
| `notification-webhook` | ❌ | `` | Webhook URL (Slack/Teams/Discord support) |
| `notification-template` | ❌ | `detailed` | Notification template (`compact` or `detailed`) |

## 📤 Outputs

| Output | Description |
|--------|-------------|
| `infected-repos` | Number of infected repositories |
| `success-count` | Number of successful cleanups |
| `failed-count` | Number of failed cleanups |
| `report-path` | Scan report path |

### Output Usage Example

```yaml
- name: Security Auto Scan
  id: scan
  uses: h7ml/security-auto-scan@v1
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}

- name: Check results
  run: |
    echo "Found ${{ steps.scan.outputs.infected-repos }} infected repositories"
    echo "Cleaned successfully ${{ steps.scan.outputs.success-count }}"
    echo "Failed to clean ${{ steps.scan.outputs.failed-count }}"
```

## 📊 Features

### ✅ Smart Scanning

- Search all your repositories (personal + organizations)
- Use GitHub Code Search API (fast, precise)
- **Pagination support**: automatically fetch all matching results (up to 1000)
- Exclude specific files (e.g., `security-auto-scan.yml`)
- Won't disable current repository workflows

### 🧹 Auto Cleanup

- Clone infected repositories
- Delete malicious workflow files
- Commit and push cleanup
- Record deletion history

### 🔐 Security Features

- **Log Masking**: use GitHub Actions `::add-mask::` to auto-hide sensitive info (Token, URL, etc.)
- **Configuration Toggle**: support enable/disable masking
- **Minimum Privilege**: only requires `repo` and `workflow` permissions
- **Prevent Mis-deletion**: exclusion list, won't delete important files
- **Skip Current Repo**: won't disable self

### 📢 Notification Integration

- **Webhook Support**: Slack/Discord/Teams/DingTalk/Feishu, etc.
- **Notification Templates**: compact and detailed templates
- **Auto Trigger**: auto send when threats found
- **Flexible Config**: customizable notification content

### 🔧 Error Handling

- Detailed push failure analysis
- Auto retry (pull before push on conflict)
- Record failed repositories and reasons
- Provide manual cleanup guide

### 📈 Performance Optimization

- Cache cloned repositories
- Avoid duplicate cloning
- Speed up by 50-80% on subsequent runs
- Auto clean cache older than 7 days

### 📝 Reports and Notifications

- Generate detailed scan reports
- Auto create alert Issues
- Upload Artifacts (30-day retention)
- Failed repository list and manual cleanup steps

## 🛡️ Security

### Token Security

- **Minimum Privilege**: only requires `repo` and `workflow` permissions
- **Temporary Token**: recommend 90-day expiration
- **Revoke After Use**: immediately revoke Token after scan
- **Log Masking**: auto-hide Token to prevent leakage

### Data Privacy

- **Local Processing**: all data processed in Actions Runner
- **No Upload**: won't upload your code to third-party services
- **Reports Only**: only commit scan reports, not logs

### Prevent Mis-deletion

- **Exclusion List**: won't delete `security-auto-scan.yml`
- **Skip Current Repo**: won't disable self
- **Scan-only Mode**: support scan before deciding to clean

## 📖 Advanced Usage

See [EXAMPLES.md](./EXAMPLES.md) for more examples:

- Basic example
- Complete configuration
- Scan-only mode
- Multi-keyword scanning
- Webhook notification integration
- Log masking configuration
- Matrix strategy scanning

## 🏗️ Technical Architecture

- **Language**: Python 3.11
- **Core Library**: requests
- **Runtime**: GitHub Actions (ubuntu-latest)
- **Cache Mechanism**: `.alcache` directory for cloned repos
- **Log Masking**: GitHub Actions `::add-mask::` workflow command

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](./CONTRIBUTING.md)

## 📄 License

[MIT License](./LICENSE)

## 🙏 Acknowledgements

- Inspired by real GitHub Actions supply chain attack incidents
- Thanks to all contributors and user feedback
- Referenced industry security best practices

## 📞 Support

- 🐛 [Report Issues](https://github.com/h7ml/security-auto-scan/issues)
- 💬 [Discussions](https://github.com/h7ml/security-auto-scan/discussions)
- 📧 Email: h7ml@qq.com

## 🔍 Related Resources

- [GitHub Actions Security Best Practices](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [GitHub Code Scanning](https://docs.github.com/en/code-security/code-scanning)
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)

---

<div align="center">

**If this Action helps you, please give it a ⭐️ Star!**

Made with ❤️ by [h7ml](https://github.com/h7ml)

</div>

