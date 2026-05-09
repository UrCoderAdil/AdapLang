"""
3PL Item Response Theory model with MLE theta estimation.
P(correct | θ, b, a, c) = c + (1-c) / (1 + exp(-a*(θ-b)))
"""
import numpy as np
from scipy.optimize import minimize
from scipy.stats import norm


class IRTModel:
    def __init__(self, theta: float = 0.0, sigma: float = 1.0):
        self.theta = theta
        self.sigma = sigma

    def probability(self, theta: float, b: float, a: float = 1.0, c: float = 0.25) -> float:
        """3PL probability of a correct response."""
        return c + (1 - c) / (1 + np.exp(-a * (theta - b)))

    def fisher_information(self, theta: float, b: float, a: float = 1.0, c: float = 0.25) -> float:
        """Fisher Information — higher means more informative at this theta."""
        p = self.probability(theta, b, a, c)
        q = 1 - p
        if p <= 0 or q <= 0:
            return 0.0
        return a**2 * ((p - c)**2 / (1 - c)**2) * (q / p)

    def update_theta(self, responses: list[dict]) -> float:
        """
        MLE theta update given response history.
        Each response: {"b": float, "a": float, "c": float, "correct": bool}
        """
        if not responses:
            return self.theta

        def neg_log_likelihood(theta_vec):
            theta = theta_vec[0]
            ll = 0.0
            for r in responses:
                p = self.probability(theta, r["b"], r.get("a", 1.0), r.get("c", 0.25))
                p = np.clip(p, 1e-9, 1 - 1e-9)
                ll += np.log(p) if r["correct"] else np.log(1 - p)
            ll += norm.logpdf(theta, 0, 1)
            return -ll

        result = minimize(
            neg_log_likelihood,
            [self.theta],
            method="L-BFGS-B",
            bounds=[(-4, 4)],
        )
        self.theta = float(result.x[0])
        return self.theta

    def select_next_question(self, question_pool: list[dict]) -> dict | None:
        """Pick the question that maximises Fisher Information at current theta."""
        if not question_pool:
            return None
        return max(
            question_pool,
            key=lambda q: self.fisher_information(
                self.theta, q["b"], q.get("a", 1.0), q.get("c", 0.25)
            ),
        )

    def standard_error(self) -> float:
        """Approximate standard error of theta estimate."""
        return self.sigma
