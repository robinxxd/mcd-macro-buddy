# optimize_combo.py 输入/输出契约

脚本路径：`scripts/optimize_combo.py`
运行方式：`python optimize_combo.py --input input.json --output out.json` 或直接 `python optimize_combo.py`（读取 stdin，输出 stdout JSON）。
依赖：仅 Python 标准库，可离线运行。

## 输入 JSON 结构

```json
{
  "mode": "nutrition | savings | balanced",   // 默认 nutrition
  "items": [
    {
      "code": "M1001",
      "name": "麦辣鸡腿堡",
      "calories": 490,
      "protein": 21,
      "fat": 24,
      "carbs": 44,
      "sodium": 890,
      "price": 21.5,
      "tags": ["burger", "spicy"],
      "is_combo": false
    }
  ],
  "constraints": {
    "max_calories": 600,
    "min_protein": 25,
    "max_sodium": 1500,
    "budget": 35,
    "avoid_tags": ["spicy", "seafood"],
    "max_items": 5
  },
  "coupons": [
    {
      "id": "C001",
      "name": "满30减8",
      "type": "threshold",     // threshold(满减) | discount(折扣) | fixed(定额立减)
      "threshold": 30,
      "value": 8,
      "applicable_codes": ["ANY"],   // ["ANY"] 表示全场通用，否则仅指定餐品编码
      "stackable": true
    }
  ],
  "top_n": 3
}
```

## 输出 JSON 结构

```json
{
  "mode": "nutrition",
  "solutions": [
    {
      "items": ["M1001", "M2002"],
      "names": ["麦辣鸡腿堡", "玉米杯"],
      "calories": 560,
      "protein": 28,
      "fat": 26,
      "carbs": 58,
      "sodium": 1010,
      "original_price": 28.5,
      "final_price": 20.5,
      "saved": 8.0,
      "used_coupons": ["C001"],
      "score": 0.92,
      "note": "蛋白密度高且在热量上限内；已用满30减8"
    }
  ]
}
```

## 评分公式（默认权重，可后续调参）

- **nutrition 模式**：`score = protein_density * w1 + satiety * w2`，其中
  `protein_density = protein / calories`，`satiety = min(calories / max_calories, 1)`；
  未满足 `min_protein` / `max_sodium` / `avoid_tags` 的组合直接淘汰。
- **savings 模式**：`score = saved_ratio`，`saved_ratio = saved / original_price`；
  超 `budget` 的组合淘汰。
- **balanced 模式**：`score = 0.5 * norm(protein_density) + 0.3 * norm(saved_ratio) + 0.2 * satiety`。

所有金额单位为元（CNY）；营养单位为 kcal / g / mg。组合搜索采用受限枚举（单餐 `max_items` 默认 5，候选商品通常 <40，暴力/剪枝均可接受）。
