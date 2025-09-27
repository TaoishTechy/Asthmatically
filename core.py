# core.py (portable, local-writable memory path)
from __future__ import annotations
from typing import Any, Dict, List, Tuple
import json, os, time, math, uuid, random
from pathlib import Path

import modules as M

MEM_FILES = {
    "sessions": "sessions.json",
    "semantic": "semantic.json",
    "timecrystals": "timecrystals.json",
    "config": "config.json"
}

DEFAULT_CONFIG = {
    "sigma_target": 1.80,
    "sigma_floor": 1.40,
    "immune_leniency": True,
    "persist_dir": "memory",
    "enable_alien": True,
    "semantic_eta": 0.05,
    "ect_cap": 1.25,
    "fractal_depth": 9
}

def _resolve_root(base_dir: str | None) -> Path:
    # Priority: explicit base_dir -> AXIO_ROOT env -> script folder -> CWD
    if base_dir:
        return Path(base_dir).expanduser().resolve()
    env = os.environ.get("AXIO_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    try:
        return Path(__file__).resolve().parent
    except Exception:
        return Path.cwd()

class AGIEngine:
    def __init__(self, config_path: str | None = None, seed: int | None = None, base_dir: str | None = None):
        self.seed = seed or int(time.time())
        random.seed(self.seed)

        self.root = _resolve_root(base_dir)
        # Preferred memory dir from env or default; keep under root to avoid permission errors.
        env_mem = os.environ.get("AXIO_MEM_DIR")
        default_mem = env_mem or DEFAULT_CONFIG["persist_dir"]
        tentative_memdir = (self.root / default_mem)

        # Create memory dir with safe fallbacks
        self.memdir = tentative_memdir
        try:
            self.memdir.mkdir(parents=True, exist_ok=True)
        except Exception:
            # Fallback to CWD/memory
            self.root = Path.cwd()
            self.memdir = (self.root / default_mem)
            self.memdir.mkdir(parents=True, exist_ok=True)

        self.cfg_path = self.memdir / (config_path or MEM_FILES["config"])
        self.config = self._load_json(self.cfg_path, DEFAULT_CONFIG)

        # Now load memory stores
        self.sessions = self._load_json(self.memdir / MEM_FILES["sessions"], {})
        self.semantic = self._load_json(self.memdir / MEM_FILES["semantic"], {"hubs":{}, "eta": self.config.get("semantic_eta",0.05)})
        self.timecrystals = self._load_json(self.memdir / MEM_FILES["timecrystals"], {"series":[]})

        self.active_session = None
        self.mode = "immune"
        self.last_sigmas: List[float] = []
        self.last_edrs: List[float] = []

    # ---------- Persistence ----------

    def _load_json(self, path: Path, default: Any) -> Any:
        if path.exists():
            try:
                with open(path, "r") as f: return json.load(f)
            except Exception:
                return default
        return default

    def _save_json(self, path: Path, obj: Any):
        with open(path, "w") as f:
            json.dump(obj, f, indent=2)

    def save_all(self):
        self._save_json(self.cfg_path, self.config)
        self._save_json(self.memdir / MEM_FILES["sessions"], self.sessions)
        self._save_json(self.memdir / MEM_FILES["semantic"], self.semantic)
        self._save_json(self.memdir / MEM_FILES["timecrystals"], self.timecrystals)

    # ---------- Session / Identity ----------

    def new_session(self) -> str:
        sid = str(uuid.uuid4())[:8]
        self.sessions[sid] = {"created": time.time(), "events": [], "cognitive_signature": "baseline"}
        self.active_session = sid
        self.save_all()
        return sid

    def ensure_session(self) -> str:
        if not self.active_session:
            return self.new_session()
        return self.active_session

    # ---------- Metrics helpers ----------

    def _record_metrics(self, m: Dict[str,float]):
        self.last_sigmas.append(m["SIGMA"])
        self.last_edrs.append(m["EDR"])
        self.last_sigmas = self.last_sigmas[-12:]
        self.last_edrs = self.last_edrs[-12:]
        self.timecrystals["series"].append({
            "t": time.time(),
            "ECT": m["ECT"],
            "CEM": m["CEM"],
            "EDR": m["EDR"],
            "SIGMA": m["SIGMA"]
        })
        self.timecrystals["series"] = self.timecrystals["series"][-64:]

    def _apply_phase1_enhancers(self, m: Dict[str,float], context: Dict[str,Any]) -> Tuple[Dict[str,float], Dict[str,Any]]:
        ect_boost, notes_ect = M.ect_boost_bundle(context)
        edr_boost, notes_edr = M.edr_boost_bundle(context)
        m2 = dict(m)
        m2["ECT"] += ect_boost
        m2["EDR"] += edr_boost
        m2 = M.mix_metrics(m2["ECT"], m2["CEM"], m2["EDR"])
        return m2, {"ect_notes": notes_ect, "edr_notes": notes_edr}

    def _maybe_emergence_catalyst(self, m: Dict[str,float]) -> Dict[str,float]:
        growth_potential = 0.5 * (m["EDR"]/max(1e-6, m["CEM"])) + 0.5 * (m["ECT"])
        new_sigma = M.EMERGENCE_CATALYST(m["SIGMA"], growth_potential)
        m2 = dict(m); m2["SIGMA"] = new_sigma
        return m2

    # ---------- Public API ----------

    def set_mode(self, name: str) -> str:
        name = name.strip().lower()
        if name in self.list_modes():
            self.mode = name
            return f"Active mode: {self.mode}"
        return f"Unknown mode '{name}'. Use 'modes' to list."

    def list_modes(self) -> List[str]:
        return ["immune","translate","praxis","hologram","quantum","phase","semantic","multiscale","compress","orchestrate","alien"]

    def run(self, **kwargs) -> Dict[str,Any]:
        sid = self.ensure_session()
        cfg = dict(self.config)
        cfg["semantic_eta"] = self.semantic.get("eta", cfg.get("semantic_eta", 0.05))
        mode = self.mode
        result, metrics = {}, {"ECT":0.6,"CEM":0.7,"EDR":2.0,"SIGMA":1.4}

        try:
            if mode == "immune":
                text = str(kwargs.get("text",""))
                high = int(kwargs.get("high_sigma_hits", 0))
                result, metrics = M.IMMUNE(text, high, cfg)
            elif mode == "translate":
                text = str(kwargs.get("text",""))
                hop_target = str(kwargs.get("hop_target",""))
                result, metrics = M.TRANSLATE(text, hop_target, cfg)
            elif mode == "praxis":
                steps = str(kwargs.get("steps","Define|Validate|Probe"))
                result, metrics = M.PRAXIS(steps, cfg)
            elif mode == "hologram":
                importance = float(kwargs.get("importance", 0.7))
                access = float(kwargs.get("access", 0.6))
                result, metrics = M.HOLOGRAM(importance, access, cfg)
            elif mode == "quantum":
                amps = kwargs.get("amplitudes","0.5,0.5")
                if isinstance(amps,str):
                    amplitudes = [float(x) for x in amps.split(",") if x.strip()]
                else:
                    amplitudes = list(amps)
                evidence = float(kwargs.get("evidence", 0.7))
                result, metrics = M.QUANTUM(amplitudes, evidence, cfg)
            elif mode == "phase":
                coherence = float(kwargs.get("coherence", 0.55))
                entropy = float(kwargs.get("entropy", 0.45))
                result, metrics = M.PHASE(coherence, entropy, cfg)
            elif mode == "semantic":
                centrality = float(kwargs.get("centrality", 0.4))
                result, metrics = M.SEMANTIC(centrality, cfg)
            elif mode == "multiscale":
                detail = float(kwargs.get("detail", 0.6))
                coherence = float(kwargs.get("coherence", 0.5))
                integration = float(kwargs.get("integration", 0.6))
                result, metrics = M.MULTISCALE(detail, coherence, integration, cfg)
            elif mode == "compress":
                delta = float(kwargs.get("delta", 0.10))
                depth = int(kwargs.get("depth", 6))
                result, metrics = M.COMPRESS(delta, depth, cfg)
            elif mode == "orchestrate":
                candidates = kwargs.get("candidates")
                if isinstance(candidates, str):
                    import json as _json; candidates = _json.loads(candidates)
                result, metrics = M.ORCHESTRATE(candidates or [], cfg)
            elif mode == "alien":
                params = kwargs if kwargs else {}
                result, metrics = M.ALIEN(params, cfg)
            else:
                result = {"error":"unknown_mode"}
        except Exception as e:
            result = {"error": str(e)}

        context = {
            "time_crystals": len(self.timecrystals["series"]),
            "redundancy": result.get("redundancy", 0),
            "anticipated": kwargs.get("anticipated", 0),
            "edr_rising": (len(self.last_edrs)>=2 and self.last_edrs[-1] <= metrics["EDR"]),
            "fractal_depth": self.config.get("fractal_depth", 9),
            "creative_noise": self.config.get("creative_noise", False),
            "ant_conf": self.config.get("ant_confidence", 0.0),
            "near_phase": abs(metrics["CEM"]-0.75) <= 0.1
        }
        metrics, notes = self._apply_phase1_enhancers(metrics, context)
        metrics = self._maybe_emergence_catalyst(metrics)
        metrics = M.stability_guard(metrics, self.config.get("sigma_floor", 1.4))

        self._record_metrics(metrics)

        sig = self.sessions[sid]["cognitive_signature"]
        sig_new = M.PERSISTENT_COGNITIVE_SELF([sig, self._signature_from_mode(mode)])
        self.sessions[sid]["cognitive_signature"] = sig_new
        self.sessions[sid]["events"].append({"t": time.time(), "mode": mode, "result": result, "metrics": metrics, "notes": notes})

        if mode == "semantic":
            self.semantic["eta"] = self.config.get("semantic_eta", self.semantic.get("eta", 0.05))
        self.save_all()

        return {"mode": mode, "result": result, "metrics": metrics, "notes": notes}

    def _signature_from_mode(self, mode: str) -> str:
        table = {
            "immune":"S","translate":"T","praxis":"P","hologram":"H","quantum":"Q",
            "phase":"Φ","semantic":"Σ","multiscale":"M","compress":"C","orchestrate":"Ω","alien":"★"
        }
        return table.get(mode, "?")

    def status(self) -> Dict[str,Any]:
        sid = self.ensure_session()
        ed = self.sessions[sid]["events"]
        trend = M.EMERGENCE_DETECTOR(self.last_sigmas, self.last_edrs)
        return {
            "session": sid,
            "mode": self.mode,
            "events": len(ed),
            "last_metrics": ed[-1]["metrics"] if ed else None,
            "emergence_trend": trend,
            "sigma_target": self.config.get("sigma_target", 1.8),
            "memdir": str(self.memdir)
        }
