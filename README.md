# Value Stream Mapping Skill

A Hermes Agent skill for interactive Value Stream Mapping (VSM) — replacing the traditional pen-and-paper process with structured chat-based analysis using SVG rendering.

## Features

- **Current State Mapping:** Extract process data from conversation, validate, and render professional SVG diagrams with standard Lean icons
- **Branch Flows:** Support process-to-process branches (e.g., machining split from main line) and external input branches (e.g., purchased components)
- **Lean Calculations:** Takt Time, Lead Time, Value Add Ratio, bottleneck detection (effective C/T vs Takt)
- **Future State Design:** Walk through Mike Rother's 8 questions systematically with Kaizen bursts
- **Action Plan:** Prioritized improvement plan with expected impact quantification
- **Data Validation:** Automatic contradiction detection (C/T > Takt, inventory inconsistencies, etc.)
- **Feishu Optimized:** PNG output recommended (SVG converted via rsvg-convert)

## Files

```
SKILL.md                          # Main workflow (8-step process)
references/
  lean-analysis.md                # Calculation engine + Rother's 8 questions + validation rules
  svg-rendering.md                # JSON schema, visual elements, bottleneck detection
scripts/
  vsm_svg.py                      # Zero-dependency Python SVG generator
templates/
  pump-truck-example.json         # Complete example with 10 processes + 4 branches
```

## Install

Clone into your Hermes skills directory:
```bash
mkdir -p ~/.hermes/skills/operations
git clone https://github.com/Feng-H/value-stream-mapping-skill.git ~/.hermes/skills/operations/value-stream-mapping
```

## Usage

Just describe your manufacturing process to the agent. Example prompts:

- "帮我画一个钢结构支架产线的价值流图"
- "我们产线有5道工序，日需求500件，帮我做VSM分析"
- "分析一下这个产线的瓶颈在哪里"

The agent will guide you through data collection, rendering, and improvement planning.

## Export Options

```bash
# PNG output (recommended for Feishu/WeChat)
python3 scripts/vsm_svg.py input.json output.png

# SVG output (for editing in Inkscape/Illustrator)
python3 scripts/vsm_svg.py input.json output.svg

# CSV export (share data with colleagues)
python3 scripts/vsm_svg.py input.json data.csv
```

## Version History

- **4.3.0** — Added supermarket/kanban icons, batch_size/available_time fields, pacemaker on current state, CSV export with new fields, finished goods supermarket option
- **4.2.0** — Added iterate & refine workflow, single-owner principle, export & share documentation
- **4.0.0** — SVG rendering engine with branch flows, multi-station, ct_unit toggle
- **2.1.0** — Fixed example data inconsistency, FIFO/Transport syntax, added effective C/T, mixed-model guidance
- **2.0.0** — Initial structured version with Mermaid rendering and Rother's 8 questions