import argparse
import json
import os
import sys

CIRC_DIR = os.environ.get("CIRC_DIR", os.path.dirname(os.path.abspath(__file__)))
src_dir = os.path.join(CIRC_DIR, "src")
if os.path.exists(src_dir):
    sys.path.insert(0, src_dir)
if os.path.exists(CIRC_DIR):
    sys.path.insert(0, CIRC_DIR)

from evaluate import circle_packing_evaluation

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AlphaEvolve Circle Packing Evaluator")
    parser.add_argument("--program-dir", type=str, required=True)
    parser.add_argument("--output-file", type=str, required=True)
    args = parser.parse_args()

    prog_dir = os.path.abspath(args.program_dir)
    if not os.path.isdir(prog_dir):
        sys.exit(f"Error: Directory not found: {prog_dir}")

    code_content = ""
    for fname in os.listdir(prog_dir):
        if fname.endswith(".py") and not fname.startswith("test") and "evaluator" not in fname:
            target_file = os.path.join(prog_dir, fname)
            with open(target_file, "r", encoding="utf-8") as f:
                code_content = f.read()
            break

    candidate_data = {
        "content": {
            "files": [
                {
                    "path": "program.py",
                    "content": code_content
                }
            ]
        }
    }

    res = circle_packing_evaluation(candidate_data)
    scores_list = res.get("scores", {}).get("scores", [])
    
    result_payload = {
        "scores": scores_list
    }

    output_path = os.path.abspath(args.output_file)
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result_payload, f, indent=2)
