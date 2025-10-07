# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个 GitHub Action，用于自动扫描和清理 GitHub Actions 中的恶意 workflow 文件。主要用于检测和移除供应链攻击中注入的恶意代码（如 `.oast.fun` 等外部数据泄露域名）。

**核心功能**：
- 扫描用户和组织的所有仓库
- 检测包含恶意特征的 workflow 文件
- 自动删除恶意文件并提交更改
- 生成详细的扫描和清理报告
- 支持 Webhook 通知（Slack/Discord/Teams 等）
- GitHub Actions 日志脱敏功能

## 开发命令

### 本地测试

```bash
# 安装依赖
pip install -r requirements.txt

# 设置必要的环境变量
export GITHUB_TOKEN="your_token_here"
export KEYWORD=".oast.fun"
export SCAN_ONLY="true"  # 仅扫描模式
export MASK_SENSITIVE_DATA="true"
export REPORT_FORMAT="markdown"  # 可选: markdown, json, html, pdf

# 运行扫描脚本
python scripts/scan.py
```

### GitHub Actions 测试

```bash
# 手动触发 workflow（在 GitHub UI 中）
# Actions → Test Action → Run workflow

# 或使用 gh cli
gh workflow run test.yml
gh workflow run test.yml -f keyword=".oast.fun" -f mask_sensitive="true"
```

### 发布新版本

```bash
# 创建并推送标签（触发自动发布）
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# 或手动触发 Release workflow
gh workflow run release.yml -f tag=v1.0.0
```

详细发布流程请参考 `MARKETPLACE.md`。

## 架构说明

### 核心模块

**`scripts/scan.py`** - 主扫描脚本，包含：

1. **`ScanConfig`** (dataclass:21-44): 扫描配置管理
   - 管理 Token、关键词、工作目录等配置
   - 支持多种报告格式：`report_format` (markdown/json/html/pdf)
   - 自动创建必要的目录结构（`.alcache`、`security/logs`、`security/reports`）

2. **`GitHubActionsMasker`** (class:58-73): 日志脱敏工具
   - 使用 `::add-mask::` workflow 命令自动隐藏敏感信息
   - 防止 Token、URL 等敏感数据泄露到日志中

3. **`NotificationSender`** (class:76-128): Webhook 通知发送器
   - 支持多种通知模板（compact/detailed）
   - 兼容 Slack/Discord/Teams 等 Webhook 格式

4. **`SecurityScanner`** (class:131-578): 主扫描引擎
   - 构造函数 (134-155): 根据 `report_format` 动态设置报告文件扩展名（.md/.json/.html/.pdf）
   - `_search_infected_repos()` (309-356): 使用 GitHub Code Search API 查找恶意文件，支持分页（最多 1000 条结果）
   - `_cleanup_repos()` (358-456): 克隆仓库、删除恶意文件、提交并推送更改
   - `_disable_workflows()` (483-502): 禁用受感染仓库的工作流
   - `_generate_report()` (504-577): 根据配置格式生成清理报告（当前实现为 Markdown）

### 执行流程

1. **获取用户信息** → 识别所有可访问的仓库（个人 + 组织）
2. **搜索感染** → 使用 GitHub Code Search API 查找包含恶意特征的 workflow 文件
3. **克隆和清理** → 对每个受感染仓库：clone → 删除恶意文件 → commit → push
4. **禁用工作流**（可选）→ 通过 API 禁用受感染仓库的所有 workflow
5. **生成报告** → 创建详细的 Markdown 报告到 `security/reports/`
6. **发送通知**（可选）→ 通过 Webhook 发送扫描结果

### Action 集成 (action.yml)

这是一个 **composite action**，步骤：
1. 设置 Python 3.11 环境
2. 安装依赖（`requirements.txt`）
3. 配置 Git 用户信息
4. 运行 `scripts/scan.py`
5. 从报告中提取输出（infected-repos、success-count、failed-count、report-path）
6. 上传扫描结果为 Artifacts（保留 30 天）
7. 创建 Issue 报警（如果发现威胁且 `create-issue: true`）

## 重要设计决策

### 缓存机制
- 使用 `.alcache` 目录缓存已克隆的仓库
- 避免重复克隆，提升性能 50-80%
- 如仓库已存在，执行 `git pull` 更新

### 报告格式支持
- **Markdown** (默认): 生成 `.md` 格式的人类可读报告
- **JSON**: 机器可读的结构化数据，便于集成到其他系统
- **HTML**: 网页格式，可在浏览器中查看
- **PDF**: 适合归档和正式文档
- 格式通过 `report_format` 配置项控制，文件扩展名自动匹配 (scripts/scan.py:144-151)

### 安全考虑
- **排除模式**：不会删除包含 `security-auto-scan` 的文件（避免删除自身）
- **跳过当前仓库**：禁用工作流时跳过当前仓库，防止自我禁用
- **日志脱敏**：使用 GitHub Actions 原生功能自动隐藏敏感数据
- **最小权限**：仅需要 `repo` 和 `workflow` 权限

### 错误处理
- **推送冲突处理** (scripts/scan.py:457-481): 尝试多个分支（main/master），失败时自动 rebase
- **分页查询** (scripts/scan.py:309-356): 自动处理 GitHub API 分页，最多获取 1000 条结果
- **失败仓库记录**：清理失败的仓库会被记录到报告中，附带失败原因和处理建议

## Action 输入参数

| 参数 | 必需 | 默认值 | 说明 |
|------|------|--------|------|
| `github-token` | ✅ | - | GitHub Token（需要 repo 和 workflow 权限） |
| `keyword` | ❌ | `.oast.fun` | 搜索关键词（恶意特征） |
| `dry-run` | ❌ | `false` | 仅扫描模式（不执行清理） |
| `create-issue` | ❌ | `true` | 发现威胁时创建 Issue |
| `disable-workflows` | ❌ | `false` | 禁用受感染仓库的工作流 |
| `mask-sensitive-data` | ❌ | `true` | 日志脱敏（自动隐藏敏感信息） |
| `notification-webhook` | ❌ | `` | Webhook URL（Slack/Teams/Discord） |
| `notification-template` | ❌ | `detailed` | 通知模板（compact/detailed/custom） |
| `report-format` | ❌ | `markdown` | 报告输出格式（markdown/json/html/pdf） |

## Action 输出

| 输出 | 说明 |
|------|------|
| `infected-repos` | 受感染仓库数量 |
| `success-count` | 清理成功数量 |
| `failed-count` | 清理失败数量 |
| `report-path` | 扫描报告路径 |

## 常见使用场景

详见 `EXAMPLES.md`，包括：
- 基础扫描
- 完整配置
- 仅扫描模式
- 多关键词扫描
- Webhook 通知集成
- 矩阵策略扫描

## 技术栈

- **语言**: Python 3.11
- **核心依赖**: `requests>=2.31.0`
- **运行环境**: GitHub Actions (ubuntu-latest)
- **API**: GitHub REST API v3

## 文件结构

```
.
├── action.yml              # GitHub Action 定义（包含 Marketplace 元数据）
├── scripts/
│   └── scan.py            # 主扫描脚本（~850 行，支持多格式报告）
├── requirements.txt       # Python 依赖
├── .github/workflows/
│   ├── test.yml          # 测试 workflow
│   └── release.yml       # 自动发布 workflow（创建 Release + Marketplace）
├── .alcache/             # 仓库克隆缓存目录（自动创建）
├── security/             # 扫描结果输出目录（自动创建）
│   ├── logs/             # 扫描日志
│   └── reports/          # 多格式报告（.md/.json/.html/.pdf）
├── MARKETPLACE.md        # GitHub Marketplace 发布指南
└── CLAUDE.md            # 本文件
```

## 开发注意事项

1. **修改脚本后**：建议先在本地以 `SCAN_ONLY=true` 模式测试
2. **Token 权限**：确保 Token 拥有 `repo` 和 `workflow` 权限
3. **排除模式**：新增功能时注意不要破坏 `excluded_pattern` 逻辑
4. **日志脱敏**：涉及敏感数据输出时，确保调用 `masker.mask_value()`
5. **API 限流**：GitHub Code Search API 有速率限制，注意处理 429 响应
6. **分支处理**：推送时尝试 main 和 master 分支，确保兼容性
7. **报告格式扩展**：新增报告格式时需要：
   - 在 `ScanConfig.report_format` 添加验证
   - 在 `format_extensions` 字典中添加扩展名映射 (scripts/scan.py:144-151)
   - 在 `_generate_report()` 中实现对应格式的生成逻辑
   - 更新 `action.yml` 的 `report-format` 参数描述
8. **版本发布**：
   - 遵循语义化版本（major.minor.patch）
   - 推送标签会自动触发 Release workflow
   - 首次发布需手动勾选 "Publish to Marketplace"
   - 详见 `MARKETPLACE.md`

## 🚀 发布流程

### 自动发布到 GitHub Release 和 Marketplace

1. **创建标签并推送**：
   ```bash
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push origin v1.0.0
   ```

2. **自动执行**（`.github/workflows/release.yml`）：
   - 生成变更日志（对比上一个标签）
   - 构建发布说明（安装方式、功能列表、使用指南）
   - 创建 GitHub Release
   - 更新 major/minor 标签（v1, v1.0）
   - 验证 Marketplace 元数据
   - 显示发布状态和链接

3. **首次发布到 Marketplace**（仅需一次）：
   - 在 GitHub 仓库页面编辑 Release
   - 勾选 "Publish to Marketplace"
   - 选择类别（Security、Automation）
   - 同意条款并发布

4. **后续版本自动发布**：
   - 推送新标签即可
   - GitHub 自动更新 Marketplace
   - beta/alpha 版本会跳过 Marketplace

### 版本标签策略

用户可以选择锁定不同精度的版本：
```yaml
uses: h7ml/security-auto-scan@v1        # 自动更新到最新 v1.x.x
uses: h7ml/security-auto-scan@v1.2      # 锁定到 v1.2.x
uses: h7ml/security-auto-scan@v1.2.3    # 锁定到精确版本
```
