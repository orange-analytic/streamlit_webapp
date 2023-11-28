import streamlit as st
import pandas as pd
import math
import locale
import plotly.express as px

# Set the locale to the user's default locale for number formatting
locale.setlocale(locale.LC_ALL, '')

# Function to format numbers with commas after rounding
def format_with_commas(number):
    rounded_number = round(number)  # Round the number to an integer
    formatted_number = locale.format("%d", rounded_number, grouping=True)  # Format with commas
    return formatted_number

# Load your data (replace 'current_data_full.csv' with your actual data source)
df_customer = pd.read_csv('current_data_full.csv', low_memory=False)

df_customer['year_month'] = pd.to_datetime(df_customer['year_month'])

# Calculate the current year and last year
current_year = pd.Timestamp.now().year
last_year = current_year - 1

# Calculate sales and gross profit for the current and last year
current_year_sales = df_customer[df_customer['year_month'].dt.year == current_year]['sales'].sum()
last_year_sales = df_customer[df_customer['year_month'].dt.year == last_year]['sales'].sum()

current_year_gp = df_customer[df_customer['year_month'].dt.year == current_year]['gross_profit'].sum()
last_year_gp = df_customer[df_customer['year_month'].dt.year == last_year]['gross_profit'].sum()

# Calculate average monthly sales
customer_monthly_avg = df_customer.groupby('year_month')['sales'].sum().mean()
formatted_average = format_with_commas(math.ceil(customer_monthly_avg))

# Calculate average items ordered
monthly_items_ordered = df_customer.groupby('year_month')['Item Number'].count().mean()
formatted_average_item_order = format_with_commas(math.ceil(monthly_items_ordered))

# Calculate last and current years
current_year = df_customer['year_month'].dt.year.max()
last_year = current_year - 1
# Layout
st.title("Customer Analysis")
st.subheader("Dashboard Overview")

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

with open('customer_style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
# In the first column
with col1:
    st.markdown("### Current Customer", unsafe_allow_html=True)
    st.write(f"{len(df_customer['Customer Number'].unique())}")

with col2:
    st.markdown("### Sales", unsafe_allow_html=True)
    st.write(f"CY YTD : ${format_with_commas(math.ceil(current_year_sales))}")
    st.write(f"PY YTD : ${format_with_commas(math.ceil(last_year_sales))}")

# In the second column
with col3:
    st.markdown("### Avg Monthly Sales", unsafe_allow_html=True)
    st.write("$" + formatted_average)
with col4:
    st.markdown("### Avg Items Ordered", unsafe_allow_html=True)
    st.write("" + formatted_average_item_order)

st.title("Select Analysis")
selected_analysis = st.selectbox("Choose Analysis", ["Monthly Sales Trend", "Monthly Unique Item Count", "Top 5 Companies by Revenue", "Customer 2 Years Value"])

# Filter data for the last two years
df_2year_data = df_customer[df_customer['year_month'] >= f'{current_year - 2}-01']

if selected_analysis == "Monthly Sales Trend":
    # st.write("Monthly Sales Trend")
    monthly_sales = df_2year_data.groupby('year_month')['sales'].sum()
    fig = px.bar(
        x=monthly_sales.index,
        y=monthly_sales.values,
        labels={"x": "Month", "y": "Total Sales"},
        title="Monthly Sales Trend",
    )
    st.plotly_chart(fig)

elif selected_analysis == "Monthly Unique Item Count":
    # st.write("Monthly Unique Item Count")
    monthly_counts = df_2year_data.groupby('year_month')['Item Number'].nunique()
    fig = px.line(
        x=monthly_counts.index,
        y=monthly_counts.values,
        labels={"x": "Month", "y": "Unique Item Count"},
        title="Monthly Unique Item Count",
    )
    st.plotly_chart(fig)

elif selected_analysis == "Top 5 Companies by Revenue":
    # st.write("Top 5 Companies by Revenue")
    company_spending = df_2year_data.groupby('Customer Number')['Net Price'].sum()
    top_5_companies = company_spending.sort_values(ascending=False).head(5)
    fig = px.bar(
        x=top_5_companies.index,
        y=top_5_companies.values,
        labels={"x": "Customer Number", "y": "Net Price"},
        title="Top 5 Companies by Revenue",
    )
    st.plotly_chart(fig)

elif selected_analysis == "Customer 2 Years Value":
    # st.write("Customer 2 Years Value")
    monthly_sales = df_customer.groupby(['Customer Number'])['sales'].sum().reset_index()
    customer_lifetime_value = monthly_sales.query('sales > 0')
    fig = px.line(
        customer_lifetime_value,
        x='Customer Number',
        y='sales',
        markers=True,
        labels={"Customer Number": "Customer ID", "sales": "2 Years Value"},
        title="Customer 2 Years Value",
    )
    st.plotly_chart(fig)
