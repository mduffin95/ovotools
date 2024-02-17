from datetime import date, time, timedelta
from ovoenergy.models import OVOHalfHour
from ovoenergy.ovoenergy import OVOEnergy
import asyncio
import os
import matplotlib.pyplot as plt

from tariff import Tariff

import pandas as pd


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


client = OVOEnergy()
authenticated = asyncio.run(client.authenticate(
    os.environ["OVO_USER"],
    os.environ["OVO_PASS"]
))

tariff: Tariff = Tariff(peak=0.3036, off_peak=0.2344)

data = []

if authenticated:

    start_date = date(2024, 2, 8)
    end_date = date(2024, 2, 16)
    for single_date in daterange(start_date, end_date):
        string_date = single_date.strftime("%Y-%m-%d")
        half_hourly_usage = asyncio.run(client.get_half_hourly_usage(string_date))
        electricity = half_hourly_usage.electricity
        data.extend([{'datetime': f.interval.start, 'consumption': f.consumption} for f in electricity])

df = pd.DataFrame(data)

df.set_index('datetime', inplace=True)

result = df.groupby([lambda x: x.date(), tariff.peak]).sum()

result.index = result.index.set_names(['datetime', 'peak'])

result['cost'] = result.apply(lambda x: tariff.cost(x['consumption'], x.name[1]), axis=1)
result = result['consumption'].unstack(level=-1)
plot = result.plot(kind='bar', stacked=True)
fig = plot.get_figure()
fig.savefig("energy.png")