import streamlit as st
import pandas as pd
import plotly.express as px
import json

st.set_page_config(layout="wide")
st.title("Video Timeline Data Analysis")

uploaded_file = st.file_uploader("Upload a JSON file", type="json")

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


if uploaded_file is not None:
    
    json_data = json.loads(uploaded_file.read().decode("utf-8"))
    st.write(json_data)

    intial_data_df = pd.DataFrame(json_data['events'])

    print(intial_data_df)
    
    intial_data_df['timestamp'] = pd.to_datetime(intial_data_df['timestamp'])
    intial_data_df['value'] = intial_data_df['value'].round().astype(int)
    intial_data_df['time'] = intial_data_df['timestamp'].dt.strftime('%I:%M:%S %p')

    
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h3 style='color: #1E90FF; font-family: Arial, sans-serif;'>Initial Data from Uploaded JSON</h3>", unsafe_allow_html=True)
        st.dataframe(intial_data_df, use_container_width=True, height=680)

    with col2:
        st.write("### Data Insights")
        
        
        total_events = len(intial_data_df)
        st.write(f"**Total number of events**: {total_events}")

        
        name_counts = intial_data_df['name'].value_counts().reset_index()
        name_counts.columns = ['Event Type', 'Count']

        
        st.write("**Contribution of Each Event Type to the Total Count**:")
        name_contribution = []
        for name, count in name_counts.itertuples(index=False, name=None):
            contribution = (count / total_events) * 100
            name_contribution.append([name, count, f"{contribution:.2f}%"])
        
        name_contribution_df = pd.DataFrame(name_contribution, columns=['Event Type', 'Count', 'Contribution'])
        st.table(name_contribution_df)

        
        top_10_values = intial_data_df['value'].value_counts().head(10).reset_index()
        top_10_values.columns = ['Value', 'Count']

        
        value_breakdown = []
        for _, row in top_10_values.iterrows():
            value = row['Value']
            value_row = [value, row['Count']]
            
            
            value_types = intial_data_df[intial_data_df['value'] == value]['name'].value_counts()
            value_row.extend([value_types.get('periodic', 0), value_types.get('seek', 0),
                             value_types.get('play', 0), value_types.get('pause', 0)])
            
            value_breakdown.append(value_row)
        
        value_breakdown_df = pd.DataFrame(value_breakdown, columns=['Value', 'Total Count', 'Periodic', 'Seek', 'Play', 'Pause'])
        
        st.write("**Top 10 Most Frequent Values with Event Type Breakdown**:")
        st.table(value_breakdown_df)

    st.write("### Data Points for Inital data")
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

    st.write("# Dataframe for periodic")
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

    st.write("# Remove isolated and non continous values from data frame")

    
    continuous_values, continues_indices = find_increasing_sequences(filtered_df['value'].tolist())
    timestamp_list = filtered_df['timestamp'].tolist()
    timestamp_values = []
    for x in continues_indices:
        timestamp_values.append(timestamp_list[x])
    
    df_rows = pd.DataFrame({'timestamp': timestamp_values, 'values': continuous_values})
    df_rows['time'] = df_rows['timestamp'].dt.strftime('%I:%M:%S %p')
    st.write(df_rows)
    
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

        
