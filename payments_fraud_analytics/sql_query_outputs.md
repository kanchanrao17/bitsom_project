# SQL Fraud-Pattern Detection — Query Outputs

Database: `paytm_payments.db` (SQLite)

Schema:
- `merchants(merchant_id PK, merchant_name, category, region)`
- `users(user_id PK, signup_date)`
- `transactions(transaction_id PK, user_id FK→users, merchant_id FK→merchants, transaction_time, amount_inr, payment_method, status, risk_score)`

SQL clause coverage: SELECT/WHERE/ORDER BY/LIMIT/DISTINCT, GROUP BY/HAVING, INNER JOIN (Q2, Q5), LEFT JOIN (Q4), aggregate functions (COUNT, SUM, AVG).

## Query 1: Chargeback Impact — count, unique users, total amount

```
 chargeback_count  unique_users_affected  total_chargeback_amount_inr
               28                     27                      54472.0

Rows returned: 1
```

## Query 2: Top 10 Merchants by Txn Count (INNER JOIN, ORDER BY, LIMIT)

```
 merchant_id merchant_name      category region  txn_count  total_gmv_inr
          16  Merchant_016  bill_payment   West         20        11130.0
          37  Merchant_037 entertainment  South         19        12931.0
          29  Merchant_029     ecommerce  North         19        13081.0
           9  Merchant_009     ecommerce  North         18         4982.0
          30  Merchant_030        travel   West         17         7883.0
          25  Merchant_025        travel  South         17        15533.0
           3  Merchant_003       grocery   East         17         8233.0
          36  Merchant_036 entertainment   East         16        12534.0
          34  Merchant_034        travel  South         16        10034.0
          27  Merchant_027     ecommerce  North         16        13584.0

Rows returned: 10
```

## Query 3: Payment Methods with > 50 Transactions (GROUP BY / HAVING / DISTINCT)

```
payment_method  txn_count  unique_users  total_amount_inr  avg_amount_inr
           UPI        276           192          172274.0          624.18
          Card        121            86          102429.0          846.52
        Wallet         96            86           71304.0          742.75
    Netbanking         54            50           36596.0          677.70

Rows returned: 4
```

## Query 4: Users with No Transactions (LEFT JOIN)

```
 user_id         signup_date
       2 2025-03-27 00:00:00
       5 2024-11-09 00:00:00
       7 2024-02-16 00:00:00
       9 2025-04-22 00:00:00
      10 2025-01-04 00:00:00
      12 2025-04-12 00:00:00
      18 2025-04-30 00:00:00
      23 2024-07-09 00:00:00
      27 2025-07-09 00:00:00
      31 2024-05-07 00:00:00
      34 2024-04-13 00:00:00
      35 2024-09-20 00:00:00
      37 2024-10-20 00:00:00
      40 2025-07-14 00:00:00
      43 2025-08-31 00:00:00
      45 2025-08-12 00:00:00
      47 2024-02-29 00:00:00
      48 2025-06-22 00:00:00
      49 2024-01-06 00:00:00
      50 2024-09-26 00:00:00

Rows returned: 20
```

## Query 5: Burner Account Detection (signup < 30 days before chargeback)

```
transaction_id  user_id         signup_date    transaction_time  days_since_signup  amount_inr  risk_score
     TXN200006      357 2026-01-19 11:00:00 2026-01-23 11:00:00                  4      1999.0          88
     TXN200008      359 2026-01-18 22:00:00 2026-01-25 22:00:00                  7      2999.0          96
     TXN200010      361 2026-01-11 07:00:00 2026-01-20 07:00:00                  9      4999.0          95
     TXN200001      352 2025-12-31 12:00:00 2026-01-11 12:00:00                 11      4999.0          95
     TXN200002      353 2026-01-10 14:00:00 2026-01-21 14:00:00                 11      1999.0          79
     TXN200004      355 2026-01-05 12:00:00 2026-01-16 12:00:00                 11      4999.0         100
     TXN200005      356 2026-01-18 07:00:00 2026-01-29 07:00:00                 11      2999.0          96
     TXN200000      351 2026-01-15 06:00:00 2026-01-30 06:00:00                 15      1999.0          79
     TXN200011      362 2026-01-08 02:00:00 2026-01-23 02:00:00                 15      4999.0          88
     TXN200012      363 2026-01-06 17:00:00 2026-01-23 17:00:00                 17       999.0          95
     TXN200013      364 2026-01-04 22:00:00 2026-01-22 22:00:00                 18       999.0          73
     TXN200007      358 2026-01-06 05:00:00 2026-01-28 05:00:00                 22       999.0         100
     TXN200009      360 2025-12-22 13:00:00 2026-01-13 13:00:00                 22      1999.0          90
     TXN200014      365 2025-12-27 21:00:00 2026-01-18 21:00:00                 22      1999.0          90
     TXN200003      354 2025-12-29 19:00:00 2026-01-21 19:00:00                 23      4999.0          80

Rows returned: 15
```

## Query 6: Velocity Attack Detection (≥ 3 txns in a 10-min window)

```
 user_id time_bucket_10min  txn_count_in_window                         transaction_ids        earliest_txn          latest_txn
      59   2026-01-09 21:0                    4 TXN300024,TXN300025,TXN300026,TXN300027 2026-01-09 21:00:00 2026-01-09 21:03:00
      73   2026-01-12 09:0                    4 TXN300008,TXN300009,TXN300010,TXN300011 2026-01-12 09:00:00 2026-01-12 09:03:00
     154   2026-01-02 22:0                    4 TXN300012,TXN300013,TXN300014,TXN300015 2026-01-02 22:00:00 2026-01-02 22:03:00
     200   2026-01-01 22:0                    4 TXN300020,TXN300021,TXN300022,TXN300023 2026-01-01 22:00:00 2026-01-01 22:03:00
     229   2026-01-12 12:0                    4 TXN300004,TXN300005,TXN300006,TXN300007 2026-01-12 12:00:00 2026-01-12 12:03:00
     287   2026-01-14 14:0                    4 TXN300016,TXN300017,TXN300018,TXN300019 2026-01-14 14:00:00 2026-01-14 14:03:00
     314   2026-01-02 18:0                    4 TXN300000,TXN300001,TXN300002,TXN300003 2026-01-02 18:00:00 2026-01-02 18:03:00
     345   2026-01-23 09:0                    4 TXN300028,TXN300029,TXN300030,TXN300031 2026-01-23 09:00:00 2026-01-23 09:03:00

Rows returned: 8
```

## Query 7: Daily GMV and Chargeback Count Trend

```
  txn_date  daily_gmv_inr  daily_chargeback_count  daily_txn_count
2026-01-01        11982.0                       0               18
2026-01-02        13430.0                       0               20
2026-01-03         4129.0                       0               21
2026-01-04        10688.0                       1               12
2026-01-05        22030.0                       1               20
2026-01-06         5036.0                       1               14
2026-01-07         2291.0                       1                9
2026-01-08         7135.0                       0               15
2026-01-09        14229.0                       0               21
2026-01-10         6384.0                       0               16
2026-01-11        28284.0                       1               16
2026-01-12        10322.0                       0               28
2026-01-13        14584.0                       2               16
2026-01-14        10031.0                       0               19
2026-01-15        18373.0                       0               27
2026-01-16        24386.0                       1               14
2026-01-17        12178.0                       0               22
2026-01-18        10981.0                       1               19
2026-01-19        12631.0                       1               19
2026-01-20        17833.0                       1               17
2026-01-21        15431.0                       2               19
2026-01-22        16830.0                       2               20
2026-01-23        20676.0                       4               24
2026-01-24        12674.0                       0               26
2026-01-25         9833.0                       2               17
2026-01-26         9282.0                       1               18
2026-01-27         6139.0                       1               11
2026-01-28        10685.0                       1               15
2026-01-29         9331.0                       3               19
2026-01-30        14785.0                       1               15

Rows returned: 30
```

