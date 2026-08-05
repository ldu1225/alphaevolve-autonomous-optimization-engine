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

try:
    from scipy.optimize import linprog, minimize
    _HAS_LINPROG = True
except ImportError:
    _HAS_LINPROG = False


def compute_max_radii_fallback(centers):
    """Fallback greedy computation of maximum radii."""
    n = centers.shape[0]
    radii = np.zeros(n)
    for i in range(n):
        x, y = centers[i]
        radii[i] = min(x, y, 1.0 - x, 1.0 - y)

    # Iterative scaling to ensure no overlaps
    for i in range(n):
        for j in range(i + 1, n):
            dist = np.sqrt(np.sum((centers[i] - centers[j]) ** 2))
            if radii[i] + radii[j] > dist:
                scale = dist / (radii[i] + radii[j] + 1e-7)
                radii[i] *= scale
                radii[j] *= scale
    return radii


def compute_optimal_radii(centers):
    """Compute the mathematically optimal radii for given centers using LP."""
    if not _HAS_LINPROG:
        return compute_max_radii_fallback(centers)

    n = centers.shape[0]
    c = -np.ones(n)  # Maximize sum(r_i) <=> Minimize sum(-r_i)

    bounds = []
    for i in range(n):
        x, y = centers[i]
        border_dist = min(x, y, 1.0 - x, 1.0 - y)
        bounds.append((0.0, max(0.0, border_dist)))

    # Pairwise constraints: r_i + r_j <= d_ij
    num_constraints = n * (n - 1) // 2
    A = np.zeros((num_constraints, n))
    b = np.zeros(num_constraints)

    idx = 0
    for i in range(n):
        for j in range(i + 1, n):
            dist = np.sqrt(np.sum((centers[i] - centers[j]) ** 2))
            A[idx, i] = 1.0
            A[idx, j] = 1.0
            b[idx] = dist
            idx += 1

    res = linprog(c, A_ub=A, b_ub=b, bounds=bounds, method='highs')
    if res.success:
        radii = np.clip(res.x, 0.0, None)
        # Ensure strict validity and no small numerical violations
        for i in range(n):
            x, y = centers[i]
            radii[i] = min(radii[i], x, y, 1.0 - x, 1.0 - y)
        for i in range(n):
            for j in range(i + 1, n):
                dist = np.sqrt(np.sum((centers[i] - centers[j]) ** 2))
                if radii[i] + radii[j] > dist:
                    overlap = (radii[i] + radii[j]) - dist
                    radii[i] -= overlap / 2.0
                    radii[j] -= overlap / 2.0
                    radii[i] = max(0.0, radii[i])
                    radii[j] = max(0.0, radii[j])
        return radii
    else:
        return compute_max_radii_fallback(centers)


def get_fibonacci_layout(n, scale=0.4, center=0.5):
    """Generate a highly packing-efficient Fibonacci/Golden spiral layout."""
    phi = (1.0 + np.sqrt(5.0)) / 2.0
    centers = []
    for i in range(n):
        r = np.sqrt(i / (n - 1)) * scale if n > 1 else 0.0
        theta = 2 * np.pi * i / (phi ** 2)
        centers.append([center + r * np.cos(theta), center + r * np.sin(theta)])
    return np.array(centers)


def get_hexagonal_layout(n, rng, spacing=0.09, noise=0.01):
    """Generate a hexagonal/triangular lattice layout centered in the unit square."""
    points = []
    for row in range(15):
        for col in range(15):
            x = col * spacing
            if row % 2 == 1:
                x += spacing / 2.0
            y = row * (spacing * np.sqrt(3) / 2.0)
            if 0.02 <= x <= 0.98 and 0.02 <= y <= 0.98:
                points.append([x, y])
    points = np.array(points)
    if len(points) < n:
        return rng.uniform(0.1, 0.9, (n, 2))
    # Select the n points closest to the center
    dists_to_center = np.sum((points - 0.5) ** 2, axis=1)
    idx = np.argsort(dists_to_center)[:n]
    return points[idx] + rng.normal(0, noise, (n, 2))


def get_ring_layout(n, config, radii_rings):
    """Generate layout based on concentric rings."""
    centers = [[0.5, 0.5]]
    for idx, num in enumerate(config[1:]):
        if idx >= len(radii_rings):
            break
        r = radii_rings[idx]
        for i in range(num):
            a = 2 * np.pi * i / num
            centers.append([0.5 + r * np.cos(a), 0.5 + r * np.sin(a)])
    centers = np.array(centers[:n])
    if len(centers) < n:
        rng = np.random.default_rng(42)
        padding = rng.uniform(0.1, 0.9, (n - len(centers), 2))
        centers = np.vstack([centers, padding])
    return centers


def get_grid_layout(n, rows, cols, rng, noise=0.01):
    """Generate rectangular or square grid layout."""
    xs = np.linspace(0.08, 0.92, cols)
    ys = np.linspace(0.08, 0.92, rows)
    points = np.array([[x, y] for x in xs for y in ys])
    if len(points) < n:
        return rng.uniform(0.1, 0.9, (n, 2))
    dists_to_center = np.sum((points - 0.5) ** 2, axis=1)
    idx = np.argsort(dists_to_center)[:n]
    return points[idx] + rng.normal(0, noise, (n, 2))


def quick_samd(n, init_centers, rng, steps=180):
    """Fast pre-optimization using Simulated Annealing Momentum Dynamics."""
    x = init_centers.copy()
    r = np.ones(n) * 0.05

    v_x = np.zeros_like(x)
    v_r = np.zeros_like(r)

    lr_x = 0.015
    lr_r = 0.015
    momentum = 0.9
    noise = 0.015

    C_overlap = 150.0
    C_boundary = 150.0

    for step in range(steps):
        diff = x[:, None, :] - x[None, :, :]
        dists = np.sqrt(np.sum(diff ** 2, axis=-1)) + 1e-9

        r_sum = r[:, None] + r[None, :]
        overlap = r_sum - dists
        overlap_mask = (overlap > 0)
        np.fill_diagonal(overlap_mask, False)

        b_left = x[:, 0]
        b_right = 1.0 - x[:, 0]
        b_bottom = x[:, 1]
        b_top = 1.0 - x[:, 1]
        bists = np.column_stack([b_left, b_right, b_bottom, b_top])
        b_overlap = r[:, None] - bists
        b_overlap_mask = b_overlap > 0

        g_x = np.zeros_like(x)
        g_r = np.zeros_like(r)

        dir_vecs = diff / dists[:, :, None]
        g_x += C_overlap * np.sum((overlap * overlap_mask)[:, :, None] * (-dir_vecs), axis=1)
        g_r += C_overlap * np.sum(overlap * overlap_mask, axis=1)

        g_x[:, 0] += C_boundary * b_overlap[:, 0] * b_overlap_mask[:, 0] * (-1.0)
        g_x[:, 0] += C_boundary * b_overlap[:, 1] * b_overlap_mask[:, 1] * (1.0)
        g_x[:, 1] += C_boundary * b_overlap[:, 2] * b_overlap_mask[:, 2] * (-1.0)
        g_x[:, 1] += C_boundary * b_overlap[:, 3] * b_overlap_mask[:, 3] * (1.0)

        g_r += C_boundary * np.sum(b_overlap * b_overlap_mask, axis=1)
        g_r += -1.0

        v_x = momentum * v_x - lr_x * g_x
        if noise > 1e-4:
            v_x += noise * rng.normal(0, 1, x.shape)
        x += v_x

        v_r = momentum * v_r - lr_r * g_r
        if noise > 1e-4:
            v_r += noise * rng.normal(0, 1, r.shape)
        r += v_r

        x = np.clip(x, 1e-5, 1.0 - 1e-5)
        r = np.clip(r, 0.005, 0.5)

        lr_x *= 0.99
        lr_r *= 0.99
        noise *= 0.98

    return x


def slsqp_optimize(n, init_centers, max_iter=100):
    """High-precision local optimization of centers and radii using SLSQP."""
    init_radii = compute_optimal_radii(init_centers)
    theta_0 = np.concatenate([init_centers.flatten(), init_radii])
    
    bounds = []
    for _ in range(n):
        bounds.extend([(0.0, 1.0), (0.0, 1.0)])
    for _ in range(n):
        bounds.append((0.0, 0.5))
        
    def objective(theta):
        return -np.sum(theta[2*n:])
        
    triu_indices = np.triu_indices(n, k=1)
    
    def constraints_func(theta):
        x = theta[:2*n].reshape((n, 2))
        r = theta[2*n:]
        
        c_bounds = np.empty(4 * n)
        c_bounds[0::4] = x[:, 0] - r
        c_bounds[1::4] = 1.0 - x[:, 0] - r
        c_bounds[2::4] = x[:, 1] - r
        c_bounds[3::4] = 1.0 - x[:, 1] - r
        
        diff = x[:, None, :] - x[None, :, :]
        dists = np.sqrt(np.sum(diff**2, axis=-1) + 1e-12)
        r_sum = r[:, None] + r[None, :]
        
        c_overlap = dists[triu_indices] - r_sum[triu_indices]
        return np.concatenate([c_bounds, c_overlap])
        
    cons = {'type': 'ineq', 'fun': constraints_func}
    
    res = minimize(
        objective,
        theta_0,
        method='SLSQP',
        bounds=bounds,
        constraints=cons,
        options={'maxiter': max_iter, 'ftol': 1e-8}
    )
    
    best_theta = res.x
    centers = np.clip(best_theta[:2*n].reshape((n, 2)), 0.0, 1.0)
    radii = compute_optimal_radii(centers)
    return centers, radii, np.sum(radii)


def refine_candidate_with_basin_hopping(n, init_centers, rng, num_hops=3):
    """Run local optimization coupled with a Basin-Hopping metaheuristic."""
    best_centers, best_radii, best_sum = slsqp_optimize(n, init_centers, max_iter=120)
    current_centers = best_centers.copy()
    
    for hop in range(num_hops):
        perturbed_centers = current_centers + rng.normal(0, 0.012, current_centers.shape)
        perturbed_centers = np.clip(perturbed_centers, 1e-5, 1.0 - 1e-5)
        
        centers, radii, cur_sum = slsqp_optimize(n, perturbed_centers, max_iter=100)
        if cur_sum > best_sum:
            best_sum = cur_sum
            best_centers = centers.copy()
            best_radii = radii.copy()
            current_centers = centers.copy()
        else:
            current_centers = best_centers.copy()
            
    return best_centers, best_radii, best_sum


def optimize_positions(n, seed):
    """Run parallelized multi-start search with diverse layout generators and joint optimization."""
    rng = np.random.default_rng(seed)

    trials = []

    # 1. Fibonacci Spiral layouts (highly optimal)
    for scale in [0.32, 0.35, 0.37, 0.39, 0.41, 0.43, 0.45]:
        trials.append(get_fibonacci_layout(n, scale))

    for scale in [0.36, 0.39, 0.42]:
        for dx, dy in [(-0.02, -0.02), (0.02, 0.02), (0.0, 0.0)]:
            trials.append(get_fibonacci_layout(n, scale, center=0.5) + np.array([dx, dy]))

    # 2. Concentric rings
    ring_configs = [
        ([1, 6, 12, 7], [0.15, 0.3, 0.44]),
        ([1, 5, 11, 9], [0.14, 0.28, 0.42]),
        ([1, 7, 12, 6], [0.16, 0.31, 0.43]),
        ([1, 6, 11, 8], [0.15, 0.29, 0.43]),
        ([1, 8, 17], [0.2, 0.4]),
        ([1, 7, 18], [0.18, 0.38]),
    ]
    for conf, rads in ring_configs:
        trials.append(get_ring_layout(n, conf, rads))

    # 3. Hexagonal lattices
    for spacing in [0.08, 0.09, 0.10, 0.11]:
        for noise in [0.0, 0.01]:
            trials.append(get_hexagonal_layout(n, rng, spacing, noise))

    # 4. Grids
    for rows, cols in [(5, 5), (5, 6), (6, 6)]:
        for noise in [0.0, 0.01]:
            trials.append(get_grid_layout(n, rows, cols, rng, noise))

    # 5. Populate remaining layouts with perturbed Fibonacci spirals & random trials
    while len(trials) < 45:
        base = get_fibonacci_layout(n, rng.uniform(0.35, 0.45))
        base += rng.normal(0, 0.02, base.shape)
        trials.append(np.clip(base, 0.05, 0.95))

    # Screen candidates using quick SAMD
    screened_candidates = []
    for init_centers in trials:
        centers = quick_samd(n, init_centers, rng)
        radii = compute_optimal_radii(centers)
        score = np.sum(radii)
        screened_candidates.append((score, centers))

    # Sort screened candidates descending by score
    screened_candidates.sort(key=lambda item: item[0], reverse=True)

    best_sum = 0
    best_centers = None
    best_radii = None

    # Refine top candidates using Basin-Hopping SLSQP
    # Run 4 hops for top 4 candidates, and 2 hops for next 4 candidates
    for idx in range(min(8, len(screened_candidates))):
        score, centers = screened_candidates[idx]
        num_hops = 4 if idx < 4 else 2
        
        refined_centers, refined_radii, refined_sum = refine_candidate_with_basin_hopping(
            n, centers, rng, num_hops=num_hops
        )
        
        if refined_sum > best_sum:
            best_sum = refined_sum
            best_centers = refined_centers.copy()
            best_radii = refined_radii.copy()

    return best_centers, best_radii, best_sum


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
    centers, radii, sum_radii = optimize_positions(n, random_seed)
    return centers, radii, sum_radii


def compute_max_radii(centers, random_seed: int = 0):
    """Compute the maximum possible radii for each circle position.

    Make sure that they don't overlap and stay within the unit square.

    Args:
        centers: np.array of shape (n, 2) with (x, y) coordinates
        random_seed: Random seed for reproducibility.

    Returns:
        np.array of shape (n) with radius of each circle
    """
    return compute_optimal_radii(centers)


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