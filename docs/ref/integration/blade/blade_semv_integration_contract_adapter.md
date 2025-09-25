# Blade ↔ SEMV Integration

This canvas captures the integration contract between **Blade Next** and **SEMV (Python rebuild)**, plus a ready‑to‑use Blade adapter module. It enables:

- SEMV as the *project version authority* (commit‑label bumping, guards, highest‑wins, build cursor).
- Blade to consume SEMV via **library API** first, **CLI JSON** second, and a safe **heuristic fallback** if SEMV is absent.
- Zero hard dependency on Boxy; pretty output when available, plain text otherwise.

---

## A) Contract for SEMV (Python rebuild)

### A1. Library API surface (preferred)

Expose `semv.api` with the following dataclasses and functions. All functions are **pure** (no printing), returning data only:

```python
# semv/api.py — required public surface for Blade integration
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Literal

Authority = Literal["manual", "package", "git", "calculated"]
DriftCode = Literal[
    "aligned",
    "package_ahead",
    "git_ahead",
    "calculated_higher",
    "no_sources",
    "unknown",
]

@dataclass
class Guards:
    on_main: bool
    clean_tree: bool

@dataclass
class BuildCursor:
    dev_vers: Optional[str]
    dev_build: Optional[int]
    dev_branch: Optional[str]
    dev_date: Optional[str]
    dev_semver: Optional[str]
    sync_source: Optional[str]
    sync_version: Optional[str]
    sync_date: Optional[str]

@dataclass
class VersionSources:
    package_versions: Dict[str, str]
    git_tag: Optional[str]
    calculated: Optional[str]

@dataclass
class SemvState:
    project_types: List[str]
    version_files: List[str]
    versions: VersionSources
    authority: Authority
    target_version: Optional[str]
    drift: DriftCode
    guards: Guards
    build_cursor: Optional[BuildCursor]
    problems: List[str]

@dataclass
class PlanStep:
    kind: Literal["write_file", "create_tag", "push_tags", "noop"]
    target: str
    before: Optional[str]
    after: Optional[str]

@dataclass
class PlanResult:
    ok: bool
    message: str
    state: SemvState
    steps: List[PlanStep]

# detection & state

def detect_project_types(path: Path) -> List[str]: ...

def get_version_files(path: Path, project_types: List[str]) -> List[Path]: ...

def read_state(path: Path) -> SemvState: ...

def guards(path: Path) -> Guards: ...

# analysis & planning

def validate(path: Path) -> PlanResult: ...

def drift(path: Path) -> PlanResult: ...

def next_version(path: Path) -> str: ...

# mutations (atomic when dry_run=False)

def sync(path: Path, *, authority: Optional[Authority] = None, dry_run: bool = True, force: bool = False) -> PlanResult: ...

def bump(path: Path, *, bump: Optional[Literal["major","minor","patch"]] = None, dry_run: bool = True, force: bool = False) -> PlanResult: ...

def release(path: Path, *, dry_run: bool = False, force: bool = False) -> PlanResult: ...
```

**Behavioral invariants**
- *Highest version wins* across manual > package files > git tags > calculated.
- *Guards* respected: operations only on main/master with clean tree unless `force=True`.
- *Dev vs Release*: `target_version` is always a clean release semver; development/build cursor lives in `build_cursor`.
- *Atomic writes*: return `steps` plan; apply all or none when `dry_run=False`.

### A2. CLI JSON mode (fallback)

If only a `semv` binary is present, provide JSON for:

```
semv state --json
semv validate --json
semv drift --json
semv next --json
semv sync --json [--authority package|git|calculated] [--dry-run] [--force]
semv bump --json [--bump major|minor|patch] [--dry-run] [--force]
semv release --json [--dry-run] [--force]
```

The JSON maps 1‑to‑1 to `SemvState` / `PlanResult` above.

---

## B) Blade expectations & graceful degradation

- Prefer `import semv.api` → fast path.
- Else call `semv ... --json` → CLI path.
- Else compute **read‑only** state from: latest semver tag, manifest versions, naive commit‑label bump; disallow write ops and clearly message that sync/bump/release are unavailable.
- Boxy optional everywhere.

**Data model Blade expects**

```json
{
  "project_types": ["rust","javascript"],
  "version_files": ["Cargo.toml","package.json"],
  "versions": {
    "package_versions": {"Cargo.toml":"1.2.5","package.json":"1.2.1"},
    "git_tag": "v1.2.3",
    "calculated": "v1.2.6"
  },
  "authority": "package",
  "target_version": "v1.2.5",
  "drift": "package_ahead",
  "guards": {"on_main": true, "clean_tree": true},
  "build_cursor": {
    "dev_vers":"v1.2.5",
    "dev_build":1247,
    "dev_branch":"main",
    "dev_date":"08/15/25",
    "dev_semver":"v1.2.6-dev_2",
    "sync_source":"cargo",
    "sync_version":"1.2.5",
    "sync_date":"2025-08-15T10:30:00Z"
  },
  "problems": []
}
```

---

## C) Blade adapter (drop‑in module)

> **Path suggestion**: `blade_next/integrations/semv_adapter.py`

This module negotiates capability (lib → CLI → heuristic) and exposes a uniform API to Blade commands (`status`, `drift`, `sync`, `bump`, `release`).

```python
# blade_next/integrations/semv_adapter.py
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Literal, Tuple

Authority = Literal["manual", "package", "git", "calculated"]
DriftCode = Literal[
    "aligned",
    "package_ahead",
    "git_ahead",
    "calculated_higher",
    "no_sources",
    "unknown",
]

@dataclass
class Guards:
    on_main: bool
    clean_tree: bool

@dataclass
class BuildCursor:
    dev_vers: Optional[str] = None
    dev_build: Optional[int] = None
    dev_branch: Optional[str] = None
    dev_date: Optional[str] = None
    dev_semver: Optional[str] = None
    sync_source: Optional[str] = None
    sync_version: Optional[str] = None
    sync_date: Optional[str] = None

@dataclass
class VersionSources:
    package_versions: Dict[str, str]
    git_tag: Optional[str]
    calculated: Optional[str]

@dataclass
class SemvState:
    project_types: List[str]
    version_files: List[str]
    versions: VersionSources
    authority: Authority
    target_version: Optional[str]
    drift: DriftCode
    guards: Guards
    build_cursor: Optional[BuildCursor]
    problems: List[str]

@dataclass
class PlanStep:
    kind: Literal["write_file", "create_tag", "push_tags", "noop"]
    target: str
    before: Optional[str]
    after: Optional[str]

@dataclass
class PlanResult:
    ok: bool
    message: str
    state: SemvState
    steps: List[PlanStep]

@dataclass
class Capabilities:
    lib: bool
    cli: bool
    boxy: bool

# ---- capability detection ----------------------------------------------------

def _has_cli() -> bool:
    try:
        subprocess.run(["semv", "--version"], capture_output=True, text=True, timeout=2)
        return True
    except Exception:
        return False


def _has_lib() -> Tuple[bool, Optional[object]]:
    try:
        import importlib
        mod = importlib.import_module("semv.api")
        return True, mod
    except Exception:
        return False, None


def _detect_boxy() -> bool:
    try:
        import shutil
        return shutil.which("boxy") is not None
    except Exception:
        return False


def detect_capabilities() -> Capabilities:
    has_lib, _ = _has_lib()
    has_cli = _has_cli()
    return Capabilities(lib=has_lib, cli=has_cli, boxy=_detect_boxy())

# ---- public adapter API ------------------------------------------------------

def read_state(repo: Path) -> SemvState:
    has_lib, lib = _has_lib()
    if has_lib and lib:
        return _state_from_json_obj(asdict(lib.read_state(repo)))
    if _has_cli():
        obj = _run_cli_json(repo, ["semv", "state", "--json"])
        if obj:
            return _state_from_json_obj(obj)
    return _heuristic_state(repo)


def validate(repo: Path) -> PlanResult:
    has_lib, lib = _has_lib()
    if has_lib and lib:
        return _plan_from_json_obj(asdict(lib.validate(repo)))
    if _has_cli():
        obj = _run_cli_json(repo, ["semv", "validate", "--json"])
        if obj:
            return _plan_from_json_obj(obj)
    return PlanResult(ok=True, message="SEMV unavailable: read-only validation", state=_heuristic_state(repo), steps=[])


def drift(repo: Path) -> PlanResult:
    has_lib, lib = _has_lib()
    if has_lib and lib:
        return _plan_from_json_obj(asdict(lib.drift(repo)))
    if _has_cli():
        obj = _run_cli_json(repo, ["semv", "drift", "--json"])
        if obj:
            return _plan_from_json_obj(obj)
    return PlanResult(ok=True, message="SEMV unavailable: heuristic drift view", state=_heuristic_state(repo), steps=[])


def sync(repo: Path, *, authority: Optional[Authority] = None, dry_run: bool = True, force: bool = False) -> PlanResult:
    has_lib, lib = _has_lib()
    if has_lib and lib:
        return _plan_from_json_obj(asdict(lib.sync(repo, authority=authority, dry_run=dry_run, force=force)))
    if _has_cli():
        cmd = ["semv", "sync", "--json"]
        if authority: cmd += ["--authority", authority]
        if dry_run:   cmd += ["--dry-run"]
        if force:     cmd += ["--force"]
        obj = _run_cli_json(repo, cmd)
        if obj:
            return _plan_from_json_obj(obj)
    return PlanResult(ok=False, message="SEMV unavailable: sync not supported (read-only mode)", state=_heuristic_state(repo), steps=[])


def bump(repo: Path, *, bump: Optional[Literal["major","minor","patch"]] = None, dry_run: bool = True, force: bool = False) -> PlanResult:
    has_lib, lib = _has_lib()
    if has_lib and lib:
        return _plan_from_json_obj(asdict(lib.bump(repo, bump=bump, dry_run=dry_run, force=force)))
    if _has_cli():
        cmd = ["semv", "bump", "--json"]
        if bump:      cmd += ["--bump", bump]
        if dry_run:   cmd += ["--dry-run"]
        if force:     cmd += ["--force"]
        obj = _run_cli_json(repo, cmd)
        if obj:
            return _plan_from_json_obj(obj)
    return PlanResult(ok=False, message="SEMV unavailable: bump not supported (read-only mode)", state=_heuristic_state(repo), steps=[])


def release(repo: Path, *, dry_run: bool = False, force: bool = False) -> PlanResult:
    has_lib, lib = _has_lib()
    if has_lib and lib:
        return _plan_from_json_obj(asdict(lib.release(repo, dry_run=dry_run, force=force)))
    if _has_cli():
        cmd = ["semv", "release", "--json"]
        if dry_run: cmd += ["--dry-run"]
        if force:   cmd += ["--force"]
        obj = _run_cli_json(repo, cmd)
        if obj:
            return _plan_from_json_obj(obj)
    return PlanResult(ok=False, message="SEMV unavailable: release not supported (read-only mode)", state=_heuristic_state(repo), steps=[])

# ---- helpers -----------------------------------------------------------------

def _run_cli_json(repo: Path, cmd: List[str]) -> Optional[dict]:
    try:
        cp = subprocess.run(cmd, cwd=repo, capture_output=True, text=True, timeout=60)
        if cp.returncode != 0:
            return None
        raw = cp.stdout.strip()
        first, last = raw.find("{"), raw.rfind("}")
        payload = raw[first:last+1] if (first != -1 and last != -1) else raw
        return json.loads(payload)
    except Exception:
        return None


def _state_from_json_obj(d: dict) -> SemvState:
    vs = d.get("versions", {})
    versions = VersionSources(
        package_versions = vs.get("package_versions", {}) or {},
        git_tag          = vs.get("git_tag"),
        calculated       = vs.get("calculated"),
    )
    guards = Guards(**d.get("guards", {"on_main": False, "clean_tree": False}))
    bc_d = d.get("build_cursor")
    bc = BuildCursor(**bc_d) if isinstance(bc_d, dict) else None
    return SemvState(
        project_types = d.get("project_types", []),
        version_files = d.get("version_files", []),
        versions      = versions,
        authority     = d.get("authority", "unknown"),
        target_version= d.get("target_version"),
        drift         = d.get("drift", "unknown"),
        guards        = guards,
        build_cursor  = bc,
        problems      = d.get("problems", []),
    )


def _plan_from_json_obj(d: dict) -> PlanResult:
    st = _state_from_json_obj(d.get("state", {}))
    steps = [
        PlanStep(
            kind   = s.get("kind","noop"),
            target = s.get("target",""),
            before = s.get("before"),
            after  = s.get("after"),
        ) for s in d.get("steps", [])
    ]
    return PlanResult(ok=bool(d.get("ok", False)), message=d.get("message",""), state=st, steps=steps)

# ---- heuristic, read‑only fallback ------------------------------------------

def _heuristic_state(repo: Path) -> SemvState:
    pt = _detect_project_types_quick(repo)
    files = _guess_version_files(repo, pt)
    pkg_versions = _read_versions_quick(repo, files)
    git_tag = _latest_git_semver(repo)
    calc = _naive_calculated(repo, git_tag)
    authority, target, drift = _highest_wins(pkg_versions, git_tag, calc)
    guards = Guards(on_main=_is_main(repo), clean_tree=_is_clean(repo))
    return SemvState(
        project_types = pt,
        version_files = [str(p) for p in files],
        versions      = VersionSources(pkg_versions, git_tag, calc),
        authority     = authority,  # type: ignore
        target_version= target,
        drift         = drift,      # type: ignore
        guards        = guards,
        build_cursor  = None,
        problems      = [],
    )

# minimal detection/parsing utils (kept conservative)

def _detect_project_types_quick(repo: Path) -> List[str]:
    types: List[str] = []
    if (repo / "Cargo.toml").exists(): types.append("rust")
    if (repo / "package.json").exists(): types.append("javascript")
    if (repo / "pyproject.toml").exists() or (repo / "setup.py").exists(): types.append("python")
    if not types and any(repo.glob("*.sh")): types.append("bash")
    return types or ["unknown"]


def _guess_version_files(repo: Path, pt: List[str]) -> List[Path]:
    files: List[Path] = []
    if "rust" in pt and (repo / "Cargo.toml").exists(): files.append(repo / "Cargo.toml")
    if "javascript" in pt and (repo / "package.json").exists(): files.append(repo / "package.json")
    if "python" in pt:
        if (repo / "pyproject.toml").exists(): files.append(repo / "pyproject.toml")
        elif (repo / "setup.py").exists():    files.append(repo / "setup.py")
    return files


def _read_versions_quick(repo: Path, files: List[Path]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for f in files:
        try:
            if f.name == "Cargo.toml":
                for line in f.read_text(encoding="utf-8").splitlines():
                    if line.strip().startswith("version"):
                        out[str(f.name)] = line.split("=",1)[1].strip().strip('"')
                        break
            elif f.name == "package.json":
                import json as _json
                v = _json.loads(f.read_text(encoding="utf-8")).get("version")
                if v: out[str(f.name)] = v
            elif f.name == "pyproject.toml":
                for line in f.read_text(encoding="utf-8").splitlines():
                    if line.strip().startswith("version"):
                        out[str(f.name)] = line.split("=",1)[1].strip().strip('"')
                        break
            elif f.name == "setup.py":
                for line in f.read_text(encoding="utf-8").splitlines():
                    if "version=" in line:
                        out[str(f.name)] = (
                            line.split("version=",1)[1].split(",")[0].strip().strip('"').strip("'")
                        )
                        break
        except Exception:
            pass
    return out


def _latest_git_semver(repo: Path) -> Optional[str]:
    try:
        cp = subprocess.run(["git", "tag"], cwd=repo, capture_output=True, text=True, timeout=5)
        if cp.returncode != 0:
            return None
        tags = [t for t in cp.stdout.splitlines() if _looks_semver(t)]
        return sorted(tags, key=_semver_sort_key)[-1] if tags else None
    except Exception:
        return None


def _is_main(repo: Path) -> bool:
    try:
        cp = subprocess.run(["git","branch","--show-current"], cwd=repo, capture_output=True, text=True, timeout=3)
        return cp.stdout.strip() in ("main","master")
    except Exception:
        return False


def _is_clean(repo: Path) -> bool:
    try:
        cp = subprocess.run(["git","diff","--exit-code"], cwd=repo)
        return cp.returncode == 0
    except Exception:
        return False


def _looks_semver(tag: str) -> bool:
    import re
    return re.match(r"^v?\d+\.\d+\.\d+([\-+].+)?$", tag) is not None


def _semver_sort_key(tag: str):
    tag = tag.lstrip("v")
    a,b,c = (int(x) for x in tag.split("-")[0].split(".")[:3])
    return (a,b,c)


def _naive_calculated(repo: Path, since_tag: Optional[str]) -> Optional[str]:
    if not since_tag:
        return None
    try:
        cp = subprocess.run(["git","log","--pretty=format:%s", f"{since_tag}..HEAD"], cwd=repo, capture_output=True, text=True, timeout=5)
        msgs = [m.strip().lower() for m in cp.stdout.splitlines()]
        def has(prefixes):
            return any(m.startswith(p + ":") for p in prefixes for m in msgs)
        major = has(["major","breaking","api"])
        minor = has(["feat","feature","add","minor"])
        patch = has(["fix","patch","bug","hotfix","up"])
        if not (major or minor or patch):
            return None
        a,b,c = (int(x) for x in since_tag.lstrip("v").split(".")[:3])
        if major: a += 1; b=0; c=0
        elif minor: b += 1; c=0
        elif patch: c += 1
        return f"v{a}.{b}.{c}"
    except Exception:
        return None


def _highest_wins(pkg_versions: Dict[str,str], git_tag: Optional[str], calc: Optional[str]):
    def N(v: Optional[str]) -> Optional[str]:
        if not v: return None
        return v if v.startswith("v") else f"v{v}"
    versions = [N(git_tag), *(N(v) for v in (pkg_versions or {}).values()), N(calc)]
    versions = [v for v in versions if v]
    if not versions:
        return "calculated", None, "no_sources"
    best = sorted(set(versions), key=_semver_sort_key)[-1]
    src = {
        "git": N(git_tag),
        "package": max([N(v) for v in pkg_versions.values()], key=_semver_sort_key) if pkg_versions else None,
        "calculated": N(calc),
    }
    if src["package"] == best:   auth = "package"
    elif src["git"] == best:     auth = "git"
    else:                          auth = "calculated"
    drift = "aligned"
    if src["package"] == best and src["git"] and src["git"] != best:
        drift = "package_ahead"
    elif src["git"] == best and src["package"] and src["package"] != best:
        drift = "git_ahead"
    elif src["calculated"] == best and best not in (src["git"], src["package"]):
        drift = "calculated_higher"
    return auth, best, drift
```

---

## D) Notes for SEMV devs

1) Keep existing behavior: commit‑label bumping (with colon suffix), guards (main/master, clean tree), highest‑wins, build cursor.

2) Library first (`semv.api`), CLI `--json` second. No Boxy required for Blade.

3) Atomic ops: return `PlanResult.steps`; on `dry_run=False` ensure all‑or‑nothing.

4) Detection should cover Rust/JS/Python/Bash with the same patterns SEMV Bash recognizes.

---

## E) Blade UX hooks (summary)

- `blade status` → adds Version Drift counters from `SemvState.drift`.
- `blade drift` → panel with authority, target, guards, build cursor.
- `blade sync|bump|release` → routed through adapter; if SEMV missing, print clear read‑only message.

---

**End of canvas.**

