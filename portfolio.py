import numpy as np

class Portfolio:

    def __init__(self, assets, cash_init):
        assert type(assets) in [list, tuple], "Portfolio assets must be either a list or tuple"
        assert type(cash_init) in [int, float], "Initial cash must be either float or integer"
        self.assets = assets
        self.cash_init = cash_init

    def simulate(self, horizon, replications=1000):
        grid = np.zeros((replications, horizon, len(self.assets), 3))
        for r in range(replications):
            cash = self.cash_init
            entities = [asset(**params) for asset, params in self.assets]
            for i in range(horizon):
                for idx, entity in enumerate(entities):
                    asset_val, debt_val, cashflow = entity.next_iter()
                    grid[r, i, idx, 0], grid[r, i, idx, 1] = asset_val, debt_val
                    cash += cashflow
                    grid[r, i, idx, 2] = cash
                    if cash <= 0:
                        raise ValueError("Cashflow is negative")
        return grid


if __name__ == "__main__":
    from assets import CashFlow, RealEstate
    assets = [(CashFlow,
               {
                   'name': 'Test2',
                   'profile_type': 'step_function',
                   'inflation': 0.02,
                   'first_step': 0,
                   'step_stride': 12,
                   'step_size_init': 5400,
                   'step_growth': '*1.02'}
               ),
              (RealEstate, {
                  'name': "4150",
                  'property_value_init': 536_000,
                  'mortgage_amt': 427_000,
                  'mortgage_rate': 0.0279,
                  'mortgage_term': 30,
                  'maintenance_fees': 480,
                  'property_tax_rate': 0.008,
                  'inflation': 0.02,
                  'returns_type': "normal",
                  'returns_params': {"std": 0.0043, "mean": 0.0036},
                  'freq': 12
              })]
    test = Portfolio(assets, cash_init=10_000)
    res = test.simulate(horizon=12*30, replications=1)
    print(res)