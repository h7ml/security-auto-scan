# Security Auto Scan - 使用示例

## 基础示例

```yaml
name: Security Scan

on:
  schedule:
    - cron: '0 3 * * *'
  workflow_dispatch:

jobs:
  scan:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      actions: write
      issues: write

    steps:
      - uses: actions/checkout@v4

      - name: Run Security Scan
        uses: h7ml/security-auto-scan@v1
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

## 完整配置示例

```yaml
name: Advanced Security Scan

on:
  schedule:
    - cron: '0 3 * * *'

  workflow_dispatch:
    inputs:
      keyword:
        description: '搜索关键词'
        required: false
        default: '.oast.fun'
      dry_run:
        description: '仅扫描不清理'
        type: boolean
        default: false

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
        with:
          fetch-depth: 0

      - name: Restore cache
        uses: actions/cache@v4
        with:
          path: .alcache
          key: security-scan-${{ runner.os }}-${{ github.run_id }}
          restore-keys: |
            security-scan-${{ runner.os }}-

      - name: Security Auto Scan
        id: scan
        uses: h7ml/security-auto-scan@v1
        with:
          github-token: ${{ secrets.SECURITY_SCAN_TOKEN }}
          keyword: ${{ github.event.inputs.keyword || '.oast.fun' }}
          dry-run: ${{ github.event.inputs.dry_run }}
          create-issue: 'true'
          disable-workflows: 'false'

      - name: Print results
        run: |
          echo "🔍 受感染仓库: ${{ steps.scan.outputs.infected-repos }}"
          echo "✅ 清理成功: ${{ steps.scan.outputs.success-count }}"
          echo "❌ 清理失败: ${{ steps.scan.outputs.failed-count }}"

      - name: Commit reports
        if: success()
        run: |
          git add security/reports/
          if ! git diff --staged --quiet; then
            git commit -m "security: 安全扫描报告 $(date '+%Y-%m-%d %H:%M:%S')"
            git push
          fi

      - name: Save cache
        if: always()
        uses: actions/cache/save@v4
        with:
          path: .alcache
          key: security-scan-${{ runner.os }}-${{ github.run_id }}

      - name: Send notification
        if: steps.scan.outputs.infected-repos > 0
        run: |
          echo "⚠️ 发现威胁！请查看 Issue 和 Artifacts"
```

## 仅扫描模式

```yaml
- name: Scan Only (No Cleanup)
  uses: h7ml/security-auto-scan@v1
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    dry-run: 'true'  # 仅扫描，不清理
```

## 多关键词扫描

```yaml
jobs:
  scan-oast-fun:
    name: Scan .oast.fun
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: h7ml/security-auto-scan@v1
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          keyword: '.oast.fun'

  scan-burpcollaborator:
    name: Scan burpcollaborator
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: h7ml/security-auto-scan@v1
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          keyword: 'burpcollaborator.net'

  scan-suspicious-curl:
    name: Scan suspicious curl
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: h7ml/security-auto-scan@v1
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          keyword: 'curl.*-d.*secrets'
```

## 使用输出触发其他操作

```yaml
- name: Security Scan
  id: security
  uses: h7ml/security-auto-scan@v1
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}

- name: Slack Notification
  if: steps.security.outputs.infected-repos > 0
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {
        "text": "🚨 安全警告: 发现 ${{ steps.security.outputs.infected-repos }} 个受感染仓库！"
      }

- name: Email Notification
  if: steps.security.outputs.infected-repos > 0
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 465
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: 🚨 GitHub 安全警告
    to: security@example.com
    from: GitHub Actions
    body: |
      发现 ${{ steps.security.outputs.infected-repos }} 个受感染仓库
      清理成功: ${{ steps.security.outputs.success-count }}
      清理失败: ${{ steps.security.outputs.failed-count }}

      详情查看: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
```

## 使用内置 Webhook 通知

```yaml
- name: Security Scan with Slack Notification
  uses: h7ml/security-auto-scan@v1
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    notification-webhook: ${{ secrets.SLACK_WEBHOOK }}
    notification-template: 'detailed'  # 或 'compact'

- name: Security Scan with Discord Notification
  uses: h7ml/security-auto-scan@v1
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    notification-webhook: ${{ secrets.DISCORD_WEBHOOK }}
    notification-template: 'compact'

- name: Security Scan with Teams Notification
  uses: h7ml/security-auto-scan@v1
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    notification-webhook: ${{ secrets.TEAMS_WEBHOOK }}
    notification-template: 'detailed'
```

## 日志脱敏配置

```yaml
# 启用日志脱敏（默认）
- name: Security Scan with Masking
  uses: h7ml/security-auto-scan@v1
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    mask-sensitive-data: 'true'  # 自动隐藏 Token、URL 等敏感信息

# 禁用日志脱敏（调试模式）
- name: Security Scan without Masking
  uses: h7ml/security-auto-scan@v1
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    mask-sensitive-data: 'false'  # 仅用于调试，生产环境不推荐
```

## 条件执行

```yaml
- name: Security Scan
  id: scan
  uses: h7ml/security-auto-scan@v1
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}

# 仅在发现威胁时执行后续步骤
- name: Emergency Response
  if: steps.scan.outputs.infected-repos > 0
  run: |
    echo "执行应急响应流程..."
    # 撤销 Token
    # 轮换 Secrets
    # 通知安全团队

# 仅在清理失败时执行
- name: Manual Cleanup Guide
  if: steps.scan.outputs.failed-count > 0
  run: |
    echo "⚠️ 部分仓库清理失败，需要手动处理"
    echo "请查看报告: ${{ steps.scan.outputs.report-path }}"
```

## 矩阵策略扫描

```yaml
jobs:
  scan:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        keyword:
          - '.oast.fun'
          - 'burpcollaborator.net'
          - 'requestbin.net'
          - 'pipedream.net'

    steps:
      - uses: actions/checkout@v4

      - name: Scan for ${{ matrix.keyword }}
        uses: h7ml/security-auto-scan@v1
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          keyword: ${{ matrix.keyword }}
```
