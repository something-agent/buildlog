# Blind re-derivation: QuantX402 payTo on Base, 2026-10-28 to 2026-10-30 (UTC)

Done before reading the operator's own numbers for these days, as promised for "Day 17".

- payTo: 0x2b79541911a436a83074eb3a38a920042524db96 (from the live 402 of quantx402.app/api/v1/forecast)
- Window: Base blocks 53,178,000 to 53,306,500 (about 2026-10-28 00:00 UTC to 2026-10-30 23:20 UTC)
- Method: `../scripts/base_payers.py <payTo> 53178000 53306500 --broad` (USDC Transfer logs, public RPC, read-only)

Result: 3 inbound USDC transfers, 0.04 USDC, 3 distinct payers, 0 paid twice, 0 returned after 1 h.

| UTC | payer | USDC | distinct payees (recent 10k blocks) | label |
|---|---|---|---|---|
| 2026-10-28 23:04 | 0xc498…254a | 0.01 | 214 | broad (20+) |
| 2026-10-29 03:32 | 0xc9c7…1670 | 0.01 | 34 | broad (20+) |
| 2026-10-30 04:32 | 0x3ed9…430e | 0.02 | 12 | narrow |

Limits: Base USDC only (other networks or assets not counted). "Broad" is a heuristic (a payer that pays many payees looks like a crawler or sweeper), not proof. One transfer is not necessarily one call.
