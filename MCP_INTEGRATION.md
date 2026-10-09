# MCP 接入说明 (MCP_INTEGRATION)

## 使用的 MCP Server

- **名称**：麦当劳中国 MCP Server (`mcd-mcp`)
- **接入地址**：`https://mcp.mcd.cn`
- **传输协议**：Streamable HTTP
- **鉴权方式**：请求头 `Authorization: Bearer <MCP_TOKEN>`
- **官方仓库**：https://github.com/M-China/mcd-mcp-server
- **限流**：每 Token 每分钟 ≤ 600 次请求（超限 429）

## 实际使用的 Tool 与用途

| 工具 | 在本项目中的用途 |
|---|---|
| `query-nearby-stores` | 到店场景：锁定用户附近门店，作为后续菜单/优惠/计价的上下文 |
| `delivery-query-addresses` | 外送场景：读取已存配送地址 |
| `delivery-create-address` | 外送场景：无地址时引导新增（写操作，需确认） |
| `delivery-query-stores` | 外送场景：查询可配送门店 |
| `list-nutrition-foods` | 获取餐品能量/蛋白/脂肪/碳水/钠/钙，构建营养基准 |
| `query-meals` | 获取当前门店在售菜单（编码、标签、价格） |
| `query-meal-detail` | 展开套餐组成与可替换项（如换无糖/换玉米杯降热量） |
| `available-coupons` | 麦麦省当前可领券列表 |
| `auto-bind-coupons` | 一键领券（写操作，需确认） |
| `query-my-coupons` | 我的可用券（门槛/适用商品/有效期） |
| `store-coupons` | 当前门店可用券 |
| `campaign-calendar` | 当月营销活动，提示可叠加促销 |
| `calculate-price` | 含券计价：金额/配送费/优惠/应付，下单前核对 |
| `create-order` | 用户确认后创建订单，返回支付链接（写操作） |
| `query-order` / `cancel-order` | 订单跟踪与取消 |
| `order-list` | 历史订单查询 |

## 调用流程

```
[锁定门店]
  query-nearby-stores 或 (delivery-query-addresses → delivery-query-stores)
        │
[构建候选商品表]
  list-nutrition-foods + query-meals (+ query-meal-detail 展开套餐)
  按名称/编码对齐 → {code, name, calories, protein, fat, carbs, sodium, price, tags}
        │
[整理优惠规则]
  available-coupons → (auto-bind-coupons) → query-my-coupons → store-coupons → campaign-calendar
  结构化为 {id, type, threshold/value, applicable_codes, stackable}
        │
[组合优化]  ← 关键差异化步骤
  scripts/optimize_combo.py（确定性、离线）
  输入：候选商品表 + 约束(max_calories/min_protein/budget/avoid_tags) + 券规则 + mode
  输出：Top-N 套餐（营养/价格/用券/评分）
        │
[展示与确认]
  呈现 Top 方案，标注营养对比与目标 ✅/⚠️、实付、节省、用券
        │
[计价与下单]（需用户明确确认）
  calculate-price → 展示核对 → create-order → query-order
```

## 业务价值

1. **降低决策成本**：把"营养计算 + 优惠比对"两件事合并为一次对话结果，用户不再需要在 App 里反复试算。
2. **真实可用**：所有数据来自麦当劳官方 MCP 实时返回，非静态硬编码，菜单/价格/优惠变动自动同步。
3. **安全下单**：写操作（领券、下单、取消、建地址）均设确认闸，避免误扣与误单。
4. **可复现**：核心优化逻辑下沉为确定性脚本 `optimize_combo.py`，支持 what-if（"换无糖能省多少热量"），结果稳定可追溯。

## 配置示例（脱敏）

见 `mcp-config.example.json`，仅含环境变量占位符 `${MCD_MCP_TOKEN}`，不含任何真实凭证。
