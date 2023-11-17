import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

flag = 0
# tiền xử lý , tạo cột City , State
# df['City']=df['Purchase Address'].apply(lambda x: x.split(', ')[1])
# df['State']=df['Purchase Address'].apply(lambda x: x.split(', ')[2])
# df.to_csv('new_sale_datas')

# tiền xử lý tạo cột month
# df["Order Date"] = pd.to_datetime(df["Order Date"])
# df['month']=df['Order Date'].dt.month
st.set_page_config(page_title="Superstore", page_icon=":bar_chart", layout="wide")
st.title(":bar_chart: Sales Dashboard")
st.markdown(
    "<style>div.block-container{padding-top:1rem}</style>", unsafe_allow_html=True
)

# Upload file
fl = st.file_uploader(
    ":file_folder: Upload a file", type=(["csv", "txt", "xlsx", "xls"])
)
if fl is not None:
    filename = fl.name
    #st.write(fl)
    df = pd.read_csv(fl)
   
else:
    st.warning("No data available based on the current filter settings!")
    st.stop() # This will halt the app from further execution.
   # os.chdir(r"D:\Python\DOAN")
   # df = pd.read_csv("/new_sale_datas_2.csv")


# ---- MAINPAGE ----
#st.title(":bar_chart: Sales Dashboard :wide")

st.markdown("##")

# Getting the min and max date
col1, col2 = st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"])
startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()
# tạo khung chọn ngày options
with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()




# tạo khung chọn bộ lọc
st.sidebar.header("Product group by:")
with st.sidebar.expander("Chọn bộ lọc:"):
    
    # Choose your filter
    products = st.sidebar.multiselect("Product:", df["Product"].unique())
    if not products:
        df2=df.copy()
    else:
        df2=df[df['Product'].isin(products)]
    categories = st.sidebar.multiselect("Categories:", df["catégorie"].unique())
    if not categories:
        df3=df2.copy()
    else:
        df3=df2[df['catégorie'].isin(categories)]

# tạo khung State và City
st.sidebar.header("Area by:")
with st.sidebar.expander("Chọn khu vực: "):
    cities=st.sidebar.multiselect("Cities: ",df['City'].unique())
    if not cities:
        df4=df3.copy()
    else:
        df4=df3[df3['City'].isin(cities)]
    states=st.sidebar.multiselect("State: ",df['State'].unique())
    if not states:
        df5=df4.copy()
    else:
        df5=df4[df4['State'].isin(states)]

# tạo khung chọn giá 
st.sidebar.header("Price:")
with st.sidebar.expander("Choose price range",True):
    # Choose your price
    header = ["Price Each", "Cost price", "turnover", "margin"]
    value_ranges = {}

    for head in header:
        min_values = int(df[head].min())
        max_values = int(df[head].max())
        value_ranges[head] = {"min_values": min_values, "max_values": max_values}

    selected_range = {}
    for head in value_ranges:
        price_range = st.slider(
            f"Select {head} range:",
            min_value=value_ranges[head]["min_values"],
            max_value=value_ranges[head]["max_values"],
            step=10,
            value=(value_ranges[head]["min_values"], value_ranges[head]["max_values"]),
        )
        selected_range[head] = price_range

filtered_df = df.copy()  # Tạo bản sao của df

# Lọc dữ liệu theo ngày
filtered_df = filtered_df[
    (filtered_df["Order Date"] >= date1) & (filtered_df["Order Date"] <= date2)
]

# Lọc dữ liệu theo Product nếu có lựa chọn
if products:
    filtered_df = filtered_df[filtered_df["Product"].isin(products)]

# Lọc dữ liệu theo Categories nếu có lựa chọn
if categories:
    filtered_df = filtered_df[filtered_df["catégorie"].isin(categories)]

# Lọc dữ liệu theo City nếu có lựa chọn
if cities:
    filtered_df = filtered_df[filtered_df["City"].isin(cities)]

# Lọc dữ liệu theo State nếu có lựa chọn
if states:
    filtered_df = filtered_df[filtered_df["State"].isin(states)]
# Lọc dữ liệu theo giá
filtered_df = filtered_df[
    (filtered_df["Price Each"] >= selected_range["Price Each"][0])
    & (filtered_df["Price Each"] <= selected_range["Price Each"][1])
    & (filtered_df["Cost price"] >= selected_range["Cost price"][0])
    & (filtered_df["Cost price"] <= selected_range["Cost price"][1])
    & (filtered_df["turnover"] >= selected_range["turnover"][0])
    & (filtered_df["turnover"] <= selected_range["turnover"][1])
    & (filtered_df["margin"] >= selected_range["margin"][0])
    & (filtered_df["margin"] <= selected_range["margin"][1])
]

# Calculate the growth rates
filtered_df["growth_rate_order"] = (filtered_df["Order ID"] - filtered_df["Order ID"].shift(1)) / filtered_df["Order ID"].shift(1) * 100
filtered_df["growth_rate_quantity"] = (filtered_df["Quantity Ordered"] - filtered_df["Quantity Ordered"].shift(1)) / filtered_df["Quantity Ordered"].shift(1) * 100
filtered_df["growth_rate_turnover"] = (filtered_df["turnover"] - filtered_df["turnover"].shift(1)) / filtered_df["turnover"].shift(1) * 100
filtered_df["growth_rate_margin"] = (filtered_df["margin"] - filtered_df["margin"].shift(1)) / filtered_df["margin"].shift(1) * 100

# Round the growth rates to two decimal places
filtered_df["growth_rate_order"] = filtered_df["growth_rate_order"].round(6)
filtered_df["growth_rate_quantity"] = filtered_df["growth_rate_quantity"].round(6)
filtered_df["growth_rate_turnover"] = filtered_df["growth_rate_turnover"].round(2)
filtered_df["growth_rate_margin"] = filtered_df["growth_rate_margin"].round(2)

#style css cho metric
st.markdown("""
<style>
div[data-testid="metric-container"] {
   background-color: rgba(240, 240, 240, 0.1);
   border: 1px solid rgba(255, 28, 28, 0.1);
   padding: 5% 5% 5% 10%;
   border-radius: 20px;
   color: rgb(30, 103, 119);
   overflow-wrap: break-word;
   
}

/* breakline for metric text         */
div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div {
   overflow-wrap: break-word;
   white-space: break-spaces;
   color: red;
   
}
</style>
"""
, unsafe_allow_html=True)


st.subheader('Growth rate for last month')
# Display the metrics
metrics = ["growth_rate_order", "growth_rate_quantity", "growth_rate_turnover", "growth_rate_margin"]
metrics1 = ["Order", "Quantity", "Turnover", "Margin"]
columns = st.columns([0.25, 0.25, 0.25, 0.25])
for i,metric, column in zip(metrics1,metrics, columns):
    column.metric(i, filtered_df[metric].iloc[-1], delta=(filtered_df[metric].iloc[-1] - filtered_df[metric].iloc[-2]))


#st.markdown("""---""")

# Hiển thị dữ liệu sản phẩm đã lọc
filtered_df_copy=filtered_df.copy()
#st.write("Dữ liệu sản phẩm đã lọc:")
#st.write(filtered_df)

st.markdown("""---""")



# KPI Metrics
st.subheader('KPI Metrics')
total_sales = int(filtered_df["turnover"].sum())
average_sale_by_transaction = round(filtered_df["turnover"].mean(), 2)
total_order = int(filtered_df["Quantity Ordered"].sum())

# Display the KPI metrics
metrics = ["Total Sales", "Total order", "Average Sales per Order"]
metrics1 = [f"$ {total_sales:,}", f"{total_order:,}",f"$ {average_sale_by_transaction:,}"]
columns = st.columns(3)
for i,metric, column in zip(metrics,metrics1, columns):
    column.metric(i, metric, delta=None)

#top 10
col1, col2, col3 = st.columns(3)

with col1:
    st.caption("Top 10 Purchase Address")
    top_customers = filtered_df.groupby('Purchase Address')['turnover'].sum().reset_index().head(10)
    st.write(top_customers)
with col3:
    st.caption("Total Sales by Product Catégorie")
    total_sales_by_product_cat = filtered_df.groupby('catégorie')['turnover'].sum().reset_index()
    st.write(total_sales_by_product_cat)
with col2:
    st.caption("Top 10 Products by Sales")
    top_products = filtered_df.groupby(['Product'])['turnover'].sum().reset_index().head(10)
    st.write(top_products)


# SALES BY PRODUCT  [BAR CHART]
sales_by_product_line = filtered_df.groupby(by=["Product"])[["turnover"]].sum().sort_values(by="turnover")
fig_product_sales = px.bar(
    sales_by_product_line,
    x="turnover",
    y=sales_by_product_line.index,
    orientation="h",
    title="<b>Tunrover by Product</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_by_product_line),
    template="plotly_white",
)
fig_product_sales.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)

# SALES BY City [BAR CHART]
sales_by_hour = filtered_df.groupby(by=["City"])[["Quantity Ordered"]].sum().sort_values(by="Quantity Ordered")
fig_hourly_sales = px.bar(
    sales_by_hour,
    x=sales_by_hour.index,
    y="Quantity Ordered",
    title="<b>Orderd by City</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_by_hour),
    template="plotly_white"
)
fig_hourly_sales.update_layout(
    xaxis=dict(tickmode="linear"),
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=(dict(showgrid=False)),
)


left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_hourly_sales, use_container_width=True)
right_column.plotly_chart(fig_product_sales, use_container_width=True)

#product by ordered

month_product = filtered_df.groupby([ 'Product']).agg({'Quantity Ordered': sum}).reset_index()
fig2=px.bar(month_product,x='Product',y='Quantity Ordered',labels={'Quantity Ordered':'Ordered'},color='Product',title="<b>Product by ordered</b>")
st.plotly_chart(fig2,use_container_width=True)

#Orderd's Product sales  by month

month_product = filtered_df.groupby([ 'month','Product']).agg({'Quantity Ordered': sum}).reset_index()
fig3=px.line(month_product,x='month',y='Quantity Ordered',labels={'month':'Month','Quantity Ordered':'Ordered'},color='Product',title="<b>Orderd's Product sales  by month</b>")
st.plotly_chart(fig3,use_container_width=True)

st.markdown("""---""")

#vẽ 2 biểu đồ city và turnover
turnover_data=filtered_df.groupby('City')['turnover'].sum().sort_values(ascending=False)
turnover_data = pd.DataFrame(turnover_data)
turnover_data['turnover'] = turnover_data['turnover'].astype(float)
top_4_City_df= turnover_data.head(4)
col1_1,col2_2 =st.columns((2))
with col1_1:    
    st.subheader('Top 4 biggest total turnover City')
    fig=px.bar(top_4_City_df,x=top_4_City_df.index,y='turnover',text=['${:,.2f}'.format(x) for x in top_4_City_df['turnover']],template='seaborn')
    st.plotly_chart(fig,use_container_width=True,height=200)
    with st.expander("Top_4_city"):
        st.write(top_4_City_df)
        csv_data=top_4_City_df.to_csv(index=False).encode('utf-8')
        st.download_button(label='Click here to download',data=csv_data,file_name='top_4_City_df.csv')

with col2_2:
    st.subheader('Turnover for each city')
    fig_donut =px.pie(filtered_df,names='City', values='turnover',hole=0.4)
    fig_donut.update_traces(textinfo='percent+label',pull=[0.1,0.1,0.1])
    st.plotly_chart(fig_donut,use_container_width=True)
    with st.expander("Turnover_data"):
        st.write(turnover_data)
        csv_data=turnover_data.to_csv(index=False).encode('utf-8')
        st.download_button(label='Click here to download',data=csv_data,file_name='Turnover_data.csv')
# Vẽ biểu đồ timeseries
st.markdown("""---""")
st.markdown("##")

st.subheader('Time Series Analysis')
month_datas= filtered_df.groupby('month')['turnover'].sum().reset_index()
fig2=px.line(month_datas,x='month',y='turnover',labels={'Turnover':'Amount'},height=500,width=1000,template='gridon')
st.plotly_chart(fig2,use_container_width=True)
with st.expander('View Data of TimeSeries:'):
    st.write(month_datas)
    csv_data=month_datas.to_csv(index=False).encode('utf-8')
    st.download_button(label='Click here to download',data=csv_data,file_name='Month_data.csv')

# Vẽ biểu đồ Treemap dựa theo city, product, categorie

st.subheader('Hierarchical view of Turnover using Tree Map')
fig3 = px.treemap(filtered_df,path=['Product','catégorie','month'],values='turnover',hover_data=['turnover'],color='Product')
st.plotly_chart(fig3,use_container_width=True)

# vẽ biểu đồ tròn theo product và categories
col3,col4=st.columns((2))
with col3:
    st.subheader('Margin for each Catégorie')
    data_product =filtered_df.groupby('catégorie')['margin'].sum()
    fig4=px.pie(filtered_df,names='catégorie',values='margin',hole=0.4)
    fig4.update_traces(textinfo='percent+label',pull=[0.1,0.1,0.1])
    st.plotly_chart(fig4,use_container_width=True)
with col4:
    st.subheader('Turnover for each Catégorie')
    data_product =filtered_df.groupby('catégorie')['turnover'].sum()
    fig4=px.pie(filtered_df,names='catégorie',values='turnover',hole=0.4)
    fig4.update_traces(textinfo='percent+label',pull=[0.1,0.1,0.1])
    st.plotly_chart(fig4,use_container_width=True)
import plotly.figure_factory as ff
st.header(':point_right: Monthly total over turn')
with st.expander('Summary Table'):
    df_sample=df[0:5][['Product','Order Date','catégorie','City','State','turnover','Quantity Ordered']]
    fig5 = ff.create_table(df_sample,colorscale='Cividis')
    st.plotly_chart(fig5,use_container_width=True)

    st.markdown('Monthly total over turn')
    sub_product_year=pd.pivot_table(data=filtered_df,values='turnover',index=['Product'],columns='month')
    st.write(sub_product_year.style.background_gradient(cmap=('Blues')))

st.subheader('Relationship between Margin and Turnover')
    # create a scatter plot
fig = px.scatter(df, x='turnover', y='margin', title='Mối quan hệ giữa X và Y',size='Quantity Ordered')
st.plotly_chart(fig)


# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
st.write(filtered_df)