"""
AlphaEvolve Generated Candidate #8
Score: 2.3856099812717035
Candidate ID: 1014377268021464115
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
from scipy.optimize import linprog, minimize


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

    def make_fibonacci_spiral(n, rng):
        centers = np.zeros((n, 2))
        golden_ratio = (1 + 5**0.5) / 2
        for i in range(n):
            theta = 2 * np.pi * i * golden_ratio
            r = np.sqrt(i / (n - 1)) * 0.42
            centers[i] = [0.5 + r * np.cos(theta), 0.5 + r * np.sin(theta)]
        return centers

    def make_concentric_rings(n, rng):
        centers = np.zeros((n, 2))
        centers[0] = [0.5, 0.5]
        for i in range(8):
            angle = 2 * np.pi * i / 8 + rng.uniform(-0.1, 0.1)
            centers[i + 1] = [0.5 + 0.22 * np.cos(angle), 0.5 + 0.22 * np.sin(angle)]
        for i in range(17):
            angle = 2 * np.pi * i / 17 + rng.uniform(-0.1, 0.1)
            centers[i + 9] = [0.5 + 0.41 * np.cos(angle), 0.5 + 0.41 * np.sin(angle)]
        return centers

    def make_hexagonal_grid_with_scale(n, scale, rng):
        points = []
        for r in range(12):
            for c in range(12):
                x = (c + 0.5 * (r % 2)) * 0.12 * scale
                y = r * (np.sqrt(3) / 2) * 0.12 * scale
                x += (1.0 - 11 * 0.12 * scale) / 2
                y += (1.0 - 11 * (np.sqrt(3) / 2) * 0.12 * scale) / 2
                if 0.02 < x < 0.98 and 0.02 < y < 0.98:
                    points.append([x, y])
        points = np.array(points)
        if len(points) < n:
            return rng.uniform(0.05, 0.95, (n, 2))
        dists = np.sum((points - 0.5) ** 2, axis=1)
        idx = np.argsort(dists)
        return points[idx[:n]]

    def make_grid_with_jitter(n, rng):
        points = []
        for x in np.linspace(0.1, 0.9, 6):
            for y in np.linspace(0.1, 0.9, 5):
                points.append([x + rng.uniform(-0.02, 0.02), y + rng.uniform(-0.02, 0.02)])
        points = np.array(points)
        rng.shuffle(points)
        return points[:n]

    def relax_centers(centers, steps=150, lr=0.008):
        pos = centers.copy()
        vel = np.zeros_like(pos)
        for _ in range(steps):
            forces = np.zeros_like(pos)
            for i in range(n):
                for j in range(i + 1, n):
                    diff = pos[i] - pos[j]
                    dist = np.linalg.norm(diff) + 1e-5
                    if dist < 0.35:
                        f_val = 1.0 / (dist**3)
                        force = (diff / dist) * f_val
                        forces[i] += force
                        forces[j] -= force

            for i in range(n):
                forces[i, 0] += 1.0 / (pos[i, 0] ** 3)
                forces[i, 0] -= 1.0 / ((1.0 - pos[i, 0]) ** 3)
                forces[i, 1] += 1.0 / (pos[i, 1] ** 3)
                forces[i, 1] -= 1.0 / ((1.0 - pos[i, 1]) ** 3)

            vel = vel * 0.85 + forces * lr
            step_len = np.linalg.norm(vel, axis=1, keepdims=True)
            max_step = 0.04
            vel = np.where(step_len > max_step, vel / step_len * max_step, vel)
            pos += vel
            pos = np.clip(pos, 0.002, 0.998)
        return pos

    candidates = []
    candidates.append(make_fibonacci_spiral(n, rng))
    candidates.append(make_concentric_rings(n, rng))
    for scale in [0.75, 0.85, 0.95]:
        candidates.append(make_hexagonal_grid_with_scale(n, scale, rng))
    for _ in range(3):
        candidates.append(make_grid_with_jitter(n, rng))
    for _ in range(2):
        candidates.append(rng.uniform(0.1, 0.9, (n, 2)))

    best_centers = None
    best_sum_radii = -1.0

    def fast_eval(centers):
        radii = np.zeros(n)
        for i in range(n):
            x, y = centers[i]
            radii[i] = min(x, y, 1.0 - x, 1.0 - y)
        for _ in range(12):
            for i in range(n):
                for j in range(i + 1, n):
                    dist = np.sqrt((centers[i, 0] - centers[j, 0]) ** 2 + (centers[i, 1] - centers[j, 1]) ** 2)
                    if radii[i] + radii[j] > dist:
                        tot = radii[i] + radii[j]
                        if tot > 0:
                            scale = dist / tot
                            radii[i] *= scale
                            radii[j] *= scale
        return np.sum(radii)

    relaxed_candidates = []
    for c in candidates:
        relaxed = relax_centers(c)
        score = fast_eval(relaxed)
        relaxed_candidates.append((score, relaxed))

    relaxed_candidates.sort(key=lambda x: x[0], reverse=True)
    top_candidates = [x[1] for x in relaxed_candidates[:3]]

    def obj(flat_centers):
        centers = np.clip(flat_centers.reshape((n, 2)), 0.001, 0.999)
        return -fast_eval(centers)

    for tc in top_candidates:
        x0 = tc.flatten()
        bounds = [(0.001, 0.999)] * (2 * n)
        res = minimize(obj, x0, method="L-BFGS-B", bounds=bounds, options={'maxiter': 60})
        opt_centers = np.clip(res.x.reshape((n, 2)), 0.001, 0.999)
        exact_radii = compute_max_radii(opt_centers, random_seed)
        score = np.sum(exact_radii)

        if score > best_sum_radii:
            best_sum_radii = score
            best_centers = opt_centers

    radii = compute_max_radii(best_centers, random_seed)
    sum_radii = np.sum(radii)

    return best_centers, radii, sum_radii


def compute_max_radii(centers, random_seed: int):
    """Compute the maximum possible radii for each circle position.

    Make sure that they don't overlap and stay within the unit square.

    Args:
        centers: np.array of shape (n, 2) with (x, y) coordinates
        random_seed: Random seed for reproducibility.

    Returns:
        np.array of shape (n) with radius of each circle
    """
    del random_seed
    n = centers.shape[0]
    c = -np.ones(n)

    bounds = []
    for i in range(n):
        x, y = centers[i]
        max_r = min(x, y, 1.0 - x, 1.0 - y)
        bounds.append((0.0, max(0.0, max_r)))

    num_pairs = n * (n - 1) // 2
    A_ub = np.zeros((num_pairs, n))
    b_ub = np.zeros(num_pairs)

    idx = 0
    for i in range(n):
        for j in range(i + 1, n):
            dist = np.sqrt(np.sum((centers[i] - centers[j]) ** 2))
            A_ub[idx, i] = 1.0
            A_ub[idx, j] = 1.0
            b_ub[idx] = dist
            idx += 1

    try:
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
        if res.success:
            return res.x
    except Exception:
        pass

    radii = np.zeros(n)
    for i in range(n):
        x, y = centers[i]
        radii[i] = min(x, y, 1.0 - x, 1.0 - y)
    for _ in range(50):
        for i in range(n):
            for j in range(i + 1, n):
                dist = np.sqrt(np.sum((centers[i] - centers[j]) ** 2))
                if radii[i] + radii[j] > dist:
                    tot = radii[i] + radii[j]
                    if tot > 0:
                        scale = dist / tot
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