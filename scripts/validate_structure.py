# scripts/validate_structure.py
from pathlib import Path

SPEC_SCOPE = {
    "domain.spec.md": "src/aitechpioneer/domain",
    "application.spec.md": "src/aitechpioneer/application",
    "infrastructure.spec.md": "src/aitechpioneer/infrastructure",
    "interfaces.spec.md": "src/aitechpioneer/interfaces",
}

for spec, path in SPEC_SCOPE.items():
    if not Path(path).exists():
        raise RuntimeError(f"{spec} requires {path}")
