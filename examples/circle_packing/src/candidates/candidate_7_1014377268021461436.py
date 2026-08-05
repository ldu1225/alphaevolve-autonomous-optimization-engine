"""
AlphaEvolve Generated Candidate #7
Score: 2.6302821454619236
Candidate ID: 1014377268021461436
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

    bounds = [(0, 1)] * (3 * n)
    best_res = None
    best_val = np.inf
    best_res_fallback = None
    best_val_fallback = np.inf
    
    # 🛁 CRAZY IDEA: The "Expanding Bubble Bath" Multiverse! 🛁
    # We simulate a bubble bath with different target radius distributions.
    # Bubbles grow over time and repel each other via vectorized forces.
    # This provides SLSQP with extremely dense, already-feasible packings to optimize!
    multiverse_x0 = []
    
    def bubble_bath(rng_seed, distribution):
        local_rng = np.random.default_rng(rng_seed)
        centers = local_rng.uniform(0.2, 0.8, (n, 2))
        
        if distribution == 'uniform':
            target_r = np.ones(n) * (0.6 / np.sqrt(n))
        elif distribution == 'bimodal':
            target_r = np.concatenate([
                local_rng.uniform(0.15, 0.25, n // 4),
                local_rng.uniform(0.02, 0.08, n - n // 4)
            ])
        elif distribution == 'power':
            target_r = local_rng.beta(1, 3, n) * 0.25 + 0.02
        else: # exponential
            target_r = local_rng.exponential(0.08, n) + 0.01
            
        target_r = np.clip(target_r, 0.01, 0.3)
        radii = np.zeros(n)
        
        # Vectorized physics relaxation loop
        for step in range(300):
            # Grow bubbles
            radii += (target_r - radii) * 0.05
            
            # Repulsion (multiple sub-steps for stability)
            for _ in range(4):
                # Wall repulsion
                centers = np.clip(centers, radii[:, None] + 1e-4, 1 - radii[:, None] - 1e-4)
                
                # Pairwise repulsion
                diffs = centers[:, np.newaxis, :] - centers[np.newaxis, :, :]
                dist = np.linalg.norm(diffs, axis=-1)
                np.fill_diagonal(dist, np.inf)
                
                rad_sums = radii[:, np.newaxis] + radii[np.newaxis, :]
                overlap = rad_sums - dist
                
                if np.max(overlap) > 0:
                    push_dirs = diffs / (dist[..., np.newaxis] + 1e-9)
                    push_mags = np.maximum(overlap, 0) * 0.25
                    centers += np.sum(push_dirs * push_mags[..., np.newaxis], axis=1)
                                
        x0 = np.zeros(3 * n)
        x0[:2 * n] = centers.flatten()
        x0[2 * n:] = radii
        return x0

    # Universe 0: Classic grid as a fallback
    x0_0 = np.zeros(3 * n)
    grid_size = int(np.ceil(np.sqrt(n)))
    for i in range(n):
        x0_0[2 * i] = (i % grid_size + 0.5) / grid_size + rng.uniform(-0.01, 0.01)
        x0_0[2 * i + 1] = (i // grid_size + 0.5) / grid_size + rng.uniform(-0.01, 0.01)
    x0_0[2 * n:] = 0.4 / grid_size
    multiverse_x0.append(x0_0)

    # Generate 15 different bubble baths
    distributions = ['uniform', 'bimodal', 'power', 'exponential']
    for idx in range(15):
        dist = distributions[idx % len(distributions)]
        multiverse_x0.append(bubble_bath(random_seed + idx, dist))

    # Evolve the multiverse!
    for x0_universe in multiverse_x0:
        res = opt.minimize(
            objective, x0_universe, bounds=bounds,
            constraints={'type': 'ineq', 'fun': constraints},
            options={'maxiter': 800, 'ftol': 1e-6}
        )
        
        # Determine if this universe reached a valid physical state
        cons_vals = constraints(res.x)
        max_viol = -np.min(np.append(cons_vals, 0.0))
        
        # We accept if violations are within small numeric tolerance
        if max_viol < 1e-3 and res.fun < best_val:
            best_val = res.fun
            best_res = res.x
            
        # Track the absolute best objective as a fallback
        if res.fun < best_val_fallback:
            best_val_fallback = res.fun
            best_res_fallback = res.x
            
    # Collapse the wavefunction to the best surviving timeline
    if best_res is None:
        best_res = best_res_fallback

    centers = best_res[:2 * n].reshape((n, 2))
    radii = best_res[2 * n:]
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