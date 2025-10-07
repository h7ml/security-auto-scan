# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-10-07

### Added

- 🎉 Initial release of Security Auto Scan Action
- 🔍 **Auto Scan**: Automatically scan all repositories (personal + organizations)
- 🧹 **Auto Clean**: Automatically clean detected malicious workflow files
- 🔐 **Log Masking**: Automatically hide sensitive information using GitHub Actions `::add-mask::`
- 📊 **Generate Reports**: Detailed scan and cleanup reports in Markdown format
- 🚨 **Create Issues**: Automatically create GitHub Issues when threats are found
- 📢 **Webhook Notifications**: Support for Slack/Discord/Teams/DingTalk/Feishu
- 💾 **Cache Optimization**: Cache cloned repositories to improve performance by 50-80%
- 🛡️ **Security First**: Won't delete important files, won't disable itself
- 🔄 **Pagination Support**: Automatically fetch all search results (up to 1000 items)
- 🌐 **Bilingual Documentation**: Complete English and Chinese documentation
- 📝 **Detailed Logging**: Comprehensive operation logs with emojis and progress indicators

### Features

#### Smart Scanning
- Search all repositories using GitHub Code Search API
- Support pagination to fetch all matching results
- Exclude specific files (e.g., `security-auto-scan.yml`)
- Skip current repository to avoid disabling self

#### Auto Cleanup
- Clone infected repositories with depth 1
- Delete malicious workflow files
- Commit and push cleanup changes
- Record deletion history with before/after SHAs

#### Security Features
- Log masking using GitHub Actions `::add-mask::` workflow command
- Configuration toggle for masking (default: enabled)
- Minimum privilege requirements (only `repo` and `workflow` permissions)
- Exclusion list to prevent mis-deletion
- Auto-hide Token and clone URLs in logs

#### Notification Integration
- Webhook support for popular platforms
- Two notification templates: `compact` and `detailed`
- Auto-trigger notifications when threats found
- Color-coded severity levels (success/info/warning/error)

#### Error Handling
- Detailed push failure analysis
- Auto retry on conflict (pull before push)
- Record failed repositories with reasons
- Provide manual cleanup guide in reports

#### Performance Optimization
- Cache cloned repositories in `.alcache` directory
- Avoid duplicate cloning
- Speed up subsequent runs by 50-80%
- Auto clean cache older than 7 days (future feature)

#### Reports and Notifications
- Generate detailed Markdown reports
- Auto create GitHub Issues with formatted content
- Upload Artifacts with 30-day retention
- Failed repository list with manual cleanup steps

### Technical Details

- **Language**: Python 3.11
- **Core Library**: requests
- **Runtime**: GitHub Actions (ubuntu-latest)
- **Cache Mechanism**: `.alcache` directory
- **Log Masking**: GitHub Actions workflow command

### Documentation

- Complete README in English and Chinese
- Comprehensive EXAMPLES.md with multiple use cases
- CONTRIBUTING.md for contributors
- CODE_OF_CONDUCT.md for community guidelines
- SECURITY.md for security policy
- MIT License

### Supported Platforms

- Slack
- Discord
- Microsoft Teams
- DingTalk (钉钉)
- Feishu (飞书)
- Any webhook-compatible service

---

## 更新日志

项目的所有重要更改都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
项目遵循 [语义化版本](https://semver.org/lang/zh-CN/spec/v2.0.0.html)。

## [未发布]

## [1.0.0] - 2025-10-07

### 新增

- 🎉 Security Auto Scan Action 首次发布
- 🔍 **自动扫描**：自动扫描所有仓库（个人 + 组织）
- 🧹 **自动清理**：自动清理检测到的恶意 workflow 文件
- 🔐 **日志脱敏**：使用 GitHub Actions `::add-mask::` 自动隐藏敏感信息
- 📊 **生成报告**：生成详细的 Markdown 格式扫描和清理报告
- 🚨 **创建 Issue**：发现威胁时自动创建 GitHub Issue
- 📢 **Webhook 通知**：支持 Slack/Discord/Teams/钉钉/飞书
- 💾 **缓存优化**：缓存克隆的仓库，性能提升 50-80%
- 🛡️ **安全优先**：不会误删重要文件，不会禁用自身
- 🔄 **分页支持**：自动获取所有搜索结果（最多 1000 条）
- 🌐 **双语文档**：完整的英文和中文文档
- 📝 **详细日志**：包含表情符号和进度指示器的详细操作日志

### 功能特性

#### 智能扫描
- 使用 GitHub Code Search API 搜索所有仓库
- 支持分页获取所有匹配结果
- 排除特定文件（如 `security-auto-scan.yml`）
- 跳过当前仓库以避免禁用自身

#### 自动清理
- 使用 depth 1 克隆受感染仓库
- 删除恶意 workflow 文件
- 提交并推送清理更改
- 记录删除历史及前后 SHA

#### 安全特性
- 使用 GitHub Actions `::add-mask::` 工作流命令进行日志脱敏
- 可配置的脱敏开关（默认：启用）
- 最小权限要求（仅需 `repo` 和 `workflow` 权限）
- 排除列表防止误删
- 自动隐藏日志中的 Token 和克隆 URL

#### 通知集成
- 支持流行平台的 Webhook
- 两种通知模板：`compact` 和 `detailed`
- 发现威胁时自动触发通知
- 按严重程度着色（成功/信息/警告/错误）

#### 错误处理
- 详细的推送失败分析
- 冲突时自动重试（先拉取再推送）
- 记录失败仓库及原因
- 在报告中提供手动清理指南

#### 性能优化
- 在 `.alcache` 目录中缓存克隆的仓库
- 避免重复克隆
- 后续运行速度提升 50-80%
- 自动清理 7 天以上的缓存（未来功能）

#### 报告和通知
- 生成详细的 Markdown 报告
- 自动创建格式化的 GitHub Issue
- 上传 Artifact（保留 30 天）
- 失败仓库列表及手动清理步骤

### 技术细节

- **语言**：Python 3.11
- **核心库**：requests
- **运行环境**：GitHub Actions (ubuntu-latest)
- **缓存机制**：`.alcache` 目录
- **日志脱敏**：GitHub Actions 工作流命令

### 文档

- 英文和中文完整 README
- 包含多个用例的 EXAMPLES.md
- 贡献者指南 CONTRIBUTING.md
- 社区准则 CODE_OF_CONDUCT.md
- 安全策略 SECURITY.md
- MIT 许可证

### 支持的平台

- Slack
- Discord
- Microsoft Teams
- 钉钉 (DingTalk)
- 飞书 (Feishu)
- 任何兼容 webhook 的服务

[Unreleased]: https://github.com/h7ml/security-auto-scan/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/h7ml/security-auto-scan/releases/tag/v1.0.0
