# -*- coding: utf-8 -*-
# Copyright 2024-2025 Streamlit Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="PlayData project analysis",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
)

"""
# :material/query_stats: PlayData project analysis

Analyze and compare your .sb3 project files.
"""

""  # Add some space.

cols = st.columns([1, 3])
# Will declare right cell later to avoid showing it when no data.

top_left_cell = cols[0].container(
    border=True, height="stretch", vertical_alignment="center"
)

with top_left_cell:
    uploaded_files = st.file_uploader("Upload your files", type="sb3", accept_multiple_files=True, key=None, help=None, on_change=None, args=None, kwargs=None, disabled=False, label_visibility="visible", width="stretch")

# Build a list of uploaded filenames (Streamlit returns UploadedFile objects)
uploaded_names = [f.name for f in uploaded_files] if uploaded_files else []

with top_left_cell:

    # Keep `tickers` (the multiselect selection) in session state and
    # automatically sync it to uploaded files when uploads change.
    # Don't overwrite the user's manual selection unless the uploaded
    # set is different from the current selection.
    if uploaded_names:
        if (
            "tickers" not in st.session_state
            or set(st.session_state.get("tickers", [])) != set(uploaded_names)
        ):
            # Preserve upload order; copy to avoid mutating original list
            st.session_state["tickers"] = uploaded_names.copy()
    else:
        # Ensure key exists so the widget has predictable state
        st.session_state.setdefault("tickers", [])

    # Selectbox for projects (use filenames as options). Use the session
    # state key to reflect automatic updates above.
    tickers = st.multiselect(
        "Projects to compare",
        options=sorted(uploaded_names),
        key="tickers",
        placeholder="Choose projects to compare",
        accept_new_options=True,
    )

# Time horizon selector
horizon_map = {
    "1 Months": "1mo",
    "3 Months": "3mo",
    "6 Months": "6mo",
    "1 Year": "1y",
    "5 Years": "5y",
    "10 Years": "10y",
    "20 Years": "20y",
}

with top_left_cell:
    # Buttons for picking time horizon
    horizon = st.pills(
        "Time horizon",
        options=list(horizon_map.keys()),
        default="6 Months",
    )

# `tickers` contains project filenames uploaded by the user; keep original casing

# Update query param when text input changes
#if tickers:
#    st.query_params["stocks"] = stocks_to_str(tickers)
#else:
#    # Clear the param if input is empty
#    st.query_params.pop("stocks", None)

#if not tickers:
#    top_left_cell.info("Pick some stocks to compare", icon=":material/info:")
#    st.stop()


right_cell = cols[1].container(
    border=True, height="stretch", vertical_alignment="center"
)

#@st.cache_resource(show_spinner=False)
#def load_data(tickers, period):
#    tickers_obj = 10
    #tickers_obj = 'yf.Tickers(tickers)'
#    data = tickers_obj.history(period=period)
#    if data is None:
#        raise RuntimeError("YFinance returned no data.")
#    return data["Close"]


# Load the data
#try:
#data = load_data(tickers, horizon_map[horizon])
#except yf.exceptions.YFRateLimitError as e:
#    st.warning("YFinance is rate-limiting us :(\nTry again later.")
#    load_data.clear()  # Remove the bad cache entry.
#    st.stop()

#empty_columns = data.columns[data.isna().all()].tolist()

#if empty_columns:
#    st.error(f"Error loading data for the tickers: {', '.join(empty_columns)}.")
#    st.stop()

# Normalize prices (start at 1)
#normalized = data.div(data.iloc[0])

#latest_norm_values = {normalized[ticker].iat[-1]: ticker for ticker in tickers}
#max_norm_value = max(latest_norm_values.items())
#min_norm_value = min(latest_norm_values.items())

bottom_left_cell = cols[0].container(
    border=True, height="stretch", vertical_alignment="center"
)

#with bottom_left_cell:
#    cols = st.columns(2)
#    cols[0].metric(
#        "Best stock",
#        max_norm_value[1],
#        delta=f"{round(max_norm_value[0] * 100)}%",
#        width="content",
#    )
#    cols[1].metric(
#        "Worst stock",
#        min_norm_value[1],
#        delta=f"{round(min_norm_value[0] * 100)}%",
#        width="content",
#    )


# Plot normalized prices
#with right_cell:
#    st.altair_chart(
#        alt.Chart(
#            normalized.reset_index().melt(
#                id_vars=["Date"], var_name="Stock", value_name="Normalized price"
#            )
#        )
#        .mark_line()
#        .encode(
#            alt.X("Date:T"),
#            alt.Y("Normalized price:Q").scale(zero=False),
#            alt.Color("Stock:N"),
#        )
#        .properties(height=400)
#    )

""
""

# Plot individual stock vs peer average
"""
## Individual stocks vs peer average

For the analysis below, the "peer average" when analyzing stock X always
excludes X itself.
"""

#if len(tickers) <= 1:
#    st.warning("Pick 2 or more tickers to compare them")
#    st.stop()

#NUM_COLS = 4
#cols = st.columns(NUM_COLS)



""
""

"""
## Raw data
"""