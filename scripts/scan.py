#!/usr/bin/env python3
"""
Security Auto Scan - GitHub Action 版本
自动扫描和清理恶意 GitHub Actions workflow 文件
"""

import os
import sys
import json
import logging
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
import requests


@dataclass
class ScanConfig:
    """扫描配置"""
    github_token: str
    search_keyword: str = ".oast.fun"
    scan_only: bool = False
    disable_workflows: bool = False
    mask_sensitive: bool = True
    webhook_url: str = ""
    notification_template: str = "detailed"
    report_format: str = "markdown"  # markdown, json, html, pdf
    work_dir: Path = None
    log_dir: Path = None
    report_dir: Path = None
    excluded_pattern: str = "security-auto-scan"

    def __post_init__(self):
        project_root = Path(os.getenv("GITHUB_WORKSPACE", ".")).resolve()
        self.work_dir = self.work_dir or project_root / ".alcache"
        self.log_dir = self.log_dir or project_root / "security" / "logs"
        self.report_dir = self.report_dir or project_root / "security" / "reports"

        # 创建必要的目录
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)


@dataclass
class ScanResult:
    """扫描结果"""
    infected_repos: List[str] = field(default_factory=list)
    cleaned_repos: List[Dict] = field(default_factory=list)
    failed_repos: List[Dict] = field(default_factory=list)
    disabled_count: int = 0
    username: str = ""
    organizations: List[str] = field(default_factory=list)


class GitHubActionsMasker:
    """GitHub Actions 日志脱敏工具"""

    @staticmethod
    def mask_value(value: str) -> None:
        """使用 GitHub Actions 的 ::add-mask:: 功能脱敏"""
        if value and os.getenv("GITHUB_ACTIONS"):
            print(f"::add-mask::{value}")

    @staticmethod
    def mask_sensitive_display(value: str, show_length: int = 4) -> str:
        """返回脱敏后的显示值"""
        if not value or len(value) <= show_length * 2:
            return "****"
        return f"{value[:show_length]}****{value[-show_length:]}"


class NotificationSender:
    """通知发送器（支持 Slack/Discord/Teams 等）"""

    def __init__(self, webhook_url: str, template: str = "detailed"):
        self.webhook_url = webhook_url
        self.template = template
        self.colors = {
            "error": "#dc3545",
            "warning": "#ffc107",
            "info": "#17a2b8",
            "success": "#28a745",
        }

    def send(self, title: str, message: str, severity: str = "info") -> bool:
        """发送通知"""
        if not self.webhook_url:
            return False

        payload = self._build_payload(title, message, severity)
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logging.warning(f"Webhook 通知发送失败: {e}")
            return False

    def _build_payload(self, title: str, message: str, severity: str) -> Dict:
        """根据模板构建通知载荷"""
        color = self.colors.get(severity, self.colors["info"])

        if self.template == "compact":
            return {
                "text": f"🔐 {title}",
                "attachments": [{
                    "color": color,
                    "text": message
                }]
            }
        else:  # detailed
            return {
                "text": "🔐 Security Auto Scan",
                "attachments": [{
                    "color": color,
                    "title": title,
                    "text": message,
                    "footer": "Security Auto Scan Action",
                    "footer_icon": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
                    "ts": int(datetime.now().timestamp())
                }]
            }


class SecurityScanner:
    """安全扫描器"""

    def __init__(self, config: ScanConfig):
        self.config = config
        self.result = ScanResult()
        self.current_repo = self._get_current_repo()

        # 设置日志
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.log_file = config.log_dir / f"cleanup-{timestamp}.log"

        # 根据格式设置报告文件扩展名
        format_extensions = {
            "markdown": "md",
            "json": "json",
            "html": "html",
            "pdf": "pdf"
        }
        ext = format_extensions.get(config.report_format, "md")
        self.report_file = config.report_dir / f"cleanup-report-{timestamp}.{ext}"

        self._setup_logging()
        self.masker = GitHubActionsMasker()
        self.notifier = NotificationSender(config.webhook_url, config.notification_template)

    def _setup_logging(self):
        """配置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )

    def _get_current_repo(self) -> str:
        """获取当前仓库名称"""
        repo = os.getenv("GITHUB_REPOSITORY")
        if not repo:
            try:
                remote_url = subprocess.check_output(
                    ["git", "remote", "get-url", "origin"],
                    stderr=subprocess.DEVNULL
                ).decode().strip()
                repo = remote_url.replace("https://github.com/", "").replace(".git", "")
                # 处理带 token 的 URL
                if "@github.com/" in repo:
                    repo = repo.split("@github.com/")[1]
            except:
                repo = ""
        return repo

    def _api_request(self, endpoint: str, method: str = "GET", data: Dict = None) -> Optional[Dict]:
        """GitHub API 请求"""
        headers = {
            "Authorization": f"token {self.config.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        url = f"https://api.github.com{endpoint}"

        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=30)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=30)
            else:
                raise ValueError(f"不支持的 HTTP 方法: {method}")

            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            logging.error(f"API 请求失败 ({endpoint}): {e}")
            return None

    def run(self) -> Tuple[int, int, int]:
        """运行扫描流程"""
        logging.info("=" * 60)
        logging.info("GitHub 恶意 Workflow 一键清理工具")
        logging.info("=" * 60)
        logging.info(f"搜索关键词: {self.config.search_keyword}")
        logging.info(f"模式: {'仅扫描' if self.config.scan_only else '完整清理'}")
        logging.info(f"日志脱敏: {'✓ 启用' if self.config.mask_sensitive else '✗ 禁用'}")
        logging.info(f"Webhook 通知: {'✓ 已配置' if self.config.webhook_url else '✗ 未配置'}")
        logging.info(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"日志文件: {self.log_file}")
        logging.info("")

        # Token 脱敏
        if self.config.mask_sensitive:
            self.masker.mask_value(self.config.github_token)

        # 1. 获取用户和组织信息
        logging.info("[1/6] 获取用户和组织信息...")
        if not self._fetch_user_info():
            return 0, 0, 0

        # 2. 搜索受感染仓库
        logging.info("[2/6] 搜索受感染仓库...")
        self._search_infected_repos()

        total_infected = len(self.result.infected_repos)
        logging.info(f"✓ 发现 {total_infected} 个受感染仓库")

        if total_infected == 0:
            self._generate_report()
            logging.info("✓ 未发现威胁，扫描完成")
            if self.config.webhook_url:
                self.notifier.send(
                    "✅ 安全扫描完成",
                    "未发现威胁，所有仓库安全。",
                    "success"
                )
            return 0, 0, 0

        # 3. 克隆并清理仓库
        if not self.config.scan_only:
            logging.info("[3/6] 克隆并清理受感染仓库...")
            self._cleanup_repos()
        else:
            logging.info("[3/6] 跳过清理（仅扫描模式）")

        # 4. 禁用工作流
        if self.config.disable_workflows and not self.config.scan_only:
            logging.info("[4/6] 禁用受感染仓库的工作流...")
            self._disable_workflows()
        else:
            logging.info("[4/6] 跳过禁用工作流")

        # 5. 生成报告
        logging.info("[5/6] 生成清理报告...")
        self._generate_report()

        # 6. 发送通知
        success_count = len(self.result.cleaned_repos)
        failed_count = len(self.result.failed_repos)

        if self.config.webhook_url:
            severity = "error" if failed_count > 0 else "warning" if success_count > 0 else "info"
            title = f"🚨 发现 {total_infected} 个受感染仓库"
            message = (
                f"扫描完成！\n"
                f"✅ 清理成功: {success_count} 个\n"
                f"❌ 清理失败: {failed_count} 个\n"
                f"🔒 禁用工作流: {self.result.disabled_count} 个\n\n"
                f"⚠️ 请立即查看报告并轮换 Secrets！"
            )
            self.notifier.send(title, message, severity)
            logging.info("✓ 已发送 Webhook 通知")

        logging.info("")
        logging.info("=" * 60)
        logging.info("清理完成")
        logging.info("=" * 60)
        logging.info(f"统计汇总:")
        logging.info(f"  受感染仓库: {total_infected}")
        logging.info(f"  清理成功: {success_count}")
        logging.info(f"  清理失败: {failed_count}")
        logging.info(f"  禁用工作流: {self.result.disabled_count}")
        logging.info("")
        logging.warning("⚠️  重要: 使用完成后立即撤销 Token！")
        logging.info("   https://github.com/settings/tokens")

        return total_infected, success_count, failed_count

    def _fetch_user_info(self) -> bool:
        """获取用户和组织信息"""
        user_info = self._api_request("/user")
        if not user_info:
            logging.error("无法获取用户信息，请检查 Token 权限")
            return False

        self.result.username = user_info.get("login", "unknown")
        logging.info(f"✓ 用户: {self.result.username}")

        # 获取组织
        orgs_data = self._api_request("/user/orgs")
        if orgs_data:
            self.result.organizations = [org["login"] for org in orgs_data]
            if self.result.organizations:
                logging.info(f"✓ 组织: {', '.join(self.result.organizations)}")

        return True

    def _search_infected_repos(self):
        """搜索受感染的仓库（支持分页查询所有结果）"""
        search_scopes = [f"user:{self.result.username}"]
        search_scopes.extend([f"org:{org}" for org in self.result.organizations])

        for scope in search_scopes:
            query = f"{self.config.search_keyword} in:file path:.github/workflows {scope}"
            page = 1
            per_page = 100
            total_processed = 0

            while True:
                logging.info(f"  搜索: {scope} (第 {page} 页)...")
                search_result = self._api_request(
                    f"/search/code?q={requests.utils.quote(query)}&per_page={per_page}&page={page}"
                )

                if not search_result or "items" not in search_result:
                    break

                items = search_result["items"]
                if not items:
                    break

                for item in items:
                    repo_name = item["repository"]["full_name"]
                    file_path = item["path"]

                    # 排除特定文件
                    if self.config.excluded_pattern in file_path:
                        logging.info(f"  跳过排除的文件: {repo_name}/{file_path}")
                        continue

                    if repo_name not in self.result.infected_repos:
                        self.result.infected_repos.append(repo_name)
                        logging.info(f"  ✓ 发现: {repo_name} - {file_path}")

                total_processed += len(items)

                # GitHub API 每页最多 100 条,总共最多 1000 条结果
                # 如果本页结果少于 per_page,说明已经是最后一页
                if len(items) < per_page or total_processed >= 1000:
                    break

                page += 1

            if total_processed > 0:
                logging.info(f"  ✓ {scope}: 处理了 {total_processed} 个搜索结果")

    def _cleanup_repos(self):
        """清理受感染的仓库"""
        for i, repo in enumerate(self.result.infected_repos, 1):
            logging.info("")
            logging.info(f"[{i}/{len(self.result.infected_repos)}] 处理仓库: {repo}")
            repo_dir = self.config.work_dir / repo.replace("/", "_")

            try:
                # 克隆或拉取仓库
                if repo_dir.exists():
                    logging.info(f"  ✓ 使用缓存: {repo_dir}")
                    logging.info(f"  📥 更新仓库...")
                    result = subprocess.run(
                        ["git", "pull"],
                        cwd=repo_dir,
                        capture_output=True,
                        check=True
                    )
                    if result.stdout:
                        logging.debug(f"  Git pull output: {result.stdout.decode().strip()}")
                    logging.info(f"  ✓ 仓库已更新")
                else:
                    logging.info(f"  📥 克隆仓库...")
                    clone_url = f"https://{self.config.github_token}@github.com/{repo}.git"
                    if self.config.mask_sensitive:
                        self.masker.mask_value(clone_url)

                    result = subprocess.run(
                        ["git", "clone", "--depth", "1", clone_url, str(repo_dir)],
                        capture_output=True,
                        check=True
                    )
                    logging.info(f"  ✓ 克隆成功")

                # 查找并删除恶意文件
                workflow_dir = repo_dir / ".github" / "workflows"
                if not workflow_dir.exists():
                    logging.warning(f"  ⚠️ workflow 目录不存在")
                    continue

                logging.info(f"  🔍 扫描 workflow 文件...")
                deleted_files = []
                for workflow_file in workflow_dir.glob("*.y*ml"):
                    logging.debug(f"  检查: {workflow_file.name}")
                    content = workflow_file.read_text(errors="ignore")
                    if self.config.search_keyword in content and self.config.excluded_pattern not in workflow_file.name:
                        deleted_files.append(workflow_file.name)
                        workflow_file.unlink()
                        logging.info(f"  🗑️  删除: {workflow_file.name}")
                    else:
                        logging.debug(f"  ✓ 跳过: {workflow_file.name}")

                if not deleted_files:
                    logging.info(f"  ℹ️  未找到恶意文件")
                    continue

                logging.info(f"  📝 提交更改 ({len(deleted_files)} 个文件)...")

                # 提交更改
                before_sha = subprocess.check_output(
                    ["git", "rev-parse", "HEAD"],
                    cwd=repo_dir
                ).decode().strip()
                logging.debug(f"  提交前 SHA: {before_sha}")

                subprocess.run(["git", "add", "."], cwd=repo_dir, check=True)
                commit_msg = f"security: 清理恶意 workflow 文件\n\n删除文件:\n" + "\n".join(f"- {f}" for f in deleted_files)
                subprocess.run(
                    ["git", "commit", "-m", commit_msg],
                    cwd=repo_dir,
                    check=True
                )

                after_sha = subprocess.check_output(
                    ["git", "rev-parse", "HEAD"],
                    cwd=repo_dir
                ).decode().strip()
                logging.info(f"  ✓ 已提交: {after_sha[:7]}")

                # 推送更改
                logging.info(f"  ⬆️  推送更改到远程仓库...")
                self._push_changes(repo, repo_dir)
                logging.info(f"  ✓ 推送成功")

                self.result.cleaned_repos.append({
                    "repo": repo,
                    "before_sha": before_sha,
                    "after_sha": after_sha,
                    "deleted_files": deleted_files
                })
                logging.info(f"  ✅ 清理完成")

            except Exception as e:
                logging.error(f"  ❌ 清理失败: {e}")
                self.result.failed_repos.append({
                    "repo": repo,
                    "reason": str(e)
                })

    def _push_changes(self, repo: str, repo_dir: Path):
        """推送更改到远程仓库"""
        # 尝试推送到 main 分支
        branches = ["main", "master"]
        for branch in branches:
            try:
                subprocess.run(
                    ["git", "push", "origin", branch],
                    cwd=repo_dir,
                    capture_output=True,
                    check=True
                )
                return
            except subprocess.CalledProcessError as e:
                error_output = e.stderr.decode()
                if "non-fast-forward" in error_output:
                    # 尝试 rebase
                    try:
                        subprocess.run(["git", "pull", "--rebase", "origin", branch], cwd=repo_dir, check=True)
                        subprocess.run(["git", "push", "origin", branch], cwd=repo_dir, check=True)
                        return
                    except:
                        pass

        raise Exception("推送失败: 所有分支推送尝试均失败")

    def _disable_workflows(self):
        """禁用受感染仓库的工作流"""
        for repo in self.result.infected_repos:
            if repo == self.current_repo:
                logging.info(f"  跳过当前仓库: {repo}")
                continue

            workflows = self._api_request(f"/repos/{repo}/actions/workflows")
            if not workflows or "workflows" not in workflows:
                continue

            for workflow in workflows["workflows"]:
                if workflow["state"] == "active":
                    result = self._api_request(
                        f"/repos/{repo}/actions/workflows/{workflow['id']}/disable",
                        method="PUT"
                    )
                    if result is not None:
                        self.result.disabled_count += 1
                        logging.info(f"  ✓ 禁用: {repo} - {workflow['name']}")

    def _generate_report(self):
        """生成报告"""
        total_infected = len(self.result.infected_repos)
        success_count = len(self.result.cleaned_repos)
        failed_count = len(self.result.failed_repos)

        # 根据格式生成不同类型的报告
        if self.config.report_format == "json":
            self._generate_json_report(total_infected, success_count, failed_count)
        elif self.config.report_format == "html":
            self._generate_html_report(total_infected, success_count, failed_count)
        elif self.config.report_format == "pdf":
            self._generate_pdf_report(total_infected, success_count, failed_count)
        else:  # markdown (default)
            self._generate_markdown_report(total_infected, success_count, failed_count)

        logging.info(f"✓ 报告已保存: {self.report_file}")

    def _generate_json_report(self, total_infected: int, success_count: int, failed_count: int):
        """生成 JSON 格式报告"""
        report_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "keyword": self.config.search_keyword,
                "executor": self.result.username,
                "log_file": str(self.log_file.name),
                "scan_mode": "scan_only" if self.config.scan_only else "full_cleanup"
            },
            "statistics": {
                "infected_repos": total_infected,
                "success_count": success_count,
                "failed_count": failed_count,
                "disabled_workflows": self.result.disabled_count
            },
            "infected_repositories": [
                {"name": repo, "url": f"https://github.com/{repo}"}
                for repo in self.result.infected_repos
            ],
            "cleaned_repositories": [
                {
                    "repo": entry["repo"],
                    "before_sha": entry["before_sha"],
                    "after_sha": entry["after_sha"],
                    "deleted_files": entry["deleted_files"]
                }
                for entry in self.result.cleaned_repos
            ],
            "failed_repositories": [
                {
                    "repo": entry["repo"],
                    "reason": entry["reason"],
                    "url": f"https://github.com/{entry['repo']}"
                }
                for entry in self.result.failed_repos
            ],
            "next_steps": {
                "p0_immediate": [
                    "撤销当前使用的 Token",
                    "轮换所有泄露的 Secrets",
                    "修改泄露的密码"
                ],
                "p1_24h": [
                    "重新生成 SSH 密钥",
                    "启用 GitHub 2FA",
                    "启用分支保护规则"
                ],
                "p2_7d": [
                    "安全审计",
                    "配置 GPG 签名提交",
                    "启用 Dependabot 和 CodeQL"
                ]
            }
        }

        with open(self.report_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

    def _generate_html_report(self, total_infected: int, success_count: int, failed_count: int):
        """生成 HTML 格式报告"""
        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub 恶意 Workflow 清理报告</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        h1 {{ color: #d73a49; border-bottom: 3px solid #d73a49; padding-bottom: 10px; }}
        h2 {{ color: #0366d6; margin-top: 30px; }}
        .metadata {{ background: #f6f8fa; padding: 15px; border-radius: 6px; margin: 20px 0; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-card.success {{ background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%); }}
        .stat-card.failed {{ background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%); }}
        .stat-number {{ font-size: 48px; font-weight: bold; }}
        .stat-label {{ font-size: 14px; opacity: 0.9; margin-top: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #e1e4e8; }}
        th {{ background: #f6f8fa; font-weight: 600; }}
        tr:hover {{ background: #f6f8fa; }}
        .badge {{ padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }}
        .badge-p0 {{ background: #d73a49; color: white; }}
        .badge-p1 {{ background: #fb8c00; color: white; }}
        .badge-p2 {{ background: #0366d6; color: white; }}
        a {{ color: #0366d6; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #e1e4e8; color: #586069; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 GitHub 恶意 Workflow 清理报告</h1>

        <div class="metadata">
            <p><strong>时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>关键词:</strong> <code>{self.config.search_keyword}</code></p>
            <p><strong>执行人:</strong> {self.result.username}</p>
            <p><strong>模式:</strong> {'仅扫描' if self.config.scan_only else '完整清理'}</p>
        </div>

        <h2>📊 统计信息</h2>
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{total_infected}</div>
                <div class="stat-label">受感染仓库</div>
            </div>
            <div class="stat-card success">
                <div class="stat-number">{success_count}</div>
                <div class="stat-label">清理成功</div>
            </div>
            <div class="stat-card failed">
                <div class="stat-number">{failed_count}</div>
                <div class="stat-label">清理失败</div>
            </div>
        </div>

        <h2>📋 受感染仓库列表</h2>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>仓库</th>
                    <th>链接</th>
                </tr>
            </thead>
            <tbody>
"""
        for i, repo in enumerate(self.result.infected_repos, 1):
            html_content += f"""                <tr>
                    <td>{i}</td>
                    <td>{repo}</td>
                    <td><a href="https://github.com/{repo}" target="_blank">查看仓库</a></td>
                </tr>
"""

        html_content += """            </tbody>
        </table>
"""

        if self.result.cleaned_repos:
            html_content += """
        <h2>🗑️ 清理的文件</h2>
        <table>
            <thead>
                <tr>
                    <th>仓库</th>
                    <th>删除前 SHA</th>
                    <th>删除后 SHA</th>
                </tr>
            </thead>
            <tbody>
"""
            for entry in self.result.cleaned_repos:
                html_content += f"""                <tr>
                    <td>{entry['repo']}</td>
                    <td><code>{entry['before_sha'][:7]}</code></td>
                    <td><code>{entry['after_sha'][:7]}</code></td>
                </tr>
"""
            html_content += """            </tbody>
        </table>
"""

        if self.result.failed_repos:
            html_content += """
        <h2>❌ 失败的仓库</h2>
        <table>
            <thead>
                <tr>
                    <th>仓库</th>
                    <th>失败原因</th>
                    <th>链接</th>
                </tr>
            </thead>
            <tbody>
"""
            for entry in self.result.failed_repos:
                html_content += f"""                <tr>
                    <td>{entry['repo']}</td>
                    <td>{entry['reason']}</td>
                    <td><a href="https://github.com/{entry['repo']}" target="_blank">查看</a></td>
                </tr>
"""
            html_content += """            </tbody>
        </table>
"""

        html_content += f"""
        <h2>⚠️ 后续操作清单</h2>
        <h3><span class="badge badge-p0">P0</span> 立即执行（2小时内）</h3>
        <ul>
            <li>🔑 <a href="https://github.com/settings/tokens">撤销当前使用的 Token</a></li>
            <li>🔄 轮换所有泄露的 Secrets</li>
            <li>🔐 修改泄露的密码</li>
        </ul>

        <h3><span class="badge badge-p1">P1</span> 24小时内执行</h3>
        <ul>
            <li>🗝️ 重新生成 SSH 密钥</li>
            <li>🛡️ <a href="https://github.com/settings/security">启用 GitHub 2FA</a></li>
            <li>🔒 启用分支保护规则</li>
        </ul>

        <h3><span class="badge badge-p2">P2</span> 7天内执行</h3>
        <ul>
            <li>🔍 安全审计</li>
            <li>✍️ 配置 GPG 签名提交</li>
            <li>🤖 启用 Dependabot 和 CodeQL</li>
        </ul>

        <div class="footer">
            <p>🤖 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 工具版本: Security Auto Scan v3.0 (Python)</p>
        </div>
    </div>
</body>
</html>"""

        self.report_file.write_text(html_content, encoding="utf-8")

    def _generate_pdf_report(self, total_infected: int, success_count: int, failed_count: int):
        """生成 PDF 格式报告（先生成 HTML，提示用户手动转换）"""
        # PDF 生成需要额外的库（如 weasyprint 或 reportlab）
        # 为了保持依赖简单，这里先生成 HTML，并在日志中提示
        logging.warning("⚠️  PDF 格式需要额外工具转换")
        logging.info("  建议: 使用 wkhtmltopdf 或浏览器打印功能将 HTML 转为 PDF")

        # 生成 HTML 作为中间格式
        html_file = self.report_file.with_suffix('.html')
        original_format = self.config.report_format
        self.config.report_format = "html"
        self.report_file = html_file
        self._generate_html_report(total_infected, success_count, failed_count)
        self.config.report_format = original_format

        logging.info(f"  HTML 报告已生成: {html_file}")
        logging.info(f"  转换命令示例: wkhtmltopdf {html_file} {self.report_file}")

    def _generate_markdown_report(self, total_infected: int, success_count: int, failed_count: int):
        """生成 Markdown 格式报告（原有实现）"""
        total_infected = len(self.result.infected_repos)
        success_count = len(self.result.cleaned_repos)
        failed_count = len(self.result.failed_repos)

        report_content = f"""# GitHub 恶意 Workflow 清理报告

**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**关键词**: `{self.config.search_keyword}`
**执行人**: {self.result.username}
**日志文件**: `{self.log_file.name}`

## 📊 统计信息

- **受感染仓库**: {total_infected} 个
- **清理成功**: {success_count} 个
- **清理失败**: {failed_count} 个
- **禁用工作流**: {self.result.disabled_count} 个

## 📋 受感染仓库列表

"""
        for i, repo in enumerate(self.result.infected_repos, 1):
            report_content += f"{i}. [{repo}](https://github.com/{repo})\n"

        report_content += "\n## 🗑️ 清理的文件\n\n"
        if self.result.cleaned_repos:
            report_content += "| 仓库 | 删除前 SHA | 删除后 SHA |\n"
            report_content += "|------|-----------|----------|\n"
            for entry in self.result.cleaned_repos:
                report_content += f"| {entry['repo']} | `{entry['before_sha'][:7]}` | `{entry['after_sha'][:7]}` |\n"
        else:
            report_content += "无文件被清理\n"

        report_content += "\n## ❌ 失败的仓库\n\n"
        if self.result.failed_repos:
            report_content += "| 仓库 | 失败原因 | 处理建议 |\n"
            report_content += "|------|---------|----------|\n"
            for entry in self.result.failed_repos:
                repo = entry['repo']
                reason = entry['reason']
                suggestion = "手动清理" if "Permission" in reason else "检查网络并重试"
                report_content += f"| [{repo}](https://github.com/{repo}) | {reason} | {suggestion} |\n"
        else:
            report_content += "✓ 所有仓库处理成功\n"

        report_content += """

## ⚠️ 后续操作清单

### 🔴 立即执行 (P0 - 2小时内)
- [ ] 🔑 [撤销当前使用的 Token](https://github.com/settings/tokens)
- [ ] 🔄 轮换所有泄露的 Secrets
- [ ] 🔐 修改泄露的密码

### 🟡 24小时内执行 (P1)
- [ ] 🗝️ 重新生成 SSH 密钥
- [ ] 🛡️ [启用 GitHub 2FA](https://github.com/settings/security)
- [ ] 🔒 启用分支保护规则

### 🟢 7天内执行 (P2)
- [ ] 🔍 安全审计
- [ ] ✍️ 配置 GPG 签名提交
- [ ] 🤖 启用 Dependabot 和 CodeQL

---

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**工具版本**: Security Auto Scan v3.0 (Python)
"""

        self.report_file.write_text(report_content, encoding="utf-8")
        logging.info(f"✓ 报告已保存: {self.report_file}")


def main():
    """主函数"""
    # 从环境变量读取配置
    config = ScanConfig(
        github_token=os.getenv("GITHUB_TOKEN", ""),
        search_keyword=os.getenv("KEYWORD", ".oast.fun"),
        scan_only=os.getenv("SCAN_ONLY", "false").lower() == "true",
        disable_workflows=os.getenv("DISABLE_WORKFLOWS", "false").lower() == "true",
        mask_sensitive=os.getenv("MASK_SENSITIVE_DATA", "true").lower() == "true",
        webhook_url=os.getenv("NOTIFICATION_WEBHOOK", ""),
        notification_template=os.getenv("NOTIFICATION_TEMPLATE", "detailed"),
        report_format=os.getenv("REPORT_FORMAT", "markdown"),
    )

    if not config.github_token:
        logging.error("错误: 请设置 GITHUB_TOKEN 环境变量")
        sys.exit(1)

    try:
        scanner = SecurityScanner(config)
        infected, success, failed = scanner.run()

        # 设置 GitHub Actions 输出
        if os.getenv("GITHUB_OUTPUT"):
            with open(os.getenv("GITHUB_OUTPUT"), "a") as f:
                f.write(f"infected-repos={infected}\n")
                f.write(f"success-count={success}\n")
                f.write(f"failed-count={failed}\n")
                f.write(f"report-path={scanner.report_file}\n")

        sys.exit(0 if failed == 0 else 1)
    except Exception as e:
        logging.exception(f"执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
