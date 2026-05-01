# SVG Rendering Reference

VSM diagrams are rendered by `scripts/vsm_svg.py` — a zero-dependency Python script.
Output is SVG, with automatic PNG conversion when the output filename ends in `.png` (requires `librsvg2-bin` / `rsvg-convert`).

## Usage

```bash
# SVG output
python3 scripts/vsm_svg.py input.json output.svg

# PNG output (auto-converts via rsvg-convert)
python3 scripts/vsm_svg.py input.json output.png
```

## Input JSON Schema

```json
{
  "title": "价值流图 - 产品名",
  "supplier": "供应商名称",
  "customer": "客户名称",
  "monthly_demand": 12000,
  "working_days": 22,
  "shifts": 1,
  "shift_hours": 8,
  "break_min": 30,

  "processes": [
    {
      "name": "工序名",
      "ct": 35,
      "co": 45,
      "uptime": 88,
      "operators": 1,
      "defect": 2.0
    }
  ],

  "inventories": [800, 200, 150, 100, 80, 300],
  "inv_labels": ["原材料", "WIP", "WIP", "WIP", "WIP", "成品"],

  "pacemaker": null,
  "future_state_kaizens": null,

  "info_flow": {
    "schedule_from": "生产计划",
    "demand_label": "月需求: 12000",
    "signals": [
      {"type": "manual", "to": "焊接", "label": "Heijunka"},
      {"type": "kanban", "to_inv": 1, "label": "看板"}
    ]
  }
}
```

### Field Reference

| Field | Required | Description |
|-------|----------|-------------|
| `title` | Yes | Map title, rendered at top center |
| `supplier` | Yes | Supplier name, shown in building icon (left) |
| `customer` | Yes | Customer name, shown in building icon (right) |
| `monthly_demand` | Yes | Monthly demand in pieces |
| `working_days` | Yes | Working days per month |
| `shifts` | Yes | Number of shifts per day |
| `shift_hours` | Yes | Gross shift hours (before breaks) |
| `break_min` | Yes | Total break/lunch minutes per shift |
| `processes` | Yes | Array of process step objects |
| `processes[].name` | Yes | Process name (keep under 6 CJK chars) |
| `processes[].ct` | Yes | Cycle Time in seconds |
| `processes[].co` | Yes | Changeover Time in minutes |
| `processes[].uptime` | Yes | Equipment uptime percentage |
| `processes[].operators` | No | Number of operators |
| `processes[].defect` | No | Defect rate percentage |
| `inventories` | Yes | Inventory counts between steps. Length must be `len(processes) + 1` |
| `inv_labels` | No | Labels for each inventory point. Same length as `inventories` |
| `pacemaker` | No | Name of pacemaker process. Shows "P" badge on the process box. Future state only. |
| `future_state_kaizens` | No | Array of Kaizen burst objects. Future state only. |
| `future_state_kaizens[].process` | Yes | Target process name (must match a process) |
| `future_state_kaizens[].text` | Yes | Burst text. Use `\n` for multiline. |
| `info_flow` | No | Information flow configuration |
| `info_flow.schedule_from` | Yes | Production control / scheduling entity name |
| `info_flow.demand_label` | Yes | Label on electronic signal from customer |
| `info_flow.signals` | No | Array of signal objects |
| `info_flow.signals[].type` | Yes | `"manual"` or `"kanban"` |
| `info_flow.signals[].to` | No | Target process name (for manual signals) |
| `info_flow.signals[].to_inv` | No | Target inventory index (for kanban signals) |
| `info_flow.signals[].label` | No | Signal label text |

## Visual Elements

| Element | Description |
|---------|-------------|
| **Process Box** | White box with grey header. Shows C/T, C/O, Uptime, Operators, Defect. |
| **Bottleneck** | Process box with **red border** when C/T > Takt Time |
| **Pacemaker** | Blue "P" circle badge on the process box corner |
| **Inventory** | Grey downward triangle with count below |
| **Supplier** | Blue factory icon (building + roof) |
| **Customer** | Green factory icon (building + windows) |
| **Timeline** | Orange bar (wait days) + Blue bar (value-add time) at bottom |
| **VA Ratio** | Red text below timeline |
| **Kaizen Burst** | Star-burst polygon above process box (future state) |
| **Info Flow** | Sawtooth line (electronic), solid line (manual), dashed line (kanban) |
| **Push Arrows** | Solid black arrows connecting material flow |

## Limitations

- **Max 8 process steps** recommended. Beyond that, the SVG gets very wide.
- **CJK process names**: keep under 6 characters for clean box rendering.
- **Font**: Uses system fonts (PingFang SC / Microsoft YaHei / Noto Sans SC). Rendering depends on the viewing environment.
- **Scale**: SVG viewBox is auto-calculated; PNG width defaults to SVG width via rsvg-convert.

## Dependencies

- Python 3.6+ (stdlib only for SVG generation)
- `rsvg-convert` (from `librsvg2-bin`) for PNG output — install with:
  ```bash
  sudo apt-get install -y librsvg2-bin
  ```
