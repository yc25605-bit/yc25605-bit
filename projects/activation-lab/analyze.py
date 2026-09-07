"""分析人工构造的新用户漏斗。仅使用 Python 标准库。"""
import json
from pathlib import Path

STAGES = ("registered", "goal_set", "first_learning", "day1_return")


def summarize(rows):
    if not rows:
        raise ValueError("至少需要一个渠道")
    for row in rows:
        values = [row[key] for key in STAGES]
        if any(type(value) is not int or value < 0 for value in values):
            raise ValueError("用户数必须是非负整数")
        if any(left < right for left, right in zip(values, values[1:])):
            raise ValueError("顺序漏斗的下游人数不能超过上游")
    return {key: sum(row[key] for row in rows) for key in STAGES}


def rate(numerator, denominator):
    return f"{numerator / denominator:.2%}" if denominator else "N/A"


def main():
    dataset = json.loads(Path(__file__).with_name("data.json").read_text(encoding="utf-8"))
    if dataset.get("dataset_type") != "synthetic":
        raise ValueError("此脚本用于明确标识的模拟数据")
    rows = dataset["channels"]
    total = summarize(rows)
    print("模拟案例 | 新用户激活漏斗")
    print("渠道 | 注册 | 目标设置 | 首次学习 | D1回访 | 激活率 | 激活用户D1回访率")
    for row in [*rows, {"channel": "合计", **total}]:
        print(" | ".join([
            row["channel"], *(str(row[key]) for key in STAGES),
            rate(row["first_learning"], row["registered"]),
            rate(row["day1_return"], row["first_learning"]),
        ]))
    print("\n相邻阶段流失（同一 cohort，顺序漏斗）")
    for left, right in zip(STAGES, STAGES[1:]):
        print(f"{left} -> {right}: 流失 {total[left] - total[right]} 人，"
              f"转化率 {rate(total[right], total[left])}")
    target = 0.42
    print(f"\n假设激活率达到 {target:.0%}："
          f"同等注册规模新增激活约 {round(total['registered'] * target - total['first_learning'])} 人。"
          "这是情景测算，不是实验结果。")


if __name__ == "__main__":
    main()
