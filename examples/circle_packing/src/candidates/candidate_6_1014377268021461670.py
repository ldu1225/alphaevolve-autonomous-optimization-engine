"""
AlphaEvolve Generated Candidate #6
Score: 2.1189655894501107
Candidate ID: 1014377268021461670
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


def construct_packing(n, random_seed: int):
    """Construct a specific arrangement of 26 circles in a unit square.

    The goal is to maximize the sum of their radii.

    Args:
        n: Number of circles.
        random_seed: Random seed for reproducibility.

    Returns:
        Tuple of (centers, radii, sum_of_radii)
        centers: np.array of shape (26, 2) with (x, y) coordinates
        radii: np.array of shape (26) with radius of each circle
        sum_of_radii: Sum of all radii
    """

    rng = np.random.default_rng(random_seed)
    
    best_centers = None
    best_radii = None
    best_sum = -1
    
    # CRAZY IDEA: Multiverse Bubble Inflation with Simulated Annealing!
    # We simulate multiple parallel universes of expanding hyperspheres.
    # Why? Because equal-sized circles mathematically optimize the sum of radii!
    for run in range(5):
        centers = rng.uniform(0.1, 0.9, (n, 2))
        R = 0.05  # Initial bubble radius
        lr = 0.15
        
        # Physics engine: Concurrent inflating bubbles with repulsion
        for step in range(2500):
            # Compute pairwise Euclidean distances
            diff = centers[:, np.newaxis, :] - centers[np.newaxis, :, :]
            dist = np.sqrt(np.sum(diff**2, axis=-1))
            np.fill_diagonal(dist, np.inf)
            
            # Electrostatic-like bubble overlap repulsion
            overlap = 2 * R - dist
            overlap[overlap < 0] = 0
            
            # Calculate repulsive forces (pushing overlapping bubbles apart)
            direction = diff / (dist[:, :, np.newaxis] + 1e-8)
            force = np.sum(direction * overlap[:, :, np.newaxis], axis=1)
            
            # Quantum-like boundary potentials (hard walls at R and 1-R)
            viol_left = R - centers[:, 0]
            viol_right = centers[:, 0] - (1 - R)
            viol_bottom = R - centers[:, 1]
            viol_top = centers[:, 1] - (1 - R)
            
            force[:, 0] += np.maximum(viol_left, 0) - np.maximum(viol_right, 0)
            force[:, 1] += np.maximum(viol_bottom, 0) - np.maximum(viol_top, 0)
            
            # Simulated annealing: inject thermal noise to jiggle into perfect Wigner crystals
            temp = 0.005 * (1.0 - step / 2500.0)**2
            force += rng.normal(0, temp, (n, 2))
            
            centers += force * lr
            centers = np.clip(centers, 0.0, 1.0)
            
            # Adaptively inflate/deflate the universe!
            max_overlap = np.max(overlap)
            max_viol = max(np.max(viol_left), np.max(viol_right), np.max(viol_bottom), np.max(viol_top))
            
            if max_overlap < 1e-5 and max_viol < 1e-5:
                R += 0.001  # Universe expands
            else:
                R -= 0.0002 # Gravity wins, shrink
            R = max(0.001, R)
            
        # CRAZY IDEA PART 2: Once we have the perfect crystalline lattice, 
        # we decouple the exact boundaries and formulate the final radii maximizing
        # step as an exact Linear Programming problem! (handled in compute_max_radii)
        radii = compute_max_radii(centers, random_seed)
        sum_radii = np.sum(radii)
        
        if sum_radii > best_sum:
            best_sum = sum_radii
            best_centers = centers.copy()
            best_radii = radii

    return best_centers, best_radii, best_sum


def compute_max_radii(centers, random_seed: int):
    """Compute the maximum possible radii for each circle position
    by solving a Linear Programming problem for optimal bounds!

    Args:
        centers: np.array of shape (n, 2) with (x, y) coordinates
        random_seed: Random seed for reproducibility.

    Returns:
        np.array of shape (n) with radius of each circle
    """
    del random_seed  # Unused.
    from scipy.optimize import linprog
    n = centers.shape[0]
    
    # Objective: maximize sum of radii -> minimize -sum(radii)
    c = -np.ones(n)
    
    A_ub = []
    b_ub = []
    
    # 1. Quantum hard-wall constraints: r_i <= distance to all 4 edges
    for i in range(n):
        x, y = centers[i]
        for val in [x, 1 - x, y, 1 - y]:
            row = np.zeros(n)
            row[i] = 1
            A_ub.append(row)
            b_ub.append(val)
            
    # 2. Relativity pairwise constraints: r_i + r_j <= euclidean distance
    for i in range(n):
        for j in range(i + 1, n):
            dist = np.sqrt((centers[i, 0] - centers[j, 0])**2 + (centers[i, 1] - centers[j, 1])**2)
            row = np.zeros(n)
            row[i] = 1
            row[j] = 1
            A_ub.append(row)
            b_ub.append(dist)
            
    # Unleash the Simplex/Interior-Point beast on the exact geometry
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), bounds=(0, None))
    
    # Fallback to greedy scaling if LP fails (extremely rare for feasible geometries)
    if not res.success:
        radii = np.ones(n)
        for i in range(n):
            radii[i] = min(centers[i,0], centers[i,1], 1-centers[i,0], 1-centers[i,1])
        for i in range(n):
            for j in range(i + 1, n):
                dist = np.sqrt(np.sum((centers[i] - centers[j]) ** 2))
                if radii[i] + radii[j] > dist:
                    scale = dist / (radii[i] + radii[j] + 1e-7)
                    radii[i] *= scale
                    radii[j] *= scale
        return radii
        
    return res.x


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