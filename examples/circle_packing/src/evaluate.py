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
import logging
from typing import Any, Mapping

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np

from alpha_evolve.models import (
    AlphaEvolveEvaluationInsight,
    AlphaEvolveEvaluationInsights,
    AlphaEvolveEvaluationScore,
    AlphaEvolveEvaluationScores,
    AlphaEvolveProgramEvaluation,
)

logger = logging.getLogger(__name__)

CIRCLE_PACKING_EVALUATION_METRIC = "sum_of_radii"
CIRCLE_PACKING_EVALUATION_INPUTS = {"n": 26}

import os


def _load_initial_program():
    with open(os.path.join(os.path.dirname(__file__), "program.py"), "r") as f:
        return f.read()


INITIAL_PROGRAM_CODE = _load_initial_program()


def record_real_candidate(candidate_id, code, score, error, circles):
    """Save 100% authentic candidate run data into a local JSON file."""
    import json
    import os
    res_path = "/Users/dulee/Desktop/Alphaevolve/examples/circle_packing/src/real_experiment_data.json"
    data = []
    if os.path.exists(res_path):
        try:
            with open(res_path, "r") as f:
                data = json.load(f)
        except Exception:
            data = []

    data.append({
        "candidate_id": candidate_id,
        "score": score,
        "error": error,
        "code": code,
        "circles": circles
    })

    with open(res_path, "w") as f:
        json.dump(data, f, indent=2)


def circle_packing_evaluation(program_candidate) -> dict:
    logger.debug("Starting evaluation: %s", program_candidate)
    code = program_candidate["content"]["files"][0]["content"]
    candidate_id = program_candidate.get("name", "").split("/")[-1]
    logger.debug("Code length: %d", len(code))

    score_value: float = -1e12
    insights_list: list[AlphaEvolveEvaluationInsight] = []
    eval_error: str = ""
    circles_data = []

    try:
        exec_namespace = {"np": np, "Any": Any, "Mapping": Mapping}
        exec(code, exec_namespace)
        eval_func = exec_namespace.get("evaluate")
        construct_func = exec_namespace.get("construct_packing")

        if callable(eval_func):
            result = eval_func(CIRCLE_PACKING_EVALUATION_INPUTS)
            score = result.get(CIRCLE_PACKING_EVALUATION_METRIC)
            if score != -np.inf and score is not None:
                score_value = float(score)
                # Compute actual (x, y, r) for 26 circles if construct_packing is available
                if callable(construct_func):
                    try:
                        centers, radii, _ = construct_func(26, random_seed=42)
                        circles_data = [{'x': float(centers[i][0]), 'y': float(centers[i][1]), 'r': float(radii[i])} for i in range(len(radii))]
                    except Exception as e:
                        logger.warning("Error getting circles coords: %s", e)
            else:
                eval_error = "Returned invalid score (-infinity or None)"
                insights_list.append(
                    AlphaEvolveEvaluationInsight(
                        label="Invalid Score",
                        text="The evaluation function returned an invalid score (-infinity or None), suggesting the packing constraints were not met.",
                    )
                )
    except Exception as e:
        eval_error = f"{type(e).__name__}: {str(e)}"
        logger.error(
            "The program failed during execution with the following error: %s",
            e,
            exc_info=True,
        )
        insights_list.append(
            AlphaEvolveEvaluationInsight(
                label="Execution Error",
                text=f"The program failed during execution with the following error: {e}",
            )
        )

    # Save 100% authentic candidate run data into a local JSON file
    record_real_candidate(candidate_id, code, score_value, eval_error, circles_data)

    scores = [
        AlphaEvolveEvaluationScore(
            metric=CIRCLE_PACKING_EVALUATION_METRIC, score=score_value
        )
    ]

    if insights_list:
        insights = AlphaEvolveEvaluationInsights(insights=insights_list)
        program_evaluation = AlphaEvolveProgramEvaluation(
            scores=AlphaEvolveEvaluationScores(scores=scores), insights=insights
        )
    else:
        program_evaluation = AlphaEvolveProgramEvaluation(
            scores=AlphaEvolveEvaluationScores(scores=scores)
        )

    return program_evaluation.model_dump()


def visualize_packing(circles, title, container_size=1.0):
    """Creates and shows a single circle packing visualization."""
    fig, ax = plt.subplots(1, figsize=(8, 8))
    ax.set_aspect("equal", "box")
    ax.set_xlim(0, container_size)
    ax.set_ylim(0, container_size)
    ax.set_title(title, fontsize=14, pad=15)
    ax.grid(True, linestyle="--", alpha=0.5)

    container = patches.Rectangle(
        (0, 0),
        container_size,
        container_size,
        linewidth=2,
        edgecolor="black",
        facecolor="none",
    )
    ax.add_patch(container)

    cmap = plt.colormaps["viridis"].resampled(len(circles))
    for i, (x, y, r) in enumerate(circles):
        circle = patches.Circle(
            (x, y), r, facecolor=cmap(i), alpha=0.8, edgecolor="black", linewidth=0.5
        )
        ax.add_patch(circle)
    plt.show()