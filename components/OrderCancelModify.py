import dash
from dash import dcc, Output, Input, State, callback_context, html
import dash_bootstrap_components as dbc
from liquibook_adapter.LiquiBookAdapter import LiquiBookAdapter


class OrderCancelModifyComponent:

    def __init__(self, prefix: str):
        self.prefix = prefix

    def layout(self):
        return html.Div([
            html.Hr(
                style={
                    "borderTop": "2px solid #6c757d",
                    "margin": "10px 0 10px"
                }
            ),
            dbc.Card(
                dbc.CardBody(
                    dbc.Row([
                        dcc.Store(id=f"{self.prefix}-selected-order"),

                        # Order Id
                        dbc.Col(
                            dbc.Label("Order Id:", className="text-end w-100"),
                            width="auto",
                            className="d-flex align-items-center"
                        ),
                        dbc.Col(
                            dbc.Label(id=f"{self.prefix}-order_id_", className="text-end w-100"),
                            width="auto",
                            className="d-flex align-items-center"
                        ),

                        dbc.Col(width=True),  # spacer

                        # Price
                        dbc.Col(
                            dbc.Label("Price", className="text-end w-100"),
                            width="auto",
                            className="d-flex align-items-center"
                        ),
                        dbc.Col(
                            dbc.Input(
                                type="number",
                                id=f"{self.prefix}-new-price-input",
                                step=100,
                                placeholder="Enter new price"
                            ),
                            width=2
                        ),

                        # Delta Qty
                        dbc.Col(
                            dbc.Label("Delta Qty", className="text-end w-100"),
                            width="auto",
                            className="d-flex align-items-center"
                        ),
                        dbc.Col(
                            dbc.Input(
                                type="number",
                                id=f"{self.prefix}-delta-quantity-input",
                                step=100,
                                placeholder="Enter quantity"
                            ),
                            width=2
                        ),

                        # Buttons
                        dbc.Col([
                            dbc.Button(
                                "Modify",
                                id=f"{self.prefix}-modify-order-button",
                                color="success",
                                className="me-2"
                            ),
                            dbc.Button(
                                "Cancel",
                                id=f"{self.prefix}-cancel-order-button",
                                color="danger",
                                className="me-2"
                            ),
                        ], width="auto", className="d-flex align-items-center"),

                    ], className="g-2 flex-nowrap"),  # prevents wrapping
                ),
                style={"borderRadius": "10px", "margin": "10px 0"},
            ),
        ], id=f"{self.prefix}-modify-cancel-panel", style={"display": "none"})

    @staticmethod
    def register_callbacks(app, prefix, adapter_container):

        @app.callback(
            Output(f"{prefix}-order_id_", "children"),
            Output(f"{prefix}-new-price-input", "value"),
            Output(f"{prefix}-delta-quantity-input", "value"),
            Output(f"{prefix}-modify-cancel-panel", "style"),
            Input(f"{prefix}-selected-order", "data"),
        )
        def handle_selected(selected_order):
            if selected_order is not None and selected_order['state_str'] == 'Accepted':
                return selected_order['order_id_'], selected_order['price'], 0, {"display": "block"}
            return None, None, None, {"display": "none"}

        @app.callback(
            Output(f"{prefix}-liquibook-order-cancel-modify", "data"),
            Input(f"{prefix}-modify-order-button", "n_clicks"),
            Input(f"{prefix}-cancel-order-button", "n_clicks"),
            State(f"{prefix}-new-price-input", "value"),
            State(f"{prefix}-delta-quantity-input", "value"),
            State(f"{prefix}-selected-order", "data"),
            prevent_initial_call=True
        )
        def handle_order(modify_clicks, cancel_clicks, new_price, delta_quantity, selected_order):
            triggered = callback_context.triggered_id
            adapter = adapter_container[prefix]
            if triggered == f"{prefix}-cancel-order-button":
                return adapter.cancel_order(selected_order)
            else:
                return adapter.modify_order(selected_order, delta_quantity, new_price)
