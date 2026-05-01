# Lean Analysis Engine

## Core Calculations

### Takt Time (节拍时间)
衡量客户需求速率，决定生产节奏。
```
Takt Time = (每班可用时间 × 班次数) / 总需求
```
- 每班可用时间 = 排除休息/午休后的净工作时间（如 8h 班次 ≈ 27600s）
- 总需求必须与可用时间使用相同时间单位（如日需求配日可用时间）
- 如果需求按月/周给出，先换算：日需求 = 月需求 / 月工作天数

### Cycle Time (周期时间)
一个工序完成单个产品所需的时间。由各工序实际测量得到。

### Lead Time (前置时间)
从原材料到成品交付给客户的全部时间，由两部分组成：
```
库存等待时间 = 库存量 / 日需求（天）
工序增值时间 = Σ(各工序 C/T)
总 Lead Time = Σ(各库存等待时间) + Σ(各工序增值时间)
```
- VSM 上方时间线标注各段**库存等待时间**（天）
- VSM 下方时间线标注**总增值时间**（Σ C/T）
- 两者之差即为消除浪费的改善空间

### Value Add Ratio (增值比)
展示改善空间的核心指标：
```
增值比 = 增值时间（Σ C/T） / 总 Lead Time × 100%
```
- 典型制造业增值比仅 1%-5%，即 95%+ 的时间在等待
- 未来状态设计的目标是显著提升此比率

### Bottleneck (瓶颈)
任何 C/T > Takt Time 的工序即为瓶颈。瓶颈决定整条产线的最大产出速率。

---

## Future State Design (Mike Rother's 8 Questions)
When guiding the user to the Future State, sequentially ask or analyze:
1. What is the Takt Time?
2. Will you build to a finished goods supermarket or directly to shipping?
3. Where can you introduce continuous flow?
4. Where will you need to use supermarket pull systems (due to distance or unreliability)?
5. At what single point in the production chain will you schedule production (the pacemaker process)?
6. How will you level the production mix at the pacemaker?
7. What increment of work will you consistently release (pitch)?
8. What process improvements are needed (e.g., SMED to reduce C/O, TPM to improve Uptime)?

---

## Data Validation Rules
When user provides data, check for these common issues:
- **C/T > Takt Time but user claims no bottleneck**: Point out the contradiction, ask user to verify
- **Missing Demand or Available Time**: Cannot calculate Takt Time — prompt user to provide both
- **Inventory = 0 between all steps**: Ask user to confirm; real processes almost always have some WIP
- **Uptime not provided**: Default assumption varies by industry; prompt user rather than assume
