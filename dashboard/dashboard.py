import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Fungsi untuk memuat data dari path relatif
def load_data():
    try:
        day_df = pd.read_csv(r'D:\DBS\submission\data\day.csv')
        hour_df = pd.read_csv(r'D:\DBS\submission\data\hour.csv')
        return day_df, hour_df
    except FileNotFoundError:
        st.error("File dataset tidak ditemukan. Pastikan file 'day.csv' dan 'hour.csv' ada di folder 'data'.")
        return None, None

# Fungsi untuk membuat visualisasi tren peminjaman berdasarkan hari
def plot_daily_trends(day_df):
    fig, ax = plt.subplots(figsize=(10, 6))
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_df['weekday'] = pd.Categorical(day_df['weekday'], categories=day_order, ordered=True)
    daily_rental = day_df.groupby('weekday')['cnt'].mean().reindex(day_order)
    
    sns.barplot(x=daily_rental.index, y=daily_rental.values, ax=ax)
    ax.set_title('Rata-rata Peminjaman Sepeda Berdasarkan Hari', fontsize=15)
    ax.set_xlabel('Hari', fontsize=12)
    ax.set_ylabel('Jumlah Peminjaman Rata-rata', fontsize=12)
    ax.tick_params(axis='x', rotation=45)
    return fig

# Fungsi untuk membuat visualisasi distribusi peminjaman berdasarkan jam
def plot_hourly_distribution(hour_df):
    fig, ax = plt.subplots(figsize=(10, 6))
    hourly_rental = hour_df.groupby('hr')['cnt'].mean()
    
    sns.barplot(x=hourly_rental.index, y=hourly_rental.values, ax=ax)
    ax.set_title('Rata-rata Peminjaman Sepeda Berdasarkan Jam', fontsize=15)
    ax.set_xlabel('Jam', fontsize=12)
    ax.set_ylabel('Jumlah Peminjaman Rata-rata', fontsize=12)
    ax.set_xticks(range(0, 24, 2))
    return fig

# Fungsi untuk membuat visualisasi korelasi suhu dan peminjaman
def plot_temperature_correlation(hour_df):
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Konversi suhu ke skala Celsius
    hour_df['temp_celsius'] = hour_df['temp'] * 41
    
    sns.scatterplot(x='temp_celsius', y='cnt', data=hour_df, alpha=0.5, ax=ax)
    ax.set_title('Korelasi antara Suhu dan Jumlah Peminjaman Sepeda', fontsize=15)
    ax.set_xlabel('Suhu (°C)', fontsize=12)
    ax.set_ylabel('Jumlah Peminjaman', fontsize=12)
    
    # Tambahkan garis regresi
    sns.regplot(x='temp_celsius', y='cnt', data=hour_df, scatter=False, color='red', ax=ax)
    return fig

# Fitur interaktif: Filter peminjaman berdasarkan kondisi cuaca
def interactive_weather_filter(hour_df):
    st.sidebar.header('Filter Peminjaman Berdasarkan Kondisi Cuaca')
    
    # Widget untuk memilih kondisi cuaca
    weather_options = {
        1: 'Cerah',
        2: 'Berawan',
        3: 'Hujan Ringan/Salju Ringan',
        4: 'Hujan Lebat/Salju Lebat'
    }
    selected_weather = st.sidebar.multiselect(
        'Pilih Kondisi Cuaca:',
        options=list(weather_options.keys()),
        format_func=lambda x: weather_options[x]
    )
    
    # Filter data berdasarkan kondisi cuaca yang dipilih
    if selected_weather:
        filtered_df = hour_df[hour_df['weathersit'].isin(selected_weather)]
        st.write(f"Jumlah peminjaman untuk kondisi cuaca terpilih:")
        st.write(filtered_df['cnt'].describe())
        
        # Visualisasi peminjaman untuk kondisi cuaca terpilih
        fig, ax = plt.subplots(figsize=(10, 6))
        # Menggunakan filtered_df untuk boxplot
        sns.boxplot(x='weathersit', y='cnt', data=filtered_df, ax=ax)
        ax.set_title('Distribusi Peminjaman Berdasarkan Kondisi Cuaca', fontsize=15)
        ax.set_xlabel('Kondisi Cuaca', fontsize=12)
        ax.set_ylabel('Jumlah Peminjaman', fontsize=12)
        
        # Mendapatkan unique values dari weathersit yang ada di data yang difilter
        weather_values = sorted(filtered_df['weathersit'].unique())
        weather_labels = [weather_options[weather] for weather in weather_values]
        
        # Set label berdasarkan weather values yang muncul di plot
        ax.set_xticklabels(weather_labels)
        st.pyplot(fig)

def main():
    st.set_page_config(page_title='Dashboard Analisis Bike Sharing', layout='wide')
    
    # Judul Utama
    st.title('Dashboard Analisis Data Bike Sharing')
    
    # Muat data
    day_df, hour_df = load_data()
    
    if day_df is not None and hour_df is not None:
        # Tab untuk visualisasi
        tab1, tab2, tab3, tab4 = st.tabs([
            'Tren Peminjaman Harian', 
            'Distribusi Jam Peminjaman', 
            'Korelasi Suhu dan Peminjaman',
            'Filter Kondisi Cuaca'
        ])
        
        with tab1:
            st.header('Tren Peminjaman Berdasarkan Hari')
            st.pyplot(plot_daily_trends(day_df))
        
        with tab2:
            st.header('Distribusi Peminjaman Berdasarkan Jam')
            st.pyplot(plot_hourly_distribution(hour_df))
        
        with tab3:
            st.header('Korelasi Suhu dan Jumlah Peminjaman')
            st.pyplot(plot_temperature_correlation(hour_df))
        
        with tab4:
            st.header('Eksplorasi Peminjaman Berdasarkan Kondisi Cuaca')
            interactive_weather_filter(hour_df)
        
        # Kesimpulan
        st.header('Kesimpulan')
        st.markdown("""
        **Temuan Utama Analisis Bike Sharing:**
        
        1. **Pola Harian:** 
           - Peminjaman sepeda tertinggi pada hari kerja
           - Puncak peminjaman di hari Selasa dan Rabu
        
        2. **Distribusi Jam:**
           - Dua puncak peminjaman pada pagi (07-09) dan sore (17-19)
           - Pola terkait aktivitas komuter
        
        3. **Pengaruh Suhu:**
           - Korelasi positif antara suhu dan jumlah peminjaman
           - Cuaca hangat mendorong peningkatan penggunaan sepeda
        
        4. **Kondisi Cuaca:**
           - Variasi peminjaman signifikan antar kondisi cuaca
           - Cuaca cerah cenderung meningkatkan jumlah peminjaman
        """)

if __name__ == '__main__':
    main()