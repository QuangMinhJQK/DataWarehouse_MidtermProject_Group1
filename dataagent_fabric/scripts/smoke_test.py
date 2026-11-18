"""Read-only connectivity and known-measure smoke test."""

from __future__ import annotations

from dataagent.agent_service import DataAgentService
from dataagent.errors import DataAgentError


def main() -> None:
    try:
        service = DataAgentService()
        health = service.health_check()
        print(f"AUTH=OK MODEL={health['name']} CATALOG={health['catalog_version']}")
        dax = (
            "EVALUATE\nSUMMARIZECOLUMNS(\n"
            '    "Net Sales", [Net Sales],\n'
            '    "Orders", [Orders],\n'
            '    "Quantity", [Quantity]\n'
            ")"
        )
        rows, warnings = service.fabric.execute_dax(dax)
        print(f"QUERY=OK ROWS={len(rows)} WARNINGS={len(warnings)}")
        if rows:
            print("MEASURES=" + ",".join(rows[0].keys()))
    except DataAgentError as exc:
        print(f"SMOKE=FAILED TYPE={type(exc).__name__} MESSAGE={exc}")
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
