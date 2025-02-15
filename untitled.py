# -*- coding: utf-8 -*-
"""Untitled

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/14wRnlbfArohtuwalx8kdxEf2NwDZkKcY
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from datetime import datetime
import requests

data = pd.read_csv("/content/covid_19_india.csv")

data.head()

data = data.rename(columns={'State/UnionTerritory':'States','Cured':'Recovery'})

data.head()

data = data.drop(['Sno', 'Time', 'ConfirmedIndianNational', 'ConfirmedForeignNational'], axis=1)

data.head()

data['Active'] = data['Confirmed'] - data['Recovery'] - data['Deaths'] ### 1 - 0 - 0 = 1

data.head()

data = data.sort_values(['Date', 'States']).reset_index(drop=True)
data['Date'] = pd.to_datetime(data['Date'])

data

india_cases = data[data['Date'] == data['Date'].max()].copy().fillna(0)
india_cases.index = india_cases['States']
india_cases = india_cases.drop(['States', 'Date'], axis=1)

df = pd.DataFrame(pd.to_numeric(india_cases.sum()),dtype=np.float64).transpose()
df.style.background_gradient(cmap='summer_r', axis=1)

india_cases.sort_values('Active', ascending= False).style\
    .background_gradient(cmap='YlGn_r', subset=['Confirmed'])\
    .background_gradient(cmap='BrBG_r', subset=["Deaths"])\
    .background_gradient(cmap='BuPu', subset=['Recovery'])\
    .background_gradient(cmap='YlOrBr', subset=['Active'])

def horizontal_bar_chart(df, x, y, title, x_label, y_label, color):
    fig = px.bar(df, x=x, y=y, orientation='h', title=title,
                 labels={x.name: x_label,
                         y.name: y_label}, color_discrete_sequence=[color])
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    fig.show()

cnf, dth, rec,act = '#393e46', '#33ccff', '#ff99cc','#fe9801'

import plotly.express as px
import plotly.graph_objs as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
from plotly.offline import init_notebook_mode, iplot

top_10_confirmed_Cases = india_cases.sort_values('Confirmed', ascending=False)[:10]
horizontal_bar_chart(top_10_confirmed_Cases,top_10_confirmed_Cases.Confirmed, top_10_confirmed_Cases.index,
                     'Top 10 States with most confirmed casess', 'Number of confiremed cases (in Thousand)','States Name', cnf)

top_10_deaths_Cases = india_cases.sort_values('Confirmed', ascending=False)[:10]
horizontal_bar_chart(top_10_deaths_Cases,top_10_deaths_Cases.Deaths, top_10_deaths_Cases.index,
                     'Top 10 States with most Deaths cases', 'Number of Deaths cases (in Thousand)','State Name', dth)

#Analyze the trends of confirmed cases, deaths, and recoveries over time for each state.
def plot_state_trends(state_name):
    state_data = data[data['States'] == state_name]
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=state_data['Date'], y=state_data['Confirmed'],
                             mode='lines+markers', name='Confirmed Cases'))
    fig.add_trace(go.Scatter(x=state_data['Date'], y=state_data['Deaths'],
                             mode='lines+markers', name='Deaths'))
    fig.add_trace(go.Scatter(x=state_data['Date'], y=state_data['Recovery'],
                             mode='lines+markers', name='Recoveries'))

    fig.update_layout(title=f'COVID-19 Trends in {state_name}',
                      xaxis_title='Date', yaxis_title='Number of Cases')
    fig.show()
for state in data['States'].unique():
  plot_state_trends(state)

# Calculate the daily/weekly growth rate of cases and identify periods of significant increase or decrease.

import pandas as pd
def calculate_growth_rate(df, group_col='States', value_col='Confirmed'):
    df['Date'] = pd.to_datetime(df['Date'])
    df['Daily Growth Rate'] = df.groupby(group_col)[value_col].pct_change()
    df['Weekly Growth Rate'] = df.groupby(group_col)[value_col].pct_change(periods=7)
    return df
data_with_growth = calculate_growth_rate(data)
significant_increase_threshold = 0.1
significant_decrease_threshold = -0.1

significant_changes = data_with_growth[
    (data_with_growth['Daily Growth Rate'] > significant_increase_threshold) |
    (data_with_growth['Daily Growth Rate'] < significant_decrease_threshold)
]

print("Periods with significant changes in daily growth rate:")
print(significant_changes[['Date', 'States', 'Daily Growth Rate']])

# Use moving averages to smooth out the data and visualize the trends more clearly.
def plot_state_trends_with_moving_average(state_name, window=7):
    state_data = data[data['States'] == state_name]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=state_data['Date'], y=state_data['Confirmed'],
                             mode='lines+markers', name='Confirmed Cases'))
    state_data['Confirmed_MA'] = state_data['Confirmed'].rolling(window=window).mean()
    fig.add_trace(go.Scatter(x=state_data['Date'], y=state_data['Confirmed_MA'],
                             mode='lines', name=f'Confirmed Cases ({window}-day MA)'))

    fig.add_trace(go.Scatter(x=state_data['Date'], y=state_data['Deaths'],
                             mode='lines+markers', name='Deaths'))
    fig.add_trace(go.Scatter(x=state_data['Date'], y=state_data['Recovery'],
                             mode='lines+markers', name='Recoveries'))
    fig.update_layout(title=f'COVID-19 Trends in {state_name} with Moving Average',
                      xaxis_title='Date', yaxis_title='Number of Cases')
    fig.show()
for state in data['States'].unique():
  plot_state_trends_with_moving_average(state)

# promptExplore the correlation between different states' infection rates.
import matplotlib.pyplot as plt
infection_rates = data.groupby(['Date', 'States'])['Confirmed'].sum().reset_index()
infection_matrix = infection_rates.pivot(index='Date', columns='States', values='Confirmed')

# Calculate the correlation matrix
correlation_matrix = infection_matrix.corr()

# Visualize the correlation matrix using a heatmap
plt.figure(figsize=(15, 10))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Correlation Matrix of Infection Rates Across States')
plt.show()

