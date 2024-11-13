import streamlit as st
import pandas as pd
import plotly.express as px
import json
import numpy as np
import altair as alt

st.set_page_config(layout="wide")
st.markdown("<h1 style='color: #4169E1;'>Analyzing Video Engagement</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #666666;'>Analyze and visualize user interaction patterns throughout video playback</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload a JSON file", type="json")

def get_frequencies(values, duration):
    counts = np.zeros(duration, dtype=int)
    
    for value in values:
        second = int(value)
        if 0 <= second < duration:
            counts[second] += 1
    counts = np.array(counts)
    x_axis = np.arange(duration)
    return counts, x_axis

def find_increasing_sequences(numbers):
    result = []
    current_sequence = []

    for i in range(len(numbers)):
        if not current_sequence or numbers[i] == current_sequence[-1][1] + 1:
            current_sequence.append((i, numbers[i]))
        else:
            if len(current_sequence) > 1:
                result.append(current_sequence)
            current_sequence = [(i, numbers[i])]

    if len(current_sequence) > 1:
        result.append(current_sequence)

    result_indices = []
    result_values = []
    for sequence in result:
        for index, value in sequence:
            result_indices.append(index)
            result_values.append(value)
    
    return result_values, result_indices

def normalize_data(data, column, min_val, max_val):
    normalized = (data[column] - data[column].min()) / (data[column].max() - data[column].min())
    return normalized * (max_val - min_val) + min_val

if uploaded_file is not None:
    json_data = json.loads(uploaded_file.read().decode("utf-8"))
    intial_data_df = pd.DataFrame(json_data['events'])
    total_events = len(intial_data_df)
    st.write(f"**Total number of events**: {total_events}")
    st.write(json_data)
    total_video_duration = int(json_data['videoDuration'])
    

    print(intial_data_df)
    
    intial_data_df['timestamp'] = pd.to_datetime(intial_data_df['timestamp'])
    intial_data_df['value'] = intial_data_df['value'].round().astype(int)
    intial_data_df['time'] = intial_data_df['timestamp'].dt.strftime('%I:%M:%S %p')

    
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h3 style='color: #1E90FF;'>Initial Data from Uploaded JSON</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #666666;'>Raw event data captured from video interactions</p>", unsafe_allow_html=True)
        st.dataframe(intial_data_df, use_container_width=True, height=720)

    with col2:
        st.markdown("<h3 style='color: #1E90FF;'>Data Insights</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #666666;'>Key metrics and patterns extracted from the event data</p>", unsafe_allow_html=True)

        
        name_counts = intial_data_df['name'].value_counts().reset_index()
        name_counts.columns = ['Event Type', 'Count']

        
        st.write("**Contribution of Each Event Type to the Total Count**:")
        name_contribution = []
        for name, count in name_counts.itertuples(index=False, name=None):
            contribution = (count / total_events) * 100
            name_contribution.append([name, count, f"{contribution:.2f}%"])
        
        name_contribution_df = pd.DataFrame(name_contribution, columns=['Event Type', 'Count', 'Contribution'])
        st.table(name_contribution_df)

        
        value_frequencies = intial_data_df['value'].value_counts().reset_index()
        value_frequencies.columns = ['Value', 'Count']

        # Create breakdown for all values
        value_breakdown = []
        for _, row in value_frequencies.iterrows():
            value = row['Value']
            value_row = [value, row['Count']]
            
            # Get counts for each event type
            value_types = intial_data_df[intial_data_df['value'] == value]['name'].value_counts()
            value_row.extend([
                value_types.get('periodic', 0), 
                value_types.get('seek', 0),
                value_types.get('play', 0), 
                value_types.get('pause', 0)
            ])
            
            value_breakdown.append(value_row)

        # Create DataFrame with all values
        value_breakdown_df = pd.DataFrame(
            value_breakdown, 
            columns=['Value', 'Total Count', 'Periodic', 'Seek', 'Play', 'Pause']
        )

        # Display with Streamlit
        st.markdown("<h3 style='color: #1E90FF;'>Complete Value Frequency Breakdown</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #666666;'>Detailed breakdown of all values and their event type distributions</p>", unsafe_allow_html=True)
        st.dataframe(
            value_breakdown_df,
            use_container_width=True,
            height=360,
        )

    st.markdown("<h3 style='color: #1E90FF;'>Data Points for Initial Data</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #666666;'>Scatter plot visualization of all event types across timeline</p>", unsafe_allow_html=True)
    fig = px.scatter(
        intial_data_df,
        x="value",
        y="timestamp",
        color="name",
        hover_data={"time": True, "name": True, "value": True},
        title=" ",
        labels={"timestamp": "Time", "value": "Value"},
    )
    fig.update_layout(
        xaxis_title="Timestamp",
        yaxis_title="Value",
        title_x=0.5,
        margin=dict(l=10, r=10, t=40, b=10),
        height=500,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<h2 style='color: #1E90FF;'>Data Points for Periodic Events</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #666666;'>Filtered view showing only periodic tracking events</p>", unsafe_allow_html=True)
    filtered_df = intial_data_df[intial_data_df['name'] == 'periodic'].sort_values(by='timestamp')
    
    fig = px.scatter(
        filtered_df,
        x="value",
        y="timestamp",
        color="name",
        hover_data={"time": True, "name": True, "value": True},
        title=" ",
        labels={"timestamp": "Time", "value": "Value"},
    )
    fig.update_layout(
        xaxis_title="Timestamp",
        yaxis_title="Value",
        title_x=0.5,
        margin=dict(l=10, r=10, t=40, b=10),
        height=500,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<h2 style='color: #1E90FF;'>Continuous Viewing Patterns</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #666666;'>Data showing only continuous viewing sequences, excluding isolated events and non continous events</p>", unsafe_allow_html=True)

    
    continuous_values, continues_indices = find_increasing_sequences(filtered_df['value'].tolist())
    timestamp_list = filtered_df['timestamp'].tolist()
    timestamp_values = []
    for x in continues_indices:
        timestamp_values.append(timestamp_list[x])
    
    df_rows = pd.DataFrame({'timestamp': timestamp_values, 'values': continuous_values})
    df_rows['time'] = df_rows['timestamp'].dt.strftime('%I:%M:%S %p')

    fig = px.scatter(
        df_rows,
        x="values",
        y="timestamp",
        title=" ",
        labels={"timestamp": "Time", "value": "Value"},
    )
    fig.update_layout(
        xaxis_title="time_value",
        yaxis_title="time_value",
        title_x=0.5,
        margin=dict(l=10, r=10, t=40, b=10),
        height=500,
    )
    st.plotly_chart(fig, use_container_width=True)

    value_frequency, time_seconds = get_frequencies(continuous_values, total_video_duration)

    data = pd.DataFrame({
        'Time': time_seconds,
        'Frequency': value_frequency
    })


    st.markdown("<h3 style='color: #1E90FF;'>Frequency Distribution</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #666666;'>Interactive visualization showing the distribution of viewing patterns over time</p>", unsafe_allow_html=True)
    
    bar_chart = alt.Chart(data).mark_bar().encode(
        x=alt.X('Time', title='Time (seconds)'),
        y=alt.Y('Frequency', title='Frequency'),
        color=alt.Color('Frequency:Q', scale=alt.Scale(scheme='oranges'))
    ).properties(
        width=600,
        height=400
    )
    st.altair_chart(bar_chart, use_container_width=True)

    MIN_VALUE = 0  
    MAX_VALUE = 10

    data['Frequency_normalized'] = normalize_data(data, 'Frequency', MIN_VALUE, MAX_VALUE)

    st.markdown("<h3 style='color: #1E90FF;'>Normalized Area Chart</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #666666;'><span style='font-size: 16px; color: #1E90FF;'>Final Data</span>, Data normalized to a scale of 1-10 for visualization</p>", unsafe_allow_html=True)

    area = alt.Chart(data).mark_area(
        clip=True,
        interpolate='monotone',
        opacity=0.6,
        color='violet',
        height=150
    ).encode(
        x=alt.X('Time', title='Time')
            .scale(zero=False, nice=False),
        y=alt.Y('Frequency_normalized', title='Normalized Frequency')
            .scale(domain=[MIN_VALUE, MAX_VALUE])
    ).properties(
        width=500,
        height=150
    )

    st.altair_chart(area, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("<h4 style='color: #1E90FF;'>Continuous Viewing Sequences</h4>", unsafe_allow_html=True)
        st.markdown("<p style='color: #666666;'>Timeline of uninterrupted viewing patterns excluding isolated events</p>", unsafe_allow_html=True)
        st.dataframe(df_rows, use_container_width=True)

    with col4:
        st.markdown("<h4 style='color: #1E90FF;'>Video Segment Popularity</h4>", unsafe_allow_html=True)
        st.markdown("<p style='color: #666666;'>Frequency distribution of views across video timeline</p>", unsafe_allow_html=True)
        st.dataframe(data,use_container_width=True)