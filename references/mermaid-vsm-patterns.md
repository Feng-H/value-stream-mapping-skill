# Mermaid VSM Mapping Guidelines

Since Mermaid does not natively support standard VSM icons, use these conventions optimized for Feishu (Lark) chat rendering.

## Flowchart Setup
Always use `graph LR` (Left to Right) for material flow.

## Nodes

### Material Flow Nodes
| Element | Mermaid Syntax | Notes |
|---------|---------------|-------|
| Customer | `C[Customer]` | End of value stream |
| Supplier | `S[Supplier]` | Start of value stream |
| Process Box | `P1[Stamping]` | Keep label under 15 chars |
| Inventory / Supermarket | `I1[(Raw: 500 pcs)]` | Database shape |
| Buffer / Safety Stock | `B1[(Buffer: 100 pcs)]` | Same shape, label as Buffer |
| FIFO Lane | `F1[/FIFO: 20 pcs/]` | Parallelogram — NO backslash before closing bracket |
| Transport | `T1[/Truck: 2 days/]` | Parallelogram |

### Future State Nodes
| Element | Mermaid Syntax | Notes |
|---------|---------------|-------|
| Kaizen Burst | `K1{{SMED: 1hr→10min}}` | Hexagon, marks improvement point |
| Load Leveling | `L1[/Leveling/]` | Parallelogram at pacemaker |
| Trigger Point | `D[(FG: 2 days)]` | Database shape, finished goods |

### Styling (use sparingly)
```mermaid
graph LR
    K1{{Kaizen}}:::kaizen
    classDef kaizen fill:#ff9,stroke:#333,stroke-width:2px
```

## Connections (Flows)
| Flow Type | Arrow | Example |
|-----------|-------|---------|
| Material Push | `==>` | `S ==> I1` |
| Material Pull | `-->` | `I1 --> P1` |
| Info Flow (Electronic) | `-.->` | `C -. "月需求: 5000" .-> P3` |
| Info Flow (Manual) | `---` | `P3 --- "生产计划" --- P1` |
| Kanban Signal | `-. "看板: 50 pcs" .->` | `P2 -. "看板" .-> I1` |

## Information Flow
Information flow runs **below** the material flow. Use `subgraph` to visually separate:
```mermaid
graph LR
    subgraph Material Flow
        S ==> I1 --> P1 ==> I2 --> P2 ==> I3 --> P3 ==> C
    end
    subgraph Information Flow
        MP[(生产计划)]
        C -. "月需求: 5000" .-> MP
        MP --- "周排产" --- P1
        P3 -. "看板: 50" .-> I2
    end
```
> **Note:** `MP[(生产计划)]` must be defined inside the Information Flow subgraph, not referenced from outside. This ensures it renders correctly.

## Diagram Complexity Management

Feishu Mermaid has limited rendering width. Follow these rules:

| Process Steps | Recommended Approach |
|--------------|---------------------|
| ≤ 5 | Single diagram, material + info flow in one |
| 6-8 | Split: material flow diagram + info flow diagram |
| 9+ | Break into logical segments (e.g., "Fab → Weld" and "Weld → Ship"), or show only key process steps and group minor ones |

**General rules:**
- Total nodes per diagram: aim for ≤ 12 (including inventory nodes)
- Node label: keep under 15 characters to avoid truncation
- Chinese characters: each CJK char ≈ 2 Latin char width; count accordingly
- Avoid `%%` comments: may cause rendering issues in some Feishu versions
- No HTML tables inside nodes: they break rendering; always put data in Markdown tables below

## Feishu-Specific Rendering Notes
- Avoid emoji in node labels (📦, 👤, etc.) — rendering is unreliable across Feishu versions. Use plain text: `S[Supplier]`, `C[Customer]`
- If a diagram gets too wide, switch to `graph TD` (top-down) for that section
- Test complex diagrams before sending; if rendering breaks, simplify and move data to Markdown tables

## Complete Example (Current State)

> **Data verification:** Monthly demand = 4400, working days = 22, daily demand = 200 pcs/day.

```mermaid
graph LR
    subgraph Material Flow
        S[Supplier] ==> I1[(Raw: 500 pcs)] --> P1[Stamping] ==> I2[(WIP: 100 pcs)] --> P2[Welding] ==> I3[(WIP: 50 pcs)] --> P3[Assembly] ==> C[Customer]
    end
    subgraph Information Flow
        MP[(生产计划)]
        C -. "月需求: 4400" .-> MP
        MP --- "周排产" --- P1
        P3 -. "看板: 200" .-> I2
    end
```

| Process | C/T | C/O | Uptime | Shifts | Operators | Defect % |
|---------|-----|-----|--------|--------|-----------|----------|
| Stamping | 45s | 1 hr | 85% | 2 | 1 | 2% |
| Welding | 62s | 30 min | 90% | 2 | 1 | 3% |
| Assembly | 40s | 10 min | 95% | 2 | 2 | 1% |

**Takt Time:** 27600s / 200 = 138s

**Time Line:**

| Segment | Inventory | Wait Time (days) | C/T (增值) |
|---------|-----------|-------------------|------------|
| Raw → Stamping | 500 pcs | 500/200 = 2.50 | 45s |
| Stamping → Welding | 100 pcs | 100/200 = 0.50 | 62s |
| Welding → Assembly | 50 pcs | 50/200 = 0.25 | 40s |
| Assembly → Customer | — | — | — |
| **Total** | — | **3.25 days** | **147s (2.5min)** |

**Value Add Ratio:** 147 / (3.25 × 86400) × 100% = 0.052%

**Bottleneck:** None (all C/T < Takt 138s)
