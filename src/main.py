import json, os, sys, argparse
from src.workflow.engine import WorkflowEngine
from src.tools.logger import set_level


def load_reviews_from_file(path: str) -> list[str]:
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def list_test_data() -> list[tuple[str, str, int]]:
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_data")
    if not os.path.isdir(data_dir):
        return []
    files = []
    for fname in sorted(os.listdir(data_dir)):
        if fname.endswith(".txt"):
            fpath = os.path.join(data_dir, fname)
            with open(fpath, encoding="utf-8") as f:
                count = sum(1 for line in f if line.strip())
            files.append((fname, fpath, count))
    return files


def choose_test_data() -> list[str] | None:
    files = list_test_data()
    if not files:
        print("  No test data files found in test_data/")
        return None
    print()
    for i, (name, _, count) in enumerate(files, 1):
        print(f"  {i}. {name} ({count} reviews)")
    print()
    try:
        choice = input("  Choose a file (1-{}): ".format(len(files))).strip()
        idx = int(choice) - 1
        if 0 <= idx < len(files):
            reviews = load_reviews_from_file(files[idx][1])
            print(f"  Loaded {len(reviews)} reviews from {files[idx][0]}\n")
            return reviews
    except (ValueError, IndexError):
        pass
    print("  Invalid choice.")
    return None


def paste_reviews() -> list[str] | None:
    print("\n  Paste your reviews (one per line). Press Enter on an empty line to finish:\n")
    lines = []
    while True:
        line = input("  ").strip()
        if not line:
            break
        lines.append(line)
    if not lines:
        print("  No reviews entered.")
        return None
    print(f"  Got {len(lines)} reviews.\n")
    return lines


def run_pipeline(reviews: list[str], debug: bool = False):
    set_level("ERROR" if not debug else "INFO")
    sample_product_info = {
        "name": "DataSync Pro",
        "version": "3.2.1",
        "category": "cloud_data_tool",
    }
    engine = WorkflowEngine(max_retries=3, debug=debug)
    result = engine.run(reviews, sample_product_info)
    print("\n" + "=" * 52)
    print("  WORKFLOW COMPLETE")
    print("=" * 52)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("=" * 52)
    final = result.get("final_state")
    if final in ("APPROVED", "REJECTED"):
        print(f"\n  SUCCESS: Terminal state '{final}'.\n")
    else:
        print(f"\n  ERROR: Unexpected final state '{final}'.\n")


def show_menu():
    print("\n" + "=" * 34)
    print("  Enterprise AI Growth Copilot")
    print("=" * 34)
    print("  1. Load sample data")
    print("  2. Paste reviews manually")
    print("  3. Exit")
    print("=" * 34)


def main():
    parser = argparse.ArgumentParser(description="Enterprise AI Growth Copilot")
    parser.add_argument("--debug", action="store_true", help="Show detailed step-by-step trace")
    args = parser.parse_args()
    if args.debug:
        print("  Debug mode enabled\n")
        reviews = paste_reviews()
        if reviews is None:
            return
        run_pipeline(reviews, debug=True)
        return
    while True:
        show_menu()
        choice = input("  Choice: ").strip()
        if choice == "1":
            reviews = choose_test_data()
            if reviews:
                run_pipeline(reviews)
        elif choice == "2":
            reviews = paste_reviews()
            if reviews:
                run_pipeline(reviews)
        elif choice == "3":
            print("\n  Bye.\n")
            break
        else:
            print("  Invalid choice. Please enter 1, 2, or 3.\n")


if __name__ == "__main__":
    main()