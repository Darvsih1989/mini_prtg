import asyncio
import threading
import sqlite3
import pandas as pd

import dash
from dash import Dash, dcc, html, callback_context
from dash.dependencies import Input, Output, State

from collector.snmp_collector import get_interfaces, collect_interface

app = Dash(__name__)
app.title = "Mini-PRTG"

interfaces_global = []

app.layout = html.Div([
    html.H2("Mini-PRTG"),

    dcc.Input(id="ip", placeholder="Target IP"),
    dcc.Input(id="community", value="public"),
    dcc.Input(id="interval", value="1"),

    html.Br(), html.Br(),
    html.Button("Discover Interfaces", id="discover"),
    html.Button("Start Monitoring", id="start"),

    html.Br(), html.Br(),
    dcc.Dropdown(id="interfaces", multi=True),

    html.Div(id="status"),
    dcc.Graph(id="live-graph"),

    dcc.Interval(id="tick", interval=1000)
])

@app.callback(
    Output("interfaces", "options"),
    Output("status", "children"),
    Input("discover", "n_clicks"),
    Input("start", "n_clicks"),
    State("ip", "value"),
    State("community", "value"),
    State("interval", "value"),
    State("interfaces", "value"),
)
def handle_actions(d, s, ip, community, interval, selected):
    ctx = callback_context
    if not ctx.triggered:
        return [], ""

    btn = ctx.triggered[0]["prop_id"].split(".")[0]

    if btn == "discover":
        def run():
            global interfaces_global
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            interfaces_global = loop.run_until_complete(
                get_interfaces(ip, community)
            )
            loop.close()

        t = threading.Thread(target=run)
        t.start()
        t.join()

        opts = [
            {"label": f"{i['alias']} ({i['name']})", "value": i["index"]}
            for i in interfaces_global
        ]
        return opts, f"{len(opts)} interfaces found"

    if btn == "start":
        def run():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            tasks = []
            for i in interfaces_global:
                if i["index"] in selected:
                    tasks.append(
                        collect_interface(
                            ip, community,
                            i["index"], i["alias"],
                            int(interval)
                        )
                    )
            loop.run_until_complete(asyncio.gather(*tasks))

        threading.Thread(target=run, daemon=True).start()
        return dash.no_update, "Monitoring started"

    return dash.no_update, ""

@app.callback(
    Output("live-graph", "figure"),
    Input("tick", "n_intervals")
)
def update_graph(_):
    conn = sqlite3.connect("traffic.db")
    df = pd.read_sql(
        "SELECT * FROM traffic ORDER BY rowid DESC LIMIT 60",
        conn
    )
    conn.close()

    if df.empty:
        return {}

    fig = {"data": [], "layout": {"title": "Live Traffic (Mbps)"}}

    for iface in df["iface"].unique():
        sub = df[df["iface"] == iface]
        fig["data"].append({"x": sub["ts"], "y": sub["rx"], "name": f"{iface} RX"})
        fig["data"].append({"x": sub["ts"], "y": sub["tx"], "name": f"{iface} TX"})

    return fig
