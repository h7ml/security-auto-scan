# Contributing to Security Auto Scan

[English](#english) | [中文](#中文)

---

## English

First off, thank you for considering contributing to Security Auto Scan! It's people like you that make this tool better for everyone.

### Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

### How Can I Contribute?

#### Reporting Bugs

Before creating bug reports, please check the existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps which reproduce the problem**
* **Provide specific examples to demonstrate the steps**
* **Describe the behavior you observed after following the steps**
* **Explain which behavior you expected to see instead and why**
* **Include screenshots and animated GIFs** if possible
* **Include your workflow file** (with sensitive data removed)

#### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a step-by-step description of the suggested enhancement**
* **Provide specific examples to demonstrate the steps**
* **Describe the current behavior** and **explain which behavior you expected to see instead**
* **Explain why this enhancement would be useful**

#### Pull Requests

* Fill in the required template
* Do not include issue numbers in the PR title
* Include screenshots and animated GIFs in your pull request whenever possible
* Follow the Python style guide (PEP 8)
* Include thoughtfully-worded, well-structured tests
* Document new code
* End all files with a newline

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/security-auto-scan.git
   cd security-auto-scan
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make your changes**
   - Write clean, readable code
   - Follow existing code style
   - Add tests if applicable
   - Update documentation

5. **Test your changes**
   - Test the action locally
   - Ensure all existing tests pass
   - Add new tests for new features

6. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

   Commit message format:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `style:` - Code style changes (formatting, etc)
   - `refactor:` - Code refactoring
   - `test:` - Adding tests
   - `chore:` - Maintenance tasks

7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Open a Pull Request**

### Code Style

* Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code
* Use meaningful variable and function names
* Write docstrings for functions and classes
* Keep functions focused and small
* Add comments for complex logic

### Testing

* Write tests for new features
* Ensure backward compatibility
* Test with different GitHub token permissions
* Test error handling scenarios

### Documentation

* Update README.md if needed
* Update EXAMPLES.md with new usage examples
* Keep both English and Chinese versions synchronized
* Use clear and concise language

### Questions?

Feel free to open an issue with your question or reach out via:
- 📧 Email: h7ml@qq.com
- 💬 [GitHub Discussions](https://github.com/h7ml/security-auto-scan/discussions)

---

## 中文

首先，感谢你考虑为 Security Auto Scan 做出贡献！正是像你这样的人让这个工具对每个人都更好。

### 行为准则

本项目及其所有参与者都受我们的[行为准则](CODE_OF_CONDUCT.md)约束。通过参与，你需要遵守此准则。

### 我该如何贡献？

#### 报告 Bug

在创建 Bug 报告之前，请检查现有的 issue，因为你可能会发现不需要创建新的。创建 Bug 报告时，请尽可能包含详细信息：

* **使用清晰描述性的标题**
* **描述重现问题的确切步骤**
* **提供具体示例来演示这些步骤**
* **描述按照步骤操作后观察到的行为**
* **解释你期望看到什么行为以及为什么**
* **如果可能，包含截图和动图**
* **包含你的 workflow 文件**（删除敏感数据）

#### 建议增强功能

增强建议作为 GitHub issue 跟踪。创建增强建议时，请包含：

* **使用清晰描述性的标题**
* **提供建议增强功能的分步说明**
* **提供具体示例来演示这些步骤**
* **描述当前行为**和**解释你期望看到什么行为**
* **解释为什么这个增强功能有用**

#### Pull Request

* 填写所需的模板
* 不要在 PR 标题中包含 issue 编号
* 尽可能在 PR 中包含截图和动图
* 遵循 Python 代码规范 (PEP 8)
* 包含编写良好的测试
* 为新代码编写文档
* 所有文件以换行符结尾

### 开发设置

1. **Fork 并克隆仓库**
   ```bash
   git clone https://github.com/YOUR_USERNAME/security-auto-scan.git
   cd security-auto-scan
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **进行更改**
   - 编写简洁可读的代码
   - 遵循现有代码风格
   - 如果适用，添加测试
   - 更新文档

5. **测试更改**
   - 本地测试 action
   - 确保所有现有测试通过
   - 为新功能添加新测试

6. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加你的功能描述"
   ```

   提交消息格式：
   - `feat:` - 新功能
   - `fix:` - Bug 修复
   - `docs:` - 文档更改
   - `style:` - 代码样式更改（格式化等）
   - `refactor:` - 代码重构
   - `test:` - 添加测试
   - `chore:` - 维护任务

7. **推送到你的 fork**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **打开 Pull Request**

### 代码风格

* Python 代码遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/)
* 使用有意义的变量和函数名
* 为函数和类编写文档字符串
* 保持函数专注和简洁
* 为复杂逻辑添加注释

### 测试

* 为新功能编写测试
* 确保向后兼容性
* 使用不同的 GitHub Token 权限测试
* 测试错误处理场景

### 文档

* 如需要，更新 README.md
* 在 EXAMPLES.md 中添加新的使用示例
* 保持英文和中文版本同步
* 使用清晰简洁的语言

### 有问题？

可以通过以下方式提问或联系：
- 📧 邮件：h7ml@qq.com
- 💬 [GitHub 讨论区](https://github.com/h7ml/security-auto-scan/discussions)
