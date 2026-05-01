---
name: value-stream-mapping
version: 2.1.0
description: Draw, create, and analyze Value Stream Maps (VSM) interactively. Use when a user wants to map a process, find bottlenecks, calculate Takt Time, or design a Future State Map based on Lean principles.
tags: [lean, vsm, value-stream, manufacturing, process-optimization, mermaid]
category: operations
linked_files:
  - references/lean-analysis.md
  - references/mermaid-vsm-patterns.md
---

# Value Stream Mapping Skill

This skill guides you to act as an expert Lean Consultant, replacing the traditional pen-and-paper Value Stream Mapping process.

> **Limitation:** Mermaid flowcharts are a simplified representation of VSM. Real VSMs use standardized icons (process boxes, triangles for inventory, etc.). This skill optimizes for Feishu/Lark chat rendering — prioritize clarity over visual fidelity.

## Workflow

Follow these steps strictly:

### 1. Scope Definition
Ask the user to define the scope of the map (e.g., door-to-door, single line, multi-facility) and the target product family. If they have multiple product families, ask them to start with the highest-volume one — multi-family VSMs add complexity (see `references/lean-analysis.md` for mixed-model guidance). Do not proceed until this is clear.

### 2. Current State Extraction

**First, collect demand and time parameters** — these are needed for Takt Time and cannot be calculated later:
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

Generate a Mermaid diagram mapping the flow, followed immediately by a Markdown Data Box table and a Time Line summary.
- **CRITICAL:** Use the conventions in `references/mermaid-vsm-patterns.md`. You must read this file before generating the Mermaid.
- **CRITICAL:** Use the calculations in `references/lean-analysis.md`. You must read this file for Takt Time, Lead Time, and Value Add Ratio formulas.
- Calculate and display: Takt Time, Total Lead Time, Value Add Ratio, and identify any bottlenecks (C/T > Takt Time).
- **For complex value streams (>8 process steps):** Split into 2 diagrams — one for material flow, one for information flow. Or break the line into logical segments (e.g., "Raw Material → Fabrication" and "Fabrication → Shipping"). Always explain the split to the user.

### 3.5 Confirm Current State
**Stop and ask the user to confirm the current state map is accurate.** Do not proceed to future state analysis until the user confirms. If the user points out errors, go back and fix them.

### 4. Future State Analysis
Walk the user through Mike Rother's 8 Future State Design questions (from `references/lean-analysis.md`).
- For each question, briefly explain the concept, then ask the user for their decision or preference.
- When user data contains contradictions (e.g., C/T > Takt Time but user says no bottleneck), point out the specific conflict and ask which value is correct before continuing.
- Identify which process improvements are needed (SMED, TPM, layout change, etc.) and note the expected impact on metrics.
- **Quantify the expected impact:** e.g., "SMED on Bending: C/O 30min→10min" — don't just say "apply SMED", estimate the new value.

### 5. Future State Rendering
Output the revised Mermaid diagram and updated data boxes reflecting the future state.
- Use Kaizen Burst nodes `{{...}}` to mark improvement points on the diagram.
- Show updated Takt Time, Lead Time, Value Add Ratio.
- **Show a before/after comparison table:**

| Metric | Current State | Future State | Improvement |
|--------|--------------|--------------|-------------|
| Lead Time | X days | Y days | -Z% |
| Value Add Ratio | A% | B% | +C% |
| Bottlenecks | N | M | -K |

### 6. Improvement Action Plan
Based on the future state analysis, output a structured improvement action plan:

| Priority | Action | Target Process | Expected Impact | Suggested Method |
|----------|--------|---------------|-----------------|------------------|
| 1 | ... | ... | C/O: Xhr → Ymin | SMED |
| 2 | ... | ... | Uptime: A% → B% | TPM |

**Priority scoring** — rank by this criteria:
1. **Eliminates bottleneck** (C/T > Takt → C/T < Takt) — highest priority
2. **Largest Lead Time reduction** (targets biggest inventory pile)
3. **Largest VA Ratio improvement** (combines #1 and #2)
4. **Quick wins** (low effort, visible impact)

- Reference specific Lean tools (SMED, TPM, 5S, Kanban, Heijunka) where applicable
- Ask the user if they want to assign owners and timelines to each action
