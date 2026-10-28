import argparse
import json
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir))

from app.db.session import SessionLocal
from app.validators.engine import run_validation_suite
from app.core.config import DATA_DIR

def run_validation_cli(profile: str = "starter"):
    print(f"[*] Executing Invariant Validation Suite on profile '{profile}'...")
    db = SessionLocal()
    try:
        report = run_validation_suite(db)
        
        # Save validation report
        val_dir = DATA_DIR / "validation"
        val_dir.mkdir(parents=True, exist_ok=True)
        report_file = val_dir / f"validation_report_{profile}.json"
        
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print("=" * 60)
        print(f"VALIDATION REPORT: {report['overall_status']}")
        print(f"Passed Checks: {report['passed_checks']} / {report['total_checks']}")
        print(f"Violations: {report['total_violations']}")
        print(f"Report saved to: {report_file}")
        print("=" * 60)
        
        for c in report["checks"]:
            symbol = "[PASS]" if c["status"] == "PASS" else "[FAIL]"
            print(f" {symbol} {c['check_name']}: {c['status']} - {c['description']}")

        if report["overall_status"] == "FAIL":
            sys.exit(1)
        else:
            sys.exit(0)
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Returns Platform Validation Engine")
    parser.add_argument("--profile", type=str, default="starter", help="Dataset profile to validate")
    args = parser.parse_args()
    run_validation_cli(args.profile)
