# 麦当劳 MCP (mcd-mcp) 工具参考

本文件汇总 `mcd-mcp` 服务器（接入地址 `https://mcp.mcd.cn`，Streamable HTTP，请求头 `Authorization: Bearer <TOKEN>`）在本技能工作流中涉及的工具。完整列表以官方仓库 https://github.com/M-China/mcd-mcp-server 为准。

## 接入与限额

- 传输协议：Streamable HTTP
- 鉴权：请求头 `Authorization: Bearer YOUR_MCP_TOKEN`
- 限流：每 Token 每分钟最多 600 次请求，超限返回 429，需降低频率
- 错误码：401（Token 无效/过期/缺失）；429（限流）

## 本技能使用的工具

### 门店与配送
| 工具 | 用途 | 关键入参 |
|---|---|---|
| `query-nearby-stores` | 查询用户位置/地址附近的可用门店 | 地址或坐标 |
| `delivery-query-addresses` | 获取用户已创建的可配送地址列表 | — |
| `delivery-create-address` | 新增配送地址（无可配送地址时使用） | 收货人、电话、地址 |
| `delivery-query-stores` | 外送场景下查询某地址附近可配送门店 | 配送地址 |

### 营养与菜单
| 工具 | 用途 | 关键入参 |
|---|---|---|
| `list-nutrition-foods` | 餐品营养信息列表：能量、蛋白质、脂肪、碳水、钠、钙 | — |
| `query-meals` | 当前门店可售餐品菜单（分类、编码、标签、价格） | 门店标识 |
| `query-meal-detail` | 餐品详情/套餐组成与可替换选项 | 餐品编码 |

### 优惠
| 工具 | 用途 | 关键入参 |
|---|---|---|
| `available-coupons` | 麦麦省当前可领取的优惠券列表 | — |
| `auto-bind-coupons` | 一键领取麦麦省所有可用券（**写操作**） | — |
| `query-my-coupons` | 我的可用优惠券列表 | — |
| `store-coupons` | 当前门店可用优惠券列表 | 门店标识 |
| `campaign-calendar` | 当月营销活动日历（进行中/往期/未来） | 月份 |

### 计价与订单
| 工具 | 用途 | 关键入参 |
|---|---|---|
| `calculate-price` | 商品价格计算（含优惠券）：金额、配送费、优惠、应付 | 商品列表、券 |
| `create-order` | 创建订单，返回订单详情与支付链接（**写操作**） | 门店、就餐方式、商品、券 |
| `cancel-order` | 取消订单 | 订单号 |
| `query-order` | 查询订单详情/进度 | 订单号 |
| `order-list` | 查询近期历史订单 | — |

## 调用顺序要点

1. 先锁定**门店**，之后所有菜单/优惠/计价都绑定该门店。
2. `list-nutrition-foods` 与 `query-meals` 是「候选商品表」的两个数据源，需按名称/编码对齐。
3. 优惠存在三类来源（麦麦省可领、我的券、门店券），且 `campaign-calendar` 的促销可能额外可叠加；整理成规则后再交给 `optimize_combo.py`。
4. 写操作（`auto-bind-coupons`、`create-order`、`cancel-order`、`delivery-create-address`）必须征得上用户明确同意。
5. 计价 (`calculate-price`) 与下单 (`create-order`) 之间务必把金额与用券清单展示给用户核对。
