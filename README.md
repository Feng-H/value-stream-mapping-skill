# Value Stream Mapping Skill

Interactive Value Stream Mapping (VSM) skill for AI agents (HermesAgent / OpenClaw). Based on Mike Rother's *Learning to See* methodology.

## What It Does

Guides an interactive 6-step Lean consulting workflow through chat:

1. **Scope Definition** — Define map boundary and product family
2. **Current State Extraction** — Collect process steps and metrics (C/T, C/O, Uptime, Inventory...)
3. **Current State Rendering** — Generate Mermaid VSM diagram + data boxes + time line
4. **Future State Analysis** — Mike Rother's 8 questions, bottleneck identification, improvement planning
5. **Future State Rendering** — Revised diagram with Kaizen Burst markers + before/after comparison
6. **Improvement Action Plan** — Prioritized action list with Lean tool recommendations

## Supported Calculations

- **Takt Time** — multi-shift aware
- **Lead Time** — inventory wait + processing time
- **Value Add Ratio** — key improvement metric
- **Bottleneck Detection** — C/T vs Takt Time

## Install

```bash
# HermesAgent
hermes skills install Feng-H/value-stream-mapping-skill

# OpenClaw
clawhub install value-stream-mapping-skill

# Manual
git clone https://github.com/Feng-H/value-stream-mapping-skill.git
cp -r value-stream-mapping-skill ~/.hermes/skills/
```

## File Structure

```
├── SKILL.md                        # Skill definition (agentskills.io standard)
└── references/
    ├── lean-analysis.md            # Lean calculations + 8 questions
    └── mermaid-vsm-patterns.md     # Mermaid rendering conventions + examples
```

## Example Output

```
Customer ─── 月需求:18400 ───→ [Production Plan] ─── 周排产 ───→ Stamping
                                                                        │
                                                                       WIP:100
                                                                        │
                                                                        ▼
Welding ──── 看板:200 ────→ Assembly ──── → Customer

| Process   | C/T  | C/O   | Uptime | Bottleneck |
|-----------|------|-------|--------|------------|
| Stamping  | 45s  | 1 hr  | 85%    | ✗          |
| Welding   | 62s  | 30min | 90%    | ✓ (C/T>Takt)|
| Assembly  | 40s  | 10min | 95%    | ✗          |

Value Add Ratio: 0.05% | Lead Time: 3.25 days
```

## License

MIT
