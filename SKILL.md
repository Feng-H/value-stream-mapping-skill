---
name: value-stream-mapping
version: 3.0.0
description: Draw, create, and analyze Value Stream Maps (VSM) with professional SVG rendering. Use when a user wants to map a process, find bottlenecks, calculate Takt Time, or design a Future State Map based on Lean principles.
tags: [lean, vsm, value-stream, manufacturing, process-optimization, svg]
category: operations
linked_files:
  - references/lean-analysis.md
  - references/svg-rendering.md
  - scripts/vsm_svg.py
---

# Value Stream Mapping Skill

This skill guides you to act as an expert Lean Consultant, producing professional Value Stream Maps with standard Lean icons (process data boxes, inventory triangles, timeline bars, Kaizen bursts) rendered as SVG.

## Rendering Engine

VSM diagrams are generated via `scripts/vsm_svg.py` — a zero-dependency Python script that outputs SVG files.

**Before rendering (Step 3 and Step 5), you MUST:**
1. Read `references/svg-rendering.md` for the SVG conventions and visual elements
2. Read `references/lean-analysis.md` for Takt Time, Lead Time, and Value Add Ratio formulas

**To generate a VSM:**
```bash
python3 scripts/vsm_svg.py input.json output.svg
rsvg-convert -w 1775 output.svg -o output.png
```

The input JSON structure is documented in `references/svg-rendering.md`.

**IMPORTANT:** Feishu does not support SVG attachments. Always convert to PNG with `rsvg-convert` before sending via `MEDIA:`. Dependency: `librsvg2-bin` (`sudo apt-get install -y librsvg2-bin`).

**User preference:** Do not over-verify SVG output programmatically. Generate, convert to PNG, send to user. They will visually inspect and provide feedback.

## Workflow

Follow these steps strictly:

### 1. Scope Definition
Ask the user to define the scope of the map (e.g., door-to-door, single line, multi-facility) and the target product family. If they have multiple product families, ask them to start with the highest-volume one — multi-family VSMs add complexity (see `references/lean-analysis.md` for mixed-model guidance). Do not proceed until this is clear.

### 2. Current State Extraction

**First, collect demand and time parameters** — these are needed for Takt Time:
- Monthly/weekly/daily demand
- Working days per month
- Shifts per day and net available time per shift (exclude breaks/lunch)

**Then collect process steps and metrics:**
- If they provide a brain-dump, extract it into a structured table.
- **Immediately show the table to the user for confirmation** — do not hide data in context. This prevents context compression loss and gives the user a chance to correct errors early.
- For each process step, collect: Cycle Time (C/T), Changeover Time (C/O), Uptime, Number of Operators, Defect Rate.
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

### 6. Improvement Action Plan

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
