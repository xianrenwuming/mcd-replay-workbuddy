#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_recap.py — 麦麦回忆局（McD Replay）回顾卡生成脚本

职责边界（重要）：
- 只接收「去标识化汇总输入 JSON」，其中不得包含订单号、门店名、地址、
  手机号、会员号、Token、券码等任何可识别个人身份的信息。
- 不联网、不读取环境变量/密钥、不调用任何 MCP 接口。
- 对订单数、金额、时段、餐品等字段做确定性计算，并渲染本地 HTML 卡片。
- 所有写入 HTML 的文本均经过 html.escape 转义。

用法：
    python build_recap.py <input.json> <output.html> [--template recap-card.html]

输入 JSON 结构（orders 中的字段均为可选的去标识化字段）：
{
  "meta": {
    "title": "我的麦麦回顾",                # 可选
    "generated_at": "2026-10-09 20:00",     # 可选
    "is_sample": false,                      # 可选，true 时卡片显示「示例数据」水印
    "scope_note": "仅统计本次接口返回记录",   # 可选，数据区间不完整时必填
    "persona": "一句由 AI 生成的画像文案"     # 可选，脚本只做转义展示，不改写
  },
  "orders": [
    {
      "create_time": "2026-08-18 10:31:34",  # 下单时间（可选）
      "status": "订单已完成",                 # 订单状态原文（可选）
      "channel": "到店",                      # 渠道：到店/外送/其他（可选）
      "amount": 13.9,                          # 实付金额，数字（可选）
      "items": [{"name": "中薯条", "quantity": 1}]  # 餐品名+数量（可选）
    }
  ]
}
"""

import json
import sys
import html
import argparse
from collections import Counter
from datetime import datetime
from pathlib import Path

# 状态判定：包含以下关键词视为「成功/已完成」；其余状态单独列出，不计入消费统计
SUCCESS_KEYWORDS = ("完成", "成功")

# 时段划分（按下单时间的小时数）
TIME_BUCKETS = [
    ("早餐 05:00-10:29", 5, 10),
    ("午餐 10:30-13:59", 10.5, 14),
    ("下午茶 14:00-16:59", 14, 17),
    ("晚餐 17:00-20:59", 17, 21),
    ("夜宵 21:00-04:59", 21, 29),  # 21 点后及次日 5 点前
]

TOP_ITEMS_LIMIT = 5


def esc(value):
    """对任何写入 HTML 的值做转义。"""
    return html.escape("" if value is None else str(value), quote=True)


def parse_time(value):
    """解析 'YYYY-MM-DD HH:MM:SS'，失败返回 None。"""
    if not value or not isinstance(value, str):
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(value.strip(), fmt)
        except ValueError:
            continue
    return None


def parse_amount(value):
    """金额解析：接受数字或可转数字的字符串，失败返回 None。"""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None


def is_success(status):
    if not status or not isinstance(status, str):
        return False
    return any(k in status for k in SUCCESS_KEYWORDS)


def bucket_of(dt):
    """返回订单所属时段名称；无法解析时间返回 None。"""
    if dt is None:
        return None
    h = dt.hour + dt.minute / 60.0
    if h >= 21 or h < 5:
        return TIME_BUCKETS[4][0]
    for name, start, end in TIME_BUCKETS[:4]:
        if start <= h < end:
            return name
    return None


def compute_stats(orders):
    """对去标识化订单列表做确定性统计，返回纯数据字典。"""
    total = len(orders)
    completed = []
    other_status = Counter()
    amount_missing = 0
    amounts = []
    times = []
    item_counter = Counter()
    time_counter = Counter()
    channel_counter = Counter()

    for o in orders:
        if not isinstance(o, dict):
            other_status["记录格式异常"] += 1
            continue
        status = o.get("status")
        if is_success(status):
            completed.append(o)
        else:
            other_status[status if isinstance(status, str) and status else "状态未知"] += 1
            continue  # 非成功订单不进入消费/餐品统计

        dt = parse_time(o.get("create_time"))
        if dt:
            times.append(dt)
            b = bucket_of(dt)
            if b:
                time_counter[b] += 1

        amount = parse_amount(o.get("amount"))
        if amount is None:
            amount_missing += 1
        else:
            amounts.append(amount)

        channel = o.get("channel")
        if isinstance(channel, str) and channel.strip():
            channel_counter[channel.strip()] += 1

        items = o.get("items")
        if isinstance(items, list):
            for it in items:
                if not isinstance(it, dict):
                    continue
                name = it.get("name")
                qty = it.get("quantity")
                if not isinstance(name, str) or not name.strip():
                    continue
                if not isinstance(qty, int) or qty <= 0:
                    qty = 1
                item_counter[name.strip()] += qty

    stats = {
        "total_records": total,
        "completed_count": len(completed),
        "other_status": dict(other_status),
        "date_min": min(times).strftime("%Y-%m-%d") if times else None,
        "date_max": max(times).strftime("%Y-%m-%d") if times else None,
        "total_spend": round(sum(amounts), 2) if amounts else None,
        "avg_spend": round(sum(amounts) / len(amounts), 2) if amounts else None,
        "amount_missing": amount_missing,
        "top_items": item_counter.most_common(TOP_ITEMS_LIMIT),
        "time_buckets": [(name, time_counter.get(name, 0)) for name, _, _ in TIME_BUCKETS],
        "channels": channel_counter.most_common(),
    }
    return stats


def render_bar_rows(pairs, unit, max_pairs=None):
    """把 (名称, 数量) 列表渲染成带比例条的 HTML 行。所有文本转义。"""
    rows = []
    data = pairs if max_pairs is None else pairs[:max_pairs]
    top = max((v for _, v in data), default=0)
    for name, value in data:
        width = int(round(value / top * 100)) if top else 0
        rows.append(
            '<div class="row">'
            f'<span class="row-name">{esc(name)}</span>'
            f'<span class="row-bar"><span class="row-fill" style="width:{width}%"></span></span>'
            f'<span class="row-val">{esc(value)}{esc(unit)}</span>'
            "</div>"
        )
    if not rows:
        return '<div class="empty">本次返回记录中无此字段</div>'
    return "\n".join(rows)


def render_other_status(other):
    if not other:
        return ""
    items = "".join(
        f"<li>{esc(status)}：{esc(count)} 笔（未计入消费统计）</li>"
        for status, count in other.items()
    )
    return f'<ul class="other-status">{items}</ul>'


def build_html(template_text, meta, stats):
    title = meta.get("title") or "我的麦麦回顾"
    generated_at = meta.get("generated_at") or datetime.now().strftime("%Y-%m-%d %H:%M")
    is_sample = bool(meta.get("is_sample"))
    scope_note = meta.get("scope_note") or ""
    persona = meta.get("persona") or ""

    if stats["date_min"] and stats["date_max"]:
        date_range = f'{stats["date_min"]} 至 {stats["date_max"]}'
    else:
        date_range = "时间字段不足，无法统计区间"

    total_spend = f'¥{stats["total_spend"]:.2f}' if stats["total_spend"] is not None else "金额字段不足"
    avg_spend = f'¥{stats["avg_spend"]:.2f}' if stats["avg_spend"] is not None else "—"

    sample_badge = (
        '<div class="sample-badge">示例数据 · 非真实账户</div>' if is_sample else ""
    )
    scope_html = f'<div class="scope-note">※ {esc(scope_note)}</div>' if scope_note else ""
    persona_html = (
        f'<div class="persona"><span class="persona-tag">麦麦画像</span>{esc(persona)}</div>'
        if persona
        else ""
    )
    amount_missing_html = (
        f'<div class="hint">另有 {stats["amount_missing"]} 笔成功订单缺少金额字段，未计入金额统计</div>'
        if stats["amount_missing"]
        else ""
    )

    replacements = {
        "%%TITLE%%": esc(title),
        "%%GENERATED_AT%%": esc(generated_at),
        "%%SAMPLE_BADGE%%": sample_badge,
        "%%SCOPE_NOTE%%": scope_html,
        "%%DATE_RANGE%%": esc(date_range),
        "%%TOTAL_RECORDS%%": esc(stats["total_records"]),
        "%%COMPLETED_COUNT%%": esc(stats["completed_count"]),
        "%%TOTAL_SPEND%%": esc(total_spend),
        "%%AVG_SPEND%%": esc(avg_spend),
        "%%AMOUNT_MISSING%%": amount_missing_html,
        "%%TOP_ITEMS_HTML%%": render_bar_rows(stats["top_items"], " 份"),
        "%%TIME_BUCKETS_HTML%%": render_bar_rows(stats["time_buckets"], " 单"),
        "%%CHANNEL_HTML%%": render_bar_rows(stats["channels"], " 单"),
        "%%OTHER_STATUS_HTML%%": render_other_status(stats["other_status"]),
        "%%PERSONA%%": persona_html,
    }
    out = template_text
    for key, value in replacements.items():
        out = out.replace(key, value)
    return out


def main():
    parser = argparse.ArgumentParser(description="生成麦麦回忆局本地回顾卡（仅处理去标识化汇总数据）")
    parser.add_argument("input", help="去标识化汇总输入 JSON 路径")
    parser.add_argument("output", help="输出 HTML 卡片路径")
    parser.add_argument(
        "--template",
        default=str(Path(__file__).resolve().parent.parent / "templates" / "recap-card.html"),
        help="卡片模板路径（默认使用技能内置模板）",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    template_path = Path(args.template)

    with input_path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise SystemExit("输入 JSON 顶层必须是对象")
    meta = payload.get("meta") or {}
    orders = payload.get("orders") or []
    if not isinstance(orders, list):
        raise SystemExit("orders 字段必须是数组")

    template_text = template_path.read_text(encoding="utf-8")
    stats = compute_stats(orders)
    html_text = build_html(template_text, meta, stats)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_text, encoding="utf-8")

    # 控制台只输出统计摘要（纯数字），不回显任何输入文本
    print(json.dumps({
        "ok": True,
        "output": str(output_path),
        "total_records": stats["total_records"],
        "completed_count": stats["completed_count"],
        "total_spend": stats["total_spend"],
        "avg_spend": stats["avg_spend"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
