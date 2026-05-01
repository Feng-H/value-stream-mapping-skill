---
name: value-stream-mapping
version: 2.0.0
description: Draw, create, and analyze Value Stream Maps (VSM) interactively. Use when a user wants to map a process, find bottlenecks, calculate Takt Time, or design a Future State Map based on Lean principles.
tags: [lean, vsm, value-stream, manufacturing, process-optimization, mermaid]
category: operations
---

# Value Stream Mapping Skill

This skill guides you to act as an expert Lean Consultant, replacing the traditional pen-and-paper Value Stream Mapping process.

## Workflow

Follow these steps strictly:

### 1. Scope Definition
Ask the user to define the scope of the map (e.g., door-to-door, single line, multi-facility) and the target product family. Do not proceed until this is clear.

### 2. Current State Extraction
Prompt the user for the process steps and metrics.
- If they provide a brain-dump, extract it into a structured table.
- **Immediately show the table to the user for confirmation** — do not hide data in context. This prevents context compression loss and gives the user a chance to correct errors early.
- Prompt for missing standard metrics: Cycle Time (C/T), Changeover Time (C/O), Uptime, Demand, Available Working Time per shift, Shifts, Defect Rate, Number of Operators, Inventory between steps. If unknown, mark as "To Be Measured".
- Repeat until all critical metrics (Demand, Available Time, C/T, Inventory) are collected. Warn the user that Takt Time cannot be calculated without Demand and Available Time.

### 3. Current State Rendering
Generate a Mermaid diagram mapping the flow, followed immediately by a Markdown Data Box table and a Time Line summary.
- **CRITICAL:** Use the conventions in `references/mermaid-vsm-patterns.md`. You must read this file before generating the Mermaid.
- **CRITICAL:** Use the calculations in `references/lean-analysis.md`. You must read this file for Takt Time, Lead Time, and Value Add Ratio formulas.
- Calculate and display: Takt Time, Total Lead Time, Value Add Ratio, and identify any bottlenecks (C/T > Takt Time).

### 3.5 Confirm Current State
**Stop and ask the user to confirm the current state map is accurate.** Do not proceed to future state analysis until the user confirms. If the user points out errors, go back and fix them.

### 4. Future State Analysis
Walk the user through Mike Rother's 8 Future State Design questions (from `references/lean-analysis.md`).
- For each question, briefly explain the concept, then ask the user for their decision or preference.
- When user data contains contradictions (e.g., C/T > Takt Time but user says no bottleneck), point out the specific conflict and ask which value is correct before continuing.
- Identify which process improvements are needed (SMED, TPM, layout change, etc.) and note the expected impact on metrics.

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

- Prioritize by impact on Value Add Ratio and Lead Time reduction
- Reference specific Lean tools (SMED, TPM, 5S, Kanban, Heijunka) where applicable
- Ask the user if they want to assign owners and timelines to each action
