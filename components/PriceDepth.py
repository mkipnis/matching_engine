# Copyright (c) Mike Kipnis - DistributedATS

import dash_ag_grid as dag
from dash import dcc, Input, Output, html, callback_context
from dash.dependencies import MATCH


class PriceDepthGrid:
    def __init__(self, prefix: str):
        self.prefix = prefix

    def layout(self):
        return html.Div([
            # Stores owned by the container, but rendered here
            dcc.Store(
                id={"type": "liquibook-order-cancel-modify", "prefix": self.prefix}
            ),

            dag.AgGrid(
                id={"type": "price-depth-grid", "prefix": self.prefix},
                columnDefs=[
                    {
                        "headerName": "BidPrice",
                        "field": "bid_price",
                        "valueFormatter": {
                            "function": "params.data && params.data.bid_size !== 0 ? params.value : ''"
                        },
                    },
                    {
                        "headerName": "AskPrice",
                        "field": "ask_price",
                        "valueFormatter": {
                            "function": "params.data && params.data.ask_size !== 0 ? params.value : ''"
                        },
                    },
                    {
                        "headerName": "BidSize",
                        "field": "bid_size",
                        "valueFormatter": {
                            "function": "params.value !== 0 ? params.value : ''"
                        },
                    },
                    {
                        "headerName": "AskSize",
                        "field": "ask_size",
                        "valueFormatter": {
                            "function": "params.value !== 0 ? params.value : ''"
                        },
                    },
                ],
                rowData=[],
                dashGridOptions={"rowSelection": "single"},
                defaultColDef={"flex": 1, "minWidth": 100, "resizable": False},
                style={"height": "290px", "width": "100%"},
                className="ag-theme-quartz-dark",
            ),
        ])

    @staticmethod
    def register_callbacks(app):

        # ----------------------------
        # Update price depth grid
        # ----------------------------
        @app.callback(
            Output({"type": "price-depth-grid", "prefix": MATCH}, "rowData"),
            Input({"type": "liquibook-state-change", "prefix": MATCH}, "data"),
            Input({"type": "liquibook-order-cancel-modify", "prefix": MATCH}, "data"),
            prevent_initial_call=True,
        )
        def on_price_depth_change(state_change, cancel_modify_change):

            triggered = callback_context.triggered_id

            if not triggered:
                return dash.no_update

            if triggered["type"] == "liquibook-state-change" and state_change:
                return state_change.get("price_depth", [])

            if triggered["type"] == "liquibook-order-cancel-modify" and cancel_modify_change:
                return cancel_modify_change.get("price_depth", [])

            return dash.no_update

        # ----------------------------
        # Emit selected price level
        # ----------------------------
        @app.callback(
            Output({"type": "selected-price-level", "prefix": MATCH}, "data"),
            Input({"type": "price-depth-grid", "prefix": MATCH}, "cellClicked"),
            prevent_initial_call=True,
        )
        def display_selected(cell):

            if not cell:
                return None

            col_id = cell.get("colId")
            if col_id in {"bid_price", "ask_price"}:
                return cell.get("value")

            return None
