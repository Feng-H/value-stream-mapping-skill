# Lean Analysis Engine

## Core Calculations

### Takt Time (节拍时间)
衡量客户需求速率，决定生产节奏。
```
Takt Time = (每班可用时间 × 班次数) / 日需求
```
- 每班可用时间 = 排除休息/午休后的净工作时间（如 8h 班次 ≈ 27000s，扣30min休息）
- 日需求 = 月需求 / 月工作天数（注意：用工作日而非自然日）
- **必须确保分子分母时间单位一致**：如果日需求按天算，可用时间也按天算（即每日可用秒数）

### Effective Cycle Time (有效周期时间)
考虑换模影响的实际产出速率：
```
有效 C/T = C/T + (C/O × 批次内换模次数) / 批量
```
- 当换模时间长且批量小时，有效 C/T 会显著高于名义 C/T
- **如果 C/O > 10min 且批量 < 100，必须计算有效 C/T 来判断真实瓶颈**

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
- 注意：库存等待时间和增值时间单位不同（天 vs 秒/分），通常分别展示

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
3. Where can you introduce continuous flow? (连续流适用于工序间距离近、C/T接近、质量稳定的场景)
4. Where will you need to use supermarket pull systems? (超市拉系统适用于距离远、工序不可靠、或C/T差异大的场景)
5. At what single point in the production chain will you schedule production (the pacemaker process)? (节拍工序是唯一接收排产指令的点)
6. How will you level the production mix at the pacemaker? (Heijunka均衡排产，避免批量生产造成的需求波动)
7. What increment of work will you consistently release (pitch)? (Pitch = 瓶颈工序一托盘/一箱的数量 × Takt Time)
8. What process improvements are needed (e.g., SMED to reduce C/O, TPM to improve Uptime)?

---

## Mixed-Model / Multi-Product Family Handling
当产线生产多个产品族时：
- 按最高产量产品族画主线，其他族作为分支或标注
- Takt Time 用总需求计算，但需各族的 C/T 分别对照
- 如果某族 C/T > Takt，考虑：专用线、外包、或加班

---

## Data Validation Rules
When user provides data, check for these common issues:
- **C/T > Takt Time but user claims no bottleneck**: Point out the contradiction, ask user to verify
- **Missing Demand or Available Time**: Cannot calculate Takt Time — prompt user to provide both
- **Inventory = 0 between all steps**: Ask user to confirm; real processes almost always have some WIP
- **Uptime not provided**: Default assumption varies by industry; prompt user rather than assume
- **Lead Time numbers don't match inventory**: Verify `库存/日需求 = 时间线天数`, flag inconsistencies
- **C/O > 10min but batch size unknown**: Cannot assess effective C/T; ask for batch size
- **Monthly demand but no working days specified**: Ask; never assume 22 days — some factories operate 25-30 days
