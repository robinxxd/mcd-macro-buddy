# 推送到 GitHub 步骤

> 前提：先在 GitHub 网页新建一个 **Public** 仓库，仓库名建议用 `mcd-macro-buddy`（不要勾选自动生成 README，保持空仓库）。

## 1. 替换下面的用户名

把 `<YOUR_GITHUB_USERNAME>` 换成你自己的 GitHub 用户名。

## 2. 在 Git Bash / 终端执行

```bash
# 进入项目目录（若已在该目录可省略）
cd /c/Users/cn-laibjinluo/WorkBuddy/2026-10-09-16-28-34/mcd-macro-buddy

# 关联远程仓库
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/mcd-macro-buddy.git

# 统一分支名为 main
git branch -M main

# 推送到 GitHub（-u 之后下次直接 git push 即可）
git push -u origin main
```

## 3. 关于身份认证（重要）

GitHub 已不支持账号密码推送，二选一：

- **方式 A（推荐）**：安装并登录 GitHub CLI
  ```bash
  gh auth login          # 按提示用浏览器授权
  gh repo create mcd-macro-buddy --public --source=. --remote=origin --push
  ```
  上面这行可一步完成「建仓库 + 关联 + 推送」。

- **方式 B**：用 Personal Access Token (PAT) 代替密码
  1. GitHub → Settings → Developer settings → Personal access tokens → 生成 token（勾选 `repo` 权限）
  2. 推送时用户名填 GitHub 账号，密码/口令处粘贴 token（不是你的登录密码）

## 4. 推送完成后

1. 打开 `https://github.com/<YOUR_GITHUB_USERNAME>/mcd-macro-buddy` 确认仓库为 **Public**。
2. 到活动仓库 https://github.com/M-China/mcd-developer-innovation-challenge 发 New Issue，复制 `ISSUE_TEMPLATE.md` 内容提交报名（截止 2026-10-25 23:59）。

## 5. 后续更新

```bash
git add -A
git commit -m "更新说明"
git push
```
