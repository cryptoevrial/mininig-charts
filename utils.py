import plotly.graph_objects as go
import pandas as pd
import datetime

class Asics:
    def __init__(self):
        self.asics = get_asics_df()

    def get_name(self, row):
        year = row['date'].year
        return self.asics[self.asics['year']==year]['name'].values[0]

    def get_th_s(self, row):
        year = row['date'].year
        return self.asics[self.asics['year']==year]['th_s'].values[0]

    def get_kwt_h(self, row):
        year = row['date'].year
        return self.asics[self.asics['year']==year]['kwt_h'].values[0]

    def get_rub_kwt(self, row):
        year = row['date'].year
        return self.asics[self.asics['year']==year]['rub_kwt'].values[0]

def get_usd_rub_df(csv='Rtsudcur.csv'):
    return pd.read_csv(csv, delimiter=';')

def get_avg_usd_rub_rate_df(rub_usd_price_df):
    rub_usd_price_df['#Date'] = pd.to_datetime(rub_usd_price_df['#Date'])
    rub_usd_price_df['year'] = rub_usd_price_df['#Date'].dt.year
    rub_usd_price_df['month'] = rub_usd_price_df['#Date'].dt.month
    return rub_usd_price_df.groupby(['year', 'month']).mean()['Value 18:50 MSK']

def get_usd_rub_rate_at_month(row):
    avg_usd_rub_rate_df = get_avg_usd_rub_rate_df(get_usd_rub_df())
    return avg_usd_rub_rate_df.loc[(row['date'].year, row['date'].month)]

def get_df_from_json(json):
    df = pd.read_json(json)
    df['date'] = pd.to_datetime(df['x'], unit='s').dt.date
    return df

def get_asics_df(xlsx='mining.xlsx'):
    asics = pd.read_excel('mining.xlsx', sheet_name='mining')
    asics.rename(columns = {
        'Год': 'year',
        'Оборудование': 'name',
        'Вычислительная мощность, Th/s': 'th_s',
        'Потребление э/э, кВт/ч': 'kwt_h',
        'Стоимость э/э, руб/кВт': 'rub_kwt',
        },
    inplace=True
    )
    return asics

def get_block_reward(row):
    halving_dates = [
        datetime.datetime.strptime('2020-05-11', '%Y-%m-%d').date(),
        datetime.datetime.strptime('2024-04-19', '%Y-%m-%d').date()
    ]
    if row['date'] < halving_dates[0]:
        return 12.5
    elif halving_dates[0] <= row['date'] < halving_dates[1]:
        return 6.25
    else:
        return 3.125

def get_final_df():
    hash_rate_df = get_df_from_json('hashrate.json')
    btc_price_df = get_df_from_json('market_price.json')
    df = pd.DataFrame()
    df['date'] = hash_rate_df['date']
    df['btc_price'] = btc_price_df['y']
    df['hashrate'] = hash_rate_df['y']
    df['btc_reward'] = df.apply(get_block_reward, axis=1)
    df['usd_rub_rate'] = df.apply(get_usd_rub_rate_at_month, axis=1)
    asics = Asics()
    df['asics_name'] = df.apply(asics.get_name, axis=1)
    df['th_s'] = df.apply(asics.get_th_s, axis=1)
    df['kwt_h'] = df.apply(asics.get_kwt_h, axis=1)
    df['rub_kwt'] = df.apply(asics.get_rub_kwt, axis=1)
    df['btc_per_th'] = (df['btc_reward'] * 144) / df['hashrate']
    df['mining_cost_in_usd'] = (df['kwt_h'] * 0.05 * 24) / ((df['th_s'] * df['btc_per_th']))
    df['total_mining_cost_in_usd'] = df['mining_cost_in_usd'] / 0.6
    df['mining_cost_in_usd'] = df['mining_cost_in_usd'].rolling(window=7).mean()
    df['total_mining_cost_in_usd'] = df['total_mining_cost_in_usd'].rolling(window=7).mean()

    return df

