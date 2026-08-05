"""
AlphaEvolve Generated Candidate #4
Score: 2.593086232248051
Candidate ID: 1014377268021464359
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
    
    # 🌌 CRAZY IDEA: The Quantum Multiverse Optimizer! 🌌
    # We spawn multiple parallel universes with drastically different topological structures 
    # (Apollonian gaskets, Twin Suns, Sunflower Spirals, and Big Bang physics relaxations).
    # We let each universe evolve locally via SLSQP, then select the timeline with the maximum sum of radii!
    multiverse_x0 = []
    
    # Universe 0: Classic grid (The Baseline Timeline)
    x0_0 = np.zeros(3 * n)
    grid_size = int(np.ceil(np.sqrt(n)))
    for i in range(n):
        x0_0[2 * i] = (i % grid_size + 0.5) / grid_size + rng.uniform(-0.01, 0.01)
        x0_0[2 * i + 1] = (i // grid_size + 0.5) / grid_size + rng.uniform(-0.01, 0.01)
    x0_0[2 * n:] = 0.4 / grid_size
    multiverse_x0.append(x0_0)

    # Universe 1: Apollonian Gas Giant (One massive center, smaller ones filling gaps)
    x0_1 = np.zeros(3 * n)
    c1, r1 = [[0.5, 0.5]], [0.4]
    for cx, cy in [(0.15, 0.15), (0.15, 0.85), (0.85, 0.15), (0.85, 0.85)]:
        c1.append([cx, cy])
        r1.append(0.09)
    for _ in range(n - 5):
        c1.append(rng.uniform(0.1, 0.9, 2))
        r1.append(rng.uniform(0.01, 0.04))
    x0_1[:2*n] = np.array(c1).flatten()
    x0_1[2*n:] = r1
    multiverse_x0.append(x0_1)

    # Universe 2: Twin Suns (Two large binary stars with planetary disks)
    x0_2 = np.zeros(3 * n)
    c2, r2 = [[0.25, 0.5], [0.75, 0.5]], [0.24, 0.24]
    for cx, cy in [(0.5, 0.15), (0.5, 0.85)]:
        c2.append([cx, cy])
        r2.append(0.14)
    for _ in range(n - 4):
        c2.append(rng.uniform(0.1, 0.9, 2))
        r2.append(rng.uniform(0.01, 0.04))
    x0_2[:2*n] = np.array(c2).flatten()
    x0_2[2*n:] = r2
    multiverse_x0.append(x0_2)
    
    # Universe 3: The Sunflower Spiral (Phyllotaxis distribution)
    x0_3 = np.zeros(3 * n)
    c3, r3 = [], []
    phi = (1 + np.sqrt(5)) / 2
    for i in range(n):
        rad_dist = np.sqrt((i + 0.5) / n) * 0.45
        theta = 2 * np.pi * i / phi
        c3.append([0.5 + rad_dist * np.cos(theta), 0.5 + rad_dist * np.sin(theta)])
        r3.append(0.04)
    x0_3[:2*n] = np.array(c3).flatten()
    x0_3[2*n:] = r3
    multiverse_x0.append(x0_3)

    # Universe 4: Big Bang Physics Relaxation (Chaotic start with repulsive forces)
    x0_4 = np.zeros(3 * n)
    c4 = rng.uniform(0.1, 0.9, (n, 2))
    r4 = rng.uniform(0.03, 0.12, n)
    for _ in range(100):
        c4 = np.clip(c4, r4[:, None] + 0.01, 1 - r4[:, None] - 0.01)
        for i in range(n):
            for j in range(i + 1, n):
                diff = c4[i] - c4[j]
                dist = np.linalg.norm(diff) + 1e-9
                overlap = r4[i] + r4[j] - dist
                if overlap > 0:
                    c4[i] += (diff / dist) * overlap * 0.5
                    c4[j] -= (diff / dist) * overlap * 0.5
    x0_4[:2*n] = c4.flatten()
    x0_4[2*n:] = r4
    multiverse_x0.append(x0_4)

    # Evolve the multiverse!
    for x0_universe in multiverse_x0:
        res = opt.minimize(
            objective, x0_universe, bounds=bounds,
            constraints={'type': 'ineq', 'fun': constraints},
            options={'maxiter': 500}
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