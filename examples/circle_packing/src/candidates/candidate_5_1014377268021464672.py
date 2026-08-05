"""
AlphaEvolve Generated Candidate #5
Score: -1000000000000.0
Candidate ID: 1014377268021464672
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

    # Define objective and its gradient
    def objective(p):
        return -np.sum(p[2 * n :])

    def objective_grad(p):
        grad = np.zeros_like(p)
        grad[2 * n :] = -1.0
        return grad

    # Define constraint function and its Jacobian
    def constraints_func(p):
        c_x = p[0:n]
        c_y = p[n : 2 * n]
        r = p[2 * n :]

        b1 = c_x - r
        b2 = 1.0 - c_x - r
        b3 = c_y - r
        b4 = 1.0 - c_y - r

        dx = c_x[:, None] - c_x[None, :]
        dy = c_y[:, None] - c_y[None, :]
        dist = np.sqrt(dx**2 + dy**2 + 1e-12)
        r_sum = r[:, None] + r[None, :]
        overlap = dist - r_sum

        iu = np.triu_indices(n, k=1)
        pairwise_constraints = overlap[iu]

        return np.concatenate([b1, b2, b3, b4, pairwise_constraints])

    def constraints_jac(p):
        c_x = p[0:n]
        c_y = p[n : 2 * n]
        r = p[2 * n :]

        M = n * (n - 1) // 2
        jac = np.zeros((4 * n + M, 3 * n))

        # Boundary constraints derivatives
        jac[0:n, 0:n] = np.eye(n)
        jac[0:n, 2 * n :] = -np.eye(n)

        jac[n : 2 * n, 0:n] = -np.eye(n)
        jac[n : 2 * n, 2 * n :] = -np.eye(n)

        jac[2 * n : 3 * n, n : 2 * n] = np.eye(n)
        jac[2 * n : 3 * n, 2 * n :] = -np.eye(n)

        jac[3 * n : 4 * n, n : 2 * n] = -np.eye(n)
        jac[3 * n : 4 * n, 2 * n :] = -np.eye(n)

        # Pairwise constraints derivatives
        iu1, iu2 = np.triu_indices(n, k=1)
        dx = c_x[iu1] - c_x[iu2]
        dy = c_y[iu1] - c_y[iu2]
        dist = np.sqrt(dx**2 + dy**2 + 1e-12)

        rows = np.arange(4 * n, 4 * n + M)
        jac[rows, iu1] = dx / dist
        jac[rows, iu2] = -dx / dist
        jac[rows, n + iu1] = dy / dist
        jac[rows, n + iu2] = -dy / dist
        jac[rows, 2 * n + iu1] = -1.0
        jac[rows, 2 * n + iu2] = -1.0

        return jac

    # Particle relaxation helper
    def relax_centers(centers, n_iter=60):
        for _ in range(n_iter):
            dx = centers[:, None, 0] - centers[None, :, 0]
            dy = centers[:, None, 1] - centers[None, :, 1]
            dist = np.sqrt(dx**2 + dy**2 + 1e-12)

            threshold = 0.18
            force_mag = np.maximum(0.0, threshold - dist)

            dir_x = dx / dist
            dir_y = dy / dist

            fx = np.sum(force_mag * dir_x, axis=1)
            fy = np.sum(force_mag * dir_y, axis=1)

            centers[:, 0] += 0.05 * fx
            centers[:, 1] += 0.05 * fy

            # Boundary force
            for i in range(n):
                x, y = centers[i]
                if x < 0.05:
                    centers[i, 0] = 0.05
                if x > 0.95:
                    centers[i, 0] = 0.95
                if y < 0.05:
                    centers[i, 1] = 0.05
                if y > 0.95:
                    centers[i, 1] = 0.95
        return centers

    # Generate diverse initial configurations
    initial_states = []

    # 1. 5x5 grid + 1 center
    grid_x, grid_y = np.meshgrid(np.linspace(0.1, 0.9, 5), np.linspace(0.1, 0.9, 5))
    grid_points = np.stack([grid_x.ravel(), grid_y.ravel()], axis=1)
    grid_points = np.vstack([grid_points, [0.5, 0.5]])
    initial_states.append(grid_points)

    # 2. Hexagonal-like grid
    hex_points = []
    for i in range(-5, 6):
        for j in range(-5, 6):
            x = i * 0.18 + (j % 2) * 0.09
            y = j * 0.15
            if 0.05 <= x + 0.5 <= 0.95 and 0.05 <= y + 0.5 <= 0.95:
                hex_points.append([x + 0.5, y + 0.5])
    hex_points = np.array(hex_points)
    if len(hex_points) >= n:
        dists = np.sum((hex_points - 0.5) ** 2, axis=1)
        idx = np.argsort(dists)
        initial_states.append(hex_points[idx[:n]])
    else:
        initial_states.append(rng.uniform(0.1, 0.9, (n, 2)))

    # 3. Fibonacci spiral
    fib_points = []
    golden_ratio = (1 + 5**0.5) / 2
    for i in range(n):
        t = i / n
        r_val = np.sqrt(t) * 0.45
        theta = 2 * np.pi * golden_ratio * i
        fib_points.append([0.5 + r_val * np.cos(theta), 0.5 + r_val * np.sin(theta)])
    initial_states.append(np.array(fib_points))

    # 4. Concentric rings
    ring_points = [[0.5, 0.5]]
    for i in range(5):
        angle = 2 * np.pi * i / 5
        ring_points.append(
            [0.5 + 0.15 * np.cos(angle), 0.5 + 0.15 * np.sin(angle)]
        )
    for i in range(9):
        angle = 2 * np.pi * i / 9
        ring_points.append([0.5 + 0.3 * np.cos(angle), 0.5 + 0.3 * np.sin(angle)])
    for i in range(11):
        angle = 2 * np.pi * i / 11
        ring_points.append(
            [0.5 + 0.43 * np.cos(angle), 0.5 + 0.43 * np.sin(angle)]
        )
    ring_points = np.array(ring_points)
    if len(ring_points) == n:
        initial_states.append(ring_points)

    # 5. Rest are random configurations
    for _ in range(40):
        initial_states.append(rng.uniform(0.1, 0.9, (n, 2)))

    # Run SLSQP optimization on all configurations
    from scipy.optimize import minimize

    best_val = -1e9
    best_centers = initial_states[0].copy()

    for init_centers in initial_states:
        relaxed = relax_centers(init_centers.copy(), n_iter=60)
        init_radii = np.ones(n) * 0.01

        p0 = np.concatenate([relaxed[:, 0], relaxed[:, 1], init_radii])
        bounds = [(0.0, 1.0)] * (2 * n) + [(0.0, 0.5)] * n

        res = minimize(
            objective,
            p0,
            method="SLSQP",
            jac=objective_grad,
            bounds=bounds,
            constraints={
                "type": "ineq",
                "fun": constraints_func,
                "jac": constraints_jac,
            },
            options={"maxiter": 80, "ftol": 1e-5},
        )

        if res.success or res.fun < 0:
            val = -res.fun
            if val > best_val:
                best_val = val
                best_centers = np.stack([res.x[0:n], res.x[n : 2 * n]], axis=1)

    # Final post-processing and clipping
    best_centers = np.clip(best_centers, 0.001, 0.999)

    # Run the exact linear program to find the absolute mathematically optimal radii
    radii = compute_max_radii(best_centers, random_seed)
    sum_radii = np.sum(radii)

    return best_centers, radii, sum_radii


def compute_max_radii(centers, random_seed: int):
    """Compute the maximum possible radii for each circle position.

    Make sure that they don't overlap and stay within the unit square.
    Uses Linear Programming to find the exact global maximum sum of radii.
    """
    del random_seed
    n = centers.shape[0]

    # Objective: minimize -sum(r)
    c = -np.ones(n)

    # Bounds: 0 <= r_i <= min(x, y, 1-x, 1-y)
    bounds = []
    for i in range(n):
        x, y = centers[i]
        max_r = min(x, y, 1.0 - x, 1.0 - y)
        bounds.append((0.0, max(0.0, max_r)))

    # Pairwise constraints: r_i + r_j <= d_ij
    M = n * (n - 1) // 2
    A = np.zeros((M, n))
    b = np.zeros(M)

    idx = 0
    for i in range(n):
        for j in range(i + 1, n):
            dist = np.sqrt(np.sum((centers[i] - centers[j]) ** 2))
            A[idx, i] = 1.0
            A[idx, j] = 1.0
            b[idx] = dist
            idx += 1

    # Solve LP using modern interior-point/simplex solvers
    from scipy.optimize import linprog

    for method in ["highs", "interior-point", "revised simplex"]:
        try:
            res = linprog(c, A_ub=A, b_ub=b, bounds=bounds, method=method)
            if res.success:
                return res.x
        except Exception:
            continue

    # Fallback to analytical scaling heuristic if LP solver is not available/fails
    radii = np.ones(n)
    for i in range(n):
        x, y = centers[i]
        radii[i] = min(x, y, 1.0 - x, 1.0 - y)

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