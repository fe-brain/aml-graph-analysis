import os
import pandas as pd
import networkx as nx

script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, "..", "data", "transactions.csv")

transactions = pd.read_csv(data_path, nrows=500000)

# bangun graph yang sama kayak sebelumnya
G = nx.DiGraph()
for _, row in transactions.iterrows():
    G.add_edge(row["Account"], row["Account.1"], is_laundering=row["Is Laundering"])

print("Jumlah node:", G.number_of_nodes())
print("Jumlah edge:", G.number_of_edges())

# cari semua cycle pendek (panjang 2-4 akun) di graph
print()
print("Mencari cycle... (ini bisa makan waktu, sabar)")
cycles = list(nx.simple_cycles(G, length_bound=6))
print(f"Jumlah cycle ditemukan (panjang <= 4, termasuk self-loop): {len(cycles)}")

# filter: buang self-loop, cuma ambil cycle beneran (minimal 2 akun berbeda)
real_cycles = [c for c in cycles if len(c) >= 2]
print(f"Jumlah cycle beneran (>=2 akun berbeda): {len(real_cycles)}")

print()
print("=== CONTOH 10 CYCLE BENERAN PERTAMA ===")
for c in real_cycles[:10]:
    print(c)

# cek: berapa banyak akun di cycle ini yang terlibat transaksi laundering?
laundering_accounts = set(transactions[transactions["Is Laundering"] == 1]["Account"]) | \
                       set(transactions[transactions["Is Laundering"] == 1]["Account.1"])

cycles_with_laundering = [c for c in real_cycles if any(acc in laundering_accounts for acc in c)]
print()
print(f"Jumlah cycle yang mengandung minimal 1 akun laundering: {len(cycles_with_laundering)}")
print(f"Persentase: {len(cycles_with_laundering)/len(real_cycles)*100:.2f}%")

print()
print("=== CONTOH CYCLE YANG MENGANDUNG AKUN LAUNDERING ===")
for c in cycles_with_laundering[:5]:
    print(c)

print()
print("=== BASE RATE PEMBANDING ===")
total_accounts = G.number_of_nodes()
total_laundering_accounts = len(laundering_accounts)
print(f"Total akun: {total_accounts}")
print(f"Total akun laundering: {total_laundering_accounts}")
print(f"Base rate akun laundering: {total_laundering_accounts/total_accounts*100:.3f}%")