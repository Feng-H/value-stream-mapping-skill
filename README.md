# Value Stream Mapping Skill

A Hermes Agent skill for interactive Value Stream Mapping (VSM) — replacing the traditional pen-and-paper process with structured chat-based analysis.

## Features

- **Current State Mapping:** Extract process data from conversation, validate, and render Mermaid diagrams
- **Lean Calculations:** Takt Time, Lead Time, Value Add Ratio, bottleneck detection
- **Future State Design:** Walk through Mike Rother's 8 questions systematically
- **Action Plan:** Prioritized improvement plan with expected impact quantification
- **Data Validation:** Automatic contradiction detection (C/T > Takt, inventory inconsistencies, etc.)
- **Feishu Optimized:** Mermaid conventions tuned for Lark/Feishu rendering

## Files

```
SKILL.md                          # Main workflow (6-step process)
references/
  lean-analysis.md                # Calculation engine + Rother's 8 questions + validation rules
  mermaid-vsm-patterns.md         # Mermaid syntax conventions + rendering guidelines + examples
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

## Version History

- **2.1.0** — Fixed example data inconsistency, FIFO/Transport syntax, added effective C/T, mixed-model guidance, diagram complexity management, priority scoring
- **2.0.0** — Initial structured version with Mermaid rendering and Rother's 8 questions
