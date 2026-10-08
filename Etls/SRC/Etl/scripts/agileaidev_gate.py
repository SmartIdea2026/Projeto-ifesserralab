#!/usr/bin/env python3
"""Capability-detecting gates for ScrumAIDev projects."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], cwd: Path = ROOT) -> int:
    print("+ " + " ".join(command))
    return subprocess.call(command, cwd=str(cwd))


def read_package_scripts(package_json: Path) -> set[str]:
    try:
        data = json.loads(package_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    scripts = data.get("scripts", {})
    return set(scripts) if isinstance(scripts, dict) else set()


def frontend_runner(frontend: Path) -> list[str]:
    if (frontend / "pnpm-lock.yaml").exists() and shutil.which("pnpm"):
        return ["pnpm", "--dir", str(frontend)]
    if (frontend / "yarn.lock").exists() and shutil.which("yarn"):
        return ["yarn", "--cwd", str(frontend)]
    return ["npm", "--prefix", str(frontend)]


def make_has_target(makefile: Path, target: str) -> bool:
    if not makefile.exists():
        return False
    try:
        lines = makefile.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return False
    prefixes = (f"{target}:", f".PHONY: {target}", f".PHONY:{target}")
    return any(line.startswith(prefixes) or f" {target}" in line for line in lines)


def run_standard_gate(gate: str) -> int:
    ran = False
    frontend = ROOT / "frontend"
    package_json = frontend / "package.json"

    if package_json.exists():
        ran = True
        scripts = read_package_scripts(package_json)
        if gate in scripts:
            return run([*frontend_runner(frontend), "run", gate])
        print(f"frontend/package.json found, but script '{gate}' is not defined. Skipping frontend {gate}.")

    backend_makefile = ROOT / "backend" / "Makefile"
    if backend_makefile.exists():
        ran = True
        if make_has_target(backend_makefile, gate):
            return run(["make", "-C", "backend", gate])
        print(f"backend/Makefile found, but target '{gate}' is not defined. Skipping backend {gate}.")
    elif (ROOT / "backend").exists():
        ran = True
        print(f"backend/ found, but no backend/Makefile exists. Skipping backend {gate}.")

    if not ran:
        print(f"No project stack detected yet: gate '{gate}' is not applicable until tooling is initialized.")
    return 0


def validate_contract() -> int:
    contracts = sorted((ROOT / "docs" / "contracts").glob("*.yaml"))
    if not contracts:
        print("No governed contracts found in docs/contracts/. Contract validation is not applicable yet.")
        return 0

    if shutil.which("spectral"):
        return run(["spectral", "lint", *map(str, contracts)])
    if shutil.which("redocly"):
        return run(["redocly", "lint", *map(str, contracts)])

    print("Contract YAML found, but no contract validator is configured.")
    print("Document the validator in docs/context.md to activate Level 3/4.")
    return 0


def test_contract() -> int:
    backend_makefile = ROOT / "backend" / "Makefile"
    contracts_makefile = ROOT / "contracts" / "Makefile"
    if make_has_target(backend_makefile, "test-contract"):
        return run(["make", "-C", "backend", "test-contract"])
    if make_has_target(contracts_makefile, "test-contract"):
        return run(["make", "-C", "contracts", "test-contract"])
    print("No executable contract test runner configured. Keep this as docs-only until the stack opts into Level 3/4.")
    return 0


def test_bdd() -> int:
    package_json = ROOT / "package.json"
    if package_json.exists() and "bdd" in read_package_scripts(package_json):
        return run(["npm", "run", "bdd"])

    frontend_package = ROOT / "frontend" / "package.json"
    if frontend_package.exists() and "bdd" in read_package_scripts(frontend_package):
        return run([*frontend_runner(ROOT / "frontend"), "run", "bdd"])

    backend_makefile = ROOT / "backend" / "Makefile"
    if make_has_target(backend_makefile, "test-bdd"):
        return run(["make", "-C", "backend", "test-bdd"])

    print("No executable BDD runner configured. docs/bdd/ remains a traceability artifact.")
    return 0


def test_mock() -> int:
    frontend = ROOT / "frontend"
    package_json = frontend / "package.json"
    if package_json.exists():
        scripts = read_package_scripts(package_json)
        for script in ("test:mock", "mock"):
            if script in scripts:
                return run([*frontend_runner(frontend), "run", script])
    print("No mock test runner configured. Add one only when the stack opts into executable contracts.")
    return 0


GATES = {
    "lint": run_standard_gate,
    "test": run_standard_gate,
    "typecheck": run_standard_gate,
    "build": run_standard_gate,
    "validate-contract": lambda _: validate_contract(),
    "test-contract": lambda _: test_contract(),
    "test-bdd": lambda _: test_bdd(),
    "test-mock": lambda _: test_mock(),
}


def main(argv: list[str]) -> int:
    gates = argv or ["lint", "test", "typecheck", "build"]
    for gate in gates:
        handler = GATES.get(gate)
        if handler is None:
            print(f"Unknown gate: {gate}", file=sys.stderr)
            return 2
        result = handler(gate)
        if result != 0:
            return result
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
