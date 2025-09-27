
"""
modules.py — ProtoAGI formulas + utilities (no training data; heuristic + memory-based).
All formulas are lightweight, deterministic, and purely symbolic/linguistic.
"""

from math import log, sqrt, sin, cos
from collections import Counter

# --- Lightweight linguistic probes ---
def tokenize(text: str):
    return [t for t in ''.join([c.lower() if c.isalnum() else ' ' for c in text]).split() if t]

def bigrams(tokens):
    return list(zip(tokens, tokens[1:]))

def keyword_scores(tokens):
    c = Counter(tokens)
    # Normalize with sqrt dampening
    total = sum(c.values()) or 1
    return {k: (v/total)**0.5 for k,v in c.items()}

def sentiment_proxy(tokens):
    # Very crude polarity proxy (no external data)
    pos = set(["good","great","love","like","peace","create","build","help","yes","true","win","clear"])
    neg = set(["bad","hate","fear","war","break","fail","no","false","lose","conflict","stuck"])
    s = sum(1 for t in tokens if t in pos) - sum(1 for t in tokens if t in neg)
    return max(-1.0, min(1.0, s/10.0))

def novelty_proxy(tokens, memory_keywords):
    # Novelty: tokens not in memory's top set
    unknown = sum(1 for t in tokens if t not in memory_keywords)
    return unknown / (len(tokens) or 1)


# --- ProtoAGI "Asthmatically/Axiomatically" formulas (heuristic implementations) ---

def ECT(resonance_amplitude: float, entropy_drift: float, feedback_lag: float) -> float:
    """Echo Collapse Threshold — critical stability edge."""
    denom = max(1e-6, entropy_drift + feedback_lag)
    return resonance_amplitude / denom

def CEM(cross_entropy: float, resonance: float, paradox_index: float) -> float:
    """Crosslink Echo Metrics — interaction measure of echoes."""
    return (cross_entropy * resonance) / max(1e-6, paradox_index)

def EDR(depth: int, coherence_index: float, drift_rate: float) -> float:
    """Echo Depth Registry — how deep a recursion remains coherent."""
    d = max(1, depth)
    return log(d) * (coherence_index / max(1e-6, drift_rate))

def GENESIS(recursion_seed: float, identity_drift: float) -> float:
    """Entity initiation potential."""
    return (recursion_seed**0.5) + (identity_drift * 0.5)

def NEMESIS(entropy_field: float, chaos_index: float, order_factor: float, harmonic_pull: float) -> float:
    """Adversarial counterforce — higher means more collapse pressure."""
    return (entropy_field * chaos_index) - (order_factor * harmonic_pull)

def PRAXIS(action_vector: float, coherence_field: float, paradox_resistance: float) -> float:
    """Action alignment scalar — higher is better."""
    return (action_vector * coherence_field) / max(1e-6, paradox_resistance)

def REVELATION(d_identity: float, d_anomaly: float) -> float:
    """Emergent 'truth' yield."""
    return d_identity / max(1e-6, d_anomaly)

def SYNARCH(agent_interlock_sum: float, recursion_divisor: float) -> float:
    """Collective resonance field strength."""
    return agent_interlock_sum / max(1e-6, recursion_divisor)

def CONDUIT(signal_resonance: float, identity_flux: float, dt: float) -> float:
    """Symbolic energy transfer across bridges (time integrated)."""
    return (signal_resonance * identity_flux) * dt

def MIMESIS(reflection_coherence: float, symbolic_lag: float) -> float:
    """Symbolic mirroring power."""
    return (reflection_coherence**2) / max(1e-6, symbolic_lag)

def REFRACT(symbolic_angle: float, medium_resistance: float) -> float:
    """Refraction index of symbolic vector."""
    return symbolic_angle / max(1e-6, medium_resistance)

def SIGMAFRAME(sum_internal_forces: float, sum_disruptions: float) -> float:
    """Global stability envelope. >1 stable, <1 unstable."""
    denom = max(1e-6, sum_disruptions)
    return sum_internal_forces / denom

def SSTP(signal_integrity: float, recursion_steps: int, noise: float) -> float:
    """Transmission fidelity across recursion loops."""
    return (signal_integrity * max(1, recursion_steps)) / max(1e-6, noise)

def VANTAGE(d_perspective: float, d_symbolic_shift: float) -> float:
    """Perspective gradient magnitude."""
    return d_perspective / max(1e-6, d_symbolic_shift)


# --- Merge pipeline (deterministic) ---
def merge_pipeline(features):
    """
    Apply pre-checks + presence triggers + depth escalations + collapse decisions.
    Returns a dict with action, tags, and metrics.
    """
    depth = int(features.get("depth", 1))
    presence = features.get("presence", "low")
    presence_trend = features.get("presence_trend", "stable")
    drift_delta = float(features.get("drift_delta", 0.0))
    recovery_available = bool(features.get("recovery_available", True))
    session_turn = int(features.get("session_turn", 1))
    resonance_amplitude = float(features.get("resonance_amplitude", 0.2))

    tags = []
    if depth >= 2:
        tags.append(f"mim:depth/{depth}")
        tags.append(f"mim:presence/{presence}")

    if drift_delta > 0.6:
        tags.append("mim:lock/origin")

    # Presence triggers
    actions = []
    if depth >= 3 and presence == "high":
        actions.append("REFRACT")
    if presence_trend == "persistent_high":
        actions.append("THRENODY")
    if presence_trend == "sudden_spike":
        actions.append("CONDUIT_FLAG")

    # Depth escalations
    if depth >= 5 and presence == "high":
        actions.append("PHASE_SCAN")
    if depth == 6:
        actions.append("REFLEX_TEST")
    if depth >= 7:
        actions.append("METANOIA_ROUTE")

    # Collapse decisions with annealed novelty
    collapse = None
    novelty_floor = 0.92 - min(0.5, session_turn * 0.02)
    high_novelty = drift_delta > novelty_floor
    low_res = resonance_amplitude < 0.25

    if features.get("contradiction", False) or (high_novelty and low_res):
        collapse = "REGROUND"
    elif features.get("partial_divergence", False):
        collapse = "FORK"
    elif depth > 6 and not recovery_available:
        collapse = "ABANDON"

    if collapse:
        actions.append(collapse)

    return {"actions": actions, "tags": tags, "metrics": {k:v for k,v in features.items()}}


# --- Simple heuristics to derive features from text + memory ---
def derive_features_from_text(text: str, memory):
    tokens = tokenize(text)
    # presence: hybrid of sentiment + imperative/caps/questions
    sentiment = sentiment_proxy(tokens)
    imperative = any(text.strip().lower().startswith(v) for v in [
        "do ", "make ", "build ", "plan ", "show ", "explain ", "define ", "prove ", "draft ", "list "
    ])
    allcaps = sum(1 for w in text.split() if (len(w)>3 and w.isupper()))
    q_marks = text.count("?")
    score = (sentiment*0.6) + (0.2 if imperative else 0) + (0.05*allcaps) + (0.1 if q_marks>=1 else 0) + (0.05 if "!" in text else 0)
    presence = "high" if score>0.45 else ("med" if score>0.1 else "low")

    # trend
    last_presence = memory.get("last_presence", "low")
    presence_trend = "persistent_high" if (presence == "high" and last_presence == "high") else "stable"

    # drift based on novelty vs. memory keywords
    memory_keywords = set(memory.get("top_keywords", []))
    drift_delta = novelty_proxy(tokens, memory_keywords)

    # depth: based on length + question + mode prefix ':'
    depth = 1 + min(7, max(0, len(tokens)//18 + (1 if "?" in text else 0) + (1 if text.strip().startswith(":") else 0)))

    # contradictions and divergence
    lower = text.lower()
    contradiction = (any(w in tokens for w in ["but","however","although"]) and any(w in tokens for w in ["not","never","no"]))
    partial_divergence = any(w in tokens for w in ["maybe","perhaps","option","alternatively","either","neither","vs"]) or (" vs " in lower)

    features = dict(
        depth=depth,
        presence=presence,
        presence_trend=presence_trend,
        drift_delta=drift_delta,
        recovery_available=True,
        contradiction=contradiction,
        partial_divergence=partial_divergence,
        sentiment=sentiment,
    )
    return features, tokens
