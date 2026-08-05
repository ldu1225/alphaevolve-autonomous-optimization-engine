"""
AlphaEvolve Generated Candidate #9
Score: 2.630438340259675
Candidate ID: 1014377268021464372
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

    def solve_lp_radii(centers, margin=1e-8):
        # Solve LP to find the mathematically optimal radii for fixed centers
        c = -np.ones(n)
        
        bounds = []
        for i in range(n):
            x, y = centers[i]
            max_r = min(x, 1.0 - x, y, 1.0 - y) - margin
            bounds.append((0.0, max(0.0, max_r)))
            
        num_pairs = n * (n - 1) // 2
        A = np.zeros((num_pairs, n))
        b = np.zeros(num_pairs)
        
        idx = 0
        for i in range(n):
            for j in range(i + 1, n):
                A[idx, i] = 1.0
                A[idx, j] = 1.0
                dist = np.linalg.norm(centers[i] - centers[j])
                b[idx] = max(0.0, dist - margin)
                idx += 1
                
        res = opt.linprog(c, A_ub=A, b_ub=b, bounds=bounds, method='highs')
        if res.success:
            return res.x, -res.fun
        else:
            return np.ones(n) * 1e-5, n * 1e-5

    def hill_climb_centers(centers, steps=120, init_sigma=0.02, seed=42):
        local_rng = np.random.default_rng(seed)
        best_centers = centers.copy()
        best_radii, best_score = solve_lp_radii(best_centers)
        
        for step in range(steps):
            sigma = init_sigma * (1.0 - step / steps)
            perturbed = best_centers + local_rng.normal(0, sigma, best_centers.shape)
            perturbed = np.clip(perturbed, 1e-5, 1.0 - 1e-5)
            
            radii, score = solve_lp_radii(perturbed)
            if score > best_score:
                best_score = score
                best_centers = perturbed
                best_radii = radii
                
        return best_centers, best_radii, best_score

    def objective(vars):
        return -np.sum(vars[2 * n:])
        
    def constraints(vars):
        centers = vars[:2 * n].reshape((n, 2))
        radii = vars[2 * n:]
        
        cons = []
        # Use 1e-9 tolerance during SLSQP to maximize continuous optimization freedom
        cons.extend(centers[:, 0] - radii - 1e-9)
        cons.extend(1 - centers[:, 0] - radii - 1e-9)
        cons.extend(centers[:, 1] - radii - 1e-9)
        cons.extend(1 - centers[:, 1] - radii - 1e-9)
        
        # Vectorized pairwise constraints
        diffs = centers[:, np.newaxis, :] - centers[np.newaxis, :, :]
        dist_sq = np.sum(diffs ** 2, axis=-1)
        rad_sums = radii[:, np.newaxis] + radii[np.newaxis, :]
        
        idx = np.triu_indices(n, k=1)
        cons.extend(dist_sq[idx] - (rad_sums[idx] + 1e-9) ** 2)
                
        return np.array(cons)

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
        elif distribution == 'mixed_large_small':
            target_r = np.zeros(n)
            num_large = local_rng.integers(1, 4)
            target_r[:num_large] = local_rng.uniform(0.25, 0.4, num_large)
            target_r[num_large:] = local_rng.uniform(0.02, 0.08, n - num_large)
        elif distribution == 'few_large':
            target_r = np.zeros(n)
            num_large = local_rng.integers(4, 8)
            target_r[:num_large] = local_rng.uniform(0.15, 0.25, num_large)
            target_r[num_large:] = local_rng.uniform(0.02, 0.06, n - num_large)
        else: # exponential
            target_r = local_rng.exponential(0.08, n) + 0.01
            
        target_r = np.clip(target_r, 0.01, 0.3)
        radii = np.zeros(n)
        
        for step in range(300):
            radii += (target_r - radii) * 0.05
            for _ in range(4):
                centers = np.clip(centers, radii[:, None] + 1e-4, 1 - radii[:, None] - 1e-4)
                diffs = centers[:, np.newaxis, :] - centers[np.newaxis, :, :]
                dist = np.linalg.norm(diffs, axis=-1)
                np.fill_diagonal(dist, np.inf)
                
                rad_sums = radii[:, np.newaxis] + radii[np.newaxis, :]
                overlap = rad_sums - dist
                
                if np.max(overlap) > 0:
                    push_dirs = diffs / (dist[..., np.newaxis] + 1e-9)
                    push_mags = np.maximum(overlap, 0) * 0.25
                    centers += np.sum(push_dirs * push_mags[..., np.newaxis], axis=1)
                                
        return centers

    # Generate diverse initial candidate center configurations
    candidates = []

    # 1. Grid arrangement
    grid_size = int(np.ceil(np.sqrt(n)))
    grid_centers = np.zeros((n, 2))
    for i in range(n):
        grid_centers[i, 0] = (i % grid_size + 0.5) / grid_size + rng.uniform(-0.01, 0.01)
        grid_centers[i, 1] = (i // grid_size + 0.5) / grid_size + rng.uniform(-0.01, 0.01)
    grid_centers = np.clip(grid_centers, 1e-5, 1.0 - 1e-5)
    candidates.append(grid_centers)

    # 2. Bubble baths
    distributions = ['uniform', 'bimodal', 'power', 'mixed_large_small', 'few_large', 'exponential']
    for idx in range(42):
        dist = distributions[idx % len(distributions)]
        candidates.append(bubble_bath(random_seed + idx, dist))

    # Evaluate all candidates with the LP solver to find their initial optimal score
    evaluated_candidates = []
    for c_idx, centers in enumerate(candidates):
        radii, score = solve_lp_radii(centers)
        evaluated_candidates.append((centers, radii, score))

    # Sort candidates by score and pick the top 6
    evaluated_candidates.sort(key=lambda item: item[2], reverse=True)
    top_candidates = evaluated_candidates[:6]

    # Perform Hill Climbing on the top 6 candidates to optimize center coordinates
    refined_candidates = []
    for c_idx, (centers, _, _) in enumerate(top_candidates):
        ref_centers, ref_radii, ref_score = hill_climb_centers(centers, steps=120, init_sigma=0.02, seed=random_seed + c_idx)
        refined_candidates.append((ref_centers, ref_radii, ref_score))

    # Sort refined candidates and pick the top 3
    refined_candidates.sort(key=lambda item: item[2], reverse=True)
    best_candidates = refined_candidates[:3]

    # Run SLSQP optimization on the top 3 candidates to co-optimize centers and radii
    best_final_score = -1.0
    best_final_centers = None
    best_final_radii = None

    bounds = [(0, 1)] * (3 * n)

    for c_idx, (centers, radii, _) in enumerate(best_candidates):
        x0 = np.zeros(3 * n)
        x0[:2 * n] = centers.flatten()
        x0[2 * n:] = radii

        res = opt.minimize(
            objective, x0, bounds=bounds,
            constraints={'type': 'ineq', 'fun': constraints},
            options={'maxiter': 500, 'ftol': 1e-7}
        )

        final_centers = res.x[:2 * n].reshape((n, 2))
        
        # Solve LP one final time to guarantee 100% feasibility (safety margin 1e-8)
        # and to find the absolute mathematically optimal radii for these final centers!
        opt_radii, opt_score = solve_lp_radii(final_centers, margin=1e-8)

        if opt_score > best_final_score:
            best_final_score = opt_score
            best_final_centers = final_centers
            best_final_radii = opt_radii

    return best_final_centers, best_final_radii, best_final_score


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