"""
AlphaEvolve Generated Candidate #2
Score: 2.307227492098305
Candidate ID: 1014377268021462807
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
from scipy.optimize import linprog


def compute_max_radii_fast(centers):
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


def compute_max_radii_lp(centers):
    n = centers.shape[0]
    c = -np.ones(n)

    bounds = []
    for i in range(n):
        x, y = centers[i]
        max_r = min(x, y, 1 - x, 1 - y)
        bounds.append((0.0, max(0.0, max_r - 1e-6)))

    A = []
    b = []
    for i in range(n):
        for j in range(i + 1, n):
            row = np.zeros(n)
            row[i] = 1.0
            row[j] = 1.0
            dist = np.linalg.norm(centers[i] - centers[j])
            A.append(row)
            b.append(max(0.0, dist - 1e-6))

    try:
        res = linprog(c, A_ub=A, b_ub=b, bounds=bounds, method="highs")
    except Exception:
        try:
            res = linprog(c, A_ub=A, b_ub=b, bounds=bounds)
        except Exception:
            return compute_max_radii_fast(centers)

    if res.success:
        return res.x
    else:
        return compute_max_radii_fast(centers)


def get_grid_initializations(n, rng):
    candidates = []
    for w in range(2, 12):
        for h in range(2, 12):
            if w * h < n:
                continue
            xs = np.linspace(1 / (2 * w), 1 - 1 / (2 * w), w)
            ys = np.linspace(1 / (2 * h), 1 - 1 / (2 * h), h)
            grid_points = []
            for y in ys:
                for x in xs:
                    grid_points.append([x, y])
            grid_points = np.array(grid_points)

            candidates.append(grid_points[:n])
            dist_to_center = np.linalg.norm(grid_points - 0.5, axis=1)
            idx_center = np.argsort(dist_to_center)[:n]
            candidates.append(grid_points[idx_center])

            if w * h > n:
                for _ in range(3):
                    idx_rand = rng.choice(w * h, size=n, replace=False)
                    candidates.append(grid_points[idx_rand])
    return candidates


def get_triangular_initializations(n, rng):
    candidates = []
    for w in range(2, 12):
        for h in range(2, 12):
            if w * h < n:
                continue
            grid_points = []
            for r in range(h):
                for c in range(w):
                    x = c + 0.5 * (r % 2)
                    y = r * np.sqrt(3) / 2
                    grid_points.append([x, y])
            grid_points = np.array(grid_points)
            min_val = grid_points.min(axis=0)
            max_val = grid_points.max(axis=0)
            grid_points = 0.05 + 0.9 * (grid_points - min_val) / (
                max_val - min_val + 1e-9
            )

            candidates.append(grid_points[:n])
            dist_to_center = np.linalg.norm(grid_points - 0.5, axis=1)
            idx_center = np.argsort(dist_to_center)[:n]
            candidates.append(grid_points[idx_center])

            if w * h > n:
                for _ in range(3):
                    idx_rand = rng.choice(w * h, size=n, replace=False)
                    candidates.append(grid_points[idx_rand])
    return candidates


def get_spiral_initialization(n):
    indices = np.arange(0, n) + 0.5
    r = np.sqrt(indices / n) / 2
    theta = np.pi * (1 + 5**0.5) * indices
    x = 0.5 + r * np.cos(theta)
    y = 0.5 + r * np.sin(theta)
    return np.column_stack((x, y))


def get_all_initializations(n, rng):
    candidates = []
    candidates.extend(get_grid_initializations(n, rng))
    candidates.extend(get_triangular_initializations(n, rng))
    candidates.append(get_spiral_initialization(n))

    centers_concentric = np.zeros((n, 2))
    centers_concentric[0] = [0.5, 0.5]
    for i in range(8):
        angle = 2 * np.pi * i / 8
        centers_concentric[i + 1] = [
            0.5 + 0.3 * np.cos(angle),
            0.5 + 0.3 * np.sin(angle),
        ]
    for i in range(17):
        if i + 9 >= n:
            break
        angle = 2 * np.pi * i / 17
        centers_concentric[i + 9] = [
            0.5 + 0.7 * np.cos(angle),
            0.5 + 0.7 * np.sin(angle),
        ]
    candidates.append(centers_concentric)

    for _ in range(20):
        candidates.append(rng.uniform(0.05, 0.95, size=(n, 2)))

    cleaned_candidates = []
    for c in candidates:
        if c.shape == (n, 2):
            c_clipped = np.clip(c, 0.01, 0.99)
            cleaned_candidates.append(c_clipped)

    return cleaned_candidates


def force_directed_relaxation(centers, steps=500, lr=0.005, decay=0.9):
    n = len(centers)
    vel = np.zeros_like(centers)
    best_centers = centers.copy()
    best_sum = 0

    for step in range(steps):
        diff = centers[:, np.newaxis, :] - centers[np.newaxis, :, :]
        dist = np.linalg.norm(diff, axis=2)
        np.fill_diagonal(dist, 1.0)
        dist3 = dist[:, :, np.newaxis] ** 3

        forces_pairwise = (diff / dist3).sum(axis=1)

        x = centers[:, 0]
        y = centers[:, 1]
        forces_boundary = np.zeros_like(centers)
        forces_boundary[:, 0] = 1.0 / (x**2 + 1e-8) - 1.0 / (
            (1 - x) ** 2 + 1e-8
        )
        forces_boundary[:, 1] = 1.0 / (y**2 + 1e-8) - 1.0 / (
            (1 - y) ** 2 + 1e-8
        )

        forces = forces_pairwise * 0.01 + forces_boundary * 0.05

        vel = vel * decay + forces * lr
        step_len = np.linalg.norm(vel, axis=1, keepdims=True) + 1e-8
        max_step = 0.02
        vel = np.where(step_len > max_step, vel / step_len * max_step, vel)

        centers += vel
        centers = np.clip(centers, 0.01, 0.99)

        if step % 50 == 0 or step == steps - 1:
            radii = compute_max_radii_fast(centers)
            s = np.sum(radii)
            if s > best_sum:
                best_sum = s
                best_centers = centers.copy()

    return best_centers


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

    # 1. Gather all candidate initializations
    candidates = get_all_initializations(n, rng)

    # 2. Evaluate all candidates using the fast radii computation
    candidate_scores = []
    for c in candidates:
        radii = compute_max_radii_fast(c)
        candidate_scores.append(np.sum(radii))

    # Sort candidates in descending order of score
    sorted_idx = np.argsort(candidate_scores)[::-1]
    sorted_candidates = [candidates[i] for i in sorted_idx]

    # 3. Take the top K candidates for relaxation
    top_k = sorted_candidates[:15]
    relaxed_candidates = []
    relaxed_scores = []

    for c in top_k:
        relaxed_c = force_directed_relaxation(c)
        radii_fast = compute_max_radii_fast(relaxed_c)
        score_fast = np.sum(radii_fast)
        relaxed_candidates.append(relaxed_c)
        relaxed_scores.append(score_fast)

    # Sort the relaxed candidates
    sorted_relaxed_idx = np.argsort(relaxed_scores)[::-1]
    best_relaxed_candidates = [relaxed_candidates[i] for i in sorted_relaxed_idx]

    # 4. Run the LP solver on the top 5 relaxed candidates to find the absolute best
    best_centers = None
    best_radii = None
    best_sum = -1.0

    for i in range(min(5, len(best_relaxed_candidates))):
        centers = best_relaxed_candidates[i]
        radii = compute_max_radii_lp(centers)
        s = np.sum(radii)
        if s > best_sum:
            best_sum = s
            best_centers = centers
            best_radii = radii

    # If something went wrong, fallback to the best fast candidate
    if best_centers is None:
        best_centers = best_relaxed_candidates[0]
        best_radii = compute_max_radii_fast(best_centers)
        best_sum = np.sum(best_radii)

    return best_centers, best_radii, best_sum


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