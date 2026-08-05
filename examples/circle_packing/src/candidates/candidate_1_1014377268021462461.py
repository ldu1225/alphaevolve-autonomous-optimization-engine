"""
AlphaEvolve Generated Candidate #1
Score: 2.5572095772003123
Candidate ID: 1014377268021462461
"""

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
# pylint: disable=g-import-not-at-top
# pylint: disable=g-bad-import-order
# pylint: disable=pointless-string-statement
from typing import Any, Mapping

# EVOLVE-BLOCK-START
"""Constructor-based circle packing for n=26 circles"""
import numpy as np


import scipy.optimize as opt

def construct_packing(n, random_seed: int):
    """Construct a specific arrangement of circles in a unit square.

    The goal is to maximize the sum of their radii using mathematical optimization.

    Args:
        n: Number of circles.
        random_seed: Random seed for reproducibility.

    Returns:
        Tuple of (centers, radii, sum_of_radii)
    """
    rng = np.random.default_rng(random_seed)

    def objective(vars):
        # vars is [x_0, y_0, x_1, y_1, ..., r_0, r_1, ...]
        return -np.sum(vars[2 * n:])
        
    def constraints(vars):
        centers = vars[:2 * n].reshape((n, 2))
        radii = vars[2 * n:]
        
        cons = []
        # Subtracting 1e-5 to strictly prevent boundary overlaps due to numeric tolerances
        cons.extend(centers[:, 0] - radii - 1e-5)
        cons.extend(1 - centers[:, 0] - radii - 1e-5)
        cons.extend(centers[:, 1] - radii - 1e-5)
        cons.extend(1 - centers[:, 1] - radii - 1e-5)
        
        # Vectorized pairwise constraints
        diffs = centers[:, np.newaxis, :] - centers[np.newaxis, :, :]
        dist_sq = np.sum(diffs ** 2, axis=-1)
        rad_sums = radii[:, np.newaxis] + radii[np.newaxis, :]
        
        # Extract upper triangle for unique pairs
        idx = np.triu_indices(n, k=1)
        cons.extend(dist_sq[idx] - (rad_sums[idx] + 1e-5) ** 2)
                
        return np.array(cons)

    # Initialize guesses on a generic grid (breaking symmetry w/ tiny jitter)
    x0 = np.zeros(3 * n)
    grid_size = int(np.ceil(np.sqrt(n)))
    for i in range(n):
        x0[2 * i] = (i % grid_size + 0.5) / grid_size + rng.uniform(-0.01, 0.01)
        x0[2 * i + 1] = (i // grid_size + 0.5) / grid_size + rng.uniform(-0.01, 0.01)
    x0[2 * n:] = 0.4 / grid_size  # Feasible initial radii
    
    bounds = [(0, 1)] * (3 * n)
    
    res = opt.minimize(
        objective, x0, bounds=bounds,
        constraints={'type': 'ineq', 'fun': constraints},
        options={'maxiter': 1000}
    )
    
    centers = res.x[:2 * n].reshape((n, 2))
    radii = res.x[2 * n:]
    return centers, radii, np.sum(radii)


# EVOLVE-BLOCK-END


def _circles_overlap(centers, radii):
    """Protected function to compute max radii."""
    n = centers.shape[0]

    for i in range(n):
        for j in range(i + 1, n):
            dist = np.sqrt(np.sum((centers[i] - centers[j]) ** 2))
            if radii[i] + radii[j] > dist:
                return True

    return False


def evaluate(eval_inputs: Mapping[str, Any]) -> dict[str, float]:
    """Construct a packing and evaluate its score."""
    n = eval_inputs["n"]
    if "random_seed" not in eval_inputs:
        random_seed = 42
    else:
        random_seed = eval_inputs["random_seed"]
    centers, radii, _ = construct_packing(n, random_seed=random_seed)
    if (
        centers.shape != (n, 2)
        or not np.isfinite(centers).all()
        or not ((radii[:, None] <= centers) & (centers <= 1 - radii[:, None])).all()
    ):
        return {"sum_of_radii": -np.inf}

    if radii.shape != (n,) or not np.isfinite(radii).all() or not (0 <= radii).all():
        return {"sum_of_radii": -np.inf}

    if _circles_overlap(centers, radii):
        return {"sum_of_radii": -np.inf}

    return {"sum_of_radii": float(np.sum(radii))}