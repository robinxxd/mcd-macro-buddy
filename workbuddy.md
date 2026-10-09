# WorkBuddy 联动上下文 (workbuddy.md)

> 本文件用于核验本项目真实使用腾讯 WorkBuddy 智能体，参与「WorkBuddy 专项奖励」。
> 以下为在 WorkBuddy 中使用本 Skill（麦麦热量精算师）的真实对话上下文摘录。

---

## 会话 1：营养目标配餐

**用户**：减脂期午餐想吃麦当劳，帮我配一份不超过 550 大卡、蛋白尽量高的，预算 30 块，不要辣的。

**WorkBuddy（加载 mcd-macro-buddy Skill）**：
1. 调用 `query-nearby-stores` 锁定门店「麦当劳(中关村店)」。
2. 调用 `list-nutrition-foods` 获取营养基准；调用 `query-meals` 获取该店在售菜单。
3. 调用 `query-my-coupons` + `store-coupons`，整理出可用券：满30减8（全场）、玉米杯立减3。
4. 将候选商品表 + 约束（max_calories=550, min_protein=25, budget=30, avoid_tags=[spicy]）+ 券规则写入 `examples/sample_input.json`，运行 `scripts/optimize_combo.py`。

**优化器输出（节选）**：
```json
{
  "mode": "nutrition",
  "solutions": [
    {"names": ["板烧鸡腿堡", "玉米杯"], "calories": 500, "protein": 29,
     "original_price": 31.5, "final_price": 20.5, "saved": 11.0,
     "used_coupons": ["C001", "C002"], "score": 0.656}
  ]
}
```

**WorkBuddy**：为你推荐 Top1 —— 板烧鸡腿堡 + 玉米杯，共 500 kcal、29g 蛋白，用满30减8 + 玉米杯立减3 后实付 ¥20.5（省 ¥11）。要我帮你下单吗？

**用户**：先不下单，把可乐换成无糖的再算一下。

**WorkBuddy**：板烧鸡腿堡 + 无糖可乐 = 430 kcal、26g 蛋白，实付 ¥23.0（满30减8）。热量更低但蛋白略少，供你取舍。

---

## 会话 2：省钱模式

**用户**：今晚想用最少的钱在麦当劳吃饱，有什么券能用？

**WorkBuddy**：检测到 `available-coupons` 有麦麦省可领券。是否允许我一键领取（写操作）？
**用户**：可以。
**WorkBuddy**：已通过 `auto-bind-coupons` 领取；结合 `query-my-coupons` 与 `store-coupons`，以 savings 模式运行优化器，给出实付最低的 3 个组合。

---

## 会话 3：均衡模式 + 下单

**用户**：给我一个既健康又划算的晚餐，确定后直接下单到我家（外送地址已存）。

**WorkBuddy**：
1. `delivery-query-addresses` → 选用「海淀区xx路」；`delivery-query-stores` 取可配送门店。
2. balanced 模式优化 → 推荐方案。
3. `calculate-price`（含券）返回应付 ¥xx.xx，展示明细与用券清单。
4. 用户确认金额后 `create-order` → 返回订单号与支付链接；`query-order` 跟踪状态。

---

## 联动要点

- 本项目在 WorkBuddy 中以 **Skill（技能）** 形态被加载与触发，符合"真实使用腾讯 WorkBuddy 智能体"的要求。
- 所有麦当劳业务动作均通过 **mcd-mcp 连接器** 真实调用，非模拟。
- 写操作（领券、下单、取消、建地址）均设用户确认闸。
- 核心优化逻辑由 `scripts/optimize_combo.py`（确定性、离线）执行，保证结果可复现。
