import dash
import dash_ag_grid as dag
from dash import dcc, Input, Output, html, callback_context


class PriceDepthGrid(object):
    def __init__(self, prefix: str):
        self.prefix = prefix

        self.grid = dag.AgGrid(
            id=f"{self.prefix}-price-depth-grid",
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
        )


    def layout(self):
        return html.Div([
            dcc.Store(id=f"{self.prefix}-liquibook-state-change"),
            dcc.Store(id=f"{self.prefix}-liquibook-order-cancel-modify"),
            self.grid,
        ])

    @staticmethod
    def register_callbacks(app, prefix):
        @app.callback(
        Output(f"{prefix}-price-depth-grid", "rowData"),
        Input(f"{prefix}-liquibook-state-change", "data"),
        Input(f"{prefix}-liquibook-order-cancel-modify", "data"),
        prevent_initial_call=True
        )
        def on_price_depth_change(price_depth_change, price_depth_change_modify):

            triggered = callback_context.triggered_id

            if triggered == f"{prefix}-liquibook-state-change":
                return price_depth_change['price_depth']
            elif triggered == f"{prefix}-liquibook-order-cancel-modify":
                return price_depth_change_modify['price_depth']

            return None

        @app.callback(
        Output(f"{prefix}-selected-price-level", "data"),
        Input(f"{prefix}-price-depth-grid", "cellClicked")
        )
        def display_selected(selected):
            if not selected:
                return None

            col_id = selected.get("colId")
            if col_id in {"bid_price", "ask_price"}:
                return selected.get("value")

            return None
