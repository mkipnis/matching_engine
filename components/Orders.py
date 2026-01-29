import dash_ag_grid as dag
from dash import html, dcc, Output, Input, callback_context

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
            {"headerName": "OrderId", "field": "order_id_", "sortable": True, "flex": 2, "filter": "agTextColumnFilter"},
            {"headerName": "OrderState", "field": "state_str", "sortable": True, "flex": 2},
            {"headerName": "Side", "field": "is_buy", "sortable": True, "flex": 2,
             "valueFormatter": side_formatter, "cellRenderer": "agTextCellRenderer"},
            {"headerName": "Price", "field": "price", "sortable": True, "flex": 2, "valueFormatter": price_formatter},
            {"headerName": "StopPx", "field": "stop_price", "sortable": True, "flex": 2, "valueFormatter": price_formatter},
            {"headerName": "Quantity", "field": "order_qty", "sortable": True, "flex": 2},
            {"headerName": "OpenQty", "field": "open_qty", "sortable": True, "flex": 2},
            {"headerName": "FilledQty", "field": "filled_qty", "sortable": True, "flex": 2, "valueFormatter": price_formatter},
            {"headerName": "Condition", "field": "conditions_str", "sortable": True, "flex": 2},
        ]

        return html.Div([
            dcc.Store(id=f"{self.prefix}-order-book-state", data={}),
            dag.AgGrid(
                id=f"{self.prefix}-order-grid",
                columnDefs=column_defs,
                rowData=self.row_data,
                dashGridOptions={"rowSelection": "single"},
                defaultColDef={"flex": 1, "minWidth": 100, "resizable": True},
                style={"height": "400px", "width": "100%"},
                className="ag-theme-quartz-dark"
            )
        ])

    @staticmethod
    def register_callbacks(app, prefix):
        @app.callback(
            Output(f"{prefix}-order-grid", "rowData"),
            Input(f"{prefix}-liquibook-state-change", "data"),
            Input(f"{prefix}-liquibook-order-cancel-modify", "data"),
            prevent_initial_call=True
        )
        def order_book_state(order_state, order_state_cancel_modify):
            triggered = callback_context.triggered_id
            if triggered == f"{prefix}-liquibook-state-change":
                return order_state['orders']
            elif triggered == f"{prefix}-liquibook-order-cancel-modify":
                return order_state_cancel_modify['orders']
            return None

        @app.callback(
            Output(f"{prefix}-selected-order", "data"),
            Input(f"{prefix}-order-grid", "selectedRows"),
            prevent_initial_call=True
        )
        def display_selected(selected):
            if selected:
                return selected[0]
            return None