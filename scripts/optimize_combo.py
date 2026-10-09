#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
麦麦热量精算师 —— 组合优化器

在给定候选商品、营养/预算约束与优惠券规则下，求解满足目标且最优的麦当劳套餐组合。
三种模式：
  - nutrition : 热量上限内，按蛋白密度与饱腹度排序（控卡/健身优先）
  - savings   : 预算内，按用券后节省比例排序（省钱优先）
  - balanced  : 综合 营养达标度 + 省钱力度 + 饱腹度 加权打分

纯标准库实现，可离线运行。输入/输出契约见 references/optimizer_schema.md。
"""
import argparse
import itertools
import json
import sys


def load_data(text):
    return json.loads(text)


def validate_constraints(constraints):
    c = constraints or {}
    c.setdefault("max_calories", float("inf"))
    c.setdefault("min_protein", 0)
    c.setdefault("max_sodium", float("inf"))
    c.setdefault("budget", float("inf"))
    c.setdefault("avoid_tags", [])
    c.setdefault("max_items", 5)
    return c


def applicable_coupons(coupon, selected_codes, subtotal):
    """判断某券是否可作用于当前已选商品小计。"""
    if coupon.get("type") == "threshold":
        if subtotal < coupon.get("threshold", 0):
            return False
    applicable = coupon.get("applicable_codes", ["ANY"])
    if applicable == ["ANY"]:
        return True
    # 指定商品编码：至少包含一个适用商品才可用
    return any(code in applicable for code in selected_codes)


def apply_coupons(subtotal, selected_codes, coupons):
    """贪心叠加可用券，返回 (final_price, saved, used_coupon_ids)。"""
    remaining = subtotal
    used = []
    # 先按节省额从大到小尝试叠加（stackable 的才继续）
    candidate = sorted(
        coupons,
        key=lambda cp: _coupon_saving(cp, subtotal, selected_codes),
        reverse=True,
    )
    for cp in candidate:
        if remaining <= 0:
            break
        if not applicable_coupons(cp, selected_codes, remaining):
            continue
        if used and not cp.get("stackable", True) and any(
            not c.get("stackable", True) for c in coupons if c["id"] in used
        ):
            # 已用过不可叠加券，且本券也不可叠加 -> 跳过
            if not cp.get("stackable", True):
                continue
        saving = _coupon_saving(cp, remaining, selected_codes)
        if saving <= 0:
            continue
        remaining -= saving
        used.append(cp["id"])
    final = max(remaining, 0.0)
    return final, subtotal - final, used


def _coupon_saving(cp, subtotal, selected_codes):
    t = cp.get("type")
    if t == "threshold":
        if subtotal < cp.get("threshold", 0):
            return 0
        return float(cp.get("value", 0))
    if t == "discount":
        return subtotal * (1 - float(cp.get("value", 1.0)))
    if t == "fixed":
        return float(min(cp.get("value", 0), subtotal))
    return 0


def combo_metrics(items):
    m = {
        "calories": sum(i.get("calories", 0) for i in items),
        "protein": sum(i.get("protein", 0) for i in items),
        "fat": sum(i.get("fat", 0) for i in items),
        "carbs": sum(i.get("carbs", 0) for i in items),
        "sodium": sum(i.get("sodium", 0) for i in items),
        "original_price": round(sum(i.get("price", 0) for i in items), 2),
    }
    return m


def passes_hard_constraints(items, metrics, c):
    if metrics["calories"] > c["max_calories"]:
        return False
    if metrics["protein"] < c["min_protein"]:
        return False
    if metrics["sodium"] > c["max_sodium"]:
        return False
    if metrics["original_price"] > c["budget"]:
        return False
    avoid = set(c["avoid_tags"])
    for it in items:
        if avoid & set(it.get("tags", [])):
            return False
    return True


def score(combo, c, mode):
    items, metrics, final_price, saved, used = combo
    cal = metrics["calories"] or 1
    protein_density = metrics["protein"] / cal
    satiety = min(metrics["calories"] / (c["max_calories"] if c["max_calories"] != float("inf") else cal), 1.0)
    saved_ratio = (saved / metrics["original_price"]) if metrics["original_price"] else 0

    if mode == "savings":
        return saved_ratio
    if mode == "balanced":
        # 归一化到 0-1 附近
        norm_pd = min(protein_density / 0.10, 1.0)   # 0.10 g/kcal 视为满分基准
        norm_sr = min(saved_ratio / 0.30, 1.0)        # 30% 节省视为满分基准
        return 0.5 * norm_pd + 0.3 * norm_sr + 0.2 * satiety
    # nutrition (默认)
    return 0.7 * min(protein_density / 0.10, 1.0) + 0.3 * satiety


def solve(data):
    mode = data.get("mode", "nutrition")
    items = data.get("items", [])
    c = validate_constraints(data.get("constraints", {}))
    coupons = data.get("coupons", [])
    top_n = data.get("top_n", 3)
    max_items = c["max_items"]

    candidates = []
    # 受限枚举：从 1 到 max_items 个商品的组合（含套餐 + 单品混搭）
    for k in range(1, max_items + 1):
        for combo in itertools.combinations(items, k):
            metrics = combo_metrics(combo)
            if not passes_hard_constraints(combo, metrics, c):
                continue
            codes = [i["code"] for i in combo]
            final_price, saved, used = apply_coupons(metrics["original_price"], codes, coupons)
            sc = score((combo, metrics, final_price, saved, used), c, mode)
            candidates.append({
                "items": codes,
                "names": [i["name"] for i in combo],
                "calories": metrics["calories"],
                "protein": metrics["protein"],
                "fat": metrics["fat"],
                "carbs": metrics["carbs"],
                "sodium": metrics["sodium"],
                "original_price": metrics["original_price"],
                "final_price": round(final_price, 2),
                "saved": round(saved, 2),
                "used_coupons": used,
                "score": round(sc, 4),
            })

    # 排序：分数降序；同分按价格升序（更省优先）
    candidates.sort(key=lambda x: (-x["score"], x["final_price"]))
    return {"mode": mode, "solutions": candidates[:top_n]}


def main():
    ap = argparse.ArgumentParser(description="麦麦热量精算师组合优化器")
    ap.add_argument("--input", help="输入 JSON 文件路径（缺省读 stdin）")
    ap.add_argument("--output", help="输出 JSON 文件路径（缺省写 stdout）")
    args = ap.parse_args()

    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    data = load_data(text)
    result = solve(data)
    out = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out)
    else:
        print(out)


if __name__ == "__main__":
    main()
