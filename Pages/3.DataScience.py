import streamlit as st
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import plotly.express as px
import statsmodels.api as sm

st.title("Data Science")

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Define custom CSS styles for the button
button_style = (
    "font-size: 20px;"
    "padding: 8px 0px;"
    "width: 100%;"
    "border: 2px solid #ff0404;"  # Set the default border color
    "background-color: #060606;"  # Set the default background color
    "color: #fffefe;"  # Set the default text color
    "border-radius: 10px;"
)

# Load the data
data = pd.read_csv('aggregated_data_cluster.csv')
data['trandate'] = pd.to_datetime(data['trandate'])
data['Gross Margin'] = data['Gross Margin'] * 100

df = pd.read_csv('price_optimization1.csv')
df['year'] = df['year_month'].str.split('-').str[0]

# Calculate DataFrames for each cluster
def calculate_cluster_data(data, num_clusters):
    kmeans = KMeans(n_clusters=num_clusters)
    data['cluster'] = kmeans.fit_predict(data[['Gross Margin', 'sales']])

    cluster_dataframes = {}  # Store DataFrames for each cluster
    for cluster_id in range(num_clusters):
        cluster_dataframes[cluster_id] = data[data['cluster'] == cluster_id].copy()

    return cluster_dataframes

def calculate_regression_statistics(x, y):
    X = sm.add_constant(x)  # Add a constant to the independent variable (x)
    model = sm.OLS(y, X).fit()  # Fit the linear regression model
    r_squared = model.rsquared
    adj_r_squared = model.rsquared_adj
    coef = model.params[1]  # Coefficient for x
    std_err = model.bse[1]  # Standard error of the coefficient for x
    return r_squared, adj_r_squared, coef, std_err

def create_scree_plot(data, num_clusters):
    wcss = []
    for k in range(1, num_clusters + 1):
        kmeans = KMeans(n_clusters=k)
        kmeans.fit(data[['Gross Margin', 'sales']])
        wcss.append(kmeans.inertia_)

    # Create the scree plot
    scree_plot = px.line(x=list(range(1, num_clusters + 1)), y=wcss, title='Scree Plot')
    scree_plot.update_layout(xaxis_title='Number of Clusters (K)', yaxis_title='Within-Cluster-Sum-of-Squares (WCSS)')

    return scree_plot 

tab1, tab2, tab3,tab4 = st.tabs(["Clustering", "Customer Segmentation", "Price Optimization", "CLV"])

with tab1:
    st.header("Clustering")
    # Sidebar - Cluster filter options
    st.title('Cluster filter option')

    col1, col2, col3 = st.columns(3)
    # In the first column
    with col1:
        start_date = st.date_input('Select start date', data['trandate'].min())

    with col2:
        end_date = st.date_input('Select end date', data['trandate'].max())

    with col3:
        selected_regions = st.multiselect('Select region name', data['region_name'].unique())

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    num_clusters = st.slider('Select number of clusters', 1, 8, 2)

    if st.button('Apply'):
        # Filter the data based on date range and selected regions
        start_date = start_date.tz_localize('UTC')
        end_date = end_date.tz_localize('UTC')
        filtered_data = data[(data['trandate'] >= start_date) & (data['trandate'] <= end_date)]
        if selected_regions:
            filtered_data = filtered_data[filtered_data['region_name'].isin(selected_regions)]

        # Perform clustering using K-Means as an example
        kmeans = KMeans(n_clusters=num_clusters)
        filtered_data['cluster'] = kmeans.fit_predict(filtered_data[['Gross Margin', 'sales']])

        cluster_summary = []

        for cluster_label, cluster_data in filtered_data.groupby('cluster'):
            min_gross_margin = cluster_data['Gross Margin'].min()
            max_gross_margin = cluster_data['Gross Margin'].max()
            min_sales = cluster_data['sales'].min()
            max_sales = cluster_data['sales'].max()

            x = cluster_data['Gross Margin']
            y = cluster_data['sales']
            r_squared, adj_r_squared, coef, std_err = calculate_regression_statistics(x, y)

            cluster_summary.append({
                'Cluster': f'Cluster {cluster_label}',
                'Min Gross Margin': round(min_gross_margin, 2),
                'Max Gross Margin': round(max_gross_margin, 2),
                'Min Sales': round(min_sales, 2),
                'Max Sales': round(max_sales, 2),
                'R-squared': round(r_squared, 2),
                'Adj. R-squared': round(adj_r_squared, 2),
                'Coefficient': round(coef, 2),
                'Std Err': round(std_err, 2)
            })

        st.title('Cluster Summary')
        st.table(pd.DataFrame(cluster_summary))
        cluster_labels = {i: f'Cluster {i}' for i in range(num_clusters)}
        filtered_data['cluster'] = filtered_data['cluster'].map(cluster_labels)
        fig = px.scatter(filtered_data, x='Gross Margin', y='sales', color='cluster', title=f'Scatter Plot with {num_clusters} Clusters')
        fig.update_xaxes(title_text='Gross Margin')
        fig.update_yaxes(title_text='Sales')
        st.plotly_chart(fig)

        scree = create_scree_plot(data, num_clusters)
        st.plotly_chart(scree)
    else:
        filtered_data = data
        if selected_regions:
            filtered_data = filtered_data[filtered_data['region_name'].isin(selected_regions)]

        # Perform clustering using K-Means as an example
        kmeans = KMeans(n_clusters=num_clusters)
        filtered_data['cluster'] = kmeans.fit_predict(filtered_data[['Gross Margin', 'sales']])

        cluster_summary = []

        for cluster_label, cluster_data in filtered_data.groupby('cluster'):
            min_gross_margin = cluster_data['Gross Margin'].min()
            max_gross_margin = cluster_data['Gross Margin'].max()
            min_sales = cluster_data['sales'].min()
            max_sales = cluster_data['sales'].max()

            x = cluster_data['Gross Margin']
            y = cluster_data['sales']
            r_squared, adj_r_squared, coef, std_err = calculate_regression_statistics(x, y)

            cluster_summary.append({
                'Cluster': f'Cluster {cluster_label}',
                'Min Gross Margin': round(min_gross_margin, 2),
                'Max Gross Margin': round(max_gross_margin, 2),
                'Min Sales': round(min_sales, 2),
                'Max Sales': round(max_sales, 2),
                'R-squared': round(r_squared, 2),
                'Adj. R-squared': round(adj_r_squared, 2),
                'Coefficient': round(coef, 2),
                'Std Err': round(std_err, 2)
            })

        st.table(pd.DataFrame(cluster_summary))
        cluster_labels = {i: f'Cluster {i}' for i in range(num_clusters)}
        filtered_data['cluster'] = filtered_data['cluster'].map(cluster_labels)
        # Scatter plot
        fig = px.scatter(filtered_data, x='Gross Margin', y='sales', color=f'cluster', title=f'Scatter Plot with {num_clusters} Clusters')
        fig.update_xaxes(title_text='Gross Margin')
        fig.update_yaxes(title_text='Sales')
        st.plotly_chart(fig)

        scree = create_scree_plot(data, 8)
        st.plotly_chart(scree)

with tab2:
   st.header("Customer Segmentation")
   st.success("work in progress")

with tab3:
    st.header("Price Optimization")
    # Sidebar - Filter options
    st.title("Prize Optimization Filter Options")

    col1, col2 = st.columns(2)

    with col1:
        graph_type = st.selectbox("Item Names", ['All Item Names'] + list(df['Item Number'].unique()))

    with col2:
        year = st.selectbox("Years", ['All Years'] + list(df['year'].unique()))

    col1, col2 = st.columns(2)

    # Adding elements to the second row
    with col1:
        year_month = st.multiselect("Year Month", ['All Year Months'] + list(df['year_month'].unique()))

    with col2:
        region_names = st.multiselect("Region Names", ['All Region Names'] + list(df['region_name'].unique()))

    col1, col2 = st.columns(2)

    # Adding elements to the second row
    with col1:
        apply_button = st.button("Apply", key="apply_button_unique_key")

    with col2:
        reset_button = st.button("Reset")

    # Main content area
    st.title("Prize Optimization")

    # Filter the data based on the selected options
    if apply_button:
        filtered_data = df.copy()

        if graph_type != 'All Item Names':
            filtered_data = filtered_data[filtered_data['Item Number'] == graph_type]

        if year != 'All Years':
            filtered_data = filtered_data[filtered_data['year'] == year]

        if year_month and 'All Year Months' not in year_month:
            filtered_data = filtered_data[filtered_data['year_month'].isin(year_month)]

        if region_names and 'All Region Names' not in region_names:
            filtered_data = filtered_data[filtered_data['region_name'].isin(region_names)]

        # Plot the graph
        if not filtered_data.empty:
            fig = px.scatter(filtered_data, x='Qty Shipped', y='cost_per_unit', color='region_name', title='Sales vs Cost')
            st.plotly_chart(fig)
        else:
            st.write("No data available for the selected filters.")
    else:
        fig = px.scatter(df, x='Qty Shipped', y='cost_per_unit', color='region_name', title='Sales vs Cost')
        st.plotly_chart(fig)

    if reset_button:
        # Reset filter values
        graph_type = 'All Item Names'
        year = 'All Years'
        year_month = []
        region_names = []

    # Show the filter values after changes (optional)
    st.write("Selected Item Name:", graph_type)
    st.write("Selected Year:", year)
    st.write("Selected Year Months:", year_month)
    st.write("Selected Region Names:", region_names)

with tab4:
   st.header("CLV")
   st.success("work in progress")