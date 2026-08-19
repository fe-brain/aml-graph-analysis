import pandas as pd

# load account data (kecil, aman full load)
accounts = pd.read_csv("../data/accounts.csv")
print("=== ACCOUNTS ===")
print("Jumlah baris:", len(accounts))
print("Kolom:", list(accounts.columns))
print(accounts.head())
print()

# load transaction data, tapi cuma 500000 baris pertama dulu buat eksplorasi
transactions = pd.read_csv("../data/transactions.csv", nrows=500000)
print("=== TRANSACTIONS (sample 50rb baris) ===")
print("Jumlah baris:", len(transactions))
print("Kolom:", list(transactions.columns))
print(transactions.head())

print()
print("=== CEK LABEL LAUNDERING ===")
print(transactions["Is Laundering"].value_counts())
print()
print("Jumlah akun unik (pengirim):", transactions["Account"].nunique())
print("Jumlah akun unik (penerima):", transactions["Account.1"].nunique())