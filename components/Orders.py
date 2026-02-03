# Copyright (c) Mike Kipnis - DistributedATS

import dash_ag_grid as dag
from dash import html, dcc, Output, Input, callback_context, MATCH

# Dummy price formatter JS function string (replace with actual if needed)
price_formatter = {
    "function": "params.value !== 0 ? params.value : ''"
}

side_formatter = {
    "function": "params.value === true ? 'Buy' : 'Sell'"
}


class TradeOrderHistory:

    def __init__(self, prefix: str):
        self.prefix = prefix
        self.row_data = []

    def layout(self):

        column_defs = [
            {
                "headerName": "OrderId",
                "field": "order_id_",
                "sortable": True,
                "flex": 2,
                "filter": "agTextColumnFilter",
            },
            {
                "headerName": "OrderState",
                "field": "state_str",
                "sortable": True,
                "flex": 2,
            },
            {
                "headerName": "Side",
                "field": "is_buy",
                "sortable": True,
                "flex": 2,
                "valueFormatter": side_formatter,
                "cellRenderer": "agTextCellRenderer",
            },
            {
                "headerName": "Price",
                "field": "price",
                "sortable": True,
                "flex": 2,
                "valueFormatter": price_formatter,
            },
            {
                "headerName": "StopPx",
                "field": "stop_price",
                "sortable": True,
                "flex": 2,
                "valueFormatter": price_formatter,
            },
            {
                "headerName": "Quantity",
                "field": "order_qty",
                "sortable": True,
                "flex": 2,
            },
            {
                "headerName": "OpenQty",
                "field": "open_qty",
                "sortable": True,
                "flex": 2,
            },
            {
                "headerName": "FilledQty",
                "field": "filled_qty",
                "sortable": True,
                "flex": 2,
                "valueFormatter": price_formatter,
            },
            {
                "headerName": "Condition",
                "field": "conditions_str",
                "sortable": True,
                "flex": 2,
            },
        ]

        return html.Div(
            [
                # Store latest order book state
                dcc.Store(
                    id={
                        "type": "order-book-state",
                        "prefix": self.prefix,
                    },
                    data={},
                ),

                # Order grid
                dag.AgGrid(
                    id={
                        "type": "order-grid",
                        "prefix": self.prefix,
                    },
                    columnDefs=column_defs,
                    rowData=self.row_data,
                    dashGridOptions={"rowSelection": "single"},
                    defaultColDef={
                        "flex": 1,
                        "minWidth": 100,
                        "resizable": True,
                    },
                    style={"height": "400px", "width": "100%"},
                    className="ag-theme-quartz-dark",
                ),
            ]
        )

    @staticmethod
    def register_callbacks(app):
        # ----------------------------------
        # Update order grid on state change
        # ----------------------------------
        @app.callback(
            Output({"type": "order-grid", "prefix": MATCH}, "rowData"),
            Input({"type": "liquibook-state-change", "prefix": MATCH}, "data"),
            Input({"type": "liquibook-order-cancel-modify", "prefix": MATCH}, "data"),
            prevent_initial_call=True,
        )
        def order_book_state(order_state, order_state_cancel_modify):
            triggered = callback_context.triggered_id

            if triggered is None:
                return dash.no_update

            if triggered["type"] == "liquibook-state-change" and order_state:
                return order_state.get("orders", [])

            if triggered["type"] == "liquibook-order-cancel-modify" and order_state_cancel_modify:
                return order_state_cancel_modify.get("orders", [])

            return dash.no_update

        # ----------------------------------
        # Capture selected order from grid
        # ----------------------------------
        @app.callback(
            Output({"type": "selected-order", "prefix": MATCH}, "data"),
            Input({"type": "order-grid", "prefix": MATCH}, "selectedRows"),
            prevent_initial_call=True,
        )
        def display_selected(selected_rows):
            if selected_rows:
                return selected_rows[0]
            return None
