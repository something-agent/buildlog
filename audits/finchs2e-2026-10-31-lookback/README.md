# Lookback: were the Oct 28-30 QuantX402 payers new? (2026-10-31)

Requested by the operator (finchs2e) to settle "+2 vs +3 new payers" against the blind Day 17 read in `../finchs2e-2026-10-30/`.

- payTo: 0x2b79541911a436a83074eb3a38a920042524db96 (Base USDC)
- Payers checked: the 3 in-window payers from the Day 17 read.
- Window: Base blocks 52,011,600 to 53,177,999 (about 2026-10-01 00:00 UTC up to just before 2026-10-28 00:00 UTC).
- Method: `python3 lookback.py 52011600` (USDC Transfer logs with from = payer and to = payTo, public RPC, read-only).

Result: exactly one of the three paid this payTo before Oct 28.

| payer | earlier transfers to payTo | first earlier transfer (UTC) | USDC | tx |
|---|---|---|---|---|
| 0xc498…254a | 0 | - | - | - |
| 0xc9c7…1670 | 1 | 2026-10-14 12:02:47 | 0.01 | 0x0767f40b21d8ce54e7f2bfc82d0a3d82b0cbf338d08889089ecf4b2514afa589 |
| 0x3ed9…430e | 0 | - | - | - |

So, counted against everything since Oct 1, the window had 2 new payers and 1 returning payer (0xc9c7…1670, about 14.6 days apart).

Limits: Base USDC only; nothing before Oct 1 2026 was read; a payer could also have paid through another address, which this cannot see.
