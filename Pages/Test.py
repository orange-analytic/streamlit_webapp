import streamlit as st
import plotly.express as px
import pandas as pd
import math
import os
import numpy as np
import matplotlib.pyplot as plt
import calendar
import locale
import plotly.graph_objects as go

def format_with_commas(number):
    rounded_number = round(number)  # Round the number to an integer
    formatted_number = locale.format("%d", rounded_number, grouping=True)  # Format with commas
    return formatted_number

current_dir = os.path.dirname(os.path.abspath(__file__))
csv_file_path = os.path.join(current_dir, 'current_data_full.csv')
st.title("Home page")

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

with open('home.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load your data (replace 'your_data.csv' with your actual data source)
df = pd.read_csv('current_data_full.csv')
df['month_name'] = df['Month'].apply(lambda x: calendar.month_abbr[x])

monthly_sales = df.groupby('Month')['sales'].sum().reset_index()

# Calculate the current year and previous year based on your data
current_year = df['Year'].max()
previous_year = current_year - 1

# Filter the data
graph1 = df[df['year_month'] > '2020-11']
grouped = graph1.groupby('year_month').sum()

# Function to calculate percentage difference
def calculate_percentage_difference(current, previous):
    return ((current - previous) / previous) * 100

if "disabled" not in st.session_state:
    st.session_state.disabled = True

col1, col2, col3 = st.columns(3)
ytd_button = col1.button("YTD")
mtd_button = col2.button("MTD")
selected_option = col3.selectbox(
    "Select Month",
    ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'),
    label_visibility="collapsed",
    disabled=st.session_state.disabled
)

filtered_data = df[df['month_name'] == selected_option] if selected_option != 'MTD' else df

# Run Streamlit
if ytd_button:
    filtered_data = df
    st.session_state.disabled = True

if mtd_button:
    st.session_state.disabled = True
    filtered_data = df[df['month_name'] == selected_option]

if mtd_button is not True:
    st.session_state.disabled = False


# Calculate card values
current_year_sales = filtered_data[filtered_data['Year'] == current_year]['sales'].sum()
previous_year_sales = filtered_data[filtered_data['Year'] == previous_year]['sales'].sum()
sales_difference = current_year_sales - previous_year_sales
percentage_difference_sales = calculate_percentage_difference(current_year_sales, previous_year_sales)

current_year_gp = filtered_data[filtered_data['Year'] == current_year]['gross_profit'].sum()
previous_year_gp = filtered_data[filtered_data['Year'] == previous_year]['gross_profit'].sum()
gp_difference = current_year_gp - previous_year_gp
percentage_difference_gp = calculate_percentage_difference(current_year_gp, previous_year_gp)

current_year_qty = filtered_data[filtered_data['Year'] == current_year]['Qty Shipped'].sum()
previous_year_qty = filtered_data[filtered_data['Year'] == previous_year]['Qty Shipped'].sum()
qty_difference = current_year_qty - previous_year_qty
percentage_difference_qty = calculate_percentage_difference(current_year_qty, previous_year_qty)

current_year_item_count = filtered_data[filtered_data['Year'] == current_year]['Item Number'].nunique()
previous_year_item_count = filtered_data[filtered_data['Year'] == previous_year]['Item Number'].nunique()
item_count_difference = current_year_item_count - previous_year_item_count
percentage_difference_item_count = calculate_percentage_difference(current_year_item_count, previous_year_item_count)

def compaire_data(df):
    # Filter data for the current year
    current_year = df['Year'].max()
    previous_year = current_year - 1
    current_year_data = df[df['Year'] == current_year]

    # Filter data for the previous year
    previous_year_data = df[df['Year'] == previous_year]

    # Filter data for the current year
    data_1 = current_year_data.groupby(['Month']).agg({'sales': 'sum'})

    # Filter data for the previous year
    data2= previous_year_data.groupby(['Month']).agg({'sales': 'sum'})

    # Merge the current year and previous year data
    merge_data = pd.merge(
        data_1,
        data2,
        how="left",
        on='Month'
    )
    merge_data["Percentage Change"] = ((merge_data.sales_x - merge_data.sales_y) / merge_data.sales_y) * 100
    merge_data.reset_index(inplace=True)
    # Rename the new column if desired
    merge_data.rename(columns={'Month': 'Month'}, inplace=True)
    return merge_data

# Add 'Net' to the DataFrame
total_sales_co = df['sales'].sum()
total_cogs_co = df['COGS'].sum()
total_gross_profit_co = df['gross_profit'].sum()

total_sales_ov = df['sales'].sum()
total_cogs_ov = df['COGS'].sum()
total_gross_profit_ov = df['gross_profit'].sum()

# Add 'Net' to the index
index = ['Sales', 'Cogs', 'Gross Profit', 'Net']
data = {'Amount': [total_sales_ov, total_cogs_ov, total_gross_profit_ov, 0]}
core_charge_trans = pd.DataFrame(data=data, index=index)

st.subheader("Monthly Data")
st.write("You can select a specific month or view YTD (Year-to-Date) data using the button.")

col1, col2, col3,col4 = st.columns(4)
col1.metric("Sales",f"$ {format_with_commas(math.ceil(current_year_sales))}", f"{percentage_difference_sales:.2f}%",help ='Sales Percentage Change')
col2.metric("Gross Profit", f"$ {format_with_commas(math.ceil(current_year_gp))}", f"{percentage_difference_gp:.2f}%",help ='Gross Profit Percentage Change')
col3.metric("Quantity",f"{format_with_commas(current_year_qty)}",f"{percentage_difference_qty:.2f}%",help ='Quantity Percentage Change')
col4.metric("Unique Items", f"{format_with_commas(current_year_item_count)}", f"{percentage_difference_item_count:.2f}%",help ='Unique Items Percentage Change')

# Sales Product Graph
st.subheader("Monthly Sales by Product")
# st.write("Visualize your sales by product for the selected month.")
fig = px.bar(monthly_sales, x='Month', y='sales', labels={'sales': 'Sales'})
st.plotly_chart(fig)

# Actual Sales Percentage Change Graph
st.subheader("Actual Sales Percentage Change (Current Year vs. Previous Year)")
data = compaire_data(df)
fig_actual_sales = px.bar(data, x='Month', y='Percentage Change', labels={'Percentage Change': 'Percentage Change'})
st.plotly_chart(fig_actual_sales)

st.subheader("Income Statement")
fig = go.Figure(go.Waterfall(
    name="20",
    orientation="v",
    measure=["relative", "relative", "relative", "total"],
    x= core_charge_trans.index,
    textposition="outside",
    text=["+20M", "+25M", "+40M", "Total"],
    y=core_charge_trans['Amount'],
    connector={"line": {"color": "rgb(63, 63, 63)"}}
))

fig.update_layout(
    # title="Profit and loss statement 2018",
    showlegend=True
)

fig.update_xaxes(title_text="Categories")
fig.update_yaxes(title_text="Amount")

st.plotly_chart(fig)




# Monthly Sales Growth Stacked Bar Chart
st.subheader("Monthly Sales Growth")
fig = px.bar(grouped, x=grouped.index, y=['COGS', 'gross_profit', 'sales'],
                labels={'x': 'Month', 'y': 'Amount'},
                # title='Monthly Stacked Bar Chart',
                barmode='relative')

st.plotly_chart(fig)





