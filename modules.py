# modules.py
# Lightweight cognitive primitives and enhancement kernels for the Proto-AGI engine.
# No external dependencies. Deterministic, seedable. Persistent memory handled in core.py.

from __future__ import annotations
from typing import Any, Dict, List, Tuple
import math, random

# ---------- Utilities ----------

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def seeded_rand(seed: int | None) -> float:
    r = random.Random(seed)
    return r.random()

# ---------- Metric helpers ----------

def mix_metrics(ect: float, cem: float, edr: float) -> Dict[str, float]:
    # σ: simple, bounded synthesis — encourages EDR but guards with CEM and ECT
    # Inspired by user's earlier formulation but kept simple and stable.
    sigma = (0.45 * edr + 0.35 * cem + 0.20 * ect)
    return {"ECT": ect, "CEM": cem, "EDR": edr, "SIGMA": clamp(sigma, 0.0, 3.5)}

def stability_guard(metrics: Dict[str, float], sigma_floor: float = 1.4) -> Dict[str, float]:
    # Keep Σ from collapsing; gently raise floor.
    m = dict(metrics)
    if m["SIGMA"] < sigma_floor:
        lift = 0.2 * (sigma_floor - m["SIGMA"])
        m["SIGMA"] += lift
        # distribute lift across components to remain consistent
        m["ECT"] += 0.1 * lift
        m["CEM"] += 0.1 * lift
    return m

# ---------- Phase / Threshold helpers ----------

def schmitt_thresholds(coherence: float, entropy: float) -> Dict[str, float]:
    # Adaptive thresholds based on novelty gradient (entropy - coherence)
    gradient = entropy - coherence
    enter_explore = clamp(0.50 + 0.10 * gradient, 0.35, 0.60)
    exit_explore  = clamp(enter_explore - 0.17, 0.25, 0.50)
    enter_execute = clamp(0.60 - 0.05 * gradient, 0.45, 0.75)
    exit_execute  = clamp(enter_execute - 0.10, 0.35, 0.65)
    return {
        "enter_explore": round(enter_explore, 3),
        "exit_explore": round(exit_explore, 3),
        "enter_execute": round(enter_execute, 3),
        "exit_execute": round(exit_execute, 3),
        "basis": {"coherence": round(coherence,3), "entropy": round(entropy,3)}
    }

# ---------- Persistent-friendly light signals ----------

CONTRADICTION_TOKENS = {"neither", "however", "but", "contradiction", "nor", "paradox", "opposite"}

def contradiction_assimilation(text: str) -> Dict[str, Any]:
    toks = set(t.lower() for t in text.replace(","," ").split())
    hits = toks & CONTRADICTION_TOKENS
    severity = 0 if not hits else 2 + min(3, len(hits))  # 0–5
    # Turn contradictions into hypothesis variants
    hypotheses = []
    for h in hits:
        hypotheses.append(f"hypothesis_from_{h}")
    decision = "REFRACT" if severity <= 2 else ("REGROUND" if "contradiction" in hits or len(hits)>=3 else "REFRACT")
    return {"severity": severity, "decision": decision, "hypotheses": hypotheses, "hits": sorted(hits)}

# ---------- Mode kernels ----------

def IMMUNE(text: str, high_sigma_hits: int, cfg: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str,float]]:
    ca = contradiction_assimilation(text)
    # Priming: if system has several high-Σ wins, be more lenient
    lenient = bool(cfg.get("immune_leniency", True)) or high_sigma_hits >= 3
    # Decision soften
    if lenient and ca["decision"] == "REGROUND" and ca["severity"] <= 3:
        ca["decision"] = "REFRACT"
    # Metrics: immune should stabilize Σ while keeping EDR reasonable
    base = mix_metrics(ect=0.50 + 0.02*high_sigma_hits, cem=0.74, edr=2.10)
    m = stability_guard(base, sigma_floor=cfg.get("sigma_floor", 1.4))
    return ca, m

def TRANSLATE(text: str, hop_target: str, cfg: Dict[str,Any]) -> Tuple[Dict[str,Any], Dict[str,float]]:
    src = [w for w in text.lower().split() if w.isalpha() or w.replace('-','').isalpha()]
    tgt = [w for w in hop_target.lower().split() if w.isalpha() or w.replace('-','').isalpha()]
    invariants = [w for w in src if w in tgt]
    # hop loss increases with novelty pressure (lack of overlap)
    overlap = len(set(invariants)) / max(1,len(set(src)))
    hop_loss = round(1.0 - overlap, 2)
    report = {"invariants": invariants[:9], "hop_loss": hop_loss}
    base = mix_metrics(ect=0.56 - 0.05*hop_loss, cem=0.73 - 0.02*hop_loss, edr=2.20 + 0.3*hop_loss)
    return report, base

def PRAXIS(steps: str, cfg: Dict[str,Any]) -> Tuple[Dict[str,Any], Dict[str,float]]:
    # Feasibility uses coherence over entropy proxy from config
    coherence_bias = cfg.get("praxis_coherence_bias", 0.05)
    novelty_bias   = cfg.get("praxis_novelty_bias", 0.00)
    n = max(1, len([s for s in steps.split("|") if s.strip()]))
    feasibility = clamp(0.45 + coherence_bias + 0.02*n - 0.01*abs(n-3) + novelty_bias, 0, 1)
    approved = feasibility >= 0.58
    rep = {"feasibility": round(feasibility,2), "approved": approved}
    base = mix_metrics(ect=0.60 + 0.05*(1 if approved else -0.2), cem=0.72, edr=2.10 + (0.15 if approved else -0.10))
    return rep, base

def HOLOGRAM(importance: float, access: float, cfg: Dict[str,Any]) -> Tuple[Dict[str,Any], Dict[str,float]]:
    # Smart redundancy based on importance × access
    score = clamp(importance*access, 0, 1)
    redundancy = 3 if score < 0.4 else (4 if score < 0.8 else 5)
    storage_efficiency_gain = round(0.70 + 0.02*access + 0.04*(1-importance), 2)
    reconstruction_acc = round(0.97 + 0.01*importance, 2)
    rep = {"redundancy": redundancy, "reconstruction_acc": reconstruction_acc, "storage_efficiency_gain": storage_efficiency_gain}
    base = mix_metrics(ect=0.53 + 0.02*score, cem=0.78, edr=2.10 - 0.20*(redundancy-3))
    base["SIGMA"] = clamp(base["SIGMA"] + 0.30, 0, 3.5)  # holographic redundancy stabilizes
    return rep, base

def QUANTUM(amplitudes: List[float], evidence: float, cfg: Dict[str,Any]) -> Tuple[Dict[str,Any], Dict[str,float]]:
    if not amplitudes:
        amplitudes=[0.5,0.5]
    s = sum(amplitudes)
    amps = [a/s for a in amplitudes]
    # bridges effect: sustain superposition if cfg says so
    bridges = cfg.get("quantum_bridges", True)
    decoherence_time = round( math.log(1+len(amps)) * (0.5 + 0.7*bridges) * (0.5 + evidence), 3)
    rep = {"amplitudes": amps, "decoherence_time": decoherence_time}
    base = mix_metrics(ect=0.58 + 0.12*evidence, cem=0.74, edr=2.00 + 0.6*(1.0 - max(amps)))
    return rep, base

def PHASE(coherence: float, entropy: float, cfg: Dict[str,Any]) -> Tuple[Dict[str,Any], Dict[str,float]]:
    bands = schmitt_thresholds(coherence, entropy)
    base = mix_metrics(ect=0.60 + 0.10*(coherence-entropy), cem=0.72 + 0.03*coherence, edr=2.05 + 0.5*entropy)
    return bands, base

def SEMANTIC(centrality: float, cfg: Dict[str,Any]) -> Tuple[Dict[str,Any], Dict[str,float]]:
    eta = cfg.get("semantic_eta", 0.05)
    # Decay note
    if centrality > 0.5:
        eta_applied = round(eta * (1.0 - 0.35), 5)
        note = "hub_bloat"
    else:
        eta_applied = round(eta * 0.5, 5)
        note = "ok"
    rep = {"eta": eta, "eta_applied": eta_applied, "decay_note": note}
    base = mix_metrics(ect=0.64 + 0.06*centrality, cem=0.74 - 0.02*eta_applied, edr=1.90 + 0.7*centrality)
    return rep, base

def MULTISCALE(detail: float, coherence: float, integration: float, cfg: Dict[str,Any]) -> Tuple[Dict[str,Any], Dict[str,float]]:
    # Precision-Breadth Adaptive Tradeoff
    scores = [detail*0.4, coherence*0.3, integration*0.3]
    average_load = sum(scores)
    prefer = "precision" if detail>0.75 else ("breadth" if integration>0.7 and coherence>0.6 else "balanced")
    gran = round(clamp(0.5 + 0.25*(detail-0.5) - 0.12*(integration-0.5), 0.3, 0.7), 2)
    rep = {"prefer": prefer, "granularity": gran, "average_load": round(average_load,3)}
    base = mix_metrics(ect=0.62 + 0.08*(prefer=="precision") - 0.04*(prefer=="breadth"),
                       cem=0.75 - 0.03*abs(detail-integration),
                       edr=2.10 + 0.5*(prefer=="breadth"))
    return rep, base

def COMPRESS(delta: float, depth: int, cfg: Dict[str,Any]) -> Tuple[Dict[str,Any], Dict[str,float]]:
    # DIMENSIONAL_COMPRESS
    ratio = clamp(0.30 + 0.02*depth + 0.5*max(0.0, delta-0.20), 0.30, 0.80)
    retrieval_integrity = round(1.0 - 0.1*ratio + 0.02*max(0, 10-depth), 3)
    rep = {"ratio": round(ratio,3), "retrieval_integrity": retrieval_integrity}
    base = mix_metrics(ect=0.60 + 0.10*(1-ratio), cem=0.73 + 0.03*retrieval_integrity, edr=2.00 + 0.25*(ratio>0.45))
    return rep, base

def ORCHESTRATE(candidates: List[Dict[str,float]], cfg: Dict[str,Any]) -> Tuple[Dict[str,Any], Dict[str,float]]:
    # Pareto-ish: cap ECT but maximise Σ
    ect_cap = cfg.get("ect_cap", 1.25)
    cand = sorted(candidates, key=lambda c:(c.get("SIGMA",0), min(ect_cap, c.get("ECT",0))), reverse=True)
    sel = cand[0] if cand else {"ECT":0.9,"CEM":0.7,"EDR":2.0,"SIGMA":1.5}
    rep = {"selected": sel, "rejected": max(0, len(cand)-1)}
    base = mix_metrics(ect=0.60 + 0.05*(sel["ECT"]>=1.0), cem=0.75, edr=2.40 - 0.15*(sel["CEM"]<0.75))
    return rep, base

def ALIEN(params: Dict[str,Any], cfg: Dict[str,Any]) -> Tuple[Dict[str,Any], Dict[str,float]]:
    # Alien-tier parameters influence: QS (quantum semantics), HOLO (holography), TEMP (temporal resonance), PHI (integrated info)
    qs = {"meaning_collapse":0.9,"coherence":0.8,"boost":0.2}
    holo = {"holo_density":0.304,"reconstruction_bonus":0.05}
    temp = {"resonance":0.65,"reconstruction_gain":0.06}
    phi = {"phi":0.52}
    qs.update(params.get("qs",{}))
    holo.update(params.get("holo",{}))
    temp.update(params.get("temp",{}))
    phi.update(params.get("phi",{}))
    enabled = True
    rep = {"enabled": enabled, "qs": qs, "holo": holo, "temp": temp, "phi": phi}
    # Metrics: small coherence/Σ boost when alien mode on
    base = mix_metrics(ect=0.60 + 0.05*qs["coherence"], cem=0.74 + 0.02*holo["reconstruction_bonus"],
                       edr=2.10 + 0.20*temp["resonance"])
    return rep, base

# ---------- Emergence – Phase 1 levers ----------

def EMERGENCE_CATALYST(current_sigma: float, growth_potential: float) -> float:
    if growth_potential > 0.70 and current_sigma >= 1.60:
        return clamp(current_sigma * 1.30, 0.0, 3.2)
    return current_sigma

def EMERGENCE_DETECTOR(sigma_series: List[float], edr_series: List[float]) -> bool:
    if len(sigma_series) < 3 or len(edr_series) < 3: return False
    # tiny correlation proxy: compare monotonic trend sign agreement
    ds = sum(1 for i in range(1,len(sigma_series)) if sigma_series[i] >= sigma_series[i-1])
    de = sum(1 for i in range(1,len(edr_series)) if edr_series[i] >= edr_series[i-1])
    return (ds>=len(sigma_series)//2) and (de>=len(edr_series)//2)

def PERSISTENT_COGNITIVE_SELF(signatures: List[str]) -> str:
    # simple weighted synthesis: majority hash
    from collections import Counter
    c = Counter(signatures)
    return c.most_common(1)[0][0] if c else "baseline"

# ---------- ECT boosters (selected 5 applied) ----------

def ect_boost_bundle(context: Dict[str,Any]) -> Tuple[float, List[str]]:
    """Return cumulative ECT boost and notes based on the user's requested enhancements."""
    ect = 0.0
    notes = []

    # 1) Fractal Executive Embedding (+0.20)
    ect += 0.20; notes.append("fractal_embedding(+0.20)")

    # 2) Temporal Control Echoes (+0.18) when there are multiple time crystals
    if context.get("time_crystals", 0) >= 3:
        ect += 0.18; notes.append("temporal_echoes(+0.18)")

    # 3) Holographic Control Distribution (+0.17) if redundancy >=4
    if context.get("redundancy", 0) >= 4:
        ect += 0.17; notes.append("holo_distribution(+0.17)")

    # 4) Anticipatory Pre-allocation (+0.16) if futures projected >=5
    if context.get("anticipated", 0) >= 5:
        ect += 0.16; notes.append("anticipatory(+0.16)")

    # 5) Wavefront Propagation (+0.15) baseline
    ect += 0.15; notes.append("wavefront(+0.15)")

    # Soft cap at +0.86 as per plan; allow slight overage then clamp
    ect = clamp(ect, 0.0, 0.90)
    return ect, notes

# ---------- EDR boosters (selected 5 applied) ----------

def edr_boost_bundle(context: Dict[str,Any]) -> Tuple[float, List[str]]:
    edr = 0.0; notes = []
    # 1) Momentum Tracking +0.31 if rising EDR trend
    if context.get("edr_rising", False):
        edr += 0.31; notes.append("momentum(+0.31)")
    # 2) Multi-Scale Nesting +0.30 if fractal depth >= 9
    if context.get("fractal_depth", 0) >= 9:
        edr += 0.30; notes.append("multiscale_nesting(+0.30)")
    # 3) Stochastic Injection +0.28 if enable_creative_noise
    if context.get("creative_noise", False):
        edr += 0.28; notes.append("stochastic(+0.28)")
    # 4) Anticipatory Seeding +0.27 if anticipation high
    if context.get("ant_conf", 0.0) >= 0.85:
        edr += 0.27; notes.append("anticipatory_seeds(+0.27)")
    # 5) Phase Catalysts +0.26 if near threshold
    if context.get("near_phase", False):
        edr += 0.26; notes.append("phase_catalyst(+0.26)")
    edr = clamp(edr, 0.0, 1.60)  # keep bounded
    return edr, notes
