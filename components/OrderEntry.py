# Copyright (c) Mike Kipnis - DistributedATS

import dash
import liquibook
from dash import dcc, Output, Input, State, callback_context, html, MATCH
import dash_bootstrap_components as dbc
from liquibook_adapter.LiquiBookAdapter import LiquiBookAdapter


class OrderFormComponent:

    def __init__(self, prefix):
        self.prefix = prefix

    def layout(self):
        return html.Div(
            dbc.Card(
                id={
                    "type": "order-form-wrapper",
                    "prefix": self.prefix,
                },
                children=dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dcc.Store(
                                    id={
                                        "type": "form-ready-store",
                                        "prefix": self.prefix,
                                    }
                                )
                                ,
                                dcc.Store(
                                    id={"type": "selected-price-level", "prefix": self.prefix}
                                )
                                ,
                                dcc.Store(id={"type": "liquibook-state-change", "prefix": self.prefix}),
                                dbc.Col(
                                    [
                                        dbc.Label("Price"),
                                        dbc.Input(
                                            type="number",
                                            id={
                                                "type": "price-input",
                                                "prefix": self.prefix,
                                            },
                                            step=100,
                                            placeholder="Enter price",
                                        ),
                                    ],
                                    width=3,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label("Quantity"),
                                        dbc.Input(
                                            type="number",
                                            id={
                                                "type": "quantity-input",
                                                "prefix": self.prefix,
                                            },
                                            step=100,
                                            placeholder="Enter quantity",
                                            value=500,
                                        ),
                                    ],
                                    width=3,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label("Order Type"),
                                        dcc.Dropdown(
                                            id={
                                                "type": "order-type-dropdown",
                                                "prefix": self.prefix,
                                            },
                                            options=[
                                                {"label": "Market", "value": "market"},
                                                {"label": "Limit", "value": "limit"},
                                                {"label": "Stop", "value": "stop"},
                                                {"label": "Stop Limit", "value": "stop_limit"},
                                            ],
                                            style={"color": "black"},
                                            value="limit",
                                            placeholder="Select order type",
                                        ),
                                    ],
                                    width=3,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label("Stop Price"),
                                        dbc.Input(
                                            type="number",
                                            id={
                                                "type": "stop-price-input",
                                                "prefix": self.prefix,
                                            },
                                            step=1,
                                            placeholder="Enter stop price",
                                            disabled=True,
                                            value=0,
                                        ),
                                    ],
                                    width=3,
                                ),
                            ],
                            className="mb-3",
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Label("Condition"),
                                        dcc.Dropdown(
                                            id={
                                                "type": "condition-dropdown",
                                                "prefix": self.prefix,
                                            },
                                            options=[
                                                {"label": "Day", "value": liquibook.oc_no_conditions},
                                                {
                                                    "label": "Immediate or cancel",
                                                    "value": liquibook.oc_immediate_or_cancel,
                                                },
                                                {
                                                    "label": "Fill or Kill",
                                                    "value": liquibook.oc_fill_or_kill,
                                                },
                                            ],
                                            style={"color": "black"},
                                            value=liquibook.oc_no_conditions,
                                            placeholder="Select condition",
                                        ),
                                    ],
                                    width=3,
                                ),
                                dbc.Col(
                                    html.Div(
                                        [
                                            dbc.Label("All or None"),
                                            dbc.Checkbox(
                                                id={
                                                    "type": "all-or-none-checkbox",
                                                    "prefix": self.prefix,
                                                },
                                                value=False,
                                            ),
                                        ],
                                        className="d-flex align-items-center gap-2 mt-4",
                                    ),
                                    width=3,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Button(
                                            "Buy",
                                            id={
                                                "type": "buy-button",
                                                "prefix": self.prefix,
                                            },
                                            color="success",
                                            className="me-2 w-25",
                                        ),
                                        dbc.Button(
                                            "Sell",
                                            id={
                                                "type": "sell-button",
                                                "prefix": self.prefix,
                                            },
                                            color="danger",
                                            className="me-2 w-25",
                                        ),
                                    ],
                                    width=6,
                                    className="d-flex justify-content-left align-items-center",
                                ),
                            ]
                        ),
                    ]
                ),
                style={"borderRadius": "10px"},
            )
        )

    @staticmethod
    def register_callbacks(app, adapter_container):
        """Register all callbacks for the OrderFormComponent (static, MATCH-based)."""

        # ----------------------------------
        # Enable / disable stop price
        # ----------------------------------
        @app.callback(
            Output({"type": "stop-price-input", "prefix": MATCH}, "disabled"),
            Input({"type": "order-type-dropdown", "prefix": MATCH}, "value"),
            prevent_initial_call=True,
        )
        def toggle_stop_price(order_type):
            return order_type not in ["stop", "stop_limit"]

        # ----------------------------------
        # Submit buy / sell order
        # ----------------------------------
        @app.callback(
            Output({"type": "liquibook-state-change", "prefix": MATCH}, "data"),
            Input({"type": "buy-button", "prefix": MATCH}, "n_clicks"),
            Input({"type": "sell-button", "prefix": MATCH}, "n_clicks"),
            State({"type": "price-input", "prefix": MATCH}, "value"),
            State({"type": "quantity-input", "prefix": MATCH}, "value"),
            State({"type": "order-type-dropdown", "prefix": MATCH}, "value"),
            State({"type": "stop-price-input", "prefix": MATCH}, "value"),
            State({"type": "condition-dropdown", "prefix": MATCH}, "value"),
            State({"type": "all-or-none-checkbox", "prefix": MATCH}, "value"),
            prevent_initial_call=True,
        )
        def handle_order(
            buy_clicks,
            sell_clicks,
            price,
            quantity,
            order_type,
            stop_price,
            order_condition,
            all_or_none,
        ):
            triggered = callback_context.triggered_id
            prefix = triggered["prefix"]

            if all_or_none:
                order_condition = order_condition | liquibook.oc_all_or_none

            operation = {
                "operation": "order",
                "price": price,
                "quantity": quantity,
                "order_type": order_type,
                "stop_price": stop_price or 0,
                "condition": order_condition,
            }

            if triggered["type"] == "buy-button":
                operation["is_buy"] = True
            elif triggered["type"] == "sell-button":
                operation["is_buy"] = False
            else:
                return dash.no_update

            adapter = adapter_container[prefix]
            return adapter.submit_order(operation)

        # ----------------------------------
        # Price selection from depth grid
        # ----------------------------------
        @app.callback(
            Output({"type": "price-input", "prefix": MATCH}, "value"),
            Input({"type": "selected-price-level", "prefix": MATCH}, "data"),
            Input({"type": "liquibook-prefix-out", "prefix": MATCH},"children"),
            State({"type": "price-input", "prefix": MATCH}, "value"),
            prevent_initial_call=True,
        )
        def price_select(price_depth_level, liquibook_prefix, latest_price):

            if price_depth_level is not None:
                return price_depth_level

            if latest_price is not None:
                return latest_price

            triggered = callback_context.triggered_id
            prefix = triggered["prefix"]

            adapter = adapter_container.get(prefix)
            if adapter and "market_price" in adapter.instrument:
                return adapter.instrument["market_price"]

            return dash.no_update
