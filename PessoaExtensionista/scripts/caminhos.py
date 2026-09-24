"""Caminhos centrais das bases do ifes-serra-lab (NFR02 — US-002)."""

from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
BASES = RAIZ / "bases"
SRC = BASES / "SRC"
EXTENSIONISTAS_INDEX = SRC / "api" / "extensionistas" / "index.json"
ATIVIDADES = SRC / "api" / "atividades"
ACOES = SRC / "api" / "acoes"
HORIZON = BASES / "horizon"
RESEARCHERS_CANONICAL = HORIZON / "researchers_canonical.parquet"
OUTPUT = RAIZ / "output"
