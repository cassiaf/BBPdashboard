import streamlit as st
import pandas as pd
import zipfile
import json
import io
import plotly.express as px

st.title("PlayData Project Analyzer")
st.write("Upload your Playdata .sb3 file to analyze your project.")

def read_sb3_timeline(uploaded_file):
    """
    Read the timeline.json file from an uploaded .sb3 file and convert it to a pandas DataFrame
    """
    try:
        # Read the uploaded file as a ZIP archive
        with zipfile.ZipFile(io.BytesIO(uploaded_file.read()), 'r') as archive:
            # Check if timeline.json exists in the archive
            if 'timeline.json' not in archive.namelist():
                st.error("timeline.json not found in the .sb3 file")
                return None
            
            # Read the timeline.json file from the archive
            with archive.open('timeline.json') as timeline_file:
                timeline_data = json.load(timeline_file)
                
        # Convert the JSON data to a DataFrame
        df_uploaded = pd.DataFrame(timeline_data)
        return df_uploaded
    
    except zipfile.BadZipFile:
        st.error("The uploaded file is not a valid .sb3 file")
        return None
    except json.JSONDecodeError:
        st.error("The timeline.json file is not valid JSON")
        return None

# File uploader
uploaded_files = st.file_uploader("Upload your files", type="sb3", accept_multiple_files=True, key=None, help=None, on_change=None, args=None, kwargs=None, disabled=False, label_visibility="visible", width="stretch")

# Summary DataFrame for all uploaded projects
df_allprojects = pd.DataFrame(columns=['project_name', 'total_time', 'num_events'])

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.subheader(f"{uploaded_file.name}")
        
        # Read the timeline data
        df_uploaded = read_sb3_timeline(uploaded_file)
        
        if df_uploaded is not None:          
            # Transpose the DataFrame (swap rows and columns)
            df = df_uploaded.transpose()
            
            # Set the name of the first column (timestamp column)
            df.index.name = 'timestamp'
            df = df.reset_index()
            
            # Convert timestamp to numeric
            df['timestamp'] = pd.to_numeric(df['timestamp'])

            # Compute time_diff as time since the first event (timestamp - first_timestamp)
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

            # Create a timeline visualization using Plotly: time since start vs timestamp
            fig = px.line(
                df,
                x="total_time",
                y=df.index,
                title='Events over time',
                labels={'timestamp': 'Time (seconds)', 'time_diff': 'Time (s)'}
            )

            fig.update_layout(
                xaxis_title="Time (seconds)",
                yaxis_title="Number of events",
                showlegend=False
            )

            # Display the plot
            st.plotly_chart(fig)

            # Display the DataFrame
            st.dataframe(df)
        
    # After processing all uploads show the summary table and allow CSV download
    st.subheader("Uploaded projects summary")
    st.dataframe(df_allprojects)  
            
else:
    st.write("After uploading, the analysis results will be displayed here.")