# 推送到 GitHub 步骤

> 当前状态：本地仓库已就绪（分支 `main`，已提交）。下面只需完成「授权 + 推送」。

## 方案：用 GitHub CLI（gh）推送（推荐，一步建库+推送）

环境里已备好**绿色版 gh**（无需安装）：
`C:/Users/cn-laibjinluo/.local/gh/bin/gh.exe`

### 第 1 步（你来做，必须交互）：登录授权

打开你自己的终端（Git Bash / PowerShell 均可），运行：

```bash
"C:/Users/cn-laibjinluo/.local/gh/bin/gh.exe" auth login
```

按提示选择 GitHub.com → 用浏览器授权（或选粘贴 Token）。这是 GitHub 的安全机制，任何自动化都无法跳过。

> 嫌每次打长路径麻烦，可把该 `bin` 目录加入 PATH，或先 `winget install GitHub.cli` 装系统版。

### 第 2 步（授权完成后告诉我，由我执行）：建库并推送

```bash
cd /c/Users/cn-laibjinluo/WorkBuddy/2026-10-09-16-28-34/mcd-macro-buddy
"C:/Users/cn-laibjinluo/.local/gh/bin/gh.exe" repo create mcd-macro-buddy --public --source=. --remote=origin --push
```

这行会：自动在**你的**账号下新建 `mcd-macro-buddy` 公开仓库 → 关联 `origin` → 推送 `main` 分支。

## 备选：用 Personal Access Token（PAT）而非 gh

1. GitHub → Settings → Developer settings → Personal access tokens → 生成 token（勾选 `repo` 权限）。
2. 把 token 给我，我执行：
   ```bash
   printf '%s' "<你的PAT>" | "C:/Users/cn-laibjinluo/.local/gh/bin/gh.exe" auth login --with-token
   ```
   随后同样用上面的 `gh repo create ... --push` 完成推送。

## 推送完成后

1. 打开 `https://github.com/<你的用户名>/mcd-macro-buddy` 确认仓库为 **Public**。
2. 到活动仓库 https://github.com/M-China/mcd-developer-innovation-challenge 发 New Issue，复制 `ISSUE_TEMPLATE.md` 内容提交报名（截止 2026-10-25 23:59）。

## 后续更新

```bash
git add -A
git commit -m "更新说明"
git push
```
