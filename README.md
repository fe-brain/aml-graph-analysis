# AML Graph Analysis

Exploring money laundering detection through graph analytics, using the IBM synthetic dataset for Anti-Money Laundering research.

## Latar Belakang
Project ini adalah eksplorasi pribadi untuk memahami bagaimana graph analytics bisa digunakan dalam transaction monitoring, sebagai respons terhadap gap skill yang teridentifikasi di riset AML/compliance (kombinasi data science + domain knowledge financial crime).

## Yang Sudah Dikerjakan
1. Membangun graph transaksi (network akun) dari 500rb sample transaksi menggunakan NetworkX
2. Analisis in-degree/out-degree untuk mengidentifikasi akun dengan volume transaksi tinggi
3. Investigasi pola pass-through (akun menerima dana lalu cepat mengirim ulang) sebagai indikator potensi layering
4. Perbandingan rasio pass-through antara akun berlabel laundering vs akun normal

## Temuan Utama
- Volume transaksi tinggi (degree) saja tidak cukup jadi sinyal deteksi yang reliable
- Threshold yang longgar menghasilkan terlalu banyak false positive (mirip masalah "alert fatigue" di industri AML)
- Fitur pass-through ratio saja belum berhasil membedakan akun laundering secara signifikan di dataset ini — kemungkinan karena pola laundering di dataset ini lebih kompleks (fan-out, cycle, scatter-gather) daripada pola pass-through sederhana

## Dataset

[IBM Transactions for Anti-Money Laundering (AML)](https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml) — a synthetic dataset from Kaggle, not included in this repository due to file size. Download separately to reproduce.

## Tools

Python · pandas · NetworkX

## Next Steps
- Eksplorasi pola fan-out/fan-in dan cycle detection
- Menggabungkan beberapa fitur menjadi satu skor kecurigaan komposit
