# interface.py (portable memory + optional --memdir override)
from __future__ import annotations
import argparse, json, shlex
from core import AGIEngine

BANNER = r"""
┌─────────────────────────────────────────────────────────────┐
│           A G I / A S I   I N T E R A C T I V E            │
│                 Type 'help' to get started                  │
└─────────────────────────────────────────────────────────────┘
"""

HELP = r"""
Commands:
  help                     Show this help.
  modes                    List available modes.
  use <mode>               Switch active mode (e.g., 'use phase').
  run k=v [k=v ...]        Run the active mode with key=value args (no newlines).
                           Examples:
                             run text="loop neither however" high_sigma_hits=3
                             run coherence=0.55 entropy=0.65
                             run amplitudes="0.25,0.25,0.25,0.25" evidence=0.8
                             run candidates='[{"ECT":1.1,"CEM":0.8,"EDR":2.2,"SIGMA":1.9}]'
  status                   Print engine status summary.
  config k=v               Set a config value (persisted).
  save                     Force-save all memory files now.
  exit / quit              Leave the program.
"""

def parse_kv(parts):
    args = {}
    for p in parts:
        if "=" not in p: continue
        k, v = p.split("=",1)
        v = v.strip()
        if len(v)>=2 and ((v[0]=="'" and v[-1]=="'") or (v[0]=='"' and v[-1]=='"')):
            v = v[1:-1]
        try:
            args[k] = json.loads(v)
        except Exception:
            args[k] = v
    return args

def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--memdir", type=str, default=None, help="Override memory directory (default: ./memory)")
    args = ap.parse_args()

    eng = AGIEngine(seed=args.seed, base_dir=args.memdir)
    print(BANNER)
    print("Config:", {"sigma_target": eng.config.get("sigma_target"),
                       "immune_leniency": eng.config.get("immune_leniency"),
                       "persist_dir": eng.config.get("persist_dir","memory"),
                       "enable_alien": eng.config.get("enable_alien"),
                       "memdir": eng.status().get("memdir")})
    print(eng.set_mode("immune"))

    while True:
        try:
            line = input(f"({eng.mode}) > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye."); break
        if not line: continue
        parts = shlex.split(line)
        cmd = parts[0].lower()

        if cmd in ("exit","quit"):
            print("Saving state..."); eng.save_all(); print("Bye."); break
        elif cmd == "help":
            print(HELP)
        elif cmd == "modes":
            print("Modes:", ", ".join(eng.list_modes()))
        elif cmd == "use" and len(parts)>=2:
            print(eng.set_mode(parts[1]))
        elif cmd == "run":
            kv = parse_kv(parts[1:])
            out = eng.run(**kv)
            print(json.dumps(out["result"], indent=2))
            print(json.dumps(out["metrics"], indent=2))
        elif cmd == "status":
            print(json.dumps(eng.status(), indent=2))
        elif cmd == "config" and len(parts)>=2:
            kv = parse_kv(parts[1:])
            for k,v in kv.items():
                try:
                    if isinstance(v,str) and v.replace(".","",1).isdigit():
                        v = float(v) if "." in v else int(v)
                except Exception: pass
                eng.config[k]=v
            eng.save_all(); print("Config updated:", kv)
        elif cmd == "save":
            eng.save_all(); print("Saved.")
        else:
            print("Unknown command. Type 'help'.")

if __name__ == "__main__":
    main()
