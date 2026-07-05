import json
import sys
from src.workflow.engine import WorkflowEngine
from src.tools.logger import info, set_level


def main():
    set_level("INFO")
    info("Main", "Enterprise AI Growth Copilot - Multi-Agent Pipeline")

    # Sample input data simulating real-world product reviews
    sample_reviews = [
        "The app crashes frequently when uploading large files",
        "Great customer support, very responsive team",
        "UI is intuitive but the dashboard loading is slow",
        "The export feature is missing CSV format",
        "Love the new collaboration features, very useful for teams",
    ]

    sample_product_info = {
        "name": "DataSync Pro",
        "version": "3.2.1",
        "category": "cloud_data_tool",
    }

    engine = WorkflowEngine(max_retries=3)
    result = engine.run(sample_reviews, sample_product_info)

    print("\n" + "=" * 60)
    print("WORKFLOW COMPLETE")
    print("=" * 60)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("=" * 60)

    final = result.get("final_state")
    if final in ("APPROVED", "REJECTED"):
        print(f"\nSUCCESS: System reached terminal state '{final}'.")
        sys.exit(0)
    else:
        print(f"\nERROR: Unexpected final state '{final}'.")
        sys.exit(1)


if __name__ == "__main__":
    main()
