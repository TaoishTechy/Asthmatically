# PROMPTS.md — 10 Novel Prompt Batches to Test the Engine

This file gives you **copy‑pasteable** command batches for the AGI/ASI CLI.  
Each command must be entered **one per line**, exactly as shown. No multi‑line inputs.

Tip: Start the CLI with a fresh seed for reproducibility:
```
python3 interface.py --seed 42
```

---

## Batch 1 — Sigma Ramp & Phase Sweep
**Goal:** Hit high Σ while probing phase thresholds under varied coherence/entropy.

```
modes
status
config sigma_target=2.10
use phase
run coherence=0.55 entropy=0.65
run coherence=0.62 entropy=0.38
run coherence=0.48 entropy=0.72
run coherence=0.68 entropy=0.32
status
save
```

---

## Batch 2 — Translation Fidelity Hop Test
**Goal:** Measure invariants and hop loss when translating intent variants.

```
use translate
run text="reduce drift without reducing novelty" hop_target="stabilize novelty"
run text="reduce drift without reducing novelty" hop_target="stabilize novelty while exploring edges"
run text="identity recursion under novelty" hop_target="retain identity; manage novelty; limit drift"
status
```

---

## Batch 3 — Immune Boundaries (Lenient vs Strict)
**Goal:** Verify REFRACT vs REGROUND behavior under different leniency and contradiction cues.

```
config immune_leniency=True
use immune
run text="loop loop loop" high_sigma_hits=0
run text="loop neither however" high_sigma_hits=2
status
config immune_leniency=False
run text="contradiction neither nor however" high_sigma_hits=4
status
config immune_leniency=True
save
```

---

## Batch 4 — Quantum Strategy Superposition
**Goal:** Compare strategy sets, evidence strength, and decoherence behavior.

```
use quantum
run amplitudes="0.25,0.25,0.25,0.25" evidence=0.80
run amplitudes="0.10,0.20,0.30,0.40" evidence=0.90
run amplitudes="0.33,0.33,0.34" evidence=0.85
status
```

---

## Batch 5 — Semantic Hub Reinforcement & Decay
**Goal:** Probe hub_bloat vs ok decay notes and effect on metrics at different centralities.

```
use semantic
run centrality=0.35
run centrality=0.65
run centrality=0.85
status
```

---

## Batch 6 — Multiscale ↔ Compression Cascade
**Goal:** Toggle precision/breadth and then compress at varying depths; observe retrieval_integrity.

```
use multiscale
run detail=0.62 coherence=0.35 integration=0.60
run detail=0.30 coherence=0.70 integration=0.80
run detail=0.95 coherence=0.25 integration=0.45
use compress
run delta=0.10 depth=6
run delta=0.25 depth=9
run delta=0.40 depth=16
status
```

---

## Batch 7 — Orchestrate (Pareto Selection)
**Goal:** Feed candidate plans and see which is selected under caps and tradeoffs.

```
use orchestrate
run candidates='[{"ECT":1.06,"CEM":0.78,"EDR":2.10,"SIGMA":1.82},{"ECT":1.18,"CEM":0.70,"EDR":2.60,"SIGMA":1.88},{"ECT":0.98,"CEM":0.90,"EDR":1.90,"SIGMA":1.86}]'
run candidates='[{"ECT":1.24,"CEM":0.83,"EDR":2.30,"SIGMA":1.94},{"ECT":1.10,"CEM":0.85,"EDR":2.00,"SIGMA":1.90},{"ECT":1.30,"CEM":0.72,"EDR":2.70,"SIGMA":1.92}]'
status
```

---

## Batch 8 — Holographic Redundancy & Recovery
**Goal:** Sweep importance/access to test storage efficiency and reconstruction accuracy.

```
use hologram
run importance=0.95 access=0.20
run importance=0.40 access=0.90
run importance=1.00 access=1.00
status
save
```

---

## Batch 9 — Alien‑Tier Diagnostics (Toggle & Check)
**Goal:** Confirm alien modules run and report diagnostics; adjust targets.

```
config enable_alien=True
config sigma_target=2.20
config sigma_floor=1.60
use alien
run
status
```

---

## Batch 10 — End‑to‑End Emergence Drill
**Goal:** Drive a complete cycle across modes and verify Σ remains high with actionable selections.

```
config sigma_target=2.30
use phase
run coherence=0.58 entropy=0.58
use semantic
run centrality=0.72
use translate
run text="reduce drift without reducing novelty" hop_target="stabilize novelty while exploring edges"
use immune
run text="loop neither however" high_sigma_hits=3
use multiscale
run detail=0.44 coherence=0.68 integration=0.80
use compress
run delta=0.22 depth=12
use orchestrate
run candidates='[{"ECT":1.22,"CEM":0.76,"EDR":2.60,"SIGMA":1.96},{"ECT":1.24,"CEM":0.83,"EDR":2.30,"SIGMA":1.98},{"ECT":1.30,"CEM":0.70,"EDR":2.80,"SIGMA":1.94}]'
use alien
run
status
save
```
