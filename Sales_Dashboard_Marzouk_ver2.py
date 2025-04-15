import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Sales Dashboard", layout="wide")

# Upload CSV file
st.sidebar.header("Upload Your Sales Data")
uploaded_file = st.sidebar.file_uploader("Choose a file", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)


    df = pd.read_excel(r"Sales_for_eda.xlsx")
    # Preprocess
    df['date_only'] = pd.to_datetime(df['date_only'])
    df['time_only'] = pd.to_datetime(df['time_only'], format='%H:%M:%S').dt.time
    df['Hour'] = pd.to_datetime(df['time_only'].astype(str)).dt.hour
    df['Day'] = df['date_only'].dt.day_name()
    
        # Sidebar filters
    st.sidebar.header("🔍 Filter Options")
    selected_cities = st.sidebar.multiselect("Select Cities", options=df['city'].unique(), default=df['city'].unique())

    # Apply filters to the data
    if selected_cities:
        df = df[df['city'].isin(selected_cities)]


    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Overall Trends",
        "🛍️ Product Performance",
        "🏪 Branch & City Insights",
        "⏰ Time-Based Analysis",
        "📊 Revenue Distribution"
    ])

    with tab1:
        st.subheader("Total Revenue and Orders Over Time")
        daily_summary = df.groupby('date_only').agg({
            'order_id': pd.Series.nunique,
            'total': 'sum'
        }).reset_index().rename(columns={'order_id': 'Unique Orders'})

        total_revenue = daily_summary['total'].sum()
        total_orders = daily_summary['Unique Orders'].sum()

        kpi1, kpi2 = st.columns(2)
        kpi1.metric("Total Revenue", f"${total_revenue:,.2f}")
        kpi2.metric("Total Unique Orders", f"{total_orders:,}")

        fig1 = px.line(daily_summary, x='date_only', y='total', title='Daily Revenue')
        st.plotly_chart(fig1, use_container_width=True)
        st.dataframe(pd.DataFrame({
            "Insight": ["Revenue trends help detect sales peaks and slowdowns."],
            "Action": ["Increase marketing around peak days and investigate low-performance periods."]
        }))

        fig2 = px.line(daily_summary, x='date_only', y='Unique Orders', title='Daily Orders')
        st.plotly_chart(fig2, use_container_width=True)
        st.dataframe(pd.DataFrame({
            "Insight": ["Unique orders trend indicates customer traffic volume."],
            "Action": ["Schedule staff accordingly and plan inventory for busy periods."]
        }))

        daily_summary['Revenue per Order'] = daily_summary['total'] / daily_summary['Unique Orders']
        low_yield_days = daily_summary[daily_summary['Revenue per Order'] < daily_summary['Revenue per Order'].median()]
        if not low_yield_days.empty:
            st.warning("⚠️ Several days had high orders but low revenue per order. Consider optimizing small order costs.")

        csv = daily_summary.to_csv(index=False).encode('utf-8')
        st.download_button("Download Daily Summary CSV", csv, "daily_summary.csv", "text/csv")

    with tab2:
        st.subheader("Top Performing Products")
        product_perf = df.groupby('product name')['total'].sum().reset_index().sort_values(by='total', ascending=False)
        product_quantity = df.groupby('product name')['quantity'].sum().reset_index()
        product_rev_qty = pd.merge(product_perf, product_quantity, on='product name')

        top_total = product_perf.head(10)['total'].sum()
        bottom_total = product_perf.tail(10)['total'].sum()

        kpi3, kpi4 = st.columns(2)
        kpi3.metric("Total Products", f"{len(product_perf):,}")
        kpi4.metric("Avg Revenue per Product", f"${product_perf['total'].mean():,.2f}")

        fig3 = px.bar(product_perf.head(10), x='product name', y='total', title='Top 10 Products by Revenue')
        st.plotly_chart(fig3, use_container_width=True)
        st.dataframe(pd.DataFrame({
            "Insight": [f"Top 10 products generated ${top_total:,.2f}."],
            "Action": ["Promote these with bundles, and ensure they’re always in stock."]
        }))

        fig4 = px.bar(product_perf.tail(10), x='product name', y='total', title='Bottom 10 Products by Revenue')
        st.plotly_chart(fig4, use_container_width=True)
        st.dataframe(pd.DataFrame({
            "Insight": [f"Bottom 10 products earned only ${bottom_total:,.2f}."],
            "Action": ["Consider replacing or discounting underperforming items."]
        }))

        fig_qty = px.scatter(product_rev_qty, x='quantity', y='total', hover_name='product name', title='Revenue vs Quantity Sold')
        st.plotly_chart(fig_qty, use_container_width=True)
        st.dataframe(pd.DataFrame({
            "Insight": ["Correlation between product popularity and profitability."],
            "Action": ["Consider adjusting pricing or promotion strategies."]
        }))

    with tab3:
        st.subheader("Revenue by Branch and City")
        branch_rev = df.groupby(['city', 'branch'])['total'].sum().reset_index()
        city_rev = df.groupby('city')['total'].sum().reset_index()

        top_city = city_rev.sort_values(by='total', ascending=False).iloc[0]

        kpi5, kpi6 = st.columns(2)
        kpi5.metric("Total Branches", f"{branch_rev['branch'].nunique()}")
        kpi6.metric("Total Cities", f"{city_rev['city'].nunique()}")

        fig5 = px.bar(branch_rev, x='branch', y='total', color='city', title='Branch Revenue by City')
        st.plotly_chart(fig5, use_container_width=True)
        st.dataframe(pd.DataFrame({
            "Insight": ["Revenue differs across branches and cities."],
            "Action": ["Focus investment and stock based on high-performing locations."]
        }))

        fig6 = px.pie(city_rev, values='total', names='city', title='Revenue Share by City')
        st.plotly_chart(fig6, use_container_width=True)
        st.dataframe(pd.DataFrame({
            "Insight": [f"{top_city['city']} contributes the highest with ${top_city['total']:,.2f}."],
            "Action": [f"Expand marketing in {top_city['city']} or evaluate potential in other cities."]
        }))

        city_time = df.groupby(['date_only', 'city'])['total'].sum().reset_index()
        fig_city_time = px.line(city_time, x='date_only', y='total', color='city', title='City-wise Revenue Over Time')
        st.plotly_chart(fig_city_time, use_container_width=True)

    with tab4:
        st.subheader("Hourly Sales Trend")
        hourly = df.groupby('Hour')['total'].sum().reset_index()
        peak_hour = hourly.loc[hourly['total'].idxmax()]

        heatmap_data = df.groupby(['Hour', 'city'])['total'].sum().reset_index()

        kpi7, kpi8 = st.columns(2)
        kpi7.metric("Peak Hour", f"{peak_hour['Hour']}h")
        kpi8.metric("Peak Hour Revenue", f"${peak_hour['total']:,.2f}")

        fig7 = px.bar(hourly, x='Hour', y='total', title='Revenue by Hour of Day')
        st.plotly_chart(fig7, use_container_width=True)
        st.dataframe(pd.DataFrame({
            "Insight": ["Shows peak and off-peak hours."],
            "Action": ["Adjust staff shifts and promotions to match demand hours."]
        }))

        fig8 = px.density_heatmap(heatmap_data, x='Hour', y='city', z='total', title='City-wise Hourly Heatmap', nbinsx=24, color_continuous_scale='Viridis')
        st.plotly_chart(fig8, use_container_width=True)
        st.dataframe(pd.DataFrame({
            "Insight": ["Regional hourly performance variations."],
            "Action": ["Schedule deliveries and operations based on active city times."]
        }))

        day_hour_heatmap = df.groupby(['Day', 'Hour'])['total'].sum().reset_index()
        fig_day_hour = px.density_heatmap(day_hour_heatmap, x='Hour', y='Day', z='total', title='Revenue by Day & Hour', color_continuous_scale='Plasma')
        st.plotly_chart(fig_day_hour, use_container_width=True)

    with tab5:
        st.subheader("Revenue by Product Category")
        cat_rev = df.groupby('product_category')['total'].sum().reset_index()
        top_cat = cat_rev.sort_values(by='total', ascending=False).iloc[0]

        kpi9, kpi10 = st.columns(2)
        kpi9.metric("# of Categories", f"{cat_rev.shape[0]}")
        kpi10.metric("Top Category Revenue", f"${top_cat['total']:,.2f}")

        fig9 = px.pie(cat_rev, names='product_category', values='total', title='Revenue by Category')
        st.plotly_chart(fig9, use_container_width=True)
        st.dataframe(pd.DataFrame({
            "Insight": [f"{top_cat['product_category']} leads with ${top_cat['total']:,.2f}."],
            "Action": ["Develop targeted strategies like upselling and bundling."]
        }))

        st.subheader("Cumulative Product Revenue Distribution")
        cumulative = product_perf.copy()
        cumulative['Cumulative %'] = cumulative['total'].cumsum() / cumulative['total'].sum() * 100
        fig10 = px.line(cumulative, x='product name', y='Cumulative %', title='Cumulative Revenue by Product')
        st.plotly_chart(fig10, use_container_width=True)
        st.dataframe(pd.DataFrame({
            "Insight": ["80/20 rule in action — few products generate most revenue."],
            "Action": ["Focus campaigns on top 20% revenue-contributing products."]
        }))

else:
    st.info("👆 Please upload your sales dataset to begin analysis.")
