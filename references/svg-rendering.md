# SVG Rendering Reference

VSM diagrams are rendered by `scripts/vsm_svg.py` — a zero-dependency Python script.
Output is SVG, with automatic PNG conversion when the output filename ends in `.png` (requires `librsvg2-bin` / `rsvg-convert`).

## Usage

```bash
# SVG output
python3 scripts/vsm_svg.py input.json output.svg

# PNG output (auto-converts via rsvg-convert, recommended for Feishu)
python3 scripts/vsm_svg.py input.json output.png
```

## Input JSON Schema

```json
{
  "title": "价值流图 - 产品名",
  "supplier": "供应商名称",
  "customer": "客户名称",
  "monthly_demand": 800,
  "working_days": 26,
  "shifts": 2,
  "shift_hours": 12,
  "break_min": 120,
  "ct_unit": "min",

  "processes": [
    {
      "name": "焊接",
      "ct": 100,
      "co": 40,
      "uptime": 78,
      "operators": 3,
      "defect": 3.5,
      "stations": 2,
      "batch_size": 30,
      "avail_time_min": 480
    }
  ],

  "inventories": [92, 30, 15, 9, 46, 15, 6, 30, 15, 15, 61],
  "inv_labels": ["原材料", "WIP", "WIP", "WIP", "WIP", "WIP", "WIP", "WIP", "WIP", "WIP", "成品"],
  "inv_types": ["raw", "wip", "wip", "wip", "wip", "wip", "wip", "wip", "wip", "wip", "fg"],

  "supermarkets": [3, 7],
  "finished_goods": "supermarket",

  "branches": [
    {"label": "机加", "from": 0, "to": 3, "ct": 50, "co": 30, "uptime": 85, "note": "~30%零件"},
    {"label": "外购底盘", "to": 7, "note": "改制60min, 提前期5天"}
  ],

  "pacemaker": null,
  "future_state_kaizens": null,

  "info_flow": {
    "schedule_from": "生产计划",
    "demand_label": "月产800台",
    "signals": [
      {"type": "manual", "to": "焊接", "label": "排产指令"}
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
| `ct_unit` | No | `"min"` (default) or `"s"`. Affects C/T display and Takt comparison. Use `"min"` for heavy industry. |
| `processes` | Yes | Array of process step objects |
| `processes[].name` | Yes | Process name (keep under 6 CJK chars) |
| `processes[].ct` | Yes | Cycle Time in `ct_unit` (default: minutes) |
| `processes[].co` | Yes | Changeover Time in minutes |
| `processes[].uptime` | Yes | Equipment uptime percentage |
| `processes[].operators` | No | Number of operators |
| `processes[].defect` | No | Defect rate percentage |
| `processes[].stations` | No | Number of parallel identical stations. Effective CT = ct / stations. Used for bottleneck detection. |
| `processes[].batch_size` | No | Batch size (units per run). Required for Effective CT calculation when C/O > 10min. |
| `processes[].avail_time_min` | No | Available working time per shift in minutes (net, after breaks). Defaults to global `shift_hours*60 - break_min` if not set. |
| `inventories` | Yes | Inventory counts between steps. Length must be `len(processes) + 1` |
| `inv_labels` | No | Labels for each inventory point. Same length as `inventories` |
| `inv_types` | No | Type of each inventory point: `"raw"`, `"wip"`, `"fg"` (finished goods). Same length as `inventories`. Used to differentiate raw material, work-in-process, and finished goods inventory on the map. |
| `supermarkets` | No | Array of inventory indices where supermarket pull systems are located. These inventory triangles will be rendered with a supermarket icon (rectangle with zigzag top). |
| `finished_goods` | No | `"supermarket"` or `"direct"`. How finished goods flow to customer. `"supermarket"` draws a supermarket icon before customer; `"direct"` draws a direct arrow. Default: `"direct"`. |
| `branches` | No | Array of branch objects. Rendered above main flow line. |
| `branches[].label` | Yes | Branch name (e.g., "机加") |
| `branches[].from` | No | Source process index (0-based). Presence makes this a from-branch. |
| `branches[].to` | Yes | Merge target process index (0-based) |
| `branches[].ct` | No | Branch process CT (displayed in box) |
| `branches[].co` | No | Branch process C/O (displayed in box) |
| `branches[].uptime` | No | Branch process uptime (displayed in box) |
| `branches[].note` | No | Additional note below the branch box |
| `pacemaker` | No | Name of pacemaker process. Shows "P" badge. Can be set on both current and future state maps — identify where scheduling instructions are currently sent. |
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
| **Process Box** | White box with grey header. Shows C/T, C/O (if >0), Stations (if >1), Uptime, Operators, Defect. |
| **Bottleneck** | Process box with **red border** when effective C/T (ct ÷ stations) > Takt Time |
| **Pacemaker** | Blue "P" circle badge on the process box corner |
| **Inventory** | Grey downward triangle with count below. If the inventory index is in `supermarkets[]`, renders as a supermarket icon (rectangle with zigzag/roof top) instead of a triangle. |
| **Supermarket** | Rectangle with a zigzag/roof top, containing inventory count. Marks a controlled buffer where upstream produces to replenish (pull system). Placed at inventory points listed in `supermarkets[]`. |
| **Finished Goods** | Before customer: if `finished_goods: "supermarket"`, draws a supermarket icon; if `"direct"` (default), normal arrow. |
| **Supplier** | Blue factory icon (building + roof) |
| **Customer** | Green factory icon (building + windows) |
| **Branch (from)** | Purple box above main flow, dashed lines from source → box → merge target |
| **Branch (external)** | Blue box above main flow, dashed line down to merge target |
| **Timeline** | Orange bar (wait days) + Blue bar (value-add time) at bottom |
| **VA Ratio** | Red text below timeline |
| **Kaizen Burst** | Star-burst polygon above process box (future state) |
| **Info Flow** | Sawtooth line (electronic), solid line (manual), dashed line (kanban) |
| **Push Arrows** | Solid black arrows connecting material flow |

## Bottleneck Detection

The script compares **effective CT** (ct ÷ stations, default 1) against Takt Time. Takt is calculated from `monthly_demand`, `working_days`, `shifts`, `shift_hours`, `break_min` and displayed in `ct_unit`.

## Limitations

- **CJK process names**: keep under 6 characters for clean box rendering.
- **Font**: Uses system fonts (PingFang SC / Microsoft YaHei / Noto Sans SC). Rendering depends on the viewing environment.
- **Scale**: SVG viewBox is auto-calculated; PNG width defaults to SVG width via rsvg-convert.
- **Branch layout**: From-branches share a single lane. External inputs with the same `to` target stack vertically. Very complex branch topologies (>5 branches) may need manual layout adjustment.

## Dependencies

- Python 3.6+ (stdlib only for SVG generation)
- `rsvg-convert` (from `librsvg2-bin`) for PNG output — install with:
  ```bash
  sudo apt-get install -y librsvg2-bin
  ```
