# Indonesian Chili Price Forecasting

🌐 **Live Application:** [indonesian-chili-price-prediction.streamlit.app](https://indonesian-chili-price-prediction.streamlit.app/)  
📊 **Dataset Source:** [World Food Programme (WFP) - Indonesia Food Prices (HDX)](https://data.humdata.org/dataset/wfp-food-prices-for-indonesia)

---

## 📌 Brief Project Data Science

Proyek ini merupakan sistem prediksi harga cabai di Indonesia yang dibangun menggunakan teknologi kecerdasan buatan. Sistem ini dirancang untuk memetakan data historis, mengidentifikasi volatilitas wilayah, serta memproyeksikan harga cabai untuk jangka menengah sebagai langkah mitigasi risiko inflasi pangan nasional.

---

## 💡 Konsep Dasar Forecasting

Forecasting atau peramalan deret waktu *(time-series forecasting)* adalah suatu metode analisis untuk memprediksi nilai di masa depan berdasarkan pola, tren, dan siklus yang terbentuk pada masa lalu. Berbeda dengan prediksi data tabular biasa, data deret waktu memiliki ketergantungan kronologis di mana harga pada suatu bulan sangat dipengaruhi oleh apa yang terjadi pada bulan-bulan sebelumnya.

Dalam konteks komoditas pangan seperti cabai, peramalan menjadi krusial karena pergerakan harganya tidak linier dan sangat fluktuatif. Fluktuasi ini dipengaruhi oleh siklus tahunan seperti pergantian cuaca (musim kemarau dan hujan) yang berdampak pada produksi tani, serta lonjakan konsumsi musiman masyarakat pada hari raya keagamaan. Dengan memahami pola historis tersebut melalui metode forecasting, kita dapat mengantisipasi lonjakan harga sebelum terjadi di pasar.

---

## 🎯 Mengenai Proyek Forecasting yang Dibuat

Proyek ini secara spesifik berfokus pada pemodelan prediksi rata-rata harga cabai eceran bulanan di tingkat nasional. Dataset yang digunakan bersumber dari **World Food Programme (WFP) Indonesia** yang mencakup riwayat pencatatan harga selama kurang lebih 17 tahun (periode 2007 hingga 2024). Data ini dikumpulkan dari 34 provinsi dan mencakup 215 pasar eceran di seluruh wilayah Indonesia.

Proyek ini tidak hanya melakukan visualisasi data historis saja, tetapi juga mengimplementasikan model *machine learning* untuk memproyeksikan harga cabai hingga 7 bulan ke depan. Model ini bekerja secara berantai *(recursive forecasting)*, di mana prediksi bulan pertama akan digunakan kembali sebagai data masukan *(input)* untuk mempredict bulan kedua, dan seterusnya. Untuk memberikan estimasi yang realistis, setiap angka proyeksi dilengkapi dengan batas ketidakpastian *(confidence interval)* yang akan melebar seiring bertambah jauhnya horizon prediksi.

---

## 🛠️ Teknologi yang Digunakan

Proyek ini dibangun menggunakan ekosistem Python 3 dengan beberapa pustaka utama:

- **Framework Dashboard:** [Streamlit](https://streamlit.io/) untuk menyajikan visualisasi data secara interaktif dalam bentuk aplikasi multi-halaman.
- **Pemodelan Machine Learning:** [Scikit-Learn](https://scikit-learn.org/) untuk algoritma `RandomForestRegressor`.
- **Pengolahan Data:** [Pandas](https://pandas.pydata.org/) dan [NumPy](https://numpy.org/) untuk pembersihan data, agregasi nilai harga, dan rekayasa fitur.
- **Visualisasi Data:** [Plotly](https://plotly.com/python/) untuk grafik interaktif yang responsif.

---

## 🔄 Alur Data dan Kecerdasan Buatan

Pemodelan prediksi harga dalam sistem ini berjalan melalui beberapa tahapan utama:

1. **Ingestion Data:** Membaca dataset harga eceran cabai rawit dan cabai merah di Indonesia periode 2007 hingga 2024 dari data resmi [WFP Indonesia Food Prices](https://data.humdata.org/dataset/wfp-food-prices-for-indonesia).
2. **Pembersihan Data:** Menyaring jenis cabai, menangani nilai kosong *(missing values)*, dan mengagregasi data dari tingkat pasar menjadi rata-rata bulanan skala provinsi serta nasional.
3. **Rekayasa Fitur:** Membuat fitur prediktor deret waktu seperti *Lag Features* (harga 1 hingga 12 bulan sebelumnya), *Rolling Statistics* (rata-rata bergerak dan standar deviasi), serta *Cyclical Encoding* (sinus dan kosinus bulan) untuk menangkap pola berulang tahunan.
4. **Pelatihan Model:** Menggunakan pembagian data kronologis *(Time-Series Split)* untuk melatih model Random Forest Regressor tanpa kebocoran data masa depan.
5. **Proyeksi Rekursif:** Memprediksi harga bulan berikutnya secara berantai *(recursive forecasting)* hingga 7 bulan ke depan, dilengkapi dengan estimasi batas ketidakpastian harga.

---

## 📱 Struktur Aplikasi Streamlit

Aplikasi ini dibagi menjadi empat bagian utama yang dapat diakses dengan *multi-page*, yang membagi dashboard menjadi 4 bagian yang meliputi Overview Eksekutif, Analisis Spasial, Tren Musiman, dan Model Proyeksi melalui menu navigasi:

- **Overview Eksekutif:** Menampilkan informasi, seperti indikator volatilitas pasar nasional, rata-rata harga cabai nasional sampai proyeksi harga cabai bulan depan.
- **Analisis Spasial:** Informasi pola disparitas geografis dan integrasi logistik dari pemetaan harga eceran pada 215 lokasi pasar di 34 provinsi.
- **Tren Historis & Pola Musiman:** Informasi data historis selama kurang lebih 17 tahun untuk menunjukkan bahwa ketidakstabilan harga cabai tidak terjadi secara acak, tetapi berdasarkan pola yang terus berulang setiap tahunnya.
- **Model Proyeksi Harga:** Menampilkan evaluasi terhadap kinerja model dalam mempelajari data historis yang berisi metrik tingkat akurasi dan variabel yang memengaruhi harga cabai.

Selain itu, Streamlit juga menyediakan komponen input (seperti *dropdown* atau *slider*) agar pengguna dapat memfilter data secara langsung. Sebagai contoh, pengguna dapat memilih antara Cabai Rawit atau Cabai Merah atau menentukan wilayah untuk melihat komparasi harga cabai.
