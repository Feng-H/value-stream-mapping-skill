# Mermaid VSM Mapping Guidelines

Since Mermaid does not natively support standard VSM icons, use these conventions optimized for Feishu (Lark) chat rendering.

## Flowchart Setup
Always use `graph LR` (Left to Right) for material flow.

## Nodes

### Material Flow Nodes
| Element | Mermaid Syntax | Notes |
|---------|---------------|-------|
| Customer | `C[👤 Customer]` | End of value stream |
| Supplier | `S[📦 Supplier]` | Start of value stream |
| Process Box | `P1[Stamping]` | Keep label under 15 chars |
| Inventory / Supermarket | `I1[(Raw: 500 pcs)]` | Database shape |
| Buffer / Safety Stock | `B1[(Buffer: 100 pcs)]` | Same shape, label as Buffer |
| FIFO Lane | `F1[/FIFO: 20 pcs\]` | Parallelogram |
| Transport | `T1[/Truck: 2 days\]` | Parallelogram |

### Future State Nodes
| Element | Mermaid Syntax | Notes |
|---------|---------------|-------|
| Kaizen Burst | `K1{{SMED: 1hr→10min}}` | Hexagon, marks improvement point |
| Load Leveling | `L1[/Leveling\]` | Parallelogram at pacemaker |
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
        C -. "月需求: 5000" .-> MP
        MP --- "周计划" --- P1
        P3 -. "看板: 50" .-> I2
    end
```

## Feishu Rendering Constraints
- **Node label**: Keep under 15 characters to avoid truncation
- **Total nodes**: Stay under 10 per diagram; Feishu Mermaid has width limits
- **No HTML tables inside nodes**: They break rendering; always put data in Markdown tables below
- **Chinese characters**: Each Chinese char ≈ 2 Latin char width; count accordingly
- **Avoid `%%` comments**: May cause rendering issues in some Feishu versions

## Complete Example (Current State)

```mermaid
graph LR
    subgraph Material Flow
        S[📦 Supplier] ==> I1[(Raw: 500 pcs)] --> P1[Stamping] ==> I2[(WIP: 100 pcs)] --> P2[Welding] ==> I3[(WIP: 50 pcs)] --> P3[Assembly] ==> C[👤 Customer]
    end
    subgraph Information Flow
        C -. "月需求: 18400" .-> MP[(生产计划)]
        MP --- "周排产" --- P1
        P3 -. "看板: 200" .-> I2
    end
```

| Process | C/T | C/O | Uptime | Shifts | Operators | Defect % |
|---------|-----|-----|--------|--------|-----------|----------|
| Stamping | 45s | 1 hr | 85% | 2 | 1 | 2% |
| Welding | 62s | 30 min | 90% | 2 | 1 | 3% |
| Assembly | 40s | 10 min | 95% | 2 | 2 | 1% |

**Time Line:**
| Segment | Inventory | Wait Time (days) | C/T (增值) |
|---------|-----------|-------------------|------------|
| Raw → Stamping | 500 pcs | 2.5 | 45s |
| Stamping → Welding | 100 pcs | 0.5 | 62s |
| Welding → Assembly | 50 pcs | 0.25 | 40s |
| Assembly → Customer | — | — | — |
| **Total** | — | **3.25 days** | **147s (增值)** |
