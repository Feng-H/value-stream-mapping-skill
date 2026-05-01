#!/usr/bin/env python3
"""
VSM SVG Generator — Generate professional Value Stream Maps as SVG.

Usage:
    python vsm_svg.py input.json output.svg
    python vsm_svg.py input.json              # prints SVG to stdout
"""

import os
import json
import math
import subprocess
import sys
from pathlib import Path

# ── Layout constants ──────────────────────────────────────────────
MARGIN = 70
SUPPLIER_W = 110
PROCESS_W = 145
PROCESS_H = 115
PROCESS_NAME_H = 30
INV_W = 55
CUSTOMER_W = 110
GAP = 30

TITLE_Y = 18
INFO_Y = 80
MATERIAL_Y = 195
SEPARATOR_Y = 345
TIMELINE_Y = 360

# ── Colors ────────────────────────────────────────────────────────
C_PROCESS_FILL = "#ffffff"
C_PROCESS_STROKE = "#333"
C_HEADER_FILL = "#f0f3f6"
C_INV_FILL = "#e0e0e0"
C_INV_STROKE = "#666"
C_SUPPLIER_FILL = "#d4e6f1"
C_SUPPLIER_ACCENT = "#2980b9"
C_CUSTOMER_FILL = "#d5f5e3"
C_CUSTOMER_ACCENT = "#27ae60"
C_PUSH = "#333"
C_PULL = "#666"
C_INFO_ELEC = "#2980b9"
C_INFO_MANUAL = "#27ae60"
C_TIMELINE_UPPER = "#e67e22"
C_TIMELINE_LOWER = "#3498db"
C_KAIZEN_FILL = "#fff3cd"
C_KAIZEN_STROKE = "#f39c12"
C_PC_FILL = "#fef9e7"
C_PC_STROKE = "#d4ac0d"

FONT = "-apple-system, 'PingFang SC', 'Microsoft YaHei', 'Noto Sans SC', Arial, sans-serif"


# ── SVG helpers ───────────────────────────────────────────────────
def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def tag(name, attrs, content="", self_close=False):
    a = " ".join(f'{k}="{v}"' for k, v in attrs.items())
    if self_close:
        return f"<{name} {a}/>"
    return f"<{name} {a}>{content}</{name}>"


def txt(x, y, text, size=11, anchor="middle", bold=False, color="#333"):
    w = "bold" if bold else "normal"
    return tag("text", {"x": x, "y": y, "font-size": size, "text-anchor": anchor,
                        "font-family": FONT, "font-weight": w, "fill": color,
                        "dominant-baseline": "central"}, esc(text))


def rect(x, y, w, h, fill=C_PROCESS_FILL, stroke=C_PROCESS_STROKE, sw=1.5, rx=2):
    return tag("rect", {"x": x, "y": y, "width": w, "height": h,
                        "fill": fill, "stroke": stroke, "stroke-width": sw, "rx": rx})


def line(x1, y1, x2, y2, color=C_PUSH, sw=2, dash=None):
    a = {"x1": x1, "y1": y1, "x2": x2, "y2": y2, "stroke": color, "stroke-width": sw}
    if dash:
        a["stroke-dasharray"] = dash
    return tag("line", a, self_close=True)


def arrow(x, y, direction="right", size=8, color=C_PUSH):
    if direction == "right":
        pts = f"{x},{y-size/2} {x+size},{y} {x},{y+size/2}"
    else:
        pts = f"{x},{y-size/2} {x-size},{y} {x},{y+size/2}"
    return tag("polygon", {"points": pts, "fill": color}, self_close=True)


def sawtooth(x1, y, x2, color, amplitude=5):
    """Zigzag line from x1 to x2."""
    length = abs(x2 - x1)
    num = max(8, int(length / 16))
    step = (x2 - x1) / num
    pts = [f"{x1},{y}"]
    for i in range(num):
        xi = x1 + step * (i + 0.5)
        yi = y + amplitude * (1 if i % 2 == 0 else -1)
        pts.append(f"{xi:.1f},{yi:.1f}")
    pts.append(f"{x2},{y}")
    return tag("polyline", {"points": " ".join(pts), "fill": "none",
                            "stroke": color, "stroke-width": "1.5"})


def starburst(cx, cy, r_outer=24, r_inner=14, n=12):
    """Kaizen burst polygon."""
    pts = []
    for i in range(n * 2):
        a = i * math.pi / n - math.pi / 2
        r = r_outer if i % 2 == 0 else r_inner
        pts.append(f"{cx + r*math.cos(a):.1f},{cy + r*math.sin(a):.1f}")
    return tag("polygon", {"points": " ".join(pts),
                           "fill": C_KAIZEN_FILL, "stroke": C_KAIZEN_STROKE, "stroke-width": "1.5"},
               self_close=True)


# ── Layout calculator ─────────────────────────────────────────────
def calc_positions(processes):
    n = len(processes)
    pos = {"supplier": MARGIN, "processes": [], "inventories": [], "customer": 0}

    x = MARGIN + SUPPLIER_W + GAP
    pos["inventories"].append(x);  x += INV_W + GAP
    for i in range(n):
        pos["processes"].append(x); x += PROCESS_W + GAP
        if i < n - 1:
            pos["inventories"].append(x); x += INV_W + GAP
    pos["inventories"].append(x); x += INV_W + GAP
    pos["customer"] = x; x += CUSTOMER_W + MARGIN

    box_cy = MATERIAL_Y + PROCESS_H / 2
    return pos, x, box_cy


# ── Drawing functions ─────────────────────────────────────────────
def draw_supplier(pos, box_cy, name):
    x, cy = pos["supplier"], box_cy
    elems = []
    # Building body
    elems.append(rect(x, cy - 28, SUPPLIER_W, 56, C_SUPPLIER_FILL, C_SUPPLIER_ACCENT))
    # Roof
    elems.append(tag("polygon", {
        "points": f"{x-4},{cy-28} {x+SUPPLIER_W/2},{cy-52} {x+SUPPLIER_W+4},{cy-28}",
        "fill": C_SUPPLIER_ACCENT}, self_close=True))
    # Door
    elems.append(rect(x + SUPPLIER_W/2 - 7, cy + 6, 14, 22, C_SUPPLIER_ACCENT, C_SUPPLIER_ACCENT))
    # Label
    elems.append(txt(x + SUPPLIER_W/2, cy - 4, esc(name), 9, bold=True, color="#1a5276"))
    return elems


def draw_customer(pos, box_cy, name):
    x, cy = pos["customer"], box_cy
    elems = []
    elems.append(rect(x, cy - 28, CUSTOMER_W, 56, C_CUSTOMER_FILL, C_CUSTOMER_ACCENT))
    elems.append(tag("polygon", {
        "points": f"{x-4},{cy-28} {x+CUSTOMER_W/2},{cy-52} {x+CUSTOMER_W+4},{cy-28}",
        "fill": C_CUSTOMER_ACCENT}, self_close=True))
    elems.append(rect(x + CUSTOMER_W/2 - 7, cy + 6, 14, 22, C_CUSTOMER_ACCENT, C_CUSTOMER_ACCENT))
    # Windows
    elems.append(rect(x + 14, cy - 18, 10, 10, C_CUSTOMER_ACCENT, C_CUSTOMER_ACCENT))
    elems.append(rect(x + CUSTOMER_W - 24, cy - 18, 10, 10, C_CUSTOMER_ACCENT, C_CUSTOMER_ACCENT))
    elems.append(txt(x + CUSTOMER_W/2, cy - 4, esc(name), 9, bold=True, color="#1e8449"))
    return elems


def draw_process_box(idx, pos, box_cy, p, is_bottleneck=False, is_pacemaker=False):
    x = pos["processes"][idx]
    y = MATERIAL_Y
    elems = []
    stroke_color = "#c0392b" if is_bottleneck else C_PROCESS_STROKE
    elems.append(rect(x, y, PROCESS_W, PROCESS_H, C_PROCESS_FILL, stroke_color))
    # Header
    elems.append(rect(x + 0.75, y + 0.75, PROCESS_W - 1.5, PROCESS_NAME_H, C_HEADER_FILL, stroke_color))
    # Process name
    elems.append(txt(x + PROCESS_W/2, y + PROCESS_NAME_H/2, esc(p["name"]), 12, bold=True, color=stroke_color))
    # Data fields
    fields = [f"C/T   {p['ct']}s", f"C/O   {p.get('co', '?')}min", f"可用  {p.get('uptime', '?')}%"]
    if "operators" in p:
        fields.append(f"人数  {p['operators']}")
    if "defect" in p:
        fields.append(f"不良  {p['defect']}%")
    for i, f in enumerate(fields):
        elems.append(txt(x + 10, y + PROCESS_NAME_H + 16 + i * 16, f, 9.5, anchor="start", color="#444"))
    # Pacemaker marker
    if is_pacemaker:
        elems.append(tag("circle", {"cx": x + PROCESS_W - 10, "cy": y + 10, "r": 6,
                                    "fill": "#3498db", "stroke": "#2980b9"}, self_close=True))
        elems.append(txt(x + PROCESS_W - 10, y + 10, "P", 7, bold=True, color="white"))
    return elems


def draw_inventory(idx, pos, box_cy, qty, label=None):
    x = pos["inventories"][idx]
    cy = box_cy
    elems = []
    tw, th = 28, 22
    ty = cy - th/2 - 2
    elems.append(tag("polygon", {
        "points": f"{x-tw/2},{ty} {x+tw/2},{ty} {x},{ty+th}",
        "fill": C_INV_FILL, "stroke": C_INV_STROKE, "stroke-width": "1.2"}, self_close=True))
    if qty > 0:
        elems.append(txt(x, ty + th + 12, str(qty), 9, color="#555"))
        if label:
            elems.append(txt(x, ty + th + 24, esc(label), 7, color="#999"))
    return elems


def draw_push_arrows(pos, box_cy, n):
    """Material flow push arrows between all elements."""
    elems = []
    y = box_cy
    # Supplier → first inventory
    elems.append(line(pos["supplier"] + SUPPLIER_W, y, pos["inventories"][0] - 14, y, C_PUSH, 2.5))
    elems.append(arrow(pos["inventories"][0] - 14, y, "right", 7, C_PUSH))
    # Inventory → Process → Inventory chain
    for i in range(n):
        # Inventory i → Process i
        elems.append(line(pos["inventories"][i] + 14, y, pos["processes"][i] - 2, y, C_PUSH, 2.5))
        elems.append(arrow(pos["processes"][i] - 2, y, "right", 7, C_PUSH))
        # Process i → Inventory i+1
        elems.append(line(pos["processes"][i] + PROCESS_W, y, pos["inventories"][i+1] - 14, y, C_PUSH, 2.5))
        elems.append(arrow(pos["inventories"][i+1] - 14, y, "right", 7, C_PUSH))
    # Last inventory → Customer
    elems.append(line(pos["inventories"][-1] + 14, y, pos["customer"] - 2, y, C_PUSH, 2.5))
    elems.append(arrow(pos["customer"] - 2, y, "right", 7, C_PUSH))
    return elems


def draw_info_flow(data, pos, width):
    """Information flow section at the top."""
    elems = []
    y = INFO_Y
    info = data.get("info_flow", {})

    # Background strip
    elems.append(rect(0, 35, width, 65, "#fafbfc", "none"))

    # Section label
    elems.append(txt(MARGIN, 42, "信息流 Information Flow", 9, anchor="start", color="#aaa"))

    # Production Control box
    pc_name = info.get("schedule_from", "生产计划")
    pc_w = 90
    pc_x = width / 2 - pc_w / 2
    elems.append(rect(pc_x, y - 14, pc_w, 28, C_PC_FILL, C_PC_STROKE))
    elems.append(txt(pc_x + pc_w/2, y, esc(pc_name), 9, bold=True, color="#7d6608"))

    # Electronic: Customer → PC (sawtooth right to left)
    cx = pos["customer"] + CUSTOMER_W / 2
    pc_right = pc_x + pc_w
    demand = info.get("demand_label", f"月需求: {data.get('monthly_demand', '?')}")
    elems.append(sawtooth(cx, y, pc_right, C_INFO_ELEC))
    elems.append(arrow(pc_right, y, "left", 7, C_INFO_ELEC))
    elems.append(txt((cx + pc_right) / 2, y - 12, esc(demand), 9, color=C_INFO_ELEC))

    # Separate manual signals and kanban signals to avoid overlap
    y_signal = y + 14
    manual_signals = [s for s in info.get("signals", []) if s.get("type") == "manual"]
    kanban_signals = [s for s in info.get("signals", []) if s.get("type") == "kanban"]

    # Manual signals: PC → target process
    for sig in manual_signals:
        target = sig.get("to", "")
        px_mid = None
        for i, p in enumerate(data["processes"]):
            if target.lower() in p["name"].lower() or target.lower() == f"p{i+1}":
                px_mid = pos["processes"][i] + PROCESS_W / 2
                break
        if px_mid:
            color = C_INFO_MANUAL
            elems.append(line(pc_x, y_signal, px_mid, y_signal, color, 1.5))
            elems.append(arrow(px_mid, y_signal, "left", 7, color))
            elems.append(txt((pc_x + px_mid) / 2, y_signal - 10, esc(sig.get("label", "")), 8, color=color))

    # Kanban signals: vertical dashed line to inventory
    for sig in kanban_signals:
        inv_idx = sig.get("to_inv")
        if inv_idx is not None and inv_idx < len(pos["inventories"]):
            ix = pos["inventories"][inv_idx]
            elems.append(line(ix, y_signal + 5, ix, MATERIAL_Y - 5, "#8e44ad", 1, "4,3"))
            elems.append(txt(ix + 18, (y_signal + 5 + MATERIAL_Y - 5) / 2,
                            esc(sig.get("label", "看板")), 8, color="#8e44ad", anchor="start"))

    return elems


def draw_timeline(data, pos):
    """Timeline with upper bar (wait days) and lower bar (VA time)."""
    elems = []
    n = len(data["processes"])
    days = max(1, data.get("working_days", 22))
    daily = data.get("monthly_demand", 0) / days
    invs = data.get("inventories", [0] * (n + 1))

    y_up = TIMELINE_Y
    y_lo = TIMELINE_Y + 30

    # Section label
    elems.append(txt(MARGIN, TIMELINE_Y - 15, "时间线", 10, anchor="start", color="#888"))

    # Calculate
    waits = [inv / daily if daily > 0 else 0 for inv in invs]
    total_wait = sum(waits)
    total_va = sum(p["ct"] for p in data["processes"])
    va_ratio = (total_va / (total_wait * 86400)) * 100 if total_wait > 0 else 0

    # Span from first process to last process
    x0 = pos["processes"][0]
    x1 = pos["processes"][-1] + PROCESS_W
    total_w = x1 - x0

    # Upper bar: wait days (proportional)
    if total_wait > 0:
        cx = x0
        for i, d in enumerate(waits):
            w = max(8, (d / total_wait) * total_w)
            elems.append(rect(cx, y_up, w - 1, 18, C_TIMELINE_UPPER, C_TIMELINE_UPPER, rx=1))
            if w > 35:
                elems.append(txt(cx + w/2, y_up + 9, f"{d:.1f}d", 8, color="white", bold=True))
            cx += w
    elems.append(txt(x1 + 10, y_up + 9, f"共 {total_wait:.1f} 天", 9, anchor="start",
                     color=C_TIMELINE_UPPER, bold=True))

    # Lower bar: VA time (proportional to C/T)
    if total_va > 0:
        cx = x0
        for p in data["processes"]:
            w = max(8, (p["ct"] / total_va) * total_w)
            elems.append(rect(cx, y_lo, w - 1, 10, C_TIMELINE_LOWER, C_TIMELINE_LOWER, rx=1))
            if w > 40:
                elems.append(txt(cx + w/2, y_lo + 5, f"{p['ct']}s", 7, color="white", bold=True))
            cx += w
    elems.append(txt(x1 + 10, y_lo + 5, f"增值 {total_va}s ({total_va/60:.1f}min)", 9, anchor="start",
                     color=C_TIMELINE_LOWER, bold=True))

    # VA Ratio
    elems.append(txt(x0 + total_w / 2, y_lo + 30,
                     f"增值比 VA Ratio: {va_ratio:.2f}%", 11, bold=True, color="#c0392b"))

    return elems


def draw_takt_box(data, width):
    """Summary metrics box in top-right."""
    elems = []
    days = max(1, data.get("working_days", 22))
    shifts = data.get("shifts", 1)
    net = (data.get("shift_hours", 8) * 3600 - data.get("break_min", 30) * 60) * shifts
    daily = data.get("monthly_demand", 0) / days
    takt = net / max(1, daily)

    x = width - MARGIN - 175
    y = INFO_Y - 8
    items = [
        f"月需求: {data.get('monthly_demand', '?')}",
        f"日需求: {daily:.0f}",
        f"可用时间: {net}s/天",
        f"Takt: {takt:.1f}s",
    ]
    elems.append(rect(x - 8, y - 18, 180, len(items) * 16 + 8, "#f8f9fa", "#ddd", rx=4))
    for i, t in enumerate(items):
        color = "#c0392b" if "Takt" in t else "#555"
        elems.append(txt(x, y + i * 16, t, 9, anchor="start", color=color, bold="Takt" in t))
    return elems


def draw_title(title, width):
    return [txt(width / 2, TITLE_Y, esc(title), 14, bold=True, color="#2c3e50")]


def draw_kaizen_bursts(future_state, pos, box_cy):
    """Draw Kaizen bursts for future state."""
    elems = []
    if not future_state:
        return elems
    for kb in future_state:
        proc_name = kb.get("process", "")
        for i, p in enumerate(pos.get("_processes", [])):
            if proc_name.lower() in p.lower():
                x = pos["processes"][i] + PROCESS_W / 2
                y = box_cy - PROCESS_H / 2 - 28
                elems.append(starburst(x, y))
                # Support multiline text (split on \n)
                text = kb.get("text", "")
                lines = text.split("\n")
                for li, line_txt in enumerate(lines):
                    elems.append(txt(x, y + (li - (len(lines)-1)/2) * 10,
                                     esc(line_txt), 7, bold=True, color="#7d6608"))
                break
    return elems


# ── Main generator ────────────────────────────────────────────────
def generate(data):
    processes = data["processes"]
    inventories = data.get("inventories", [0] * (len(processes) + 1))
    inv_labels = data.get("inv_labels", None)
    future = data.get("future_state_kaizens", None)
    pacemaker = data.get("pacemaker", None)

    # Calculate Takt for bottleneck detection
    days = max(1, data.get("working_days", 22))
    shifts = data.get("shifts", 1)
    net = (data.get("shift_hours", 8) * 3600 - data.get("break_min", 30) * 60) * shifts
    daily = data.get("monthly_demand", 0) / days
    takt = net / max(1, daily)

    pos, width, box_cy = calc_positions(processes)
    pos["_processes"] = [p["name"] for p in processes]  # for kaizen lookup

    height = TIMELINE_Y + 90

    # Collect all SVG elements
    all_elems = []
    all_elems += draw_title(data.get("title", "Value Stream Map"), width)
    all_elems += draw_info_flow(data, pos, width)
    all_elems += draw_takt_box(data, width)

    # Material flow
    all_elems += draw_supplier(pos, box_cy, data.get("supplier", "Supplier"))
    for i, p in enumerate(processes):
        is_bn = p["ct"] > takt
        is_pm = pacemaker is not None and (i == pacemaker or processes[i]["name"] == pacemaker)
        all_elems += draw_process_box(i, pos, box_cy, p, is_bottleneck=is_bn, is_pacemaker=is_pm)
    for i in range(len(inventories)):
        label = inv_labels[i] if inv_labels and i < len(inv_labels) else None
        all_elems += draw_inventory(i, pos, box_cy, inventories[i], label)
    all_elems += draw_customer(pos, box_cy, data.get("customer", "Customer"))
    all_elems += draw_push_arrows(pos, box_cy, len(processes))

    # Kaizen bursts (future state)
    if future:
        all_elems += draw_kaizen_bursts(future, pos, box_cy)

    # Timeline
    # Separator line
    all_elems.append(line(MARGIN, SEPARATOR_Y, width - MARGIN, SEPARATOR_Y, "#ddd", 1))
    all_elems += draw_timeline(data, pos)

    # Bottleneck legend
    bn_procs = [p["name"] for p in processes if p["ct"] > takt]
    if bn_procs:
        all_elems.append(rect(MARGIN, height - 30, 12, 12, "none", "#c0392b", sw=2, rx=1))
        all_elems.append(txt(MARGIN + 18, height - 24,
                             f"瓶颈: {', '.join(bn_procs)} (C/T > Takt {takt:.1f}s)",
                             9, anchor="start", color="#c0392b"))

    svg_body = "\n".join(all_elems)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" 
     width="{width}" height="{height}" style="background:#fff;font-family:{FONT}">
{svg_body}
</svg>"""


def svg_to_png(svg_path, png_path, width=None):
    """Convert SVG to PNG using rsvg-convert."""
    cmd = ["rsvg-convert"]
    if width:
        cmd.extend(["-w", str(width)])
    cmd.extend([svg_path, "-o", png_path])
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"rsvg-convert failed: {result.stderr}", file=sys.stderr)
        return False
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python vsm_svg.py input.json [output.svg|output.png]", file=sys.stderr)
        print("  If output ends with .png, automatically converts via rsvg-convert", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    svg = generate(data)

    if len(sys.argv) >= 3:
        out = sys.argv[2]
        if out.endswith(".png"):
            svg_tmp = out + ".tmp.svg"
            Path(svg_tmp).write_text(svg, encoding="utf-8")
            if svg_to_png(svg_tmp, out):
                os.remove(svg_tmp)
                print(f"Saved to {out}", file=sys.stderr)
            else:
                print(f"Fallback: saved SVG to {svg_tmp}", file=sys.stderr)
        else:
            Path(out).write_text(svg, encoding="utf-8")
            print(f"Saved to {out}", file=sys.stderr)
    else:
        print(svg)


if __name__ == "__main__":
    main()
