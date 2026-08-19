import os
import pandas as pd
import networkx as nx

# cari lokasi folder tempat script ini berada, lalu turun ke folder data
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, "..", "data", "transactions.csv")

transactions = pd.read_csv(data_path, nrows=500000)

G = nx.DiGraph()

for _, row in transactions.iterrows():
    G.add_edge(row["Account"], row["Account.1"], amount=row["Amount Paid"], is_laundering=row["Is Laundering"])

print("Jumlah node (akun):", G.number_of_nodes())
print("Jumlah edge (transaksi):", G.number_of_edges())

print()
print("=== TOP 5 AKUN PALING BANYAK MENERIMA TRANSAKSI ===")
in_degrees = dict(G.in_degree())
top_receivers = sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)[:5]
for account, count in top_receivers:
    print(f"Akun {account}: menerima dari {count} transaksi berbeda")

print()
print("=== TOP 5 AKUN PALING BANYAK MENGIRIM TRANSAKSI ===")
out_degrees = dict(G.out_degree())
top_senders = sorted(out_degrees.items(), key=lambda x: x[1], reverse=True)[:5]
for account, count in top_senders:
    print(f"Akun {account}: mengirim ke {count} transaksi berbeda")

print()
print("=== CONTOH TRANSAKSI YANG DILABEL LAUNDERING ===")
laundering_edges = [(u, v, d) for u, v, d in G.edges(data=True) if d["is_laundering"] == 1]
print(f"Total edge laundering di graph: {len(laundering_edges)}")
for u, v, d in laundering_edges[:5]:
    print(f"Dari akun {u} -> ke akun {v}, jumlah: {d['amount']}")

print()
print("=== INVESTIGASI KHUSUS AKUN 100428660 ===")
target = "100428660"
target_edges = list(G.out_edges(target, data=True))
total_out = len(target_edges)
laundering_out = sum(1 for u, v, d in target_edges if d["is_laundering"] == 1)
print(f"Total transaksi keluar dari akun ini: {total_out}")
print(f"Dari jumlah itu, yang dilabel laundering: {laundering_out}")
print(f"Persentase laundering: {laundering_out/total_out*100:.2f}%")

print()
print("=== BANDINGKAN: rata-rata rasio laundering di seluruh graph ===")
total_edges_all = G.number_of_edges()
total_laundering_all = sum(1 for u, v, d in G.edges(data=True) if d["is_laundering"] == 1)
print(f"Rasio laundering keseluruhan graph: {total_laundering_all/total_edges_all*100:.4f}%")