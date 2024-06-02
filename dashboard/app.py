import pandas as pd
import plotly.express as px
import streamlit as st
import seaborn as sns

st.set_page_config(page_title="Bike Sharing", page_icon=":bar_chart:", layout="wide")
sns.set(style='dark')


df = pd.read_csv("dashboard/hour_modified.csv")



# ---- SIDEBAR ----
st.sidebar.header("Please Filter Here:")
season = st.sidebar.multiselect(
    "Select the Season:",
    options=df["season"].unique(),
    default=df["season"].unique()
)

df_selection = df.query(
    "season == @season"
)

# Check if the dataframe is empty:
if df_selection.empty:
    st.warning("No data available based on the current filter settings!")
    st.stop() # This will halt the app from further execution.



#------- MAIN PAGE ----------
st.header('Bicycle Rental Dashboard :sparkles:')


#TANGGAL
col1, col2 = st.columns((2))
df["dteday"] = pd.to_datetime(df["dteday"])

# Getting the min and max date 
startDate = pd.to_datetime(df["dteday"]).min()
endDate = pd.to_datetime(df["dteday"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["dteday"] >= date1) & (df["dteday"] <= date2)].copy()


#------ TOP -------
total_sales = int(df_selection["cnt"].sum())
hourly_rentals = df.groupby('hr')['cnt'].sum()
# Temukan jam paling ramai (modus)
busiest_hour = hourly_rentals.idxmax()


left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader("Total Units Rented:")
    st.subheader(f"{total_sales:,}")
with right_column:
    st.subheader("busiest hours for renters:")
    st.subheader(f"{busiest_hour}.00")

st.markdown("""---""")

#--------- chart ---------

# Menghitung total casual dan registered
total_casual = df["casual"].sum()
total_registered = df["registered"].sum()

# Membuat data untuk pie chart
data_pie = pd.DataFrame({
    "Category": ["Casual", "Registered"],
    "Total": [total_casual, total_registered]
})

# Membuat pie chart menggunakan Plotly Express
fig_pie = px.pie(
    data_pie,
    values='Total',
    names='Category',
    title='Comparison of Casual and Registered',
    color_discrete_sequence=[ "#800080", "#A9A9A9"],  # Menggunakan warna yang berbeda untuk setiap kategori
    template="plotly_white"
)

# SALES BY HOUR [BAR CHART]
sales_by_hour = df_selection.groupby(by=["weekday"])[["cnt"]].sum()

max_value = sales_by_hour["cnt"].max()
min_value = sales_by_hour["cnt"].min()
fig_hourly_sales = px.bar(
    sales_by_hour,
    x=sales_by_hour.index,
    y="cnt",
    title="<b>Unit Rented per day</b>",
    color="cnt",  # Menggunakan nilai penjualan sebagai skala warna
    color_continuous_scale=px.colors.sequential.Blues,  # Menggunakan skala warna biru
    range_color=[min_value, max_value],  # Menyesuaikan rentang warna dengan nilai tertinggi dan terendah
    template="plotly_white",
)
fig_hourly_sales.update_layout(
    xaxis=dict(
        tickmode="array",  # Menggunakan mode array untuk menentukan label sumbu x
        tickvals=list(range(7)),  # Label hari dari 0 hingga 6 (Senin hingga Minggu)
        ticktext=["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"],  # Menetapkan label teks untuk setiap nilai tick
    ),
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=(dict(showgrid=False)),
)


left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_hourly_sales, use_container_width=True)
right_column.plotly_chart(fig_pie, use_container_width=True)


# line chart penjualan tiap bulan
df['dteday'] = pd.to_datetime(df['dteday'])
df['month'] = df['dteday'].dt.month
monthly_rentals = df.groupby('month')['cnt'].sum().reset_index()
fig = px.line(monthly_rentals, x='month', y='cnt', title='Jumlah Tersewa Tiap Bulannya')

# Menampilkan line chart
st.plotly_chart(fig)