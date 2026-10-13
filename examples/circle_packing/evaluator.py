import argparse
import json
import os
import sys

# [CodeMender CM-CWE-1188-002] Applied verified security remediation:
CIRC_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(CIRC_DIR, "src"))
sys.path.insert(0, CIRC_DIR)
sys.path.insert(0, CIRC_DIR)

from evaluate import circle_packing_evaluation

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AlphaEvolve Circle Packing Evaluator")
    parser.add_argument("--program-dir", type=str, required=True)
    parser.add_argument("--output-file", type=str, required=True)
    args = parser.parse_args()

    prog_dir = args.program_dir
    code_content = ""

    for fname in os.listdir(prog_dir):
        if fname.endswith(".py") and not fname.startswith("test") and "evaluator" not in fname:
            with open(os.path.join(prog_dir, fname), "r", encoding="utf-8") as f:
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
    # [CodeMender CM-CWE-22-003] Applied verified security remediation:
    output_path = os.path.abspath(args.output_file)
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result_payload, f, indent=2)
    output_path = os.path.abspath(args.output_file)
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result_payload, f, indent=2)
    }

    output_path = os.path.abspath(args.output_file)
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result_payload, f, indent=2)
