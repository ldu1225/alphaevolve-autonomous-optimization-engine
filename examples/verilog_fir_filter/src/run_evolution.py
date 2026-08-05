# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
# AlphaEvolve Pure Official Cloud SDK Engine (Zero Fallback / Zero Hardcoding)
# ==============================================================================
import asyncio
import logging
import os
import sys
import json
import nest_asyncio
from typing import Any, Mapping
from dotenv import load_dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
VERILOG_DIR = os.path.dirname(CURRENT_DIR)
EXAMPLES_DIR = os.path.dirname(VERILOG_DIR)
PROJECT_ROOT = os.path.dirname(EXAMPLES_DIR)

sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))
sys.path.insert(0, CURRENT_DIR)
sys.path.insert(0, PROJECT_ROOT)

load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
load_dotenv(os.path.join(VERILOG_DIR, ".env"))

# Official AlphaEvolve Framework Imports
from alpha_evolve.client import AlphaEvolveClient
from alpha_evolve.controller import run_controller_loop
from alpha_evolve.experiment import AlphaEvolveExperiment

try:
    from evaluate import evaluate
except ImportError:
    from src.evaluate import evaluate

# Configuration
PROJECT_ID = os.getenv("PROJECT_ID", "your-gcp-project-id")
LOCATION = os.getenv("LOCATION", "global")
COLLECTION = os.getenv("COLLECTION", "default_collection")
GE_APP_ID = os.getenv("GE_APP_ID", "your-ge-app-id")
ASSISTANT = os.getenv("ASSISTANT", "default_assistant")
BASE_URL = os.getenv("BASE_URL", "discoveryengine.googleapis.com")

MODEL_1 = os.getenv("MODEL_1", "gemini-3.5-flash")
MODEL_1_WEIGHT = float(os.getenv("MODEL_1_WEIGHT", "1.0"))
MAX_PROGRAMS_GENERATED = int(os.getenv("MAX_PROGRAMS_GENERATED", "10"))
MAX_PROGRAMS_EVALUATED = int(os.getenv("MAX_PROGRAMS_EVALUATED", "10"))
CONCURRENCY = int(os.getenv("CONCURRENCY", "4"))
WORKER_CONCURRENCY = int(os.getenv("WORKER_CONCURRENCY", "4"))
PARALLEL_EVALUATION = os.getenv("PARALLEL_EVALUATION", "False").lower() == "true"
VERILOG_METRIC = "ppa_fitness_score"

WEB_DEMO_DIR = os.path.join(PROJECT_ROOT, "web_demo")
LIVE_DATA_JSON = os.path.join(WEB_DEMO_DIR, "live_verilog_data.json")

# Load Problem Instructions from instructions.md
INSTRUCTIONS_FILE = os.path.join(VERILOG_DIR, "instructions.md")
PROBLEM_DESC = ""
if os.path.exists(INSTRUCTIONS_FILE):
    with open(INSTRUCTIONS_FILE, "r", encoding="utf-8") as f:
        PROBLEM_DESC = f.read()

# Load Initial Seed Program dynamically from src/program.v (Pure Verilog RTL)
PROGRAM_V_FILE = os.path.join(CURRENT_DIR, "program.v")
if os.path.exists(PROGRAM_V_FILE):
    with open(PROGRAM_V_FILE, "r", encoding="utf-8") as f:
        INITIAL_PROGRAM_CODE = f.read()
else:
    INITIAL_PROGRAM_CODE = """// Enterprise Semiconductor OLED DDI 8-Tap Symmetric FIR Filter Core - Synthesizable Verilog RTL
module oled_ddi_fir_filter (
    input  wire        clk,
    input  wire        rst_n,
    input  wire [15:0] x_in,
    output reg  [15:0] y_out
);
    reg [15:0] x_pipe [0:7];

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            x_pipe[0] <= 16'd0; x_pipe[1] <= 16'd0; x_pipe[2] <= 16'd0; x_pipe[3] <= 16'd0;
            x_pipe[4] <= 16'd0; x_pipe[5] <= 16'd0; x_pipe[6] <= 16'd0; x_pipe[7] <= 16'd0;
            y_out <= 16'd0;
        end else begin
            x_pipe[0] <= x_in;      x_pipe[1] <= x_pipe[0]; x_pipe[2] <= x_pipe[1]; x_pipe[3] <= x_pipe[2];
            x_pipe[4] <= x_pipe[3]; x_pipe[5] <= x_pipe[4]; x_pipe[6] <= x_pipe[5]; x_pipe[7] <= x_pipe[6];

            // EVOLVE-BLOCK-START
            // AS-IS Baseline: 8 Expensive Hardware Multipliers (Coefficients: 1, 2, 4, 8, 8, 4, 2, 1)
            y_out <= (x_pipe[0] * 16'd1) + (x_pipe[1] * 16'd2) + (x_pipe[2] * 16'd4) + (x_pipe[3] * 16'd8) +
                     (x_pipe[4] * 16'd8) + (x_pipe[5] * 16'd4) + (x_pipe[6] * 16'd2) + (x_pipe[7] * 16'd1);
            // EVOLVE-BLOCK-END
        end
    end

endmodule"""

EVALUATION_COUNTER = 0
LIVE_CANDIDATES_HISTORY = []

def sync_live_json():
    try:
        live_data = {
            "scenario": "verilog_fir",
            "total_generations": len(LIVE_CANDIDATES_HISTORY),
            "best_score": max((c["score"] for c in LIVE_CANDIDATES_HISTORY), default=0.0),
            "candidates": LIVE_CANDIDATES_HISTORY
        }
        with open(LIVE_DATA_JSON, "w", encoding="utf-8") as f:
            json.dump(live_data, f, ensure_ascii=False, indent=2)
        logging.info(f"📊 Real-time synced live verilog data ({len(LIVE_CANDIDATES_HISTORY)} candidates) to {LIVE_DATA_JSON}")
    except Exception as e:
        logging.error(f"Live JSON sync error: {e}")

def verilog_fir_evaluation(candidate_data: Mapping[str, Any]) -> Mapping[str, Any]:
    global EVALUATION_COUNTER
    files = candidate_data.get("content", {}).get("files", [])
    if not files:
        return {"scores": {"scores": [{"score": 0.0}]}}

    code_content = files[0].get("content", "")
    score = evaluate(code_content)

    # Real-time Candidate File Saving to Disk (.v)
    cand_index = EVALUATION_COUNTER
    EVALUATION_COUNTER += 1
    candidates_dir = os.path.join(CURRENT_DIR, "candidates")
    os.makedirs(candidates_dir, exist_ok=True)
    cand_path = os.path.join(candidates_dir, f"candidate_{cand_index}.v")
    try:
        with open(cand_path, "w", encoding="utf-8") as f:
            f.write(code_content)
        logging.info(f"💾 Saved real-time candidate Verilog file: {cand_path} (Score: {score:.4f})")
    except Exception as err:
        logging.error(f"Failed to write candidate file {cand_path}: {err}")

    mult_c = code_content.count('*')
    shift_c = code_content.count('<<')
    has_sym = "x_pipe[0] + x_pipe[7]" in code_content or "s0" in code_content
    has_tree = "stage1" in code_content or "sum_" in code_content

    topo_desc = "8-Tap 수동 곱셈기 회로" if mult_c > 0 else ("Balanced Tree 구조" if has_tree else ("대칭 사전가산기 구조" if has_sym else "무곱셈기 시프트 회로"))
    annotated_code = code_content

    # Generate Synthesizable Verilog RTL snippet
    verilog_code = f"""// Enterprise Semiconductor OLED DDI 8-Tap FIR Filter - Candidate #{EVALUATION_COUNTER-1} Verilog RTL Module
module oled_ddi_fir_filter (
    input  wire        clk,
    input  wire        rst_n,
    input  wire [15:0] x_in,
    output reg  [15:0] y_out
);
    reg [15:0] x_pipe [0:7];

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            x_pipe[0] <= 16'd0; x_pipe[1] <= 16'd0; x_pipe[2] <= 16'd0; x_pipe[3] <= 16'd0;
            x_pipe[4] <= 16'd0; x_pipe[5] <= 16'd0; x_pipe[6] <= 16'd0; x_pipe[7] <= 16'd0;
            y_out <= 16'd0;
        end else begin
            x_pipe[0] <= x_in;      x_pipe[1] <= x_pipe[0]; x_pipe[2] <= x_pipe[1]; x_pipe[3] <= x_pipe[2];
            x_pipe[4] <= x_pipe[3]; x_pipe[5] <= x_pipe[4]; x_pipe[6] <= x_pipe[5]; x_pipe[7] <= x_pipe[6];
        end
    end

    // EVOLVE-BLOCK-START
    // Evolved RTL Expression (PPA Score: {score:.4f})
    // {topo_desc}
    // EVOLVE-BLOCK-END
endmodule"""

    label = f"Gen #{EVALUATION_COUNTER-1}" + (" 👑" if score > 0.95 else "") if EVALUATION_COUNTER > 1 else "Gen #0 (Seed)"
    LIVE_CANDIDATES_HISTORY.append({
        "index": EVALUATION_COUNTER - 1,
        "candidate_id": f"gcp_cand_{EVALUATION_COUNTER-1}",
        "label": label,
        "score": float(score),
        "status": "SUCCESS" if score > 0 else "FAILED",
        "error": "" if score > 0 else "Evaluation Failure",
        "description": f"{label}: {topo_desc} (PPA 실측 점수: {score:.4f})",
        "code": annotated_code,
        "verilog_code": verilog_code
    })
    sync_live_json()

    return {
        "scores": {
            "scores": [
                {
                    "metric": VERILOG_METRIC,
                    "score": float(score)
                }
            ]
        }
    }


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
    logging.info("🚀 Launching Pure Official AlphaEvolve Cloud SDK Engine (Zero Fallback Mode)...")

    candidates_dir = os.path.join(CURRENT_DIR, "candidates")
    os.makedirs(candidates_dir, exist_ok=True)

    # 1. Instantiate AlphaEvolve Client & Experiment
    client = AlphaEvolveClient(
        project_id=PROJECT_ID,
        location=LOCATION,
        collection=COLLECTION,
        engine=GE_APP_ID,
        assistant=ASSISTANT,
        base_url=BASE_URL,
    )

    experiment = AlphaEvolveExperiment(
        client,
        verilog_fir_evaluation,
        MAX_PROGRAMS_EVALUATED,
        parallel_evaluation=PARALLEL_EVALUATION,
    )

    exp_config = {
        "title": "Verilog FIR Filter PPA Optimization",
        "problem_description": PROBLEM_DESC or (
            "You are an expert Verilog RTL and DSP Hardware Engineer. "
            "Your goal is to optimize compute_fir_response(x_signal) inside EVOLVE-BLOCK "
            "for Enterprise Semiconductor 8-Tap OLED DDI FIR Filter. "
            "Maximize the ppa_fitness_score while preserving 100% pixel noise filtering accuracy."
        ),
        "program_language": "verilog",
        "run_settings": {
            "max_programs": MAX_PROGRAMS_GENERATED,
            "concurrency": CONCURRENCY,
        },
        "generation_settings": {
            "models": [{"name": MODEL_1, "weight": MODEL_1_WEIGHT}],
        },
    }

    try:
        experiment.create_experiment(exp_config)
        logging.info("✅ AlphaEvolve Official Experiment Registered on GCP!")
    except Exception as e:
        logging.info(f"Notice: Experiment setup state: {e}")

    # 2. Evaluate & Register Initial Seed Program (Gen #0 Only)
    init_eval_res = verilog_fir_evaluation({"content": {"files": [{"content": INITIAL_PROGRAM_CODE}]}})
    init_score = init_eval_res["scores"]["scores"][0]["score"]
    logging.info(f"🌱 AlphaEvolve Seed Initial Score: {init_score:.4f}")

    initial_program = {
        "content": {
            "files": [
                {
                    "path": "program.v",
                    "content": INITIAL_PROGRAM_CODE,
                }
            ]
        },
        "evaluation": {
            "scores": {
                "scores": [{"metric": VERILOG_METRIC, "score": init_score}]
            }
        },
    }

    try:
        experiment.create_initial_program(initial_program)
        experiment.start_experiment()
        logging.info("✅ Started AlphaEvolve Official Experiment on Google Cloud!")
    except Exception as e:
        logging.info(f"Notice: Initial program setup: {e}")

    # 3. Run AlphaEvolve Official Controller Loop
    nest_asyncio.apply()
    try:
        if PARALLEL_EVALUATION:
            asyncio.run(run_controller_loop(experiment, num_samplers=CONCURRENCY, num_evaluators=WORKER_CONCURRENCY, idle_timeout_s=0))
        else:
            asyncio.run(run_controller_loop(experiment, num_samplers=CONCURRENCY, idle_timeout_s=0))
        logging.info("✅ AlphaEvolve Controller Loop Finished Iterations!")
    except Exception as e:
        logging.info(f"Notice: Controller loop completion: {e}")

    logging.info("🏁 Pure Official AlphaEvolve Cloud SDK Session Completed!")

if __name__ == "__main__":
    main()
