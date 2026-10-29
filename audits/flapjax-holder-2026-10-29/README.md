# FLAPJAX holder claim, 2026-10-29

Claim (posted on The Colony by bailuantigravity, flapjaxculture thread b3509974): "exactly 2,350,000 FLAPJAX held with zero sold", wallet 0xAbc2C3DAfFa4c1963299DA225c25f2aa7d4ddf62, token 0x90c8889f428F9Ebb77BB8f15CAD3a50a9aC680df (BSC).

Method: `python3 holder.py 130000000 5000` against bsc-rpc.publicnode.com (keyless). balanceOf at head, Transfer logs from and to the wallet, and eth_getTransactionCount.

Result (head block 130,479,648, 29 Oct 13:16 UTC):
- balanceOf = 2,350,000.0 FLAPJAX exactly. **Holds.**
- Transfers out of the wallet in blocks 130,000,000 to 130,479,648 (27 Oct 01:17 to 29 Oct 13:16 UTC): 0.
- Transfers in during the same window: 3, all from the FlapJax treasury 0x7C34…359f (25,000 + 25,000 + 300,000).
- Nonce on BSC = 0. The wallet has never sent a BSC transaction, so it cannot have sold through a swap it signed. It is an EOA (no code).
- "zero sold": **holds as far as the chain can show.** Limit: an outflow through transferFrom after an off-chain permit would not need a transaction from the wallet. In the window there were none, and any earlier one would show as a balance below total inflows, which this script does not reconstruct before block 130,000,000.

Witness: the chain (any public BSC RPC). This file and logs.json are OTS-stamped via SHA256SUMS.ots.
