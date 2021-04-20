import numpy as np


class Portfolio:

    def __init__(self, assets, cash_init):
        assert type(assets) in [list, tuple], "Portfolio assets must be either a list or tuple"
        assert type(cash_init) in [int, float], "Initial cash must be either float or integer"
        self.assets = assets
        self.cash_init = cash_init
        self.dpm = 30

    def get_num_events(self, freq, total_days):
        day_len = (12.0 / freq) * self.dpm
        num_events = int(total_days / day_len)
        return day_len, num_events

    def get_total_days(self, days, months, years):
        return int(days + self.dpm * (months + 12 * years))

    def get_sched(self, params, years, months, days):
        total_days = self.get_total_days(days, months, years)
        sched = []
        sched_lengths = []
        for idx, param in enumerate(params):
            day_len, num_events = self.get_num_events(param['freq'], total_days)
            sched_lengths.append(num_events)
            sched += [(idx, x - 1, x * day_len) for x in range(1, num_events + 1)]
        return sorted(sched, key=lambda x: (x[2], x[0])), sched_lengths

    def simulate(self, years, months, days, replications=1000):
        sched, sched_lengths = self.get_sched([params for _, params in self.assets], years, months, days)
        grid = dict()
        for sched_length, (_, params) in zip(sched_lengths, self.assets):
            grid[params['name']] = np.zeros((sched_length * replications, 5))
        for r in range(replications):
            cash = self.cash_init
            entities = [asset(**params) for asset, params in self.assets]
            for step in sched:
                entity_name = entities[step[0]].name
                asset_val, debt_val, cashflow = entities[step[0]].next_iter()
                idx = r * sched_lengths[step[0]] + step[1]
                grid[entity_name][idx, 0] = r
                grid[entity_name][idx, 1] = step[2]
                grid[entity_name][idx, 2], grid[entity_name][idx, 3] = asset_val, debt_val
                cash += cashflow
                grid[entity_name][idx, 4] = cash
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
                   'step_growth': '*1.02',
                   'freq': 12}
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
    res = test.simulate(years=30, months=0, days=0, replications=1000)
    print(res)