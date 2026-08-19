import os
import pandas as pd
from datetime import timedelta

script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, "..", "data", "transactions.csv")

transactions = pd.read_csv(data_path, nrows=500000)
transactions["Timestamp"] = pd.to_datetime(transactions["Timestamp"])

incoming_by_account = transactions.groupby("Account.1")
outgoing_by_account = transactions.groupby("Account")

receive_counts = transactions["Account.1"].value_counts()
send_counts = transactions["Account"].value_counts()
candidate_accounts = set(receive_counts[receive_counts >= 2].index) & set(send_counts[send_counts >= 2].index)
print(f"Jumlah akun kandidat: {len(candidate_accounts)}")

TIME_WINDOW = timedelta(hours=2)
AMOUNT_TOLERANCE = 0.02

results = []

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

    total_incoming = len(ins)
    if match_count > 0 and total_incoming >= 5:
        results.append({
            "account": account,
            "pass_through_count": match_count,
            "total_incoming": total_incoming,
            "pass_through_ratio": match_count / total_incoming
        })

print(f"Jumlah akun dengan pola pass-through: {len(results)}")

laundering_accounts = set(transactions[transactions["Is Laundering"] == 1]["Account"]) | \
                       set(transactions[transactions["Is Laundering"] == 1]["Account.1"])

for r in results:
    r["is_flagged_laundering"] = r["account"] in laundering_accounts

results.sort(key=lambda x: x["pass_through_ratio"], reverse=True)
print()
print("=== TOP 10 AKUN DENGAN POLA PASS-THROUGH TERBANYAK (by ratio) ===")
for r in results[:10]:
    print(r)

print()
print("=== FOKUS KE AKUN YANG MEMANG DILABEL LAUNDERING ===")
flagged_results = [r for r in results if r["is_flagged_laundering"]]
print(f"Jumlah akun laundering yang masuk hasil pass-through: {len(flagged_results)}")

flagged_results.sort(key=lambda x: x["pass_through_ratio"], reverse=True)
for r in flagged_results[:10]:
    print(r)

if flagged_results:
    avg_ratio_flagged = sum(r["pass_through_ratio"] for r in flagged_results) / len(flagged_results)
    avg_ratio_all = sum(r["pass_through_ratio"] for r in results) / len(results)
    print()
    print(f"Rata-rata rasio akun laundering: {avg_ratio_flagged:.3f}")
    print(f"Rata-rata rasio semua akun: {avg_ratio_all:.3f}")