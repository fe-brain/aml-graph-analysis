import os
import pandas as pd
import networkx as nx
from datetime import timedelta

script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, "..", "data", "transactions.csv")

transactions = pd.read_csv(data_path, nrows=2000000)
transactions["Timestamp"] = pd.to_datetime(transactions["Timestamp"])

# bangun graph
G = nx.DiGraph()
for _, row in transactions.iterrows():
    G.add_edge(row["Account"], row["Account.1"], amount=row["Amount Paid"], is_laundering=row["Is Laundering"])

print("Graph selesai dibangun:", G.number_of_nodes(), "node,", G.number_of_edges(), "edge")

laundering_accounts = set(transactions[transactions["Is Laundering"] == 1]["Account"]) | \
                       set(transactions[transactions["Is Laundering"] == 1]["Account.1"])

# ============ FITUR 1: DEGREE (dinormalisasi) ============
in_degrees = dict(G.in_degree())
out_degrees = dict(G.out_degree())
max_in = max(in_degrees.values())
max_out = max(out_degrees.values())

# ============ FITUR 2: CYCLE MEMBERSHIP ============
print("Mencari cycle...")
cycles = list(nx.simple_cycles(G, length_bound=4))
real_cycles = [c for c in cycles if len(c) >= 2]
accounts_in_cycles = set()
for c in real_cycles:
    accounts_in_cycles.update(c)
print(f"Akun yang terlibat cycle: {len(accounts_in_cycles)}")

# ============ FITUR 3: PASS-THROUGH RATIO ============
print("Menghitung pass-through ratio...")
incoming_by_account = transactions.groupby("Account.1")
outgoing_by_account = transactions.groupby("Account")
receive_counts = transactions["Account.1"].value_counts()
send_counts = transactions["Account"].value_counts()
candidate_accounts = set(receive_counts[receive_counts >= 5].index) & set(send_counts[send_counts >= 2].index)

TIME_WINDOW = timedelta(hours=2)
AMOUNT_TOLERANCE = 0.02
pass_through_ratios = {}

for account in candidate_accounts:
    ins = incoming_by_account.get_group(account)
    outs = outgoing_by_account.get_group(account)
    match_count = 0
    for _, in_row in ins.iterrows():
        in_time = in_row["Timestamp"]
        in_amount = in_row["Amount Received"]
        matches = outs[
            (outs["Timestamp"] >= in_time) &
            (outs["Timestamp"] <= in_time + TIME_WINDOW) &
            (abs(outs["Amount Paid"] - in_amount) <= in_amount * AMOUNT_TOLERANCE)
        ]
        if len(matches) > 0:
            match_count += 1
    pass_through_ratios[account] = match_count / len(ins)

print(f"Akun dengan pass-through ratio dihitung: {len(pass_through_ratios)}")

# ============ GABUNGKAN JADI COMPOSITE SCORE ============
print()
print("Menghitung composite score...")

all_accounts = set(G.nodes())
scores = []

for acc in all_accounts:
    degree_score = (in_degrees.get(acc, 0) / max_in + out_degrees.get(acc, 0) / max_out) / 2
    cycle_score = 1.0 if acc in accounts_in_cycles else 0.0
    pass_through_score = pass_through_ratios.get(acc, 0.0)

    # bobot: cycle paling kuat sinyalnya (dari temuan kita), degree paling lemah
    composite = (0.2 * degree_score) + (0.5 * cycle_score) + (0.3 * pass_through_score)

    scores.append({
        "account": acc,
        "degree_score": degree_score,
        "cycle_score": cycle_score,
        "pass_through_score": pass_through_score,
        "composite_score": composite,
        "is_laundering": acc in laundering_accounts
    })

scores_df = pd.DataFrame(scores)
scores_df = scores_df.sort_values("composite_score", ascending=False)

print()
print("=== TOP 20 AKUN DENGAN COMPOSITE SCORE TERTINGGI ===")
print(scores_df.head(20).to_string(index=False))

print()
print("=== VALIDASI: apakah top-N score berkorelasi dengan laundering? ===")
for n in [50, 100, 500, 1000]:
    top_n = scores_df.head(n)
    laundering_in_top = top_n["is_laundering"].sum()
    print(f"Top {n}: {laundering_in_top} akun laundering ({laundering_in_top/n*100:.2f}%)")

overall_rate = scores_df["is_laundering"].sum() / len(scores_df) * 100
print(f"Baseline (semua akun): {overall_rate:.3f}%")