# python -m venv C:\Users\pc\MyCodebase\Streamlit\sltest
# activate
# python -m pip install --upgrade pip
# pip install streamlit
# pip install datetime
# pip install quantstats
# pip freeze (per vedere le versioni da mettere in requirements.txt)
# streamlit run main.py
# ctrl+C
# deactivate

from requests.api import request
import streamlit as sl
import pandas as pd
import numpy as np
from requests import get
from datetime import date
from io import BytesIO
import quantstats as qs
import altair as alt

qs.extend_pandas()

# @sl.cache


def load_wsbmention(year):
    baseurl = "http://avmcode.pythonanywhere.com/public/datascraping/wsbmm/WSBmm-"
    fullurl = f"{baseurl}{year}.csv"
    r = get(fullurl)
    df = pd.read_csv(BytesIO(r.content), index_col=[0, 1], header=0)
    return df


def load_strategy_returns(filename):
    baseurl = "http://avmcode.pythonanywhere.com/public/datascraping/strategiesreturns/"
    fullurl = f"{baseurl}{filename}"
    r = get(fullurl)
    df = pd.read_csv(BytesIO(r.content), index_col=[0], header=0)
    s = pd.Series(df['PortfolioReturns'].values, index=df.index)
    return s


def load_benchmark_returns(ticker):
    try:
        benchmark_returns = qs.utils.download_returns(ticker)
        return benchmark_returns
    except:
        global data2_load_state
        data2_load_state.text('Non riesco a caricare il Benchmark')


sl.sidebar.header("Opzioni")
main_options = sl.sidebar.selectbox(
    "Cosa vuoi Fare", ('WSB Mentions', 'Strategy Check')
)
if main_options == 'WSB Mentions':

    sl.header('WSB Mentions')

    year = sl.sidebar.slider("Anno", 2020, date.today().year, 2020)

    data_load_state = sl.text("Caricando...")

    df = load_wsbmention(year)

    data_load_state.text('Caricando... Fatto!')

    # style per avere interi senza virgola
    sl.dataframe(df.style.format("{:.0f}"))


elif main_options == 'Strategy Check':

    sl.header('Strategy Check')

    strategy_options = sl.sidebar.selectbox(
        "Cosa vuoi Fare", ('Unger Games pattern x', 'placeholder')
    )

    if strategy_options == 'Unger Games pattern x':
        data_load_state = sl.text("Caricando Risultati Strategia...")

        filename = 'ungames_patternX_f2016t2021_returns.csv'

        strategy_returns = load_strategy_returns(filename)

        data_load_state.text('Caricando Risultati Strategia... Fatto!')

        ticker = sl.sidebar.text_input("Benchmark", value="SPY", max_chars=5)

        data2_load_state = sl.text("Caricando Ritorni Benchmark...")

        benchmark_returns = load_benchmark_returns(ticker.upper())

        data2_load_state.text('Caricando Ritorni Benchmark... Fatto!')

        data3_load_state = sl.text("Sistemando i dati...")

        # pareggiamo le date di ritorno
        benchmark_returns = benchmark_returns[strategy_returns.index[0]:strategy_returns.index[-1]]

        oldindex = benchmark_returns.index.tolist()
        newindex = []
        for ind in oldindex:
            newindex.append(ind.strftime('%Y-%m-%d'))

        benchmark_returns.index = newindex

        benchmark_equity = benchmark_returns.to_prices(10000)

        strategy_equity = strategy_returns.to_prices(10000)

        report = pd.concat([strategy_equity, benchmark_equity], axis=1)

        report.reset_index(level=0, inplace=True)

        report.columns = ['Date', 'Strategy', 'Benchmark']

        # https://altair-viz.github.io/user_guide/data.html?highlight=wide#long-form-vs-wide-form-data
        replong = report.melt('Date', var_name='EqLine', value_name='Equity')

        data3_load_state.text('Sistemando i dati... Fatto!')

        chart = alt.Chart(replong).mark_line().encode(
            x='Date:T',
            y='Equity:Q',
            color='EqLine:N'
        )

        sl.altair_chart(chart, use_container_width=True)
