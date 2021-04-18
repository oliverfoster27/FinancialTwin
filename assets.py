import numpy as np
from itertools import count
import math


class BaseAsset:

    def update_inflation(self, inflation_rate):
        self.inflation = inflation_rate


class CashSource(BaseAsset):

    def __init__(self, profile_type, params):
        self.profile_type = profile_type
        self.params = params
        assert self.profile_type in ["constant",
                                     "linear_interpolation",
                                     "step_function",
                                     "discrete"], f"Returns type '{self.profile_type}' not supported"
        if self.profile_type == "step_function":
            assert "first_step" in self.params.keys(), f"Undefined first_step in step_function type"
            assert "step_stride" in self.params.keys(), f"Undefined step_stride in step_function type"
            assert "step_size_init" in self.params.keys(), f"Undefined step_size_init in step_function type"
            assert "step_growth" in self.params.keys(), f"Undefined step_growth in step_function type"
            # TODO: allow user to specify growth by inflation which references state variable
            self.growth_function = self.extract_growth_fn(self.params['step_growth'])
            self.age = 0
            self.step_val = None
            self.last_step_num = None
            self.last_step_val = None

        elif self.profile_type == "constant":
            # TODO
            pass
        elif self.profile_type == "linear_interpolation":
            # TODO
            pass
        elif self.profile_type == "discrete":
            # TODO
            pass
        else:
            raise NotImplementedError("What?")

    def next_iter(self) -> tuple:
        if self.profile_type == "step_function":
            return 0., 0., self.gen_step_fn_cashflow()

    def gen_step_fn_cashflow(self):
        self.age += 1
        if self.age < self.params['first_step']:
            return 0.
        else:
            step_num = math.ceil((self.age - self.params['first_step'] + 1) / self.params['step_stride'])
            if step_num == 1:
                self.last_step_num = step_num
                self.last_step_val = self.params['step_size_init']
                return self.params['step_size_init']
            else:
                if self.last_step_num != step_num:
                    self.step_val = self.growth_function(self.last_step_val)
                    self.last_step_num = step_num
                    self.last_step_val = self.step_val
                return self.step_val

    @staticmethod
    def extract_growth_fn(step_growth):
        operator = step_growth[0]
        assert operator in ["+", "-", "*", "/"], f"Unsupported operator '{operator}'"
        try:
            coef = float(step_growth[1:])
        except ValueError:
            raise ValueError(f"Growth coefficient '{step_growth[1:].strip()}' not recognized as numeric")
        return lambda x: eval(f"x {operator} {coef}")

    def liquidate(self):
        # TODO: fix this up to alter the class state - Convert all (assets - debts) to cash
        return 0.


class RealEstate(BaseAsset):

    def __init__(self, name, property_value_init, mortgage_amt, mortgage_rate, mortgage_term, maintenance_fees,
                 property_tax_rate, inflation, returns_type, returns_params, mortgage_age=None, freq=12,
                 mortgage_amt_remaining=None):
        self.name = name
        self.property_value_init = property_value_init
        self.mortgage_amt = mortgage_amt
        self.mortgage_rate = mortgage_rate
        self.mortgage_term = mortgage_term
        self.maintenance_fees = maintenance_fees
        self.property_tax_rate = property_tax_rate
        self.inflation = inflation
        self.returns_type = returns_type
        self.returns_params = returns_params
        self.mortgage_age = mortgage_age
        self.freq = freq
        self.mortgage_amt_remaining = mortgage_amt_remaining

        assert self.returns_type in ["normal"], f"Returns type '{self.returns_type}' not supported"
        if self.returns_type == "normal":
            assert "std" in self.returns_params.keys(), f"Standard Deviation not defined for normal returns"
            assert "mean" in self.returns_params.keys(), f"Mean not defined for normal returns"
        if not self.mortgage_amt_remaining: self.mortgage_amt_remaining = self.mortgage_amt
        self.asset_val = self.property_value_init
        self.debt_val = self.mortgage_amt_remaining
        self.i = self.mortgage_rate / self.freq
        self.n = self.mortgage_term * self.freq
        # Formula for value of mortgage payment
        self.p = round(self.mortgage_amt * \
                 (self.i * (1 + self.i) ** self.n) / \
                 ((1 + self.i) ** self.n - 1), 2)

    def next_iter(self) -> tuple:
        # Evaluate property tax payment before updating asset value
        property_tax_pmt = (self.asset_val * self.property_tax_rate) / self.freq
        self.maintenance_fees *= (1 + self.inflation / self.freq)
        self.asset_val = (1 + self.get_return()) * self.asset_val
        if self.debt_val >= 0:
            interest_payment = self.debt_val * self.i
            principal_payment = self.p - interest_payment
            if self.debt_val >= self.p:
                self.debt_val = self.debt_val - principal_payment
                return self.asset_val, max(self.debt_val, 0.), self.p + property_tax_pmt + self.maintenance_fees
            else:
                last_payment = self.debt_val
                self.debt_val = 0.
                return self.asset_val, 0., last_payment + property_tax_pmt + self.maintenance_fees
        else:
            return self.asset_val, 0., property_tax_pmt + self.maintenance_fees

    def liquidate(self):
        # TODO: convert all (assets - debts) to cash
        pass

    def get_return(self) -> float:
        # TODO: Different continuous distributions, KDE
        return np.random.normal(self.returns_params['mean'], self.returns_params['std'], 1)[0]


if __name__ == "__main__":
    # test = RealEstate(name="4150",
    #                   property_value_init=536_000,
    #                   mortgage_amt=427_000,
    #                   mortgage_rate=.0279,
    #                   mortgage_term=30,
    #                   maintenance_fees=480,
    #                   property_tax_rate=0.008,
    #                   inflation=0.02,
    #                   returns_type="normal",
    #                   returns_params={"std": 0.0043, "mean": 0.0036})
    # for i in range(30*12 + 10):
    #     print(test.next_iter())
    test2 = CashSource(profile_type='step_function',
                       params={'first_step': 5, 'step_stride': 12, 'step_size_init': 2, 'step_growth': '*1.2'})
    for i in range(30):
        print(test2.next_iter())
