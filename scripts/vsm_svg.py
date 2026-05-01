#!/usr/bin/env python3
"""
VSM SVG Generator — Generate professional Value Stream Maps as SVG.
Supports linear flows and branch (parallel) flows.

Usage:
    python vsm_svg.py input.json output.svg
    python vsm_svg.py input.json output.png   # auto-converts via rsvg-convert
"""

import json
import math
import os
import subprocess
import sys, json, os, csv
from pathlib import Path

# ── Layout constants ──────────────────────────────────────────────
MARGIN = 50
SUPPLIER_W = 90
PROCESS_W = 120
PROCESS_H = 105
PROCESS_NAME_H = 26
INV_W = 42
CUSTOMER_W = 90
GAP = 18

TITLE_Y = 18
INFO_Y = 72
BRANCH_ZONE_TOP = 108
MATERIAL_Y = 210
SEPARATOR_Y = 355
TIMELINE_Y = 370

# ── Colors ────────────────────────────────────────────────────────
C_FILL = "#ffffff"
C_STROKE = "#333"
C_HEADER = "#f0f3f6"
C_INV_FILL = "#e0e0e0"
C_INV_STROKE = "#666"
C_SUPPLIER = "#d4e6f1"
C_SUP_ACCENT = "#2980b9"
C_CUSTOMER = "#d5f5e3"
C_CUST_ACCENT = "#27ae60"
C_PUSH = "#333"
C_ELEC = "#2980b9"
C_MANUAL = "#27ae60"
C_UPPER = "#e67e22"
C_LOWER = "#3498db"
C_KAIZEN = "#fff3cd"
C_KAIZEN_S = "#f39c12"
C_PC = "#fef9e7"
C_PC_S = "#d4ac0d"
C_BRANCH = "#e8daef"
C_BRANCH_S = "#8e44ad"

FONT = "'PingFang SC','Microsoft YaHei','Noto Sans SC',Arial,sans-serif"


# ── SVG helpers ───────────────────────────────────────────────────
def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def T(name, attrs, content="", sc=False):
    a = " ".join(f'{k}="{v}"' for k, v in attrs.items())
    if sc:
        return f"<{name} {a}/>"
    return f"<{name} {a}>{content}</{name}>"


def txt(x, y, text, sz=11, anchor="middle", bold=False, color="#333"):
    w = "bold" if bold else "normal"
    return T("text", {"x": x, "y": y, "font-size": sz, "text-anchor": anchor,
                      "font-family": FONT, "font-weight": w, "fill": color,
                      "dominant-baseline": "central"}, esc(text))


def rect(x, y, w, h, fill=C_FILL, stroke=C_STROKE, sw=1.5, rx=2):
    return T("rect", {"x": x, "y": y, "width": w, "height": h,
                      "fill": fill, "stroke": stroke, "stroke-width": sw, "rx": rx})


def ln(x1, y1, x2, y2, color=C_PUSH, sw=2, dash=None):
    a = {"x1": x1, "y1": y1, "x2": x2, "y2": y2, "stroke": color, "stroke-width": sw}
    if dash:
        a["stroke-dasharray"] = dash
    return T("line", a, sc=True)


def arrow(x, y, d="right", sz=7, color=C_PUSH):
    if d == "right":
        pts = f"{x},{y - sz / 2} {x + sz},{y} {x},{y + sz / 2}"
    elif d == "left":
        pts = f"{x},{y - sz / 2} {x - sz},{y} {x},{y + sz / 2}"
    elif d == "down":
        pts = f"{x - sz / 2},{y} {x},{y + sz} {x + sz / 2},{y}"
    return T("polygon", {"points": pts, "fill": color}, sc=True)


def sawtooth(x1, y, x2, color, amp=4):
    length = abs(x2 - x1)
    num = max(8, int(length / 16))
    step = (x2 - x1) / num
    pts = [f"{x1},{y}"]
    for i in range(num):
        xi = x1 + step * (i + 0.5)
        yi = y + amp * (1 if i % 2 == 0 else -1)
        pts.append(f"{xi:.1f},{yi:.1f}")
    pts.append(f"{x2},{y}")
    return T("polyline", {"points": " ".join(pts), "fill": "none",
                           "stroke": color, "stroke-width": "1.5"})


def starburst(cx, cy, ro=22, ri=13, n=12):
    pts = []
    for i in range(n * 2):
        a = i * math.pi / n - math.pi / 2
        r = ro if i % 2 == 0 else ri
        pts.append(f"{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}")
    return T("polygon", {"points": " ".join(pts),
                          "fill": C_KAIZEN, "stroke": C_KAIZEN_S, "stroke-width": "1.5"}, sc=True)


# ── Layout ────────────────────────────────────────────────────────
def calc_positions(processes, material_y=None):
    my = material_y or MATERIAL_Y
    n = len(processes)
    pos = {"supplier": MARGIN, "processes": [], "inventories": [], "customer": 0}
    x = MARGIN + SUPPLIER_W + GAP
    pos["inventories"].append(x); x += INV_W + GAP
    for i in range(n):
        pos["processes"].append(x); x += PROCESS_W + GAP
        if i < n - 1:
            pos["inventories"].append(x); x += INV_W + GAP
    pos["inventories"].append(x); x += INV_W + GAP
    pos["customer"] = x; x += CUSTOMER_W + MARGIN
    box_cy = my + PROCESS_H / 2
    return pos, x, box_cy


# ── Drawing functions ─────────────────────────────────────────────
def draw_supplier(pos, box_cy, name):
    x, cy = pos["supplier"], box_cy
    e = []
    e.append(rect(x, cy - 22, SUPPLIER_W, 44, C_SUPPLIER, C_SUP_ACCENT))
    e.append(T("polygon", {
        "points": f"{x - 3},{cy - 22} {x + SUPPLIER_W / 2},{cy - 40} {x + SUPPLIER_W + 3},{cy - 22}",
        "fill": C_SUP_ACCENT}, sc=True))
    e.append(rect(x + SUPPLIER_W / 2 - 5, cy + 4, 10, 16, C_SUP_ACCENT, C_SUP_ACCENT))
    e.append(txt(x + SUPPLIER_W / 2, cy - 3, esc(name), 8, bold=True, color="#1a5276"))
    return e


def draw_customer(pos, box_cy, name):
    x, cy = pos["customer"], box_cy
    e = []
    e.append(rect(x, cy - 22, CUSTOMER_W, 44, C_CUSTOMER, C_CUST_ACCENT))
    e.append(T("polygon", {
        "points": f"{x - 3},{cy - 22} {x + CUSTOMER_W / 2},{cy - 40} {x + CUSTOMER_W + 3},{cy - 22}",
        "fill": C_CUST_ACCENT}, sc=True))
    e.append(rect(x + CUSTOMER_W / 2 - 5, cy + 4, 10, 16, C_CUST_ACCENT, C_CUST_ACCENT))
    e.append(rect(x + 10, cy - 14, 8, 8, C_CUST_ACCENT, C_CUST_ACCENT))
    e.append(rect(x + CUSTOMER_W - 18, cy - 14, 8, 8, C_CUST_ACCENT, C_CUST_ACCENT))
    e.append(txt(x + CUSTOMER_W / 2, cy - 3, esc(name), 8, bold=True, color="#1e8449"))
    return e


def draw_process_box(idx, pos, box_cy, p, is_bn=False, is_pm=False):
    x = pos["processes"][idx]
    my = pos.get("_material_y", MATERIAL_Y)
    y = my
    e = []
    sc = "#c0392b" if is_bn else C_STROKE
    e.append(rect(x, y, PROCESS_W, PROCESS_H, C_FILL, sc))
    e.append(rect(x + .75, y + .75, PROCESS_W - 1.5, PROCESS_NAME_H, C_HEADER, sc))
    e.append(txt(x + PROCESS_W / 2, y + PROCESS_NAME_H / 2, esc(p["name"]), 10, bold=True, color=sc))
    # Data fields - support stations
    fields = [f"C/T  {p['ct']}min"]
    if p.get("co", 0) > 0:
        fields.append(f"C/O  {p['co']}min")
    if p.get("stations", 1) > 1:
        fields.append(f"工位  x{p['stations']}")
    fields.append(f"可用  {p.get('uptime', '?')}%")
    if "operators" in p:
        fields.append(f"人数  {p['operators']}")
    if p.get("defect", 0) > 0:
        fields.append(f"不良  {p['defect']}%")
    for i, f in enumerate(fields):
        e.append(txt(x + 8, y + PROCESS_NAME_H + 14 + i * 14, f, 8.5, anchor="start", color="#444"))
    if is_pm:
        e.append(T("circle", {"cx": x + PROCESS_W - 8, "cy": y + 8, "r": 5,
                               "fill": "#3498db", "stroke": "#2980b9"}, sc=True))
        e.append(txt(x + PROCESS_W - 8, y + 8, "P", 6, bold=True, color="white"))
    return e


def draw_inventory(idx, pos, box_cy, qty, label=None):
    x = pos["inventories"][idx]
    cy = box_cy
    e = []
    tw, th = 22, 18
    ty = cy - th / 2 - 1
    e.append(T("polygon", {
        "points": f"{x - tw / 2},{ty} {x + tw / 2},{ty} {x},{ty + th}",
        "fill": C_INV_FILL, "stroke": C_INV_STROKE, "stroke-width": "1"}, sc=True))
    if qty > 0:
        e.append(txt(x, ty + th + 9, str(qty), 8, color="#555"))
        if label:
            e.append(txt(x, ty + th + 19, esc(label), 6, color="#999"))
    return e


def draw_push_arrows(pos, box_cy, n):
    e = []
    y = box_cy
    e.append(ln(pos["supplier"] + SUPPLIER_W, y, pos["inventories"][0] - 10, y, C_PUSH, 2))
    e.append(arrow(pos["inventories"][0] - 10, y, "right", 6, C_PUSH))
    for i in range(n):
        e.append(ln(pos["inventories"][i] + 10, y, pos["processes"][i] - 1, y, C_PUSH, 2))
        e.append(arrow(pos["processes"][i] - 1, y, "right", 6, C_PUSH))
        e.append(ln(pos["processes"][i] + PROCESS_W, y, pos["inventories"][i + 1] - 10, y, C_PUSH, 2))
        e.append(arrow(pos["inventories"][i + 1] - 10, y, "right", 6, C_PUSH))
    e.append(ln(pos["inventories"][-1] + 10, y, pos["customer"] - 1, y, C_PUSH, 2))
    e.append(arrow(pos["customer"] - 1, y, "right", 6, C_PUSH))
    return e


def draw_branches(data, pos):
    """Draw branch flows above the main material flow."""
    e = []
    branches = data.get("branches", [])
    if not branches:
        return e

    # Separate "from" branches (process-to-process) and external input branches
    from_branches = [b for b in branches if "from" in b]
    ext_branches = [b for b in branches if "from" not in b]

    box_w, box_h = 95, 32
    my = pos.get("_material_y", MATERIAL_Y)

    # Draw from-branches in a single lane
    for bi, br in enumerate(from_branches):
        from_idx = br["from"]
        to_idx = br["to"]
        from_x = pos["processes"][from_idx] + PROCESS_W / 2
        to_x = pos["processes"][to_idx] + PROCESS_W / 2
        mid_x = (from_x + to_x) / 2
        lane_y = BRANCH_ZONE_TOP + 5

        # Box
        bx = mid_x - box_w / 2
        by = lane_y
        e.append(rect(bx, by, box_w, box_h, C_BRANCH, C_BRANCH_S))
        e.append(txt(mid_x, by + 10, esc(br.get("label", "")), 8, bold=True, color="#6c3483"))

        # Info line
        info_parts = []
        if "ct" in br:
            info_parts.append(f"CT:{br['ct']}min")
        if "co" in br:
            info_parts.append(f"CO:{br['co']}min")
        if "uptime" in br:
            info_parts.append(f"可用:{br['uptime']}%")
        if info_parts:
            e.append(txt(mid_x, by + 23, " | ".join(info_parts), 6, color="#999"))
        if "note" in br:
            e.append(txt(mid_x, by + box_h + 8, esc(br["note"]), 6.5, color="#bbb"))

        # Connecting lines: from source → up → box → down → merge
        e.append(ln(from_x, my - 8, from_x, lane_y + box_h / 2, C_BRANCH_S, 1, "4,3"))
        e.append(ln(from_x, lane_y + box_h / 2, bx, lane_y + box_h / 2, C_BRANCH_S, 1, "4,3"))
        e.append(ln(bx + box_w, lane_y + box_h / 2, to_x, lane_y + box_h / 2, C_BRANCH_S, 1, "4,3"))
        e.append(ln(to_x, lane_y + box_h / 2, to_x, my - 8, C_BRANCH_S, 1, "4,3"))
        e.append(arrow(to_x, my - 14, "down", 5, C_BRANCH_S))

    # Draw external input branches - group by "to" and stack
    to_groups = {}
    for br in ext_branches:
        to_idx = br["to"]
        to_groups.setdefault(to_idx, []).append(br)

    # Count from-branches lanes to offset ext branches
    ext_offset = BRANCH_ZONE_TOP + 5 + box_h + 15  # below from-branch lane

    for to_idx, brs in to_groups.items():
        merge_x = pos["processes"][to_idx] + PROCESS_W / 2
        for si, br in enumerate(brs):
            si_y = ext_offset + si * (box_h + 6)
            bx = merge_x - box_w / 2
            by = si_y

            e.append(rect(bx, by, box_w, box_h, "#eaf2f8", "#5dade2"))
            e.append(txt(merge_x, by + 10, esc(br.get("label", "")), 7.5, bold=True, color="#1a5276"))

            # Info
            info_parts = []
            if "ct" in br:
                info_parts.append(f"CT:{br['ct']}min")
            if "note" in br:
                info_parts.append(br["note"])
            if info_parts:
                e.append(txt(merge_x, by + 23, " | ".join(info_parts), 5.5, color="#888"))

            # Arrow down to merge point
            bottom_y = by + box_h
            e.append(ln(merge_x, bottom_y, merge_x, my - 8, "#5dade2", 1, "4,3"))
            e.append(arrow(merge_x, my - 14, "down", 5, "#5dade2"))

    return e


def draw_info_flow(data, pos, width):
    e = []
    y = INFO_Y
    info = data.get("info_flow", {})
    e.append(rect(0, 30, width, 55, "#fafbfc", "none"))

    # PC box
    pc_name = info.get("schedule_from", "生产计划")
    pc_w = 80
    pc_x = width / 2 - pc_w / 2
    e.append(rect(pc_x, y - 11, pc_w, 22, C_PC, C_PC_S))
    e.append(txt(pc_x + pc_w / 2, y, esc(pc_name), 8, bold=True, color="#7d6608"))

    # Electronic: Customer → PC
    cx = pos["customer"] + CUSTOMER_W / 2
    demand = info.get("demand_label", f"月需求: {data.get('monthly_demand', '?')}")
    e.append(sawtooth(cx, y, pc_x + pc_w, C_ELEC))
    e.append(arrow(pc_x + pc_w, y, "left", 6, C_ELEC))
    e.append(txt((cx + pc_x + pc_w) / 2, y - 10, esc(demand), 8, color=C_ELEC))

    # Signals
    ys = y + 12
    for sig in info.get("signals", []):
        target = sig.get("to", "")
        px_mid = None
        for i, p in enumerate(data["processes"]):
            if target.lower() in p["name"].lower():
                px_mid = pos["processes"][i] + PROCESS_W / 2
                break
        if px_mid:
            c = C_MANUAL if sig["type"] == "manual" else "#8e44ad"
            e.append(ln(pc_x, ys, px_mid, ys, c, 1.2))
            e.append(arrow(px_mid, ys, "left", 6, c))
            e.append(txt((pc_x + px_mid) / 2, ys - 8, esc(sig.get("label", "")), 7, color=c))

        inv_idx = sig.get("to_inv")
        if inv_idx is not None and inv_idx < len(pos["inventories"]):
            ix = pos["inventories"][inv_idx]
            my = pos.get("_material_y", MATERIAL_Y)
            e.append(ln(ix, ys + 4, ix, my - 4, "#8e44ad", .8, "4,3"))
            e.append(txt(ix + 14, (ys + 4 + my - 4) / 2,
                        esc(sig.get("label", "看板")), 7, color="#8e44ad", anchor="start"))
    return e


def draw_timeline(data, pos, timeline_y=None):
    e = []
    n = len(data["processes"])
    days = max(1, data.get("working_days", 22))
    daily = data.get("monthly_demand", 0) / days
    invs = data.get("inventories", [0] * (n + 1))
    ct_unit = data.get("ct_unit", "min")
    ty = timeline_y or TIMELINE_Y

    y_up = ty
    y_lo = ty + 26

    e.append(txt(MARGIN, ty - 12, "时间线", 9, anchor="start", color="#888"))

    waits = [inv / daily if daily > 0 else 0 for inv in invs]
    total_wait = sum(waits)
    total_va = sum(p["ct"] for p in data["processes"])

    # Convert VA to same time unit as waits for ratio
    if ct_unit == "min":
        va_in_days = total_va / 60 / 24
    else:  # seconds
        va_in_days = total_va / 86400
    va_ratio = (va_in_days / total_wait * 100) if total_wait > 0 else 0

    x0 = pos["processes"][0]
    x1 = pos["processes"][-1] + PROCESS_W
    total_w = x1 - x0

    if total_wait > 0:
        cx = x0
        for d in waits:
            w = max(6, (d / total_wait) * total_w)
            e.append(rect(cx, y_up, w - .5, 16, C_UPPER, C_UPPER, rx=1))
            if w > 30:
                e.append(txt(cx + w / 2, y_up + 8, f"{d:.1f}d", 7, color="white", bold=True))
            cx += w
    e.append(txt(x1 + 8, y_up + 8, f"{total_wait:.1f}天", 8, anchor="start",
                 color=C_UPPER, bold=True))

    if total_va > 0:
        cx = x0
        for p in data["processes"]:
            w = max(6, (p["ct"] / total_va) * total_w)
            e.append(rect(cx, y_lo, w - .5, 9, C_LOWER, C_LOWER, rx=1))
            if w > 30:
                e.append(txt(cx + w / 2, y_lo + 4.5, f"{p['ct']}{ct_unit[0]}", 6, color="white", bold=True))
            cx += w
    unit_label = "min" if ct_unit == "min" else "s"
    e.append(txt(x1 + 8, y_lo + 4.5, f"{total_va}{unit_label}", 8, anchor="start",
                 color=C_LOWER, bold=True))

    e.append(txt(x0 + total_w / 2, y_lo + 24,
                 f"VA Ratio: {va_ratio:.2f}%", 10, bold=True, color="#c0392b"))
    return e


def draw_takt_box(data, width):
    e = []
    days = max(1, data.get("working_days", 22))
    shifts = data.get("shifts", 1)
    net = (data.get("shift_hours", 8) * 3600 - data.get("break_min", 30) * 60) * shifts
    daily = data.get("monthly_demand", 0) / days
    takt = net / max(1, daily)
    ct_unit = data.get("ct_unit", "min")

    x = width - MARGIN - 155
    y = INFO_Y - 6
    takt_display = f"{takt / 60:.1f}min" if ct_unit == "min" else f"{takt:.0f}s"
    items = [
        f"月产: {data.get('monthly_demand', '?')}台",
        f"日需求: {daily:.0f}台",
        f"可用: {net / 3600:.0f}h/天",
        f"Takt: {takt_display}",
    ]
    e.append(rect(x - 6, y - 15, 155, len(items) * 14 + 6, "#f8f9fa", "#ddd", rx=3))
    for i, t in enumerate(items):
        c = "#c0392b" if "Takt" in t else "#555"
        e.append(txt(x, y + i * 14, t, 8, anchor="start", color=c, bold="Takt" in t))
    return e


def draw_title(title, width):
    return [txt(width / 2, TITLE_Y, esc(title), 13, bold=True, color="#2c3e50")]


def draw_kaizen_bursts(future, pos, box_cy):
    e = []
    if not future:
        return e
    for kb in future:
        proc_name = kb.get("process", "")
        for i, p in enumerate(pos.get("_procs", [])):
            if proc_name in p:
                x = pos["processes"][i] + PROCESS_W / 2
                y = box_cy - PROCESS_H / 2 - 24
                e.append(starburst(x, y))
                lines = kb.get("text", "").split("\n")
                for li, lt in enumerate(lines):
                    e.append(txt(x, y + (li - (len(lines) - 1) / 2) * 9,
                                esc(lt), 6.5, bold=True, color="#7d6608"))
                break
    return e


# ── Main generator ────────────────────────────────────────────────
def generate(data):
    processes = data["processes"]
    inventories = data.get("inventories", [0] * (len(processes) + 1))
    inv_labels = data.get("inv_labels")
    future = data.get("future_state_kaizens")
    pacemaker = data.get("pacemaker")
    ct_unit = data.get("ct_unit", "min")

    days = max(1, data.get("working_days", 22))
    shifts = data.get("shifts", 1)
    net = (data.get("shift_hours", 8) * 3600 - data.get("break_min", 30) * 60) * shifts
    daily = data.get("monthly_demand", 0) / days
    takt_s = net / max(1, daily)
    takt_display = takt_s / 60 if ct_unit == "min" else takt_s

    pos, width, box_cy = calc_positions(processes)  # initial layout for info_flow width
    pos["_procs"] = [p["name"] for p in processes]

    # Dynamic layout: account for branches
    branch_count = len(data.get("branches", []))
    branch_h = max(80, branch_count * 40 + 60) if branch_count > 0 else 0
    needed_material_y = BRANCH_ZONE_TOP + branch_h + 10
    material_y = max(MATERIAL_Y, needed_material_y)
    if material_y != MATERIAL_Y:
        pos, width, box_cy = calc_positions(processes, material_y=material_y)
    pos["_material_y"] = material_y

    height = max(TIMELINE_Y, material_y + PROCESS_H + 30) + 80

    e = []
    e += draw_title(data.get("title", "Value Stream Map"), width)
    e += draw_info_flow(data, pos, width)
    e += draw_takt_box(data, width)
    e += draw_branches(data, pos)

    e += draw_supplier(pos, box_cy, data.get("supplier", "Supplier"))
    for i, p in enumerate(processes):
        stations = p.get("stations", 1)
        eff_ct = p["ct"] / stations
        is_bn = eff_ct > takt_display
        is_pm = pacemaker is not None and (i == pacemaker or processes[i]["name"] == pacemaker)
        e += draw_process_box(i, pos, box_cy, p, is_bn=is_bn, is_pm=is_pm)
    for i in range(len(inventories)):
        label = inv_labels[i] if inv_labels and i < len(inv_labels) else None
        e += draw_inventory(i, pos, box_cy, inventories[i], label)
    e += draw_customer(pos, box_cy, data.get("customer", "Customer"))
    e += draw_push_arrows(pos, box_cy, len(processes))

    if future:
        e += draw_kaizen_bursts(future, pos, box_cy)

    sep_y = material_y + PROCESS_H + 15
    e.append(ln(MARGIN, sep_y, width - MARGIN, sep_y, "#ddd", 1))
    timeline_y = sep_y + 15
    e += draw_timeline(data, pos, timeline_y=timeline_y)

    # Bottleneck legend at bottom
    bn_procs = [p["name"] for p in processes if p["ct"] / p.get("stations", 1) > takt_display]
    if bn_procs:
        leg_y = height - 28
        e.append(rect(MARGIN, leg_y, 10, 10, "none", "#c0392b", sw=2, rx=1))
        takt_str = f"{takt_display:.1f}" + ("min" if ct_unit == "min" else "s")
        e.append(txt(MARGIN + 15, leg_y + 5,
                     f"瓶颈(有效CT>Takt {takt_str}): {', '.join(bn_procs)}",
                     8, anchor="start", color="#c0392b"))

    svg_body = "\n".join(e)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}"
     width="{width}" height="{height}" style="background:#fff;font-family:{FONT}">
{svg_body}
</svg>"""


def svg_to_png(svg_path, png_path, width=None):
    cmd = ["rsvg-convert"]
    if width:
        cmd.extend(["-w", str(width)])
    cmd.extend([svg_path, "-o", png_path])
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"rsvg-convert failed: {r.stderr}", file=sys.stderr)
        return False
    return True


def export_csv(data, out_path):
    """Export VSM data as CSV for sharing or importing into other tools."""
    ct_unit = data.get("ct_unit", "min")
    fields = ["type", "name", "index", f"ct({ct_unit})", "co(min)", "uptime(%)",
              "operators", "defect(%)", "stations", "inventory", "inv_label"]
    rows = []
    for i, p in enumerate(data.get("processes", [])):
        inv = data.get("inventories", [])[i] if i < len(data.get("inventories", [])) else ""
        inv_l = data.get("inv_labels", [])[i] if i < len(data.get("inv_labels", [])) else ""
        rows.append([
            "process", p["name"], i,
            p.get("ct", ""), p.get("co", ""), p.get("uptime", ""),
            p.get("operators", ""), p.get("defect", ""), p.get("stations", 1),
            inv, inv_l
        ])
    for b in data.get("branches", []):
        rows.append([
            "branch", b["label"], b.get("from", ""),
            b.get("ct", ""), b.get("co", ""), b.get("uptime", ""),
            "", "", "",
            "", b.get("note", "")
        ])
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(fields)
        writer.writerows(rows)
    return out_path


def main():
    if len(sys.argv) < 2:
        print("Usage: vsm_svg.py input.json [output.svg|.png|.csv]", file=sys.stderr)
        sys.exit(1)
    with open(sys.argv[1]) as f:
        data = json.load(f)
    if len(sys.argv) >= 3:
        out = sys.argv[2]
        if out.endswith(".csv"):
            export_csv(data, out)
            print(f"Saved CSV to {out}", file=sys.stderr)
        elif out.endswith(".png"):
            svg = generate(data)
            tmp = out + ".tmp.svg"
            Path(tmp).write_text(svg, encoding="utf-8")
            if svg_to_png(tmp, out):
                os.remove(tmp)
                print(f"Saved to {out}", file=sys.stderr)
            else:
                print(f"Fallback: saved SVG to {tmp}", file=sys.stderr)
        else:
            svg = generate(data)
            Path(out).write_text(svg, encoding="utf-8")
            print(f"Saved to {out}", file=sys.stderr)
    else:
        print(generate(data))


if __name__ == "__main__":
    main()
