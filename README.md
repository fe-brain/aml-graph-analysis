# AML Graph Analysis

Exploring money laundering detection through graph analytics, using the IBM synthetic dataset for Anti-Money Laundering research.

## Why This Project

Financial crime compliance is often treated as a purely regulatory discipline, but the most valuable analysts increasingly sit at the intersection of compliance domain knowledge and data science. This project is a hands-on exploration of that intersection: applying graph theory to transaction monitoring, a technique that's gaining traction in AML research but remains rare in practice.

## What This Project Does

Starting from raw transaction data, this project builds a directed graph of accounts and money flows, then tests progressively more sophisticated signals for identifying money laundering:

1. **Degree analysis**, identifying accounts with unusually high transaction volume (in/out degree)
2. **Pass-through detection**, flagging accounts that receive funds and quickly forward them (a classic layering signature)
3. **Cycle detection**, finding money that flows through multiple accounts and returns to its origin
4. **Cluster analysis**, grouping connected accounts to reveal potential laundering networks, not just isolated transactions
5. **Composite scoring**, combining all signals above into a single weighted suspicion score per account

## Key Findings

| Signal | Result | Verdict |
|---|---|---|
| High out-degree (volume) | Top sender had 3,421 transactions, only 0.09% flagged as laundering (vs. 0.05% baseline) | Weak signal, volume alone doesn't separate laundering from legitimate high-activity accounts |
| Pass-through ratio (raw count) | 93% of candidate accounts flagged, signal collapsed under loose thresholds | Too noisy, mirrors real-world "alert fatigue" in poorly tuned transaction monitoring systems |
| Pass-through ratio (refined, min. 5 transactions) | Laundering accounts averaged 0.332 ratio vs. 0.345 for all accounts | No meaningful difference, pass-through alone is not a reliable signal in this dataset |
| **Cycle detection** | **15.45% of detected cycles contained a laundering account, vs. 0.376% base rate — a ~41x enrichment** | **Strong signal** |
| **Cluster analysis** | Found a fully-connected 6-account cluster where **100% of accounts were labeled laundering**, forming a complete cycle with funds returning to origin within 4 days | **Strongest single-feature signal, a traceable laundering network** |
| **Composite score** | **Top 50 ranked accounts had a 20% laundering rate — a ~53x enrichment over baseline** | **Best overall result, combining signals outperforms any single feature** |

### Composite Suspicion Score

Combining degree, cycle membership, and pass-through ratio into a single weighted score (cycle weighted highest, reflecting its strength as a standalone signal) produced strong concentration of true laundering accounts at the top of the ranking:

| Top N accounts flagged | Laundering rate | Enrichment vs. baseline (0.376%) |
|---|---|---|
| Top 50 | 20.00% | ~53x |
| Top 100 | 14.00% | ~37x |
| Top 500 | 11.20% | ~30x |
| Top 1000 | 7.10% | ~19x |

This demonstrates the practical value of network-based composite scoring: investigating the top 50 flagged accounts out of 510,000 total would surface laundering accounts at a rate 53 times higher than random sampling, a meaningful efficiency gain for a compliance investigation team. The declining enrichment as N grows is expected and worth noting honestly: only ~600 accounts in this sample carry the strongest signal (cycle membership), so ranking beyond that point increasingly relies on the weaker pass-through signal.

### Case Study: A Complete Laundering Cycle

Cluster analysis surfaced a clean example of layering: a large sum (~1.3M) enters through one account, gets broken into smaller amounts and passed through 5 intermediary accounts, and returns to the originating account — all within a 4-day window, interspersed with unrelated "noise" transactions to obscure the pattern.

**Fund flow:** 803A568D0 → 8012F9500 → 8102CA2C0 → 8040FAF80 → 80AC28E60 → 80CF37D80 → 803A568D0

This is a textbook example of why single-feature detection (volume, pass-through) fails where network-based detection succeeds: the pattern only becomes visible when you trace the full path of funds, not just individual transaction pairs.

## Why This Matters for AML Practice

This progression, from naive signals to network-based detection, mirrors a real challenge in the AML industry: rule-based transaction monitoring systems generate excessive false positives (analyst "alert fatigue"), while graph-based approaches that trace fund flow across accounts are increasingly seen as the next frontier, though still underused due to a shortage of practitioners who can bridge compliance domain knowledge with the technical skills to implement them.

## Dataset

[IBM Transactions for Anti-Money Laundering (AML)](https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml) — a synthetic dataset from Kaggle, not included in this repository due to file size. Download separately to reproduce.

## Tools

Python · pandas · NetworkX

## Next Steps

- Explore fan-out/fan-in patterns as additional composite score features
- Investigate transaction amount patterns within detected clusters (e.g., structuring below reporting thresholds)
- Tune composite score weights systematically (e.g., grid search) rather than manually assigned weights

---

*This is a personal learning project exploring the intersection of AML compliance and data science. Not intended for production use.*