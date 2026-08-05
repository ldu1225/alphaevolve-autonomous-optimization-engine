"""
AlphaEvolve Generated Candidate #3
Score: 2.132200140788197
Candidate ID: 1014377268021461591
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


def compute_max_radii_heuristic_vectorized(centers):
    n = len(centers)
    radii = np.minimum(
        np.minimum(centers[:, 0], centers[:, 1]),
        np.minimum(1.0 - centers[:, 0], 1.0 - centers[:, 1]),
    )
    diffs = centers[:, np.newaxis, :] - centers[np.newaxis, :, :]
    dists = np.sqrt(np.sum(diffs**2, axis=-1))

    for _ in range(3):
        sum_r = radii[:, np.newaxis] + radii[np.newaxis, :]
        overlap = sum_r - dists
        overlap[np.diag_indices(n)] = 0.0

        scale_matrix = dists / (sum_r + 1e-9)
        scale_matrix[dists == 0] = 1.0
        scale_matrix = np.where(overlap > 0, scale_matrix, 1.0)
        min_scales = np.min(scale_matrix, axis=1)
        radii *= min_scales

    return radii


def relax_centers(centers, rng, num_steps=200):
    n = len(centers)
    centers = centers.copy()
    for step in range(num_steps):
        radii = compute_max_radii_heuristic_vectorized(centers)
        diffs = centers[:, np.newaxis, :] - centers[np.newaxis, :, :]
        dists = np.sqrt(np.sum(diffs**2, axis=-1, keepdims=True))

        sum_r = radii[:, np.newaxis, np.newaxis] + radii[np.newaxis, :, np.newaxis]
        overlap = sum_r - dists

        mask = (overlap > 0) & (dists > 0)
        force_direction = diffs / (dists + 1e-9)
        pairwise_forces = np.where(mask, (overlap / (dists + 1e-9)) * force_direction, 0.0)
        forces = np.sum(pairwise_forces, axis=1)

        left_dist = centers[:, 0]
        right_dist = 1.0 - centers[:, 0]
        forces[:, 0] += np.where(left_dist < radii, radii - left_dist, 0.0)
        forces[:, 0] -= np.where(right_dist < radii, radii - right_dist, 0.0)

        bottom_dist = centers[:, 1]
        top_dist = 1.0 - centers[:, 1]
        forces[:, 1] += np.where(bottom_dist < radii, radii - bottom_dist, 0.0)
        forces[:, 1] -= np.where(top_dist < radii, radii - top_dist, 0.0)

        step_size = 0.05 * (1.0 - step / num_steps)

        if step < num_steps // 3:
            noise = rng.normal(0, 1e-3 * (1 - step / (num_steps // 3)), centers.shape)
            centers += noise

        force_norm = np.linalg.norm(forces, axis=1, keepdims=True)
        max_force = 0.05
        scale = np.minimum(1.0, max_force / (force_norm + 1e-8))
        forces *= scale

        centers += step_size * forces
        centers = np.clip(centers, 1e-5, 1 - 1e-5)

    return centers


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
    candidates = []

    # 1. Concentric rings (various configurations)
    if n >= 9:
        c = np.zeros((n, 2))
        c[0] = [0.5, 0.5]
        r1 = min(8, n - 1)
        for i in range(r1):
            angle = 2 * np.pi * i / r1
            c[i + 1] = [0.5 + 0.25 * np.cos(angle), 0.5 + 0.25 * np.sin(angle)]
        r2 = n - 1 - r1
        if r2 > 0:
            for i in range(r2):
                angle = 2 * np.pi * i / r2
                c[i + 1 + r1] = [0.5 + 0.45 * np.cos(angle), 0.5 + 0.45 * np.sin(angle)]
        candidates.append(c)

    if n >= 20:
        c = np.zeros((n, 2))
        c[0] = [0.5, 0.5]
        for i in range(6):
            angle = 2 * np.pi * i / 6
            c[i + 1] = [0.5 + 0.18 * np.cos(angle), 0.5 + 0.18 * np.sin(angle)]
        for i in range(12):
            angle = 2 * np.pi * i / 12
            c[i + 7] = [0.5 + 0.35 * np.cos(angle), 0.5 + 0.35 * np.sin(angle)]
        r3 = n - 19
        for i in range(r3):
            angle = 2 * np.pi * i / r3
            c[i + 19] = [0.5 + 0.46 * np.cos(angle), 0.5 + 0.46 * np.sin(angle)]
        candidates.append(c)

    # 2. Fibonacci spiral
    c = np.zeros((n, 2))
    golden_ratio = (1 + 5**0.5) / 2
    for i in range(n):
        theta = 2 * np.pi * i / golden_ratio**2
        r = 0.45 * np.sqrt((i + 0.5) / n)
        c[i] = [0.5 + r * np.cos(theta), 0.5 + r * np.sin(theta)]
    candidates.append(c)

    # 3. Hexagonal lattices
    for rows in [6, 7]:
        for cols in [6, 7]:
            pts = []
            for r in range(rows):
                for col in range(cols):
                    x = (col + 0.5 * (r % 2)) / (cols - 0.5) if cols > 1 else 0.5
                    y = r / (rows - 1) if rows > 1 else 0.5
                    pts.append([x, y])
            pts = np.array(pts)
            pts = 0.05 + 0.9 * pts
            if len(pts) >= n:
                dists = np.sum((pts - 0.5) ** 2, axis=1)
                idx = np.argsort(dists)[:n]
                candidates.append(pts[idx])

    # 4. Grid selections
    grid_w = int(np.ceil(np.sqrt(n * 1.2)))
    grid_h = int(np.ceil(n * 1.2 / grid_w))
    xs = np.linspace(0.1, 0.9, grid_w)
    ys = np.linspace(0.1, 0.9, grid_h)
    grid = np.array([[x, y] for x in xs for y in ys])
    if len(grid) >= n:
        for _ in range(5):
            idx = rng.choice(len(grid), n, replace=False)
            candidates.append(grid[idx])

    # 5. Random uniform
    for _ in range(5):
        candidates.append(rng.uniform(0.1, 0.9, (n, 2)))

    # Relax candidates
    relaxed_candidates = []
    heuristic_scores = []
    for cand in candidates:
        relaxed = relax_centers(cand, rng, num_steps=200)
        relaxed_candidates.append(relaxed)
        h_radii = compute_max_radii_heuristic_vectorized(relaxed)
        heuristic_scores.append(np.sum(h_radii))

    top_indices = np.argsort(heuristic_scores)[::-1][:6]
    best_centers = None
    best_radii = None
    best_sum = -1.0

    for idx in top_indices:
        cand = relaxed_candidates[idx]
        radii = compute_max_radii(cand, random_seed)
        s = np.sum(radii)
        if s > best_sum:
            best_sum = s
            best_centers = cand
            best_radii = radii

    return best_centers, best_radii, best_sum


def compute_max_radii(centers, random_seed: int = 42):
    """Compute the maximum possible radii for each circle position.

    Make sure that they don't overlap and stay within the unit square.

    Args:
        centers: np.array of shape (n, 2) with (x, y) coordinates
        random_seed: Random seed for reproducibility.

    Returns:
        np.array of shape (n) with radius of each circle
    """
    try:
        from scipy.optimize import linprog

        n = centers.shape[0]
        c = -np.ones(n)
        bounds = []
        for i in range(n):
            x, y = centers[i]
            max_r = min(x, y, 1 - x, 1 - y)
            bounds.append((0.0, max(1e-6, max_r)))

        A = []
        b = []
        for i in range(n):
            for j in range(i + 1, n):
                dist = np.linalg.norm(centers[i] - centers[j])
                row = np.zeros(n)
                row[i] = 1.0
                row[j] = 1.0
                A.append(row)
                b.append(dist)

        res = linprog(c, A_ub=A, b_ub=b, bounds=bounds, method="highs")
        if res.success:
            return res.x
    except Exception:
        pass

    # Fallback to a simple heuristic if LP fails
    n = centers.shape[0]
    radii = np.ones(n)
    for i in range(n):
        x, y = centers[i]
        radii[i] = min(x, y, 1 - x, 1 - y)

    for i in range(n):
        for j in range(i + 1, n):
            dist = np.sqrt(np.sum((centers[i] - centers[j]) ** 2))
            if radii[i] + radii[j] > dist:
                scale = dist / (radii[i] + radii[j] + 1e-7)
                radii[i] *= scale
                radii[j] *= scale
    return radii


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