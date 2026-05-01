---
name: value-stream-mapping
version: 4.2.0
description: Draw, create, and analyze Value Stream Maps (VSM) with professional SVG rendering. Supports linear flows, branch/merge processes, and external input suppliers. Use when a user wants to map a process, find bottlenecks, calculate Takt Time, or design a Future State Map based on Lean principles.
tags: [lean, vsm, value-stream, manufacturing, process-optimization, svg]
category: operations
linked_files:
  - references/lean-analysis.md
  - references/svg-rendering.md
  - scripts/vsm_svg.py
  - templates/pump-truck-example.json
---

# Value Stream Mapping Skill

This skill guides you to act as an expert Lean Consultant, producing professional Value Stream Maps with standard Lean icons (process data boxes, inventory triangles, timeline bars, Kaizen bursts, branch/merge flows) rendered as SVG.

## Rendering Engine

VSM diagrams are generated via `scripts/vsm_svg.py` — a zero-dependency Python script that outputs SVG files.

**Before rendering (Step 3 and Step 5), you MUST:**
1. Read `references/svg-rendering.md` for the JSON schema and visual elements
2. Read `references/lean-analysis.md` for Takt Time, Lead Time, and Value Add Ratio formulas

**To generate a VSM:**
```bash
# PNG output (auto-converts, recommended for Feishu)
python3 scripts/vsm_svg.py input.json output.png

# Or SVG → PNG in two steps
python3 scripts/vsm_svg.py input.json output.svg
rsvg-convert -w 1775 output.svg -o output.png
```

The input JSON structure is documented in `references/svg-rendering.md`. A complete example is in `templates/pump-truck-example.json`.

**IMPORTANT:** Feishu does not support SVG attachments. Always convert to PNG before sending via `MEDIA:`. Dependency: `librsvg2-bin` (`sudo apt-get install -y librsvg2-bin`).

**User preference:** Do not over-verify SVG output programmatically. Generate, convert to PNG, send to user. They will visually inspect and provide feedback.

### Key Features (v4.0)
- **Branch flows**: `branches[]` array supports process-to-process branches (e.g., 机加 from 下料 to 焊接) and external input branches (e.g., 外购底盘 to 整体组装)
- **Multi-station**: `stations` field on processes shows effective CT per station (C/T ÷ stations), which is used for bottleneck detection
- **CT unit toggle**: `ct_unit` field — `"min"` (default, better for heavy industry) or `"s"`
- **Dynamic layout**: SVG height auto-adjusts for branch count

## Workflow

Follow these steps strictly:

### 1. Scope Definition
Ask the user to define the scope of the map (e.g., door-to-door, single line, multi-facility) and the target product family. If they have multiple product families, ask them to start with the highest-volume one — multi-family VSMs add complexity (see `references/lean-analysis.md` for mixed-model guidance). Do not proceed until this is clear.

**Listen first, structure later.** When the user starts describing the process verbally:
- Let them finish their description without interrupting
- Note branching/merge points, dual-source components, and re-entry loops
- After they finish, present a structured summary for confirmation
- Ask about anything ambiguous (e.g., "机加后的零件回到焊接，是汇入主焊接线还是单独再焊一次？")

**Branch handling:** The SVG renderer supports two types of branches via the `branches[]` array:
- **From-branches** (has `from` + `to` process indices): process-to-process parallel paths rendered above the main flow line (e.g., 机加: 部分零件从下料分流到机加工再汇入焊接)
- **External inputs** (has `to` index only): external suppliers converging into a main process (e.g., 外购底盘、外购件汇入整体组装)

> **Pitfall:** When the user says "I don't have exact data", offer to estimate based on industry benchmarks, generate the map with estimated values, and flag them for the user to correct. Mark uncertain values clearly (e.g., "行业估算" note on the diagram or in the data table).

### 2. Current State Extraction

**First, collect demand and time parameters** — these are needed for Takt Time:
- Monthly/weekly/daily demand
- Working days per month
- Shifts per day and net available time per shift (exclude breaks/lunch)

**Then collect process steps and metrics:**
- If they provide a brain-dump, extract it into a structured table.
- **Immediately show the table to the user for confirmation** — do not hide data in context. This prevents context compression loss and gives the user a chance to correct errors early.
- For each process step, collect: Cycle Time (C/T), Changeover Time (C/O), Uptime, Number of Operators, Defect Rate, Number of Stations (parallel identical stations).
- **Effective CT = C/T ÷ Stations** — this is what matters for bottleneck comparison against Takt Time.
- Use `ct_unit: "min"` for heavy industry / equipment manufacturing (values are cleaner), `"s"` for high-speed assembly.
- For inventory between steps: ask for WIP count or days of supply.
- If unknown, mark as "待测量 (TBM)" — do not assume values.
- **Run data validation immediately after collection** (see `references/lean-analysis.md` Data Validation Rules). Flag any contradictions before rendering.

### 3. Current State Rendering

1. Prepare the input JSON (see `references/svg-rendering.md` for the full schema)
2. Run `python3 scripts/vsm_svg.py input.json output.svg`
3. Convert: `rsvg-convert -w 1775 output.svg -o output.png`
4. Send the PNG to the user via `MEDIA:/path/to/output.png`
4. Also show a Markdown summary table with key metrics:
   - Takt Time, Total Lead Time, Value Add Ratio
   - Any bottlenecks (C/T > Takt Time)

### 3.5 Confirm Current State
**Stop and ask the user to confirm the current state map is accurate.** Do not proceed to future state analysis until the user confirms. If the user points out errors, go back and fix them.

### 4. Future State Analysis
Walk the user through Mike Rother's 8 Future State Design questions (from `references/lean-analysis.md`).
- For each question, briefly explain the concept, then ask the user for their decision or preference.
- When user data contains contradictions, point out the specific conflict and ask which value is correct.
- Identify which process improvements are needed (SMED, TPM, layout change, etc.) and note the expected impact.
- **Quantify the expected impact:** e.g., "SMED on Bending: C/O 30min→10min" — don't just say "apply SMED".

### 5. Future State Rendering
1. Update the input JSON with future state data:
   - Modified process metrics (improved C/T, C/O, Uptime, etc.)
   - Reduced inventory levels
   - Add `future_state_kaizens` array for Kaizen bursts
   - Set `pacemaker` to the pacemaker process name
2. Run the script again to generate future-state SVG, then convert to PNG
3. Send PNG via `MEDIA:`
4. Show before/after comparison table:

| Metric | Current State | Future State | Improvement |
|--------|--------------|--------------|-------------|
| Lead Time | X days | Y days | -Z% |
| Value Add Ratio | A% | B% | +C% |
| Bottlenecks | N | M | -K |

### 7. Iterate & Refine (Load Existing VSM)

After the initial map is generated, users will want to update it with real data or modify the flow. **The JSON file is the persistent source of truth** — the user never needs to edit it manually.

**When the user says something like:**
- "加载泵车那条线" / "打开上次的价值流图"
- "焊接的CT改成实测值45min"
- "加一道探伤工序在焊接后面"
- "去掉机加分支"

**Do this:**

1. **Locate the JSON** — ask the user for the file path, or check `~/vsm-data/` (the default storage directory). If no directory exists, create it and suggest saving there for future access.
2. **Show current state** — read the JSON, display a compact summary table of current processes and metrics so the user knows what they're working with.
3. **Apply changes** — modify the JSON based on user's request:
   - **Data update**: change specific fields (ct, co, uptime, inventory, etc.)
   - **Add process**: insert into `processes[]`, adjust `inventories[]` and `inv_labels[]` length, update any `branches[].from/to` indices that shift
   - **Remove process**: delete from `processes[]`, adjust inventory arrays, fix branch indices
   - **Add/remove branch**: modify `branches[]` array
   - **Structural change** (e.g., split a process, merge two): adjust all affected arrays and indices
4. **Save a versioned copy** before overwriting: `vsm-name-YYYYMMDD-HHMMSS.json` — so the user can always go back
5. **Re-render** — run `vsm_svg.py` on the updated JSON, convert to PNG, send to user
6. **Show what changed** — brief diff: "焊接 CT: 100min → 45min, 新增: 探伤(CT 15min), 移除: 无"

**Auto-save on first render:** After Step 3 (first Current State render), always save the JSON to `~/vsm-data/` with a descriptive name (e.g., `pump-truck-current.json`). Tell the user: "数据已保存到 ~/vsm-data/pump-truck-current.json，下次可以直接修改。"

**Single owner principle:** Per Mike Rother's "Learning to See", VSM should be owned by one person (the Value Stream Manager). This person walks the process, collects data from various sources, and iterates on the map. Others only provide data — they don't edit the map. Do not design multi-user collaboration features. One person + AI + one JSON file is the correct workflow.

### 8. Export & Share

Users may want to share VSM data with colleagues who don't use this tool, or import it into other software (Excel, Minitab, PowerPoint, other VSM tools). Support these export formats:

**When the user says:** "导出数据" / "export" / "导出Excel" / "分享给同事"

**Available exports:**

| Format | Command | Use Case |
|--------|---------|----------|
| JSON | Already saved in `~/vsm-data/` | Machine-readable, re-import into this tool, share with developers |
| CSV | `python3 scripts/vsm_svg.py input.json export.csv` | Open in Excel, share data with colleagues, import into analysis tools |
| SVG | `python3 scripts/vsm_svg.py input.json output.svg` | Vector image, embed in documents, edit in Inkscape/Illustrator |
| PNG | `python3 scripts/vsm_svg.py input.json output.png` | Share via Feishu/WeChat, embed in PPT |

**CSV format:**
```csv
type,name,index,ct,co,uptime,operators,defect,stations,inventory,inv_label
process,下料,0,12,15,85,2,1.5,1,50,原材料
process,折弯成型,1,18,20,82,1,2.0,1,92,WIP
branch,机加,-,50,30,85,1,-,1,-,-
```

- Process rows: full data for each process step
- Branch rows: branch process data (index = source process)
- Inventory: each row has the inventory count and label between that process and the next
- Header row for clarity, UTF-8 encoding
- Colleagues can open in Excel and fill in real measurements, then send back for the owner to update

**Implement CSV export in `vsm_svg.py`:** When output filename ends in `.csv`, generate a CSV file instead of SVG/PNG. Include all process and branch data in a flat table format.

### 8. Improvement Action Plan

| Priority | Action | Target Process | Expected Impact | Suggested Method |
|----------|--------|---------------|-----------------|------------------|
| 1 | ... | ... | C/O: Xhr → Ymin | SMED |
| 2 | ... | ... | Uptime: A% → B% | TPM |

**Priority scoring** — rank by:
1. **Eliminates bottleneck** (C/T > Takt → C/T < Takt) — highest priority
2. **Largest Lead Time reduction** (targets biggest inventory pile)
3. **Largest VA Ratio improvement**
4. **Quick wins** (low effort, visible impact)

- Ask the user if they want to assign owners and timelines
