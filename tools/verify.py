from __future__ import annotations

import ast
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mapa_silencio.demo import build_demo_document
from mapa_silencio.validation import evaluate_detectors


def main() -> None:
    subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=ROOT,
        check=True,
    )
    external_imports = find_external_imports()
    if external_imports:
        raise SystemExit(f"Dependências externas não declaradas: {', '.join(external_imports)}")

    artifacts = ROOT / "artifacts"
    artifacts.mkdir(exist_ok=True)
    validation = evaluate_detectors(build_demo_document())
    write_json(artifacts / "validation-report.json", validation)
    write_json(
        artifacts / "license-report.json",
        {
            "generated_at": generated_at(),
            "project_version": "0.1.0",
            "project_license": "Apache-2.0",
            "direct_package_dependencies": [],
            "transitive_package_dependencies": [],
            "external_runtime": {"name": "CPython", "version": platform_python_version(), "spdx": "Python-2.0"},
            "external_imports_detected": external_imports,
            "result": "pass-no-external-packages",
            "vulnerability_note": "No PyPI/npm package to scan; scan the Python runtime and OS in the delivery environment.",
        },
    )
    write_json(ROOT / "sbom.spdx.json", build_sbom())
    print("Verificação concluída: testes, imports, validação, licenças e SBOM.")


def find_external_imports() -> list[str]:
    imports: set[str] = set()
    for path in [*(ROOT / "src").rglob("*.py"), *(ROOT / "tests").rglob("*.py"), *(ROOT / "tools").rglob("*.py")]:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                imports.add(node.module.split(".")[0])
    local = {"mapa_silencio"}
    return sorted(imports - set(sys.stdlib_module_names) - local - {"__future__"})


def build_sbom() -> dict[str, object]:
    return {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": "Pulso-Territorial-0.1.0",
        "documentNamespace": "https://github.com/pedrograngeiro/pulso-territorial/spdx/0.1.0",
        "creationInfo": {
            "created": generated_at(),
            "creators": ["Tool: tools/verify.py"],
            "licenseListVersion": "3.27",
        },
        "packages": [
            {
                "name": "IBGE Rio de Janeiro geographic assets",
                "SPDXID": "SPDXRef-Package-IBGE",
                "downloadLocation": "https://servicodados.ibge.gov.br/api/v3/malhas/estados/33",
                "filesAnalyzed": False,
                "licenseConcluded": "CC-BY-4.0",
                "licenseDeclared": "CC-BY-4.0",
                "copyrightText": "Instituto Brasileiro de Geografia e Estatistica (IBGE)",
                "comment": "API-minimum state and municipal boundaries, accessed 2026-09-05; edition unspecified. Accompanying IBGE technical note included. See THIRD_PARTY_NOTICES.md.",
            },
            {
                "name": "Pulso Territorial",
                "SPDXID": "SPDXRef-Package-PulsoTerritorial",
                "versionInfo": "0.1.0",
                "downloadLocation": "https://github.com/pedrograngeiro/pulso-territorial",
                "filesAnalyzed": False,
                "licenseConcluded": "NOASSERTION",
                "licenseDeclared": "Apache-2.0",
                "copyrightText": "Copyright 2026 Pedro Grangeiro and contributors",
                "comment": "Original material: Apache-2.0. IBGE assets retain CC-BY-4.0; see NOTICE.",
            },
            {
                "name": "CPython",
                "SPDXID": "SPDXRef-Package-CPython",
                "versionInfo": platform_python_version(),
                "downloadLocation": "https://www.python.org/downloads/",
                "filesAnalyzed": False,
                "licenseConcluded": "Python-2.0",
                "licenseDeclared": "Python-2.0",
                "copyrightText": "Copyright Python Software Foundation",
                "comment": "External runtime; not bundled in this repository.",
            },
        ],
        "relationships": [
            {"spdxElementId": "SPDXRef-Package-PulsoTerritorial", "relationshipType": "CONTAINS", "relatedSpdxElement": "SPDXRef-Package-IBGE"},
            {"spdxElementId": "SPDXRef-DOCUMENT", "relationshipType": "DESCRIBES", "relatedSpdxElement": "SPDXRef-Package-PulsoTerritorial"},
            {"spdxElementId": "SPDXRef-Package-PulsoTerritorial", "relationshipType": "DEPENDS_ON", "relatedSpdxElement": "SPDXRef-Package-CPython"},
        ],
    }


def generated_at() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def platform_python_version() -> str:
    return ".".join(str(part) for part in sys.version_info[:3])


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
