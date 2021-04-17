from dataclasses import dataclass, field
import numpy as np


@dataclass(frozen=False, order=True)
class RealEstate:
    name: str
    property_value_init: float
    mortgage_amt: float
    mortgage_rate: float
    mortgage_term: int
    returns_type: str
    returns_params: dict
    mortgage_age: int = 0
    freq: int = 12
    mortgage_amt_remaining: float = None

    def __post_init__(self):
        assert self.returns_type in ["normal"], f"Returns type '{self.returns_type}' not supported"
        if self.returns_type == "normal":
            assert "std" in self.returns_params.keys(), f"Standard Deviation not defined for normal returns"
            assert "mean" in self.returns_params.keys(), f"Mean not defined for normal returns"
        self.age = 0
        if not self.mortgage_amt_remaining: self.mortgage_amt_remaining = self.mortgage_amt
        self.asset_val = self.property_value_init
        self.debt_val = self.mortgage_amt_remaining
        self.i = self.mortgage_rate / self.freq
        self.n = self.mortgage_term * self.freq
        # Formula for value of mortgage payment
        self.p = self.mortgage_amt * \
                 (self.i * (1 + self.i) ** self.n) / \
                 ((1 + self.i) ** self.n - 1)

    def next_iter(self):
        self.age += 1
        self.asset_val = (1 + self.get_return()) * self.asset_val
        if self.age <= self.n:
            interest_payment = self.debt_val * self.i
            principal_payment = self.p - interest_payment
            self.debt_val -= principal_payment
            return self.asset_val, max(self.debt_val, 0.), self.p
        else:
            return self.asset_val, 0., 0.

    def get_return(self) -> float:
        return np.random.normal(self.returns_params['mean'], self.returns_params['std'], 1)[0]


if __name__ == "__main__":
    test = RealEstate(name="4150",
                      property_value_init=536_000,
                      mortgage_amt=427_000,
                      mortgage_rate=.0279,
                      mortgage_term=30,
                      returns_type="normal",
                      returns_params={"std": 0.0043, "mean": 0.0036})
    for i in range(30*12):
        print(test.next_iter())