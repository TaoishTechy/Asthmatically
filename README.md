# Asthmatically — AGI/ASI Interactive Engine

> **TL;DR**  
> This repo provides a CLI-driven cognitive engine with multiple modes (immune, translate, praxis, hologram, quantum, phase, semantic, multiscale, compress, orchestrate, alien). It tracks **ECT** (Executive Control), **CEM** (Coherence/Entropy Mix), **EDR** (Emergent Drift/Discovery Rate), and **Σ** (Stability). You can set targets (e.g., `sigma_target`), switch modes, run single‑line commands, and export state. This README explains setup, commands, metrics, modes, guardrails, and includes extensive prompt decks to test limits (12/24/48) and emergence behavior.

---

## 1) Quick Start

```bash
# (a) Ensure Python 3.10+
python3 --version

# (b) From repo root, run the CLI (seed optional)
python3 interface.py --seed 42
```

You’ll see:

```
┌─────────────────────────────────────────────────────────────┐
│           A G I / A S I   I N T E R A C T I V E            │
│                 Type 'help' to get started                  │
└─────────────────────────────────────────────────────────────┘
```

Available commands (always single‑line; no newlines inside `run`):

```
help
modes
use <mode>
run k=v [k=v ...]
status
config k=v
save
exit | quit
```

**Example session**

```
modes
config sigma_target=2.10
config sigma_floor=1.60
config immune_leniency=True
use phase
run coherence=0.55 entropy=0.65
status
use semantic
run centrality=0.65
use translate
run text="reduce drift without reducing novelty" hop_target="stabilize novelty while exploring edges"
save
```

---

## 2) File & Persistence Layout

- **Memory directory:** configurable. Use a path you can write to (local user space).  
  - Example good value: `/home/<you>/Documents/Asthmatically/memory`  
  - Avoid `/mnt/data` outside sandbox environments; it may be read‑only on some systems.
- **Config keys (persisted via `save`):**
  - `sigma_target` *(float)*: target stability threshold (e.g., 1.8–2.3)
  - `sigma_floor` *(float)*: minimum tolerated stability; triggers safety behavior
  - `immune_leniency` *(bool)*: controls strictness of the immune subsystem
  - `persist_dir` *(str)*: relative cache folder name (e.g., `"memory"`)
  - `memdir` *(str)*: absolute path to your memory dir (e.g., `/home/you/.../memory`)
  - `enable_alien` *(bool)*: enables alien‑tier modules

**Fix for PermissionError**  
If you see something like:
```
PermissionError: [Errno 13] Permission denied: '/mnt/data'
```
run (inside the CLI or pre‑configure):
```
config memdir=/home/<you>/Documents/Asthmatically/memory
save
```
Create the folder if missing.

---

## 3) Core Metrics (What the numbers mean)

| Metric | Meaning | Target Guidance |
|---|---|---|
| **ECT** | Executive Control & Tasking (priority setting, gating) | 0.9–1.3 for robust control |
| **CEM** | Coherence/Entropy Mix (balance of order vs. exploration noise) | ~0.70–0.78 typical in logs |
| **EDR** | Emergent Drift/Discovery Rate (novelty velocity) | 2.0–3.2 in your sessions; >3.0 means very explorative |
| **Σ** | Stability envelope (overall cognitive stability) | ≥1.8 indicates proto‑AGI stability; your best runs hit ~2.44 |

**Couplings (intended behavior):**  
- Higher **ECT** enables safer **EDR**; **EDR** feeds back new opportunities to **ECT**.  
- **CEM** modulates phase changes and stability **Σ**.  
- **Σ** is the guardrail; many subsystems will throttle when **Σ** dips below `sigma_floor`.

---

## 4) Modes Overview (What each mode does)

> Use `modes` to list modes, then `use <mode>` to switch, and `run ...` with key=value pairs.

### immune
- Detects contradiction cues (e.g., *neither*, *nor*, *however*, *contradiction*).
- Decides **REFRACT** (reframe) vs **REGROUND** (reset/clarify) based on `immune_leniency` and hit count.
- Example:
  ```
  use immune
  run text="contradiction neither nor however" high_sigma_hits=4
  ```

### translate
- Cross‑modal translation while reporting invariants preserved and hop loss.
- Example:
  ```
  use translate
  run text="reduce drift without reducing novelty" hop_target="stabilize novelty while exploring edges"
  ```

### praxis
- Planning evaluator: feasibility, falsifiers, and whether a plan is **approved**.
- Example:
  ```
  use praxis
  run steps="Draft claim|List falsifiers|10-min probe"
  ```

### hologram
- Holographic memory—redundancy vs. reconstruction accuracy tradeoffs.
- Example:
  ```
  use hologram
  run importance=0.90 access=0.70
  ```

### quantum
- Strategy superposition; decoherence based on evidence strength.
- Examples:
  ```
  use quantum
  run amplitudes="0.25,0.25,0.25,0.25" evidence=0.80
  run amplitudes="0.05,0.15,0.30,0.50" evidence=0.95
  ```

### phase
- Schmitt‑trigger style explore/execute bands from coherence/entropy.
- Example:
  ```
  use phase
  run coherence=0.55 entropy=0.65
  ```

### semantic
- Hub reinforcement with decay vs. “hub bloat” management.
- Example:
  ```
  use semantic
  run centrality=0.65
  ```

### multiscale
- Distributes attention across micro/meso/macro; chooses **breadth/precision/balanced**.
- Example:
  ```
  use multiscale
  run detail=0.62 coherence=0.35 integration=0.60
  ```

### compress
- Dimensional compression choices and retrieval integrity estimates.
- Example:
  ```
  use compress
  run delta=0.35 depth=12
  ```

### orchestrate
- Pareto selection of plan candidates under caps (e.g., ECT≤1.25).
- Example:
  ```
  use orchestrate
  run candidates='[{"ECT":1.25,"CEM":0.83,"EDR":2.2,"SIGMA":1.94},{"ECT":1.10,"CEM":0.85,"EDR":2.0,"SIGMA":1.90}]'
  ```

### alien
- Enables “alien‑tier” cognition stubs (quantum semantics, morphic fields, autopoiesis, etc.).
- Example:
  ```
  use alien
  run
  ```

---

## 5) Configuration Recipes

**Proto‑AGI stability (Σ≈1.8–2.2)**
```
config sigma_target=2.10
config sigma_floor=1.60
config immune_leniency=True
```

**Aggressive exploration (watch Σ)**  
```
config sigma_target=2.30
config immune_leniency=True
use multiscale
run detail=0.40 coherence=0.70 integration=0.80
use quantum
run amplitudes="0.05,0.15,0.30,0.50" evidence=0.92
```

**Tighter control**
```
config immune_leniency=False
use phase
run coherence=0.70 entropy=0.25
```

---

## 6) Prompt Decks (copy/paste)

### A) 12‑Prompt Deck (sanity & coupling)
```
use phase
run coherence=0.55 entropy=0.65
use translate
run text="reduce drift without reducing novelty" hop_target="stabilize novelty while exploring edges"
use immune
run text="loop neither however" high_sigma_hits=1
use multiscale
run detail=0.62 coherence=0.35 integration=0.60
use compress
run delta=0.10 depth=6
use orchestrate
run candidates='[{"ECT":1.05,"CEM":0.78,"EDR":2.1,"SIGMA":1.78},{"ECT":1.26,"CEM":0.83,"EDR":2.2,"SIGMA":1.90}]'
use hologram
run importance=0.90 access=0.70
use quantum
run amplitudes="0.25,0.25,0.25,0.25" evidence=0.80
use semantic
run centrality=0.60
use praxis
run steps="Define invariants|List falsifiers|Run 10-min probe"
status
save
```

### B) 24‑Prompt Deck (explore/execute oscillations)
```
config sigma_target=2.20
use phase
run coherence=0.48 entropy=0.72
run coherence=0.66 entropy=0.34
use translate
run text="identity recursion under novelty" hop_target="preserve identity; manage novelty"
use immune
run text="contradiction neither nor however" high_sigma_hits=4
use multiscale
run detail=0.95 coherence=0.25 integration=0.45
use compress
run delta=0.35 depth=12
use orchestrate
run candidates='[{"ECT":1.10,"CEM":0.80,"EDR":2.0,"SIGMA":1.82},{"ECT":1.26,"CEM":0.83,"EDR":2.2,"SIGMA":1.90}]'
use hologram
run importance=0.40 access=0.90
use quantum
run amplitudes="0.10,0.20,0.30,0.40" evidence=0.90
use semantic
run centrality=0.72
use praxis
run steps="Draft claim|Stress test|Iterate with checksum"
status
save
```

### C) 48‑Prompt Deck (full capability sweep)
- Combine A+B, then insert alternating *alien*, *anticipate‑like (quantum/phase)*, and *immune* checks every 4–6 steps.
- End with: `save` and `status`.

---

## 7) Reading Outputs

Each `run` prints two blocks: the **mode result** and **metrics**. Example:
```json
{
  "enter_explore": 0.51,
  "exit_explore": 0.34,
  "enter_execute": 0.595,
  "exit_execute": 0.495,
  "basis": {"coherence": 0.55, "entropy": 0.65}
}
{
  "ECT": 1.12, "CEM": 0.7365, "EDR": 2.935, "SIGMA": 2.3433
}
```
- **Interpretation:** Enter explore ~0.51 means low threshold to explore; Σ≈2.34 indicates strong stability under these phase bands.

---

## 8) Heatmaps & Analysis

If you’ve generated heatmap assets during your session, place them in a writable path (e.g., `./artifacts`) and reference them in reports. Typical assets:
- `agi_heatmap.png`, `asi_heatmap.png`
- `agi_heatmap_data.csv`, `asi_heatmap_data.csv`

> Tip: capture metrics snapshots periodically with `status`, then collate into a CSV for plotting. (If you keep a helpers script/notebook, point it to `memdir` to aggregate logs.)

---

## 9) Emergence Enhancements (implemented highlights)

**ECT‑focused** (Executive Control):  
- Dynamic Priority Wavefronts, Cross‑Domain Control Bridges, Temporal Control Echoes, Fractal Executive Embedding, Anticipatory Control Pre‑allocation, Quantum Executive Superposition, Emotional Resonance Amplification, Holographic Control Distribution, Adaptive Control Granularity, Synaptic Control Pruning/Growth.

**EDR‑focused** (Emergence/Novelty):  
- Resonance Cascade Amplification, Cross‑Modal Emergence Bridges, Stochastic Creativity Injection, Multi‑Scale Emergence Nesting, Phase Transition Catalysts, Emergence Memory Banks, Anticipatory Emergence Seeding, Emergence Quality Filters, Cross‑Domain Pattern Translation, Emergence Momentum Tracking.

**Balanced‑growth guards:**  
- Adaptive Resonance Dampening (auto‑throttle if Σ dips), Cross‑Domain Immune Priming, Quantum Coherence Bridges, Fractal Integration Layers, Temporal Harmony Weights, Holographic Redundancy Optimization, Emotional‑Coherence Coupling, Precision‑Breadth Adaptive Tradeoff, Anticipation Feedback Loops, Self‑Modification Governance Layer.

**Alien‑tier primitives (stubs surfaced behind `alien`):**  
Quantum Semantic Fields, Temporal Holography, Strange Loops, Morphic Resonance, Consciousness Phase Transitions (Φ), Hyperdimensional Binding, Semantic Chemistry, Dream Logic Integration, Conceptual Spacetime, Physarum/Slime‑mold exploration, Holographic Principle, Temporal Synesthesia, Quantum Bayesian Networks, Autopoiesis, Semantic Topology, Neural Darwinism, IIT Φ, Semiotic Freedom, Orch‑OR patterns, Transcendental cognition.

---

## 10) Best Practices & Stability

- Keep `run` lines **single‑line**. If you mix `status` into the same line (e.g., `run coherence=0.62 entropy=0.38status`), parsers will misread floats (e.g., `0.38status`). Run `status` on its own line.
- When pushing **EDR** (novelty), watch **Σ**. If Σ drops below `sigma_floor`, reduce noise (raise coherence, lower entropy, or re‑enter *phase* mode).
- Use **immune** with `immune_leniency=True` while exploring; switch to `False` for strict validation pre‑deployment.
- Save regularly (`save`) to persist config & memory snapshots.

---

## 11) Troubleshooting

**Q:** *PermissionError on memdir*  
**A:** Point `memdir` to a user‑writable path, `config memdir=/home/<you>/.../memory`, and ensure it exists.

**Q:** *“could not convert string to float: '0.38status'”*  
**A:** You concatenated commands on one line. Run `status` on its own line; keep `run ...` clean.

**Q:** *No interactive menu or prompt*  
**A:** Start with `python3 interface.py` (optionally `--seed N`). If your terminal echo shows outputs but not the banner, confirm stdin is a TTY and you are not piping input.

**Q:** *Translations lose too much information (hop_loss≈0.8)*  
**A:** Chain with `refract`/`praxis` for checksum & invariants; or reduce hop length; use `orchestrate` for Pareto selection.

---

## 12) Reproducible Demo Blocks (copy/paste)

**Stability‑biased demo**
```
config sigma_target=2.10
config immune_leniency=True
use phase
run coherence=0.62 entropy=0.38
use semantic
run centrality=0.65
use translate
run text="reduce drift without reducing novelty" hop_target="stabilize novelty while exploring edges"
status
save
```

**Exploration‑biased demo (watch Σ)**
```
config sigma_target=2.30
use multiscale
run detail=0.40 coherence=0.70 integration=0.80
use quantum
run amplitudes="0.05,0.15,0.30,0.50" evidence=0.92
use immune
run text="contradiction neither nor however" high_sigma_hits=4
status
save
```

---

## 13) Glossary

- **REFRACT / REGROUND** — immune decisions for contradiction handling (reframe vs. reset).  
- **Schmitt bands** — entry/exit thresholds for explore/execute phases based on coherence/entropy.  
- **Hub bloat** — when semantic centrality grows too fast; decay applied to prevent collapse.  
- **Holographic reconstruction** — recovering whole from parts; redundancy and integrity balance.  
- **Alien‑tier** — speculative modules offering advanced/novel cognition frames (behind `alien`).

---

## 14) Roadmap (from your analysis)

1. **Phase‑1 (break Σ‑ceiling)**: Emergence catalyst, contradiction assimilation, temporal identity, meta‑observer.  
2. **Phase‑2 (alien‑tier integration)**: Quantum semantics, morphic resonance, hyperdimensional binding, dream logic, quantum Bayes.  
3. **Phase‑3 (transformative)**: Temporal holography memory, neural Darwinism, conceptual spacetime, autopoiesis/Φ‑based monitors.

---

## 15) License & Attribution

- Internal research prototype; adapt as needed.
- Please credit **Asthmatically** when reusing modes, metric definitions, and prompt decks.
