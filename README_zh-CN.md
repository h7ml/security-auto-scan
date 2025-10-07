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

**自动扫描和清理 GitHub Actions 中的恶意 workflow 文件**

[English](./README.md) | [简体中文](./README_zh-CN.md)

</div>

## 📖 简介

Security Auto Scan 是一个 GitHub Action，用于自动检测和清理被植入的恶意 workflow 文件。它可以：

- 🔍 **自动扫描** 你的所有仓库（个人 + 组织）
- 🧹 **自动清理** 检测到的恶意文件
- 🔐 **日志脱敏** 使用 GitHub Actions `::add-mask::` 自动隐藏敏感信息
- 📊 **生成报告** 详细的扫描和清理报告
- 🚨 **创建 Issue** 发现威胁时自动创建告警
- 📢 **Webhook 通知** 支持 Slack/Discord/Teams/钉钉/飞书等
- 💾 **缓存优化** 避免重复克隆，提升 50-80% 性能
- 🛡️ **安全优先** 不会误删重要文件，不会禁用自身

## 🎯 使用场景

### 遭遇供应链攻击

如果你的 GitHub 账户被入侵，攻击者可能会：

1. 植入恶意 workflow 文件
2. 窃取你的 GitHub Secrets
3. 通过 `*.oast.fun` 等域名外传数据

**本 Action 可以帮你一键清理所有受感染的仓库！**

### 定期安全扫描

即使没有遭遇攻击，也建议定期运行扫描：

- 每天自动扫描（cron: '0 3 * * *'）
- 发现可疑文件立即告警
- 保护你的代码和 Secrets 安全

## 🚀 快速开始

### 1. 创建 Workflow 文件

在你的仓库中创建 `.github/workflows/security-scan.yml`：

```yaml
name: Security Scan

on:
  # 每天凌晨 3 点自动扫描
  schedule:
    - cron: '0 3 * * *'

  # 手动触发
  workflow_dispatch:
    inputs:
      keyword:
        description: '搜索关键词'
        required: false
        default: '.oast.fun'
      dry_run:
        description: '仅扫描不清理 (true/false)'
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

### 2. 配置 Token

**选项 A：使用默认 GITHUB_TOKEN（推荐）**

默认的 `GITHUB_TOKEN` 只能访问当前仓库。如果你想扫描所有仓库，请使用选项 B。

**选项 B：使用 Personal Access Token**

1. 访问 https://github.com/settings/tokens/new
2. 创建 Token，勾选权限：
   - ✅ `repo` - 完整仓库访问
   - ✅ `workflow` - 工作流权限
3. 将 Token 添加到仓库 Secrets：
   - Settings → Secrets → Actions → New repository secret
   - 名称：`SECURITY_SCAN_TOKEN`
   - 值：粘贴你的 Token

4. 修改 workflow：
   ```yaml
   with:
     github-token: ${{ secrets.SECURITY_SCAN_TOKEN }}
   ```

### 3. 运行扫描

**自动运行**：每天凌晨 3 点自动执行

**手动运行**：
1. 进入 Actions 标签页
2. 选择 "Security Scan"
3. 点击 "Run workflow"
4. 配置参数并运行

## 📋 输入参数

| 参数 | 必需 | 默认值 | 说明 |
|------|------|--------|------|
| `github-token` | ✅ | - | GitHub Token（需要 `repo` 和 `workflow` 权限） |
| `keyword` | ❌ | `.oast.fun` | 搜索关键词（恶意特征） |
| `dry-run` | ❌ | `false` | 仅扫描模式（不执行清理） |
| `create-issue` | ❌ | `true` | 发现威胁时创建 Issue |
| `disable-workflows` | ❌ | `false` | 禁用受感染仓库的工作流 |
| `mask-sensitive-data` | ❌ | `true` | 日志脱敏（自动隐藏敏感信息） |
| `notification-webhook` | ❌ | `` | Webhook URL（支持 Slack/Teams/Discord 等） |
| `notification-template` | ❌ | `detailed` | 通知模板（`compact` 或 `detailed`） |

## 📤 输出

| 输出 | 说明 |
|------|------|
| `infected-repos` | 受感染仓库数量 |
| `success-count` | 清理成功数量 |
| `failed-count` | 清理失败数量 |
| `report-path` | 扫描报告路径 |

### 使用输出示例

```yaml
- name: Security Auto Scan
  id: scan
  uses: h7ml/security-auto-scan@v1
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}

- name: Check results
  run: |
    echo "发现 ${{ steps.scan.outputs.infected-repos }} 个受感染仓库"
    echo "清理成功 ${{ steps.scan.outputs.success-count }} 个"
    echo "清理失败 ${{ steps.scan.outputs.failed-count }} 个"
```

## 📊 功能特性

### ✅ 智能扫描

- 搜索你的所有仓库（个人 + 组织）
- 使用 GitHub Code Search API（快速、精确）
- **支持分页查询**：自动获取所有匹配结果（最多 1000 条）
- 排除特定文件（如 `security-auto-scan.yml`）
- 不会禁用当前仓库的工作流

### 🧹 自动清理

- 克隆受感染仓库
- 删除恶意 workflow 文件
- 提交并推送清理
- 记录删除历史

### 🔐 安全特性

- **日志脱敏**：使用 GitHub Actions `::add-mask::` 自动隐藏敏感信息（Token、URL等）
- **配置开关**：支持开启/关闭脱敏功能
- **最小权限**：只需要 `repo` 和 `workflow` 权限
- **防误删**：排除列表，不会删除重要文件
- **跳过当前仓库**：不会禁用自身工作流

### 📢 通知集成

- **Webhook 支持**：支持 Slack/Discord/Teams/钉钉/飞书等
- **通知模板**：提供 compact 和 detailed 两种模板
- **自动触发**：发现威胁时自动发送通知
- **灵活配置**：可自定义通知内容和格式

### 🔧 错误处理

- 详细的推送失败原因分析
- 自动重试（冲突时先 pull 再 push）
- 记录失败仓库和原因
- 提供手动清理指南

### 📈 性能优化

- 缓存克隆的仓库
- 避免重复克隆
- 后续运行提速 50-80%
- 自动清理超过 7 天的缓存

### 📝 报告和通知

- 生成详细的扫描报告
- 自动创建告警 Issue
- 上传 Artifacts（保留 30 天）
- 失败仓库列表和手动清理步骤

## 🛡️ 安全性

### Token 安全

- **最小权限原则**：只需要 `repo` 和 `workflow` 权限
- **临时 Token**：建议设置 90 天过期
- **使用后撤销**：扫描完成后立即撤销 Token
- **日志脱敏**：自动隐藏 Token，防止泄露

### 数据隐私

- **本地处理**：所有数据在 Actions Runner 中处理
- **不上传**：不会上传你的代码到第三方服务
- **仅报告**：只提交扫描报告，不提交日志

### 防误删

- **排除列表**：不会删除 `security-auto-scan.yml`
- **跳过当前仓库**：不会禁用自身工作流
- **仅扫描模式**：支持先扫描再决定是否清理

## 📖 高级用法

查看 [EXAMPLES.md](./EXAMPLES.md) 获取更多使用示例：

- 基础示例
- 完整配置示例
- 仅扫描模式
- 多关键词扫描
- Webhook 通知集成
- 日志脱敏配置
- 矩阵策略扫描

## 🏗️ 技术架构

- **语言**: Python 3.11
- **核心库**: requests
- **运行环境**: GitHub Actions (ubuntu-latest)
- **缓存机制**: `.alcache` 目录存储克隆的仓库
- **日志脱敏**: 使用 GitHub Actions `::add-mask::` workflow command

## 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](./CONTRIBUTING.md)

## 📄 许可证

[MIT License](./LICENSE)

## 🙏 致谢

- 灵感来源于真实的 GitHub Actions 供应链攻击事件
- 感谢所有贡献者和用户的反馈
- 参考了业界最佳安全实践

## 📞 支持

- 🐛 [报告问题](https://github.com/h7ml/security-auto-scan/issues)
- 💬 [讨论](https://github.com/h7ml/security-auto-scan/discussions)
- 📧 邮件：h7ml@qq.com

## 🔍 相关资源

- [GitHub Actions 安全最佳实践](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [GitHub Code Scanning](https://docs.github.com/en/code-security/code-scanning)
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)

---

<div align="center">

**如果这个 Action 对你有帮助，请给个 ⭐️ Star！**

Made with ❤️ by [h7ml](https://github.com/h7ml)

</div>
