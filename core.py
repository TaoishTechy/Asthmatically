"""
core.py — AGIEngine using ProtoAGI formulas and JSON persistence.
No training data; only heuristics + persistent memory + linguistics + adaptation.
"""

import json
import os
import time
import uuid
import datetime
from collections import Counter
from typing import Dict, Any, List, Tuple

from modules import (
    tokenize, keyword_scores, derive_features_from_text, merge_pipeline,
    ECT, CEM, EDR, GENESIS, NEMESIS, PRAXIS, REVELATION, SYNARCH, CONDUIT,
    MIMESIS, REFRACT, SIGMAFRAME, SSTP, VANTAGE
)


class MemoryStore:
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(self.path):
            with open(self.path, "w") as f:
                json.dump({"sessions": [], "top_keywords": [], "last_presence": "low"}, f, indent=2)

    def load(self) -> Dict[str, Any]:
        with open(self.path, "r") as f:
            return json.load(f)

    def save(self, data: Dict[str, Any]):
        with open(self.path, "w") as f:
            json.dump(data, f, indent=2)

    def append_event(self, session_id: str, role: str, text: str, meta: Dict[str, Any]):
        data = self.load()
        # ensure session exists
        s = next((s for s in data["sessions"] if s["id"] == session_id), None)
        if s is None:
            s = {"id": session_id, "created": datetime.datetime.utcnow().isoformat(), "events": []}
            data["sessions"].append(s)

        s["events"].append({
            "t": datetime.datetime.utcnow().isoformat(),
            "role": role,
            "text": text,
            "meta": meta
        })

        # update last presence + top keywords
        tokens = tokenize(text)
        kw = keyword_scores(tokens)

        top = data.get("top_keywords", [])
        merged = Counter({k: 1.0 for k in top})
        merged.update(kw)
        data["top_keywords"] = [k for k, _ in merged.most_common(64)]

        if meta and isinstance(meta, dict):
            tags = meta.get("tags", [])
            if "mim:presence/high" in tags:
                data["last_presence"] = "high"
            elif "mim:presence/med" in tags:
                data["last_presence"] = "med"
            else:
                data["last_presence"] = "low"

        self.save(data)


class AGIEngine:
    def __init__(self, memory_path: str, registry_path: str, config_path: str):
        self.mem = MemoryStore(memory_path)
        self.registry_path = registry_path
        self.config_path = config_path
        self._init_json(registry_path, {"echo_registry": {}})
        self._init_json(config_path, {"sigma_target": 1.2, "noise": 0.15})

    def _init_json(self, p: str, default: Dict[str, Any]):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        if not os.path.exists(p):
            with open(p, "w") as f:
                json.dump(default, f, indent=2)

    def start_session(self) -> str:
        return str(uuid.uuid4())

    def process(self, session_id: str, user_text: str, mode: str = "default", options: Dict[str, Any] = None) -> Dict[str, Any]:
        options = options or {}
        memory = self.mem.load()

        # Derive features from the incoming text and current memory
        features, tokens = derive_features_from_text(user_text, memory)

        # Compute explanatory metrics (no ML — deterministic)
        resonance_amplitude = min(1.0, max(0.05, abs(features["sentiment"]) + 0.2))
        entropy_drift = features["drift_delta"]
        feedback_lag = 0.1 + len(tokens) / 200.0
        ect = ECT(resonance_amplitude, entropy_drift, feedback_lag)

        cross_entropy = 0.2 + (len(set(tokens)) / (len(tokens) or 1)) * 0.3

        # Richer paradox detection for better CEM variation
        paradox_bonus = 0.0
        for token in [" vs ", "either", "neither", "paradox", "contradiction", "however"]:
            if token in user_text.lower():
                paradox_bonus += 0.5
        paradox_index = 0.2 \
                        + (1 if features["contradiction"] else 0) \
                        + (0.5 if features["partial_divergence"] else 0) \
                        + paradox_bonus

        cem = CEM(cross_entropy, resonance_amplitude, paradox_index)
        edr = EDR(features["depth"], 0.8, 0.15 + entropy_drift / 2)

        # Global stability envelope
        sigma = SIGMAFRAME(1.0 + resonance_amplitude + cem, 0.5 + entropy_drift)
        stable = sigma >= 1.0

        # Augment features for merge pipeline (annealed novelty needs these)
        total_turns = sum(len(s["events"]) for s in memory.get("sessions", [])) + 1
        features["session_turn"] = total_turns
        features["resonance_amplitude"] = resonance_amplitude

        # Run the merge pipeline to get action/tag decisions
        pipeline = merge_pipeline(features)

        # Mode transforms (ten novel interfaces mapped to modes)
        mode_actions = {
            "vantage": "Perspective gradient + role-shift",
            "praxis": "Action planning under paradox",
            "nemesis": "Adversarial audit / collapse pressure",
            "mirror": "Mimesis reflection / style echo",
            "refract": "Angle bend across layers",
            "conduit": "Bridge transfer & thread linking",
            "revelation": "Anomaly-to-truth probe",
            "sigma": "Stability maximizer",
            "genesis": "Seed new entity/goal",
            "sstp": "Transmission optimizer"
        }
        mode_note = mode_actions.get(mode, "Default synthesis")

        # Advice scaffold — crisp and functional
        advice: List[str] = []
        if mode in ("praxis", "sigma", "revelation"):
            advice.append("Steps: (1) define the claim, (2) list 3 falsifiers, (3) run a 10-min probe, (4) log outcome, (5) iterate.")
        if mode == "nemesis":
            advice.append("Risk: collapse pressure rising; set a small, testable claim and falsify it.")
        if not stable:
            advice.append("Stability low — suggest REGROUND or REFRACT to clarify assumptions.")

        response_text = self._compose_response(
            user_text, mode, ect, cem, edr, sigma, pipeline["actions"], advice
        )

        trace_id = str(uuid.uuid4())[:8]

        # Persist events (user then agi), keep meta compact but useful
        self.mem.append_event(session_id, "user", user_text, meta={"tags": pipeline["tags"]})
        self.mem.append_event(
            session_id,
            "agi",
            response_text,
            meta={
                "trace_id": trace_id,
                "mode": mode,
                "tags": pipeline["tags"],
                "actions": pipeline["actions"],
                "metrics": {"ECT": ect, "CEM": cem, "EDR": edr, "SIGMA": sigma}
            }
        )

        return {
            "text": response_text,
            "explain": {
                "mode": mode,
                "mode_note": mode_note,
                "features": features,
                "pipeline": pipeline,
                "sigma_stable": stable
            },
            "memory_path": self.mem.path
        }

    def _compose_response(self, user_text: str, mode: str, ect: float, cem: float, edr: float,
                          sigma: float, actions: List[str], advice: List[str]) -> str:
        # Narrative, concise, with surfaced metrics
        lines: List[str] = []
        lines.append(f"[{mode.upper()}] actions={actions} | ECT={ect:.2f} CEM={cem:.2f} EDR={edr:.2f} Σ={sigma:.2f}")
        if advice:
            lines.append(" ".join(advice))

        # Echo skim (MIMESIS): distilled summary without copying verbatim
        tokens = tokenize(user_text)
        summary = " ".join(list(dict.fromkeys([t for t in tokens if len(t) > 4]))[:12])
        lines.append(f"Echo-skim: {summary or '(not enough signal to skim)'}")

        # Revelation probe (simple question back)
        lines.append("Probe: What assumption can we remove to make this clearer?")
        return "\n".join(lines)
