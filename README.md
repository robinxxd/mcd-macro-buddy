# 麦麦热量精算师 (McDonald's Macro Buddy)

[![GitHub stars](https://img.shields.io/github/stars/robinxxd/mcd-macro-buddy?style=social)](https://github.com/robinxxd/mcd-macro-buddy/stargazers)
![Powered by](https://img.shields.io/badge/Powered%20by-McDonalds%20MCP-ffc72c)
![Platform](https://img.shields.io/badge/Platform-WorkBuddy-00b4d8)
![Contest](https://img.shields.io/badge/Contest-MCD%20Innovation%20Challenge-e4002b)

> 麦当劳程序员创意开发大赛参赛作品 · 基于麦当劳中国官方 MCP 开发的 WorkBuddy Skill

**一句话简介**：帮健身/控卡/想理性消费的用户，在麦当劳点餐时**同时满足热量与蛋白质目标，并叠加最优优惠券**，生成可按营养达标度和省钱力度排序的套餐方案。

⭐ 如果你也在减脂期馋麦当劳、或想算清优惠券怎么叠加最省，这个 Skill 一次帮你算明白。**欢迎 Star / Fork，也欢迎提 Issue 和 PR！**

---

## 为什么做这个

吃麦当劳和"吃得好/吃得健康"并不冲突。真实痛点有两个：

1. **营养盲区**：套餐热量动辄 800+ kcal，减脂/健身人群不知道怎么搭配能在目标热量内吃够蛋白。
2. **优惠碎片化**：麦麦省可领券、我的券、门店券、当月活动四套优惠，人工很难算清"怎样组合最省"。

本 Skill 把这两件事用麦当劳官方 MCP 真实数据一次性算清楚。

## 目标用户

- 健身 / 减脂 / 控卡人群（关注热量、蛋白、钠）
- 精打细算、希望叠加优惠券省钱的消费者
- 想快速决策"今天吃啥"的普通用户

## 核心能力

| 能力 | 说明 |
|---|---|
| 营养目标配餐 | 在热量/蛋白/钠约束下，按蛋白密度与饱腹度排序推荐套餐 |
| 优惠叠加省钱 | 整合麦麦省、我的券、门店券与当月活动，算最低实付 |
| 均衡模式 | 同时权衡营养达标度与省钱力度综合打分 |
| 一键下单（需确认） | 计价核对后由用户确认再下单，安全可控 |

## 🎬 效果演示

减脂期午餐，目标「≤550 kcal、蛋白尽量高、预算 30 元」，Skill 返回 Top3 方案（节选自 `examples/sample_output.json`）：

| 排名 | 套餐 | 热量 | 蛋白 | 原价 | 实付 | 省 | 用券 |
|---|---|---|---|---|---|---|---|
| 1 | 板烧鸡腿堡 + 玉米杯 | 500 | 29g | ¥31.5 | **¥20.5** | ¥11.0 | 满减 + 单品券 |
| 2 | 板烧鸡腿堡 | 430 | 26g | ¥22.0 | ¥22.0 | ¥0.0 | — |
| 3 | 板烧鸡腿堡 + 无糖可乐 | 430 | 26g | ¥31.0 | ¥23.0 | ¥8.0 | 单品券 |

> 💡 建议在文档顶部或此处补充一张 **WorkBuddy 实际对话截图**（命名为 `docs/demo.png`），视觉冲击力远胜文字，能显著提升访客 Star 意愿。

## 安装与使用

### 1. 申请麦当劳 MCP Token

按官方指引 https://github.com/M-China/mcd-mcp-server 登录 `open.mcd.cn/mcp`，在控制台「激活」申请 Token。

### 2. 在 WorkBuddy 中配置 MCP 连接器

左侧【专家·技能·连接器】→【连接器】→【自定义连接器】→【配置 MCP】，填入 `mcp-config.example.json` 内容，将 `${MCD_MCP_TOKEN}` 替换为你的真实 Token 并启用。

### 3. 安装本 Skill

将本仓库复制到 WorkBuddy 技能目录：

```
# 用户级（推荐，跨项目可用）
拷贝整个 mcd-macro-buddy/ 到 ~/.workbuddy/skills/

# 或项目级
拷贝到 <你的项目>/.workbuddy/skills/
```

重启/刷新 WorkBuddy 后，对话中提到"麦当劳""热量""套餐推荐""优惠券"等即会触发本 Skill。

### 4. 示例对话

```
用户：减脂期午餐想吃麦当劳，帮我配一份不超过 550 大卡、蛋白尽量高的，预算 30 块
→ 锁定门店 → 拉取营养与菜单 → 整理可用券 → 运行 optimize_combo.py
→ 返回 Top3 方案（含热量/蛋白/实付/用券），并询问是否下单
```

## 仓库结构

```
mcd-macro-buddy/
├── SKILL.md                       # WorkBuddy 技能定义（核心）
├── README.md                      # 本文件
├── CONTEST_DECLARATION.md         # 参赛声明（官方模板，不可修改）
├── MCP_INTEGRATION.md             # MCP 接入说明
├── mcp-config.example.json        # 脱敏 MCP 配置（仅占位符）
├── workbuddy.md                   # WorkBuddy 联动上下文（专项奖励用）
├── references/
│   ├── tools.md                   # mcd-mcp 工具清单与参数
│   └── optimizer_schema.md        # 优化器输入/输出契约
├── scripts/
│   └── optimize_combo.py          # 营养/价格组合优化器（可离线运行）
└── examples/
    ├── sample_input.json          # 示例输入
    └── sample_output.json         # 示例输出
```

## 免责声明

本项目为大赛参赛作品，非麦当劳官方产品。输出仅供参考，不构成医疗/营养专业建议；餐品信息、价格及供应状态以麦当劳官方实时结果为准。

## 许可

示例配置与代码按"现状"提供，仅限非商业用途、用于连接与使用麦当劳 MCP 服务。
