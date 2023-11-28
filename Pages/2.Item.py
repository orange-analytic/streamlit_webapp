import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import math
import locale

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

df_customer = pd.read_csv('current_data_full.csv', low_memory=False)

def format_with_commas(number):
    rounded_number = round(number)  # Round the number to an integer
    formatted_number = locale.format("%d", rounded_number, grouping=True)  # Format with commas
    return formatted_number

#item
unique_item_count = df_customer['Item Number'].unique()
Monthly_Items_orders = df_customer.groupby('year_month')['Item Number'].count()
# Calculate the monthly average
monthly_item_avg = format_with_commas(math.ceil(Monthly_Items_orders.mean()))

monthly_unique_item_count = df_customer.groupby('year_month')['Item Number'].nunique()
monthly_unique_item_count_mean = format_with_commas(math.ceil(monthly_unique_item_count.mean()))

agg_df_item = df_customer.groupby('Item Number').agg({
    'sales': 'sum',
    'Net Price': 'sum',
    'gross_profit': 'sum',
    'Item Number': ['count', 'nunique'],  # Perform both count and nunique aggregations
    'Qty Shipped': 'sum',
}).reset_index()

# Rename the columns for clarity
agg_df_item.columns = ['item_name', 'sales', 'amount_flipped', 'gross_profit', 'Item Number1', 'Item Number', 'quantity']

# Calculate Gross Margin (Gross Profit / Sales)
agg_df_item['GM%'] = agg_df_item['gross_profit'] / agg_df_item['sales']
agg_df_item.rename(columns={'sales': 'Sales','amount_flipped': "Amount",'gross_profit': "Gross Profit",'Item Number1':"Total Item",
                      "Item Number":"Total invoices","item_name": "Item Name","quantity":'Quentity'}, inplace=True)

# Main content
st.title("Item Analysis")
st.subheader("Dashboard Overview")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Unique Item Count")
    st.write(f'{len(unique_item_count)}')

with col2:
    st.markdown("### Avg Item monthly")
    st.write(f'{monthly_item_avg}')
with col3:
    st.markdown("### Monthly unique item")
    st.write(f'{monthly_unique_item_count_mean}')

st.title("Select Analysis")
selected_analysis = st.selectbox("Choose Analysis", ["Monthly Item Counts", "Top 10 Selling Items", "Item Analysis (Gross Profit and Total Item)", "Top 12 Items by Revenue"])

if selected_analysis == "Monthly Item Counts":
    # st.write("Monthly Item Counts")
    df_2yeardata = df_customer[df_customer['year_month'] >= '2021-01']
    monthly_counts = df_2yeardata.groupby('year_month')['Item Number'].count().reset_index()
    
    # Create a bar graph to visualize the counts
    fig = {
        'data': [
            {'x': monthly_counts['year_month'], 'y': monthly_counts['Item Number'], 'type': 'bar', 'name': 'Item Count'}
        ],
        'layout': {
            'title': 'Monthly Item Counts',
            'xaxis': {
                'title': 'Month',
                'tickangle': -45,  # Rotate x-axis labels to make them more visible
                'tickfont': {'size': 10},
            },
            'yaxis': {'title': 'Item Count'},
        }
    }
    st.plotly_chart(fig)

elif selected_analysis == "Top 10 Selling Items":
    # st.write("Top 10 Selling Items")
    top_10_items = agg_df_item.sort_values(by='Quentity', ascending=False).head(10)

    fig = px.bar(
        top_10_items,
        x='Item Name',
        y='Quentity',
        labels={'sales': 'Sales',
                
                },
        title='Top 10 Selling Items',
    )
        # return fig
    st.plotly_chart(fig)

elif selected_analysis == "Item Analysis (Gross Profit and Total Item)":
    # st.write("Item Analysis (Gross Profit and Total Item)")
    agg_df_item.query('Sales > 0')
    traces = []
    top__10_companies_graph = agg_df_item.sort_values('Sales', ascending=False).head(10)

    duplicate_columns = agg_df_item.columns[agg_df_item.columns.duplicated()]

    # Generate unique names for duplicate columns
    unique_names = [(col, f"{col}_{i}") for i, col in enumerate(duplicate_columns)]

    # Rename duplicate columns with unique names
    for col, new_col in unique_names:
        agg_df_item = agg_df_item.rename(columns={col: new_col})
    # top__10_companies_graph
    # Create a trace for 'Gross Profit'
    trace_gross_profit = go.Bar(
        x=top__10_companies_graph['Item Name'],
        y=top__10_companies_graph['Gross Profit'],
        name='Gross Profit'
    )
    traces.append(trace_gross_profit)

    # Create a trace for 'Total Item'
    trace_total_item = go.Bar(
        x=top__10_companies_graph['Item Name'],
        y=top__10_companies_graph['Total Item'],
        name='Total Item'
    )
    traces.append(trace_total_item)

    # Create the figure with the traces
    fig = go.Figure(data=traces)
    fig.update_layout(barmode='group', title='Top 10 Items Analysis')

    # Display the bar chart
    st.plotly_chart(fig)

elif selected_analysis == "Top 12 Items by Revenue":
    # st.write("Top 12 Items by Revenue")
    top_10_items = df_customer.sort_values(by='sales', ascending=False).head(12)
    st.dataframe(top_10_items)

# Display additional components or information as needed
