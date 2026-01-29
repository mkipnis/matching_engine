import dash
import liquibook
from dash import dcc, Output, Input, State, callback_context, html
import dash_bootstrap_components as dbc
from liquibook_adapter.LiquiBookAdapter import LiquiBookAdapter


class OrderFormComponent(object):

    def __init__(self, prefix):
        self.prefix = prefix
        self.order_details = {}

    def layout(self):
        return html.Div(
            dbc.Card(
                id=f"{self.prefix}-order-form-wrapper",
                children=dbc.CardBody([
                    dbc.Row([
                        dcc.Store(id=f"{self.prefix}-form-ready-store"),
                        dcc.Store(id=f"{self.prefix}-selected-price-level"),
                        dbc.Col([
                            dbc.Label("Price"),
                            dbc.Input(type="number", id=f"{self.prefix}-price-input", step=100, placeholder="Enter price")
                        ], width=3),
                        dbc.Col([
                            dbc.Label("Quantity"),
                            dbc.Input(type="number", id=f"{self.prefix}-quantity-input", step=100, placeholder="Enter quantity", value=500)
                        ], width=3),
                        dbc.Col([
                            dbc.Label("Order Type"),
                            dcc.Dropdown(
                                id=f"{self.prefix}-order-type-dropdown",
                                options=[
                                    {"label": "Market", "value": "market"},
                                    {"label": "Limit", "value": "limit"},
                                    {"label": "Stop", "value": "stop"},
                                    {"label": "Stop Limit", "value": "stop_limit"},
                                ],
                                style={"color": "black"},
                                value="limit",
                                placeholder="Select order type"
                            )
                        ], width=3),
                        dbc.Col([
                            dbc.Label("Stop Price"),
                            dbc.Input(type="number", id=f"{self.prefix}-stop-price-input", step=1, placeholder="Enter stop price",
                                      disabled=True, value=0)
                        ], width=3),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Condition"),
                            dcc.Dropdown(
                                id=f"{self.prefix}-condition-dropdown",
                                options=[
                                    {"label": "Day", "value": liquibook.oc_no_conditions},
                                    {"label": "Immediate or cancel", "value": liquibook.oc_immediate_or_cancel},
                                    {"label": "Fill or Kill", "value": liquibook.oc_fill_or_kill},
                                ],
                                style={"color": "black"},
                                value=liquibook.oc_no_conditions,
                                placeholder="Select condition"
                            )
                        ], width=3),
                        dbc.Col(
                            html.Div([
                                dbc.Label("All or None"),
                                dbc.Checkbox(id=f"{self.prefix}-all-or-none-checkbox", value=False)
                            ], className="d-flex align-items-center gap-2 mt-4"),
                            width=3
                        ),
                        dbc.Col([
                            dbc.Button("Buy", id=f"{self.prefix}-buy-button", color="success", className="me-2 w-25"),
                            dbc.Button("Sell", id=f"{self.prefix}-sell-button", color="danger", className="me-2 w-25"),
                        ], width=6, className="d-flex justify-content-left align-items-center")
                    ]),
                ]),
                style={"borderRadius": "10px"},
            )
        )

    @staticmethod
    def register_callbacks(app, prefix, adapter_container):
        """Register all callbacks for the OrderFormComponent."""

        @app.callback(
            Output(f"{prefix}-stop-price-input", "disabled"),
            Input(f"{prefix}-order-type-dropdown", "value"),
            prevent_initial_call=True
        )
        def toggle_stop_price(order_type):
            return order_type not in ["stop", "stop_limit"]

        @app.callback(
            Output(f"{prefix}-liquibook-state-change", "data"),
            Input(f"{prefix}-buy-button", "n_clicks"),
            Input(f"{prefix}-sell-button", "n_clicks"),
            State(f"{prefix}-price-input", "value"),
            State(f"{prefix}-quantity-input", "value"),
            State(f"{prefix}-order-type-dropdown", "value"),
            State(f"{prefix}-stop-price-input", "value"),
            State(f"{prefix}-condition-dropdown", "value"),
            State(f"{prefix}-all-or-none-checkbox", "value"),
            prevent_initial_call=True
        )
        def handle_order(buy_clicks, sell_clicks, price, quantity, order_type, stop_price, order_condition,
                         all_or_none):

            triggered = callback_context.triggered_id

            if all_or_none:
                order_condition = order_condition | liquibook.oc_all_or_none

            operation = {
                'operation': 'order',
                'price': price,
                'quantity': quantity,
                'order_type': order_type,
                'stop_price': stop_price or 0,
                'condition': order_condition,
            }

            if triggered == f"{prefix}-buy-button":
                operation['is_buy'] = True
            elif triggered == f"{prefix}-sell-button":
                operation['is_buy'] = False

            adapter = adapter_container[prefix]
            liquibook_state = adapter.submit_order(operation)

            return liquibook_state

        @app.callback(
            Output(f"{prefix}-price-input", "value"),
            Input(f"{prefix}-selected-price-level", "data"),
            State(f"{prefix}-price-input", "value"),
            prevent_initial_call = True
        )
        def price_select(price_depth_level, latest_price):

            # User clicked a price level
            if price_depth_level is not None:
                return price_depth_level

            # Preserve manually typed value
            if latest_price is not None:
                return latest_price

            # Fallback to market price
            adapter = adapter_container.get(prefix)
            if adapter and "market_price" in adapter.instrument:
                return adapter.instrument["market_price"]

            return dash.no_update


