---
name: mcd-macro-buddy
description: 麦当劳「麦麦热量精算师」——面向健身/控卡用户的智能点餐助手。当用户想在麦当劳点餐同时满足热量/蛋白质目标并叠加最优优惠时使用本技能。它能串联麦当劳 MCP 的营养查询、菜单、门店、优惠券与计价工具，生成可按营养达标度和省钱力度排序的套餐方案。This skill should be used when users ask to build a McDonald's meal that fits calorie/macro goals, find the healthiest or most protein-dense McDonald's combo, compare McDonald's meals by nutrition and price, or stack McDonald's coupons (麦麦省/我的券/门店券) for the cheapest valid order.
agent_created: true
---

# 麦麦热量精算师 (McDonald's Macro Buddy)

## Overview

本技能把「吃得健康」和「吃得便宜」两个真实痛点合二为一：帮助健身、减脂、控卡或只是想理性点餐的用户，在麦当劳完成一次**同时满足营养目标与省钱目标**的点餐决策。

它通过麦当劳中国官方 MCP（`mcd-mcp`）真实调用以下能力：

- **营养决策**——`list-nutrition-foods` 提供能量、蛋白质、脂肪、碳水、钠、钙等数据
- **菜单与商品**——`query-meals`（门店在售菜单）、`query-meal-detail`（套餐组成/可替换项）
- **门店与配送**——`query-nearby-stores` / `delivery-query-stores` / `delivery-query-addresses`
- **优惠叠加**——`available-coupons`（麦麦省可领）、`auto-bind-coupons`、`query-my-coupons`（我的券）、`store-coupons`（门店券）
- **活动感知**——`campaign-calendar`（当月营销活动）
- **计价与下单**——`calculate-price`（含券计价）、`create-order` / `cancel-order` / `query-order` / `order-list`

核心产物：一组**营养达标 + 价格最优**的候选套餐，按「营养满足度 / 性价比 / 省钱力度」排序展示，用户确认后再决定是否下单。

> 安全原则：本技能只推荐、不复盘式下单。`create-order` 等写操作必须在用户**明确确认**后才执行；下单前展示完整金额、优惠与使用券清单。所有餐品信息、价格、供应状态以麦当劳官方实时返回为准。

## 何时使用本技能

触发场景示例：

- "减脂期中午想吃麦当劳，帮我配一份不超过 500 大卡、蛋白尽量高的套餐"
- "我想用最少的钱在麦当劳吃饱，今天有什么优惠券能用？"
- "帮我对比麦辣鸡腿堡套餐和板烧鸡腿堡套餐的热量和价格"
- "附近哪家麦当劳能外送，给我算一个 600 大卡内、预算 30 块的午餐"
- "我有哪些麦当劳优惠券？能不能叠加到这个订单上"

不在本技能范围：纯物流/招聘/无关品牌对比、对麦当劳品牌的负面或对比式表述（违反活动合规要求），以及任何需要真实支付却未经确认的操作。

## 工作流 (Workflow)

### 第 0 步：明确目标与约束

向用户收集（缺失时主动追问，但尽量从一句话里推断）：

- 餐别：早餐 / 午餐 / 晚餐 / 加餐
- 营养目标：`max_calories`（上限，必填之一）、`min_protein`（下限）、`max_sodium`（可选）
- 预算：`budget`（可选）
- 禁忌：`avoid_tags`（如 海鲜、辛辣、含酒精、素食）、过敏原
- 场景：到店自取 / 麦乐送外送（决定用 `query-nearby-stores` 还是 `delivery-query-stores`）

### 第 1 步：锁定门店

- 到店：调用 `query-nearby-stores`（传入用户位置/地址）→ 选最近或指定门店。
- 外送：先 `delivery-query-addresses` 取已存地址；若无则 `delivery-create-address` 引导新增；再 `delivery-query-stores` 取可配送门店。
- 后续所有菜单/优惠/计价调用都**绑定该门店**。

### 第 2 步：拉取营养与菜单数据

- `list-nutrition-foods`：获取常见餐品营养基准（能量/蛋白/脂肪/碳水/钠/钙）。
- `query-meals`：获取该门店**当前在售**菜单（分类、餐品编码、标签、是否套餐、原价/优惠价）。
- 对重点套餐用 `query-meal-detail` 展开组成与可替换选项（如把可乐换成无糖、薯条换成玉米杯以降低热量）。
- 将两份数据按餐品名称/编码对齐，形成「候选商品表」（含 calories / protein / price / tags / is_combo）。

### 第 3 步：拉取可用优惠

- `available-coupons`：麦麦省当前可领券 → 提示用户用 `auto-bind-coupons` 一键领券（写操作，先征得同意）。
- `query-my-coupons`：账户已持有券（含门槛、适用商品、有效期）。
- `store-coupons`：当前门店可用券。
- `campaign-calendar`：当月进行中/未来活动，提示可叠加的促销（如买一送一、特价）。
- 把券整理成结构化规则：适用商品编码、满减门槛、折扣、叠加优先级。

### 第 4 步：组合优化（核心）

调用本技能自带的 `scripts/optimize_combo.py`，把候选商品表 + 约束 + 优惠规则作为输入，求解候选套餐：

- **营养模式**（默认）：在 `max_calories` 内，按「蛋白密度（protein/calorie）」与「饱腹/满足度」排序，给出 Top-N。
- **省钱模式**：在预算内，用券后实付最低，给出 Top-N，并标注节省金额。
- **均衡模式**：同时考虑营养达标度与省钱力度，综合打分排序。

输入/输出契约见 `references/optimizer_schema.md`。脚本是确定性的，不依赖网络，可反复调用做「what-if」（如"把可乐换成无糖能省多少热量"）。

### 第 5 步：展示与确认

以可读列表呈现 Top 方案，每个方案包含：

- 组合明细（商品 + 可替换建议）
- 营养合计（热量/蛋白/脂肪/碳水/钠）与目标对比 ✅/⚠️
- 单价 / 优惠后价 / 节省金额 / 使用券清单
- 关联活动（如有）

**不自动下单**。提示用户："要不要我帮你用这个方案下单？" 用户确认后再进入第 6 步。

### 第 6 步：计价与下单（需确认）

- `calculate-price`：传入商品列表 + 选定券，返回金额、配送费、优惠、应付总价，先展示核对。
- `create-order`：用户再次确认金额后调用，返回订单详情与支付链接。
- 下单后可用 `query-order` 跟踪，或 `cancel-order` 取消（30 分钟内未支付通常可取消，以官方规则为准）。

## 资源

### references/

- `references/tools.md`——`mcd-mcp` 全部工具的用途、参数要点与调用顺序，遇到不确定时查阅。
- `references/optimizer_schema.md`——`optimize_combo.py` 的输入/输出 JSON 契约与评分公式。

### scripts/

- `scripts/optimize_combo.py`——营养/价格组合优化器（确定性、可离线运行）。输入候选商品表、约束与券规则，输出排序后的候选套餐。是「第 4 步」的执行体，强烈建议用它而非凭感觉组合，以保证结果可复现。

### 工具调用顺序速查

```
query-nearby-stores / delivery-query-addresses → delivery-query-stores   (锁定门店)
list-nutrition-foods + query-meals [+ query-meal-detail]                 (候选商品表)
available-coupons → auto-bind-coupons* → query-my-coupons → store-coupons → campaign-calendar  (优惠)
optimize_combo.py                                                          (组合优化)
calculate-price → (确认) → create-order → query-order                     (计价/下单)
```
带 `*` 为写操作，需用户同意。
