import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime

# Fungsi untuk memuat data dari file
def load_data():
    try:
        # Mencoba berbagai lokasi file
        try:
            day_df = pd.read_csv('day.csv')
            hour_df = pd.read_csv('hour.csv')
        except:
            day_df = pd.read_csv('./data/day.csv')
            hour_df = pd.read_csv('./data/hour.csv')
            
        # Preprocessing data
        # Konversi tanggal
        day_df['dteday'] = pd.to_datetime(day_df['dteday'])
        hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
        
        # Menambahkan nama hari
        day_names = {0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday'}
        day_df['weekday_name'] = day_df['weekday'].map(day_names)
        
        # Konversi suhu, kelembaban, dan kecepatan angin ke nilai sebenarnya
        day_df['temp_celsius'] = day_df['temp'] * 41
        day_df['hum_percent'] = day_df['hum'] * 100
        day_df['windspeed_kph'] = day_df['windspeed'] * 67
        
        hour_df['temp_celsius'] = hour_df['temp'] * 41
        hour_df['hum_percent'] = hour_df['hum'] * 100
        hour_df['windspeed_kph'] = hour_df['windspeed'] * 67
        
        return day_df, hour_df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.error("Pastikan file 'day.csv' dan 'hour.csv' tersedia di path yang benar.")
        return None, None

# Fungsi interaktif untuk analisis tren harian
def interactive_daily_trends(day_df):
    st.subheader("Analisis Tren Harian")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Pilihan visualisasi
        plot_type = st.selectbox(
            "Pilih Jenis Visualisasi:",
            ["Bar Chart", "Line Chart", "Box Plot"]
        )
        
        # Pilihan agregasi
        agg_method = st.selectbox(
            "Pilih Metode Agregasi:",
            ["Mean", "Median", "Sum", "Min", "Max"]
        )
        
        # Pilihan variabel untuk visualisasi
        y_var = st.selectbox(
            "Pilih Variabel untuk Divisualisasi:",
            ["cnt", "casual", "registered"]
        )
        
    with col2:
        # Menciptakan visualisasi berdasarkan pilihan pengguna
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Mendapatkan tata urutan hari
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        # Menentukan fungsi agregasi
        agg_func = {
            "Mean": np.mean,
            "Median": np.median,
            "Sum": np.sum,
            "Min": np.min,
            "Max": np.max
        }[agg_method]
        
        # Agregasi data
        if 'weekday_name' in day_df.columns:
            daily_data = day_df.groupby('weekday_name')[y_var].agg(agg_func)
            daily_data = daily_data.reindex(day_order)
        else:
            day_df['weekday_name'] = day_df['weekday'].map({0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday'})
            daily_data = day_df.groupby('weekday_name')[y_var].agg(agg_func)
            daily_data = daily_data.reindex(day_order)
        
        # Membuat visualisasi
        if plot_type == "Bar Chart":
            sns.barplot(x=daily_data.index, y=daily_data.values, ax=ax)
        elif plot_type == "Line Chart":
            sns.lineplot(x=daily_data.index, y=daily_data.values, ax=ax, marker='o')
        else:  # Box Plot
            sns.boxplot(x='weekday_name', y=y_var, data=day_df, order=day_order, ax=ax)
        
        var_labels = {
            "cnt": "Total Peminjaman",
            "casual": "Peminjaman Pengguna Casual",
            "registered": "Peminjaman Pengguna Terdaftar"
        }
        
        ax.set_title(f'{agg_method} {var_labels.get(y_var, y_var)} Berdasarkan Hari', fontsize=15)
        ax.set_xlabel('Hari', fontsize=12)
        ax.set_ylabel(f'{var_labels.get(y_var, y_var)}', fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        
        st.pyplot(fig)
        
        # Tabel data
        st.write("Data Agregasi:")
        st.dataframe(daily_data.reset_index().rename(columns={
            'weekday_name': 'Hari', 
            y_var: var_labels.get(y_var, y_var)
        }))

# Fungsi interaktif untuk analisis distribusi jam
def interactive_hourly_distribution(hour_df):
    st.subheader("Analisis Distribusi Berdasarkan Jam")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Pilihan variabel
        y_var = st.selectbox(
            "Pilih Variabel untuk Analisis:",
            ["cnt", "casual", "registered"],
            key="hourly_y_var"
        )
        
        # Filter berdasarkan hari kerja vs akhir pekan
        workday_filter = st.radio(
            "Filter Berdasarkan Hari:",
            ["Semua Hari", "Hari Kerja", "Akhir Pekan"]
        )
        
        # Filter musim
        seasons = {1: "Musim Semi", 2: "Musim Panas", 3: "Musim Gugur", 4: "Musim Dingin"}
        selected_seasons = st.multiselect(
            "Filter Berdasarkan Musim:",
            options=list(seasons.keys()),
            default=list(seasons.keys()),
            format_func=lambda x: seasons[x]
        )
        
    with col2:
        # Filter data berdasarkan pilihan pengguna
        filtered_df = hour_df.copy()
        
        if workday_filter != "Semua Hari":
            if workday_filter == "Hari Kerja":
                filtered_df = filtered_df[filtered_df['workingday'] == 1]
            else:  # Akhir Pekan
                filtered_df = filtered_df[filtered_df['workingday'] == 0]
        
        if selected_seasons:
            filtered_df = filtered_df[filtered_df['season'].isin(selected_seasons)]
        
        # Membuat visualisasi
        fig, ax = plt.subplots(figsize=(10, 6))
        
        hourly_data = filtered_df.groupby('hr')[y_var].mean()
        
        sns.lineplot(x=hourly_data.index, y=hourly_data.values, ax=ax, marker='o')
        
        var_labels = {
            "cnt": "Total Peminjaman",
            "casual": "Peminjaman Pengguna Casual",
            "registered": "Peminjaman Pengguna Terdaftar"
        }
        
        ax.set_title(f'Rata-rata {var_labels.get(y_var, y_var)} Berdasarkan Jam', fontsize=15)
        ax.set_xlabel('Jam', fontsize=12)
        ax.set_ylabel(f'Rata-rata {var_labels.get(y_var, y_var)}', fontsize=12)
        ax.set_xticks(range(0, 24))
        
        # Menambahkan anotasi pola
        if y_var == "cnt":
            morning_peak = hourly_data.iloc[7:10].idxmax()
            evening_peak = hourly_data.iloc[16:20].idxmax()
            
            # Pastikan nilai peak ada sebelum menambahkan anotasi
            if not pd.isna(hourly_data[morning_peak]):
                ax.annotate(f'Puncak Pagi: {morning_peak}:00', 
                           xy=(morning_peak, hourly_data[morning_peak]), 
                           xytext=(morning_peak-1, hourly_data[morning_peak]+100),
                           arrowprops=dict(facecolor='black', shrink=0.05))
            
            if not pd.isna(hourly_data[evening_peak]):
                ax.annotate(f'Puncak Sore: {evening_peak}:00', 
                           xy=(evening_peak, hourly_data[evening_peak]), 
                           xytext=(evening_peak-1, hourly_data[evening_peak]+100),
                           arrowprops=dict(facecolor='black', shrink=0.05))
        
        st.pyplot(fig)
        
        # Heatmap per jam dan hari
        st.write("Heatmap Berdasarkan Jam dan Hari:")
        
        # Menambahkan kolom hari jika belum ada
        if 'weekday' in filtered_df.columns:
            if 'weekday_name' not in filtered_df.columns:
                day_names = {0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday'}
                filtered_df['weekday_name'] = filtered_df['weekday'].map(day_names)
            
            # Membuat heatmap
            pivot_df = filtered_df.pivot_table(
                index='hr', 
                columns='weekday_name', 
                values=y_var, 
                aggfunc='mean'
            )
            
            # Mengurutkan kolom hari
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            pivot_df = pivot_df.reindex(columns=day_order)
            
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(pivot_df, cmap='YlGnBu', ax=ax, annot=False, fmt=".0f")
            ax.set_title(f'Rata-rata {var_labels.get(y_var, y_var)} Berdasarkan Jam dan Hari', fontsize=15)
            st.pyplot(fig)

# Fungsi interaktif untuk analisis korelasi dengan faktor cuaca
def interactive_weather_analysis(df):
    st.subheader("Analisis Korelasi dengan Faktor Cuaca")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Pilihan variabel x (faktor cuaca)
        x_var = st.selectbox(
            "Pilih Faktor Cuaca:",
            ["temp_celsius", "hum_percent", "windspeed_kph"],
            format_func=lambda x: {
                "temp_celsius": "Suhu (°C)",
                "hum_percent": "Kelembaban (%)",
                "windspeed_kph": "Kecepatan Angin (km/h)"
            }.get(x, x)
        )
        
        # Pilihan variabel y (jenis peminjaman)
        y_var = st.selectbox(
            "Pilih Tipe Peminjaman:",
            ["cnt", "casual", "registered"],
            key="weather_y_var",
            format_func=lambda x: {
                "cnt": "Total Peminjaman",
                "casual": "Peminjaman Pengguna Casual", 
                "registered": "Peminjaman Pengguna Terdaftar"
            }.get(x, x)
        )
        
        # Filter berdasarkan kondisi cuaca
        weather_options = {
            1: 'Cerah',
            2: 'Berawan',
            3: 'Hujan Ringan/Salju Ringan',
            4: 'Hujan Lebat/Salju Lebat'
        }
        selected_weather = st.multiselect(
            'Filter Berdasarkan Kondisi Cuaca:',
            options=list(weather_options.keys()),
            default=list(weather_options.keys()),
            format_func=lambda x: weather_options[x]
        )
        
    with col2:
        # Filter data berdasarkan pilihan pengguna
        filtered_df = df.copy()
        
        if selected_weather:
            filtered_df = filtered_df[filtered_df['weathersit'].isin(selected_weather)]
        
        # Membuat scatter plot dengan garis regresi
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Scatter plot dengan faktor cuaca
        scatter = sns.scatterplot(
            x=x_var, 
            y=y_var, 
            data=filtered_df, 
            hue='weathersit',
            palette='viridis',
            alpha=0.6,
            ax=ax
        )
        
        # Garis regresi
        sns.regplot(
            x=x_var, 
            y=y_var, 
            data=filtered_df, 
            scatter=False, 
            color='red',
            ax=ax
        )
        
        x_labels = {
            "temp_celsius": "Suhu (°C)",
            "hum_percent": "Kelembaban (%)",
            "windspeed_kph": "Kecepatan Angin (km/h)"
        }
        
        y_labels = {
            "cnt": "Total Peminjaman",
            "casual": "Peminjaman Pengguna Casual",
            "registered": "Peminjaman Pengguna Terdaftar"
        }
        
        # Mempercantik legend
        handles, labels = ax.get_legend_handles_labels()
        weather_labels = [weather_options.get(int(float(label)), label) if label.replace('.', '', 1).isdigit() else label for label in labels]
        ax.legend(handles, weather_labels, title='Kondisi Cuaca')
        
        ax.set_title(f'Korelasi antara {x_labels.get(x_var, x_var)} dan {y_labels.get(y_var, y_var)}', fontsize=15)
        ax.set_xlabel(x_labels.get(x_var, x_var), fontsize=12)
        ax.set_ylabel(y_labels.get(y_var, y_var), fontsize=12)
        
        # Menghitung dan menampilkan korelasi
        correlation = filtered_df[[x_var, y_var]].corr().iloc[0, 1]
        ax.annotate(f'Korelasi: {correlation:.2f}', 
                   xy=(0.05, 0.95), 
                   xycoords='axes fraction',
                   bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))
        
        st.pyplot(fig)
        
        # Menampilkan pola berdasarkan statistik deskriptif
        st.write("Statistik Deskriptif Berdasarkan Kondisi Cuaca:")
        
        if selected_weather:
            stats_df = filtered_df.groupby('weathersit')[y_var].agg(['mean', 'median', 'std', 'count']).reset_index()
            stats_df['weathersit'] = stats_df['weathersit'].map(weather_options)
            stats_df.columns = ['Kondisi Cuaca', 'Rata-rata', 'Median', 'Std Dev', 'Jumlah Data']
            st.dataframe(stats_df)

# Fungsi untuk analisis tren waktu interaktif
def interactive_time_series(day_df):
    st.subheader("Analisis Tren Waktu")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Pilihan periode waktu
        min_date = day_df['dteday'].min().date()
        max_date = day_df['dteday'].max().date()
        
        date_range = st.date_input(
            "Pilih Rentang Waktu:",
            [min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )
        
        # Pilihan frekuensi agregasi
        freq = st.selectbox(
            "Pilih Frekuensi Agregasi:",
            ["Harian", "Mingguan", "Bulanan"]
        )
        
        # Pilihan variabel untuk visualisasi
        y_vars = st.multiselect(
            "Pilih Variabel untuk Divisualisasi:",
            ["cnt", "casual", "registered"],
            default=["cnt"],
            format_func=lambda x: {
                "cnt": "Total Peminjaman",
                "casual": "Peminjaman Pengguna Casual",
                "registered": "Peminjaman Pengguna Terdaftar"
            }.get(x, x)
        )
        
        # Toggle untuk rolling average
        use_rolling = st.checkbox("Tampilkan Rolling Average")
        
        if use_rolling:
            window_size = st.slider("Window Size Rolling Average:", 1, 30, 7)
    
    with col2:
        # Filter berdasarkan rentang tanggal
        if len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df = day_df[(day_df['dteday'].dt.date >= start_date) & 
                                (day_df['dteday'].dt.date <= end_date)]
        else:
            filtered_df = day_df
        
        # Mengatur frekuensi agregasi
        if freq == "Harian":
            filtered_df['period'] = filtered_df['dteday']
        elif freq == "Mingguan":
            filtered_df['period'] = filtered_df['dteday'].dt.to_period('W').dt.start_time
        else:  # Bulanan
            filtered_df['period'] = filtered_df['dteday'].dt.to_period('M').dt.start_time
        
        # Agregasi data
        agg_df = filtered_df.groupby('period')[y_vars].sum().reset_index()
        
        # Membuat visualisasi
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for y_var in y_vars:
            sns.lineplot(
                x='period', 
                y=y_var, 
                data=agg_df, 
                label={
                    "cnt": "Total Peminjaman",
                    "casual": "Pengguna Casual",
                    "registered": "Pengguna Terdaftar"
                }.get(y_var, y_var),
                ax=ax
            )
            
            # Menambahkan rolling average jika diminta
            if use_rolling and len(agg_df) > window_size:
                rolling_data = agg_df[y_var].rolling(window=window_size).mean()
                sns.lineplot(
                    x=agg_df['period'],
                    y=rolling_data,
                    ax=ax,
                    linestyle='--',
                    alpha=0.7,
                    label=f"{y_var} (Rolling Avg {window_size})"
                )
        
        ax.set_title(f'Tren Peminjaman Sepeda ({freq})', fontsize=15)
        ax.set_xlabel('Periode', fontsize=12)
        ax.set_ylabel('Jumlah Peminjaman', fontsize=12)
        
        # Format sumbu x berdasarkan frekuensi
        if freq == "Harian":
            plt.xticks(rotation=45)
        else:
            # Untuk mingguan dan bulanan, format label tanggal
            date_fmt = '%b %d' if freq == "Mingguan" else '%b %Y'
            new_labels = [d.strftime(date_fmt) for d in agg_df['period']]
            
            # Jika terlalu banyak label, pilih subset
            if len(new_labels) > 12:
                step = len(new_labels) // 12
                plt.xticks(range(0, len(new_labels), step), [new_labels[i] for i in range(0, len(new_labels), step)], rotation=45)
            else:
                plt.xticks(range(len(new_labels)), new_labels, rotation=45)
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # Download data
        csv = agg_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Download Data",
            csv,
            f"bike_rental_{freq.lower()}.csv",
            "text/csv",
            key='download-csv'
        )

# Fungsi untuk perbandingan interaktif (casual vs registered)
def interactive_user_comparison(day_df, hour_df):
    st.subheader("Perbandingan Pengguna Casual vs Terdaftar")
    
    # Pilih dataset untuk analisis
    dataset = st.radio(
        "Pilih Dataset:",
        ["Data Harian", "Data Per Jam"]
    )
    
    df = day_df if dataset == "Data Harian" else hour_df
    
    # Pilih tipe perbandingan
    comparison_type = st.selectbox(
        "Pilih Tipe Perbandingan:",
        ["Proporsi Harian", "Tren Waktu", "Berdasarkan Cuaca", "Berdasarkan Suhu"]
    )
    
    if comparison_type == "Proporsi Harian":
        # Agregasi data untuk proporsi harian
        if 'weekday_name' not in df.columns:
            day_names = {0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday'}
            df['weekday_name'] = df['weekday'].map(day_names)
        
        daily_casual = df.groupby('weekday_name')['casual'].sum()
        daily_registered = df.groupby('weekday_name')['registered'].sum()
        
        # Menyusun dataframe untuk visualisasi
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        comp_df = pd.DataFrame({
            'weekday': day_order,
            'casual': [daily_casual.get(day, 0) for day in day_order],
            'registered': [daily_registered.get(day, 0) for day in day_order]
        })
        
        # Menghitung total dan persentase
        comp_df['total'] = comp_df['casual'] + comp_df['registered']
        comp_df['casual_pct'] = (comp_df['casual'] / comp_df['total'] * 100).round(1)
        comp_df['registered_pct'] = (comp_df['registered'] / comp_df['total'] * 100).round(1)
        
        # Membuat visualisasi
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Plot 1: Jumlah absolut
        comp_df_melted = pd.melt(comp_df, id_vars=['weekday'], value_vars=['casual', 'registered'],
                                var_name='user_type', value_name='count')
        
        sns.barplot(x='weekday', y='count', hue='user_type', data=comp_df_melted, ax=ax1)
        ax1.set_title('Jumlah Pengguna Berdasarkan Hari', fontsize=15)
        ax1.set_xlabel('Hari', fontsize=12)
        ax1.set_ylabel('Jumlah Peminjaman', fontsize=12)
        ax1.tick_params(axis='x', rotation=45)
        
        # Plot 2: Persentase
        percentages = np.array([comp_df['casual_pct'], comp_df['registered_pct']])
        ax2.bar(comp_df['weekday'], comp_df['registered_pct'], label='Terdaftar')
        ax2.bar(comp_df['weekday'], comp_df['casual_pct'], bottom=comp_df['registered_pct'], label='Casual')
        
        ax2.set_title('Proporsi Pengguna Berdasarkan Hari (%)', fontsize=15)
        ax2.set_xlabel('Hari', fontsize=12)
        ax2.set_ylabel('Persentase (%)', fontsize=12)
        ax2.tick_params(axis='x', rotation=45)
        ax2.legend()
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # Tabel data
        st.write("Data Proporsi Pengguna:")
        display_df = comp_df[['weekday', 'casual', 'registered', 'total', 'casual_pct', 'registered_pct']]
        display_df.columns = ['Hari', 'Casual', 'Terdaftar', 'Total', '% Casual', '% Terdaftar']
        st.dataframe(display_df)
        
    elif comparison_type == "Tren Waktu":
        # Filter waktu
        col1, col2 = st.columns(2)
        
        with col1:
            # Pilihan periode waktu
            min_date = df['dteday'].min().date()
            max_date = df['dteday'].max().date()
            
            date_range = st.date_input(
                "Pilih Rentang Waktu:",
                [min_date, max_date],
                min_value=min_date,
                max_value=max_date,
                key="comp_date_range"
            )
        
        with col2:
            # Pilihan frekuensi agregasi
            freq = st.selectbox(
                "Pilih Frekuensi Agregasi:",
                ["Harian", "Mingguan", "Bulanan"],
                key="comp_freq"
            )
        
        # Filter berdasarkan rentang tanggal
        if len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df = df[(df['dteday'].dt.date >= start_date) & 
                            (df['dteday'].dt.date <= end_date)]
        else:
            filtered_df = df
        
        # Mengatur frekuensi agregasi
        if freq == "Harian":
            filtered_df['period'] = filtered_df['dteday']
        elif freq == "Mingguan":
            filtered_df['period'] = filtered_df['dteday'].dt.to_period('W').dt.start_time
        else:  # Bulanan
            filtered_df['period'] = filtered_df['dteday'].dt.to_period('M').dt.start_time
        
        # Agregasi data
        agg_casual = filtered_df.groupby('period')['casual'].sum()
        agg_registered = filtered_df.groupby('period')['registered'].sum()
        
        # Membuat dataframe untuk visualisasi
        trend_df = pd.DataFrame({
            'period': agg_casual.index,
            'casual': agg_casual.values,
            'registered': agg_registered.values
        })
        
        trend_df['total'] = trend_df['casual'] + trend_df['registered']
        trend_df['casual_pct'] = (trend_df['casual'] / trend_df['total'] * 100).round(1)
        trend_df['registered_pct'] = (trend_df['registered'] / trend_df['total'] * 100).round(1)
        
        # Membuat visualisasi
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
        
        # Plot 1: Jumlah absolut
        sns.lineplot(x='period', y='casual', data=trend_df, marker='o', label='Casual', ax=ax1)
        sns.lineplot(x='period', y='registered', data=trend_df, marker='o', label='Terdaftar', ax=ax1)
        
        ax1.set_title(f'Tren Jumlah Pengguna ({freq})', fontsize=15)
        ax1.set_ylabel('Jumlah Peminjaman', fontsize=12)
        ax1.legend()
        
        # Plot 2: Persentase
        sns.lineplot(x='period', y='casual_pct', data=trend_df, marker='o', label='% Casual', ax=ax2)
        sns.lineplot(x='period', y='registered_pct', data=trend_df, marker='o', label='% Terdaftar', ax=ax2)
        
        ax2.set_title(f'Tren Proporsi Pengguna ({freq})', fontsize=15)
        ax2.set_xlabel('Periode', fontsize=12)
        ax2.set_ylabel('Persentase (%)', fontsize=12)
        ax2.legend()
        
        # Format sumbu x berdasarkan frekuensi
        if freq == "Harian":
            plt.xticks(rotation=45)
        else:
            # Untuk mingguan dan bulanan, format label tanggal
            date_fmt = '%b %d' if freq == "Mingguan" else '%b %Y'
            new_labels = [d.strftime(date_fmt) for d in trend_df['period']]
            
            # Jika terlalu banyak label, pilih subset
            if len(new_labels) > 12:
                step = len(new_labels) // 12
                plt.xticks(range(0, len(new_labels), step), [new_labels[i] for i in range(0, len(new_labels), step)], rotation=45)
            else:
                plt.xticks(range(len(new_labels)), new_labels, rotation=45)
        
        plt.tight_layout()
        st.pyplot(fig)
        
    elif comparison_type == "Berdasarkan Cuaca":
        # Analisis berdasarkan cuaca
        weather_options = {
            1: 'Cerah',
            2: 'Berawan',
            3: 'Hujan Ringan/Salju Ringan',
            4: 'Hujan Lebat/Salju Lebat'
        }
        
        # Agregasi data berdasarkan kondisi cuaca
        weather_casual = df.groupby('weathersit')['casual'].sum()
        weather_registered = df.groupby('weathersit')['registered'].sum()
        
        # Menyusun dataframe untuk visualisasi
        weather_df = pd.DataFrame({
            'weathersit': list(weather_options.keys()),
            'weather_name': list(weather_options.values()),
            'casual': [weather_casual.get(w, 0) for w in weather_options.keys()],
            'registered': [weather_registered.get(w, 0) for w in weather_options.keys()]
        })
        
        weather_df['total'] = weather_df['casual'] + weather_df['registered']
        weather_df['casual_pct'] = (weather_df['casual'] / weather_df['total'] * 100).round(1)
        weather_df['registered_pct'] = (weather_df['registered'] / weather_df['total'] * 100).round(1)
        
        # Membuat visualisasi
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Plot 1: Jumlah absolut
        weather_df_melted = pd.melt(weather_df, id_vars=['weather_name'], value_vars=['casual', 'registered'],
                                   var_name='user_type', value_name='count')
        
        sns.barplot(x='weather_name', y='count', hue='user_type', data=weather_df_melted, ax=ax1)
        ax1.set_title('Jumlah Pengguna Berdasarkan Kondisi Cuaca', fontsize=15)
        ax1.set_xlabel('Kondisi Cuaca', fontsize=12)
        ax1.set_ylabel('Jumlah Peminjaman', fontsize=12)
        ax1.tick_params(axis='x', rotation=45)
        
        # Plot 2: Persentase
        ax2.bar(weather_df['weather_name'], weather_df['registered_pct'], label='Terdaftar')
        ax2.bar(weather_df['weather_name'], weather_df['casual_pct'], bottom=weather_df['registered_pct'], label='Casual')
        
        ax2.set_title('Proporsi Pengguna Berdasarkan Kondisi Cuaca (%)', fontsize=15)
        ax2.set_xlabel('Kondisi Cuaca', fontsize=12)
        ax2.set_ylabel('Persentase (%)', fontsize=12)
        ax2.tick_params(axis='x', rotation=45)
        ax2.legend()
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # Tabel data
        st.write("Data Proporsi Pengguna Berdasarkan Cuaca:")
        display_df = weather_df[['weather_name', 'casual', 'registered', 'total', 'casual_pct', 'registered_pct']]
        display_df.columns = ['Kondisi Cuaca', 'Casual', 'Terdaftar', 'Total', '% Casual', '% Terdaftar']
        st.dataframe(display_df)
        
    else:  # Berdasarkan Suhu
        # Membuat bins untuk suhu
        df['temp_bins'] = pd.cut(df['temp_celsius'], 
                                bins=[0, 10, 15, 20, 25, 30, 35, 45],
                                labels=['0-10°C', '10-15°C', '15-20°C', '20-25°C', '25-30°C', '30-35°C', '35-45°C'])
        
        # Agregasi data berdasarkan rentang suhu
        temp_casual = df.groupby('temp_bins')['casual'].sum()
        temp_registered = df.groupby('temp_bins')['registered'].sum()
        
        # Menyusun dataframe untuk visualisasi
        temp_df = pd.DataFrame({
            'temp_range': temp_casual.index,
            'casual': temp_casual.values,
            'registered': temp_registered.values
        })
        
        temp_df['total'] = temp_df['casual'] + temp_df['registered']
        temp_df['casual_pct'] = (temp_df['casual'] / temp_df['total'] * 100).round(1)
        temp_df['registered_pct'] = (temp_df['registered'] / temp_df['total'] * 100).round(1)
        
        # Membuat visualisasi
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Plot 1: Jumlah absolut
        temp_df_melted = pd.melt(temp_df, id_vars=['temp_range'], value_vars=['casual', 'registered'],
                                var_name='user_type', value_name='count')
        
        sns.barplot(x='temp_range', y='count', hue='user_type', data=temp_df_melted, ax=ax1)
        ax1.set_title('Jumlah Pengguna Berdasarkan Rentang Suhu', fontsize=15)
        ax1.set_xlabel('Rentang Suhu', fontsize=12)
        ax1.set_ylabel('Jumlah Peminjaman', fontsize=12)
        ax1.tick_params(axis='x', rotation=45)
        
        # Plot 2: Persentase
        ax2.bar(temp_df['temp_range'], temp_df['registered_pct'], label='Terdaftar')
        ax2.bar(temp_df['temp_range'], temp_df['casual_pct'], bottom=temp_df['registered_pct'], label='Casual')
        
        ax2.set_title('Proporsi Pengguna Berdasarkan Rentang Suhu (%)', fontsize=15)
        ax2.set_xlabel('Rentang Suhu', fontsize=12)
        ax2.set_ylabel('Persentase (%)', fontsize=12)
        ax2.tick_params(axis='x', rotation=45)
        ax2.legend()
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # Tabel data
        st.write("Data Proporsi Pengguna Berdasarkan Suhu:")
        display_df = temp_df[['temp_range', 'casual', 'registered', 'total', 'casual_pct', 'registered_pct']]
        display_df.columns = ['Rentang Suhu', 'Casual', 'Terdaftar', 'Total', '% Casual', '% Terdaftar']
        st.dataframe(display_df)

# Fungsi untuk analisis kondisi cuaca interaktif
def interactive_weather_conditions(df):
    st.subheader("Eksplorasi Pengaruh Kondisi Cuaca")
    
    # Filter berdasarkan kondisi cuaca
    weather_options = {
        1: 'Cerah',
        2: 'Berawan',
        3: 'Hujan Ringan/Salju Ringan',
        4: 'Hujan Lebat/Salju Lebat'
    }
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        selected_weather = st.multiselect(
            'Pilih Kondisi Cuaca:',
            options=list(weather_options.keys()),
            default=[1, 2],
            format_func=lambda x: weather_options[x]
        )
        
        # Pilihan variabel
        y_var = st.selectbox(
            "Pilih Variabel untuk Analisis:",
            ["cnt", "casual", "registered"],
            key="weather_cond_var",
            format_func=lambda x: {
                "cnt": "Total Peminjaman",
                "casual": "Peminjaman Pengguna Casual", 
                "registered": "Peminjaman Pengguna Terdaftar"
            }.get(x, x)
        )
        
        # Pilihan tipe visualisasi
        viz_type = st.radio(
            "Pilih Tipe Visualisasi:",
            ["Box Plot", "Violin Plot", "Strip Plot"]
        )
    
    with col2:
        if selected_weather:
            # Filter data berdasarkan kondisi cuaca
            filtered_df = df[df['weathersit'].isin(selected_weather)]
            
            # Membuat visualisasi
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Mapping kondisi cuaca untuk display
            filtered_df['weather_name'] = filtered_df['weathersit'].map(weather_options)
            
            # Memilih tipe visualisasi
            if viz_type == "Box Plot":
                sns.boxplot(x='weather_name', y=y_var, data=filtered_df, ax=ax)
            elif viz_type == "Violin Plot":
                sns.violinplot(x='weather_name', y=y_var, data=filtered_df, ax=ax)
            else:  # Strip Plot
                sns.stripplot(x='weather_name', y=y_var, data=filtered_df, jitter=True, alpha=0.5, ax=ax)
                
            var_label = {
                "cnt": "Total Peminjaman",
                "casual": "Peminjaman Pengguna Casual",
                "registered": "Peminjaman Pengguna Terdaftar"
            }.get(y_var, y_var)
            
            ax.set_title(f'Distribusi {var_label} Berdasarkan Kondisi Cuaca', fontsize=15)
            ax.set_xlabel('Kondisi Cuaca', fontsize=12)
            ax.set_ylabel(var_label, fontsize=12)
            
            st.pyplot(fig)
            
            # Statistik deskriptif
            st.write("Statistik Deskriptif:")
            stats = filtered_df.groupby('weather_name')[y_var].describe().reset_index()
            st.dataframe(stats)
            
            # Analisis ANOVA
            if len(selected_weather) > 1:
                st.write("Perbandingan Rata-rata Antar Kondisi Cuaca:")
                
                from scipy import stats as scipy_stats
                
                # Menyiapkan data untuk ANOVA
                weather_groups = []
                for weather in selected_weather:
                    group_data = filtered_df[filtered_df['weathersit'] == weather][y_var].values
                    if len(group_data) > 0:
                        weather_groups.append(group_data)
                
                if len(weather_groups) > 1:
                    # Melakukan ANOVA
                    f_stat, p_value = scipy_stats.f_oneway(*weather_groups)
                    
                    st.write(f"F-statistic: {f_stat:.2f}")
                    st.write(f"p-value: {p_value:.4f}")
                    
                    if p_value < 0.05:
                        st.write("Kesimpulan: Terdapat perbedaan signifikan dalam peminjaman sepeda antar kondisi cuaca yang dipilih.")
                    else:
                        st.write("Kesimpulan: Tidak ada perbedaan signifikan dalam peminjaman sepeda antar kondisi cuaca yang dipilih.")

# Fungsi utama aplikasi
def main():
    st.set_page_config(
        page_title='Dashboard Analisis Bike Sharing Interaktif',
        layout='wide',
        initial_sidebar_state='expanded'
    )
    
    # Sidebar untuk navigasi
    st.sidebar.title('Navigasi Dashboard')
    
    # Muat data
    with st.spinner('Memuat dan memproses data...'):
        day_df, hour_df = load_data()
    
    if day_df is not None and hour_df is not None:
        # Tampilkan info dataset
        with st.sidebar.expander("Informasi Dataset"):
            st.write(f"Jumlah Data Harian: {len(day_df)}")
            st.write(f"Jumlah Data Per Jam: {len(hour_df)}")
            st.write(f"Periode: {day_df['dteday'].min().date()} hingga {day_df['dteday'].max().date()}")
        
        # Menu analisis
        analysis_option = st.sidebar.radio(
            "Pilih Analisis:",
            ["Dashboard Utama", "Tren Harian", "Distribusi Jam", "Korelasi Cuaca", 
             "Tren Waktu", "Pengguna Casual vs Terdaftar", "Kondisi Cuaca"]
        )
        
        if analysis_option == "Dashboard Utama":
            # Judul Utama
            st.title('Dashboard Analisis Data Bike Sharing')
            st.write("""
            Dashboard ini menyajikan analisis data peminjaman sepeda dengan fitur interaktif yang memungkinkan pengguna
            untuk mengeksplorasi dan memanipulasi data secara langsung.
            """)
            
            # KPI metrics
            st.subheader("Metrik Utama")
            col1, col2, col3, col4 = st.columns(4)
            
            total_rentals = int(day_df['cnt'].sum())
            avg_daily = int(day_df['cnt'].mean())
            max_daily = int(day_df['cnt'].max())
            peak_month = day_df.groupby(day_df['dteday'].dt.month)['cnt'].mean().idxmax()
            month_names = {1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April', 5: 'Mei', 6: 'Juni',
                          7: 'Juli', 8: 'Agustus', 9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'}
            
            col1.metric("Total Peminjaman", f"{total_rentals:,}")
            col2.metric("Rata-rata Harian", f"{avg_daily:,}")
            col3.metric("Peminjaman Maksimum", f"{max_daily:,}")
            col4.metric("Bulan Terpadat", month_names.get(peak_month, peak_month))
            
            # Visualisasi ringkasan
            st.subheader("Ringkasan Visualisasi")
            
            # Baris 1: Tren waktu dan distribusi jam
            row1_col1, row1_col2 = st.columns(2)
            
            with row1_col1:
                # Tren waktu bulanan
                monthly_data = day_df.groupby(day_df['dteday'].dt.to_period('M').dt.start_time)['cnt'].sum().reset_index()
                
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.lineplot(x='dteday', y='cnt', data=monthly_data, marker='o', ax=ax)
                
                ax.set_title('Tren Peminjaman Sepeda Bulanan', fontsize=15)
                ax.set_xlabel('Bulan', fontsize=12)
                ax.set_ylabel('Total Peminjaman', fontsize=12)
                
                # Format sumbu x untuk menampilkan bulan
                date_labels = [d.strftime('%b %Y') for d in monthly_data['dteday']]
                if len(date_labels) > 12:
                    step = len(date_labels) // 12
                    plt.xticks(range(0, len(date_labels), step), [date_labels[i] for i in range(0, len(date_labels), step)], rotation=45)
                else:
                    plt.xticks(range(len(date_labels)), date_labels, rotation=45)
                
                plt.tight_layout()
                st.pyplot(fig)
            
            with row1_col2:
                # Distribusi jam
                hourly_data = hour_df.groupby('hr')['cnt'].mean()
                
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.lineplot(x=hourly_data.index, y=hourly_data.values, marker='o', ax=ax)
                
                ax.set_title('Rata-rata Peminjaman Sepeda Berdasarkan Jam', fontsize=15)
                ax.set_xlabel('Jam', fontsize=12)
                ax.set_ylabel('Rata-rata Peminjaman', fontsize=12)
                ax.set_xticks(range(0, 24, 2))
                
                plt.tight_layout()
                st.pyplot(fig)
            
            # Baris 2: Pengaruh cuaca dan proporsi pengguna
            row2_col1, row2_col2 = st.columns(2)
            
            with row2_col1:
                # Korelasi suhu dan peminjaman
                fig, ax = plt.subplots(figsize=(10, 6))
                
                sns.scatterplot(x='temp_celsius', y='cnt', data=day_df, alpha=0.7, ax=ax)
                sns.regplot(x='temp_celsius', y='cnt', data=day_df, scatter=False, ax=ax)
                
                ax.set_title('Korelasi antara Suhu dan Jumlah Peminjaman', fontsize=15)
                ax.set_xlabel('Suhu (°C)', fontsize=12)
                ax.set_ylabel('Jumlah Peminjaman', fontsize=12)
                
                plt.tight_layout()
                st.pyplot(fig)
            
            with row2_col2:
                # Proporsi pengguna casual vs registered
                casual_total = day_df['casual'].sum()
                registered_total = day_df['registered'].sum()
                
                proportions = [casual_total, registered_total]
                labels = ['Casual', 'Registered']
                
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.pie(proportions, labels=labels, autopct='%1.1f%%', startangle=90,
                      wedgeprops={'edgecolor': 'white', 'linewidth': 1})
                
                ax.set_title('Proporsi Pengguna Casual vs Terdaftar', fontsize=15)
                
                plt.tight_layout()
                st.pyplot(fig)
            
            # Tabel Temuan Utama
            st.subheader("Temuan Utama")
            
            st.write("""
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
            
            5. **Profil Pengguna:**
              - Pengguna terdaftar mendominasi peminjaman sepeda
              - Pengguna casual lebih terpengaruh oleh kondisi cuaca
            """)
        
        elif analysis_option == "Tren Harian":
            interactive_daily_trends(day_df)
        
        elif analysis_option == "Distribusi Jam":
            interactive_hourly_distribution(hour_df)
        
        elif analysis_option == "Korelasi Cuaca":
            interactive_weather_analysis(hour_df)
        
        elif analysis_option == "Tren Waktu":
            interactive_time_series(day_df)
            
        elif analysis_option == "Pengguna Casual vs Terdaftar":
            interactive_user_comparison(day_df, hour_df)
            
        elif analysis_option == "Kondisi Cuaca":
            interactive_weather_conditions(hour_df)

if __name__ == '__main__':
    main()
