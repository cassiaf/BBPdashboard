import streamlit as st
import pandas as pd
import zipfile
import json
import io
import plotly.express as px
from block_categories import block_categories


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

cols = st.columns([1, 2, 2])

last_cell = cols[2].container(
    border=True, height="stretch", vertical_alignment="center"
)

top_left_cell = cols[0].container(
    border=True, height="stretch", vertical_alignment="top"
)


with top_left_cell:
    uploaded_files = st.file_uploader("Upload your files", type="sb3", accept_multiple_files=True, key=None, help=None, on_change=None, args=None, kwargs=None, disabled=False, label_visibility="collapsed", width="stretch")

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

# Type of analysis selector
analysis_map = {
    "Timeline": "analysis_timeline",
    "Final Project": "analysis_final",
}

with top_left_cell:
    # Buttons for picking analysis selector
    analysis = st.pills(
        "What type of analysis?",
        options=list(analysis_map.keys()),
        default="Final Project",
    )

right_cell = cols[1].container(
    border=True, height="stretch", vertical_alignment="center"
)   

## Reading the uploeaded files 

def read_sb3_files(uploaded_file):
    """
    Read the timeline.json and project.json files from an uploaded .sb3 file.
    Returns a tuple: (timeline_df, project_data)
      - timeline_df: pandas DataFrame or None
      - project_data: dict or None
    """
    try:
        # Open uploaded .sb3 file as a ZIP archive
        with zipfile.ZipFile(io.BytesIO(uploaded_file.read()), 'r') as archive:
            
            # Initialize variables
            timeline_df = None
            project_data = None

            # ---- Read timeline.json ----
            if "timeline.json" in archive.namelist():
                with archive.open("timeline.json") as timeline_file:
                    try:
                        timeline_json = json.load(timeline_file)
                        timeline_df = pd.DataFrame(timeline_json)
                    except Exception as e:
                        st.error(f"Error reading timeline.json: {e}")
            else:
                st.warning("timeline.json not found in the .sb3 file")

            # ---- Read project.json ----
            if "project.json" in archive.namelist():
                with archive.open("project.json") as project_file:
                    try:
                        project_data = json.load(project_file)
                    except Exception as e:
                        st.error(f"Error reading project.json: {e}")
            else:
                st.warning("project.json not found in the .sb3 file")

            # ---- Validation ----
            if timeline_df is None and project_data is None:
                st.error("Neither timeline.json nor project.json was found in the .sb3 file.")
                return None, None

            return timeline_df, project_data

    except zipfile.BadZipFile:
        st.error("The uploaded file is not a valid .sb3 file.")
        return None, None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None, None

    # CREATING CHARTS AND TABLES FOR SELECTED PROJECTS

    # Summary DataFrame for all uploaded projects
df_allprojects = pd.DataFrame(columns=['project_name', 'total_time', 'num_events'])

if uploaded_files:
    all_blocks_df = []  

    for uploaded_file in uploaded_files:
        st.subheader(f"{uploaded_file.name}")
        
        # Read the data
        df_uploaded, project_data = read_sb3_files(uploaded_file)
        
        if df_uploaded is not None:          
            # Timeline analysis
            df = df_uploaded.transpose()
            df.index.name = 'timestamp'
            df = df.reset_index()
            df['timestamp'] = pd.to_numeric(df['timestamp'])

            # Compute time_diff between events
            if len(df) > 0:
                first_ts = df['timestamp'].iloc[0]
            else:
                first_ts = 0
            df['time_diff'] = (df['timestamp'] - first_ts)/1000 

            # Total time spent = last_timestamp - first_timestamp (seconds)
            if len(df) > 1:
                df['total_time'] = (df['timestamp'] - first_ts)/1000
                total_time = df['total_time'].iloc[-1]
            else:
                total_time = 0.0

            num_events = len(df)

            # Append a row for this uploaded project to the summary DataFrame
            df_allprojects.loc[len(df_allprojects)] = [uploaded_file.name, total_time, num_events]

            # Display basic statistics
            st.write(f"Number of events: {len(df)}")
            st.write(f"Total time spent: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")

            # Timeline chart
            fig = px.line(
                df,
                x="total_time",
                y=df.index,
                title='Events over time',
                hover_data ={'total_time', 'event'}
            )   

            fig.update_layout(
                title=uploaded_file.name,
                xaxis_title="Time (seconds)",
                yaxis_title="Number of events",
                showlegend=False,
                width=700, 
                height=250,
            )

            with right_cell:
                st.plotly_chart(fig)
 
            # Project.json analysis (NEW PART) ---
            if project_data is not None and "targets" in project_data:
                block_types = []
                for target in project_data["targets"]:
                    blocks = target.get("blocks", {})
                    for _, block_data in blocks.items():
                        if isinstance(block_data, dict):
                            opcode = block_data.get("opcode", "unknown")
                            block_types.append(opcode)

                if block_types:
                    df_blocks = pd.DataFrame(block_types, columns=["block_type"])
                    df_blocks = df_blocks.value_counts().reset_index(name="count")
                    df_blocks["project"] = uploaded_file.name
                    all_blocks_df.append(df_blocks)
                else:
                    st.info("No blocks found in this project.json file.")

            # Display DataFrames
            st.dataframe(df)
            st.dataframe(df_allprojects)

    # --- After loop: show combined block-type chart ---
    if all_blocks_df:
        df_all_blocks = pd.concat(all_blocks_df, ignore_index=True)

        fig_blocks = px.bar(
            df_all_blocks,
            x="project", y="count", color="block_type",
            barmode="group",
            title="Number of Blocks by type",
            height=400
        )
        
        # Sort block types by total count
        order = (
            df_all_blocks.groupby("block_type")["count"]
            .sum()
            .sort_values(ascending=False)
            .index
        )
        fig_blocks.update_xaxes(categoryorder="array", categoryarray=order, tickangle=45)

        with last_cell:
            st.plotly_chart(fig_blocks, use_container_width=True)


        # Display the DataFrame
        st.dataframe(df)
        st.dataframe(df_allprojects)


