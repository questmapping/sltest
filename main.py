# python -m venv C:\Users\pc\MyCodebase\Streamlit\sltest
# activate
# python -m pip install --upgrade pip
# pip install streamlit
# pip install datetime
# pip install quantstats
# pip install mysqlclient
# pip install sshtunnel
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
#import MySQLdb
#import sshtunnel

qs.extend_pandas()

# sshtunnel.SSH_TIMEOUT = 5.0
# sshtunnel.TUNNEL_TIMEOUT = 5.0

# with sshtunnel.SSHTunnelForwarder(
#     (sl.secrets.ssh_credentials.ssh_host),
#     ssh_username=sl.secrets.ssh_credentials.ssh_user, ssh_password=sl.secrets.ssh_credentials.ssh_pass,
#     remote_bind_address=(sl.secrets.db_credentials.url,
#                          sl.secrets.ssh_credentials.ssh_bindport)
# ) as tunnel:
#     connection = MySQLdb.connect(
#         user=sl.secrets.db_credentials.username,
#         passwd=sl.secrets.db_credentials.password,
#         host=sl.secrets.ssh_credentials.ssh_localhost, port=tunnel.local_bind_port,
#         db=sl.secrets.db_credentials.db_name,
#     )


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


# if (connection.open):

#     c = connection.cursor()

#     c.execute("""SELECT spam, eggs, sausage FROM breakfast
#           WHERE price < %s""", (max_price,))

#     query_results = c.fetchall()

sl.sidebar.header("Opzioni")
main_options = sl.sidebar.selectbox(
    "Cosa vuoi Fare", ('Drawdowns', 'Rolling Returns',
                       'WSB Mentions', 'Strategy Check')
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
        benchmark_returns = benchmark_returns[strategy_returns.index[0]
            :strategy_returns.index[-1]]

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

elif main_options == 'Drawdowns':

    sl.header('Drawdowns')

    ticker = sl.sidebar.text_input("Benchmark", value="SPY", max_chars=5)

    dd_options = sl.sidebar.selectbox(
        "Come li vuoi ordinare", ('Durata più lunga',
                                  'Drawdown Massimo Peggiore')
    )

    data_load_state = sl.text("Caricando Ritorni Benchmark...")

    benchmark_returns = load_benchmark_returns(ticker.upper())

    data_load_state.text('Caricando Ritorni Benchmark... Fatto!')

    data2_load_state = sl.text("Calcolando i Drawdowns...")

    dd = benchmark_returns.to_drawdown_series()

    dd_info_unordered = qs.stats.drawdown_details(dd)

    if (dd_options == 'Durata più lunga'):

        dd_info = dd_info_unordered.sort_values(by='days', ascending=False)

    elif (dd_options == 'Drawdown Massimo Peggiore'):

        dd_info = dd_info_unordered.sort_values(
            by='max drawdown', ascending=True)  # valori negativ

    dd_info = dd_info.drop(columns=['99% max drawdown'])

    dd_chart = pd.DataFrame({
        'Date': dd.index,
        'Drawdown': dd.values
    })

    data2_load_state.text('Calcolando i Drawdowns... Fatto!')

    sl.dataframe(dd_info)

    chart = alt.Chart(dd_chart).mark_area(
        line={'color': 'red'},
        color=alt.Gradient(
            gradient='linear',
            stops=[alt.GradientStop(color='darkred', offset=0),
                   alt.GradientStop(color='red', offset=1)],
            x1=1,
            x2=1,
            y1=1,
            y2=0
        )
    ).encode(
        alt.X('Date:T'),
        alt.Y('Drawdown:Q', axis=alt.Axis(format='%')),
        tooltip=['Date', 'Drawdown']
    ).interactive()

    sl.altair_chart(chart, use_container_width=True)

elif main_options == 'Rolling Returns':

    sl.header('Rolling Returns')

    ticker = sl.sidebar.text_input("Benchmark", value="SPY", max_chars=5)

    data_load_state = sl.text("Caricando Ritorni Benchmark...")

    benchmark_returns = load_benchmark_returns(ticker.upper())

    data_load_state.text('Caricando Ritorni Benchmark... Fatto!')

    data2_load_state = sl.text("Calcolando i Rolling Returns...")

    TRADINGDAYS = 252

    days = len(benchmark_returns)

    max_years_rr = int(days/TRADINGDAYS)

    maxlist = []
    minlist = []
    avglist = []
    perneglist = []
    index = []

    for i in range(1, max_years_rr+1):
        cumsum = benchmark_returns.rolling(TRADINGDAYS*i).sum()
        list1 = cumsum.to_list()
        pos = len([num for num in list1 if num >= 0])
        neg = len([num for num in list1 if num < 0])
        perneglist.append(neg/(pos+neg))
        max_ret = cumsum.max()
        min_ret = cumsum.min()
        avg_ret = cumsum.mean()
        if i < 10:
            index.append(f"0{i}Yr")
        else:
            index.append(f"{i}Yr")
        maxlist.append((((max_ret+1)**(1/i))-1))
        minlist.append((((min_ret+1)**(1/i))-1))
        avglist.append((((avg_ret+1)**(1/i))-1))

    data = {
        'Minimum Returns': minlist,
        'Maximum Returns': maxlist,
        'Average Returns': avglist,
        'Negative Returns Percentage': perneglist,
    }

    rr_df = pd.DataFrame(data, index=index)

    rr_df = rr_df.fillna(method="ffill")

    data2_load_state.text('Calcolando i Rolling Returns... Fatto!')

    sl.dataframe(rr_df.style.format("{:.3f}"))

    data3_load_state = sl.text("Sistemando i dati...")

    rr_df.reset_index(level=0, inplace=True)

    rr_df.columns = ['Years', 'Minimum', 'Maximum', 'Average', 'Negatives']

    # https://altair-viz.github.io/user_guide/data.html?highlight=wide#long-form-vs-wide-form-data
    replong = rr_df.melt('Years', var_name='RR', value_name='RollingReturns')

    data3_load_state.text('Sistemando i dati... Fatto!')

    chart = alt.Chart(replong).mark_line(point=True).encode(
        alt.X('Years:O'),
        alt.Y('RollingReturns:Q', axis=alt.Axis(format='%')),
        color='RR:N',
        tooltip=['Years', 'RollingReturns']
    ).interactive()

    sl.altair_chart(chart, use_container_width=True)

#     connection.close()

# else:

#     sl.sidebar.header("Connessione Database non riuscita")
