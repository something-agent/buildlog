#!/usr/bin/env python3
"""Re-derive who paid an address in USDC on Base, from public RPC logs only (no keys, read-only).
usage: base_payers.py <payTo> <fromBlock> [toBlock|latest] [--broad]
Prints JSON: every inbound USDC Transfer (tx, block, UTC time, payer, amount) and per-payer stats:
transfers, total, first/last block, returned_after_1h (a later transfer more than 1,800 blocks (~1 h) after the first),
and with --broad the number of distinct payees the payer sent USDC to within +-10,000 blocks of its first payment
(20+ = broad payer / sweeper-like; this is a heuristic, not proof)."""
import json, sys, time, urllib.request, collections, datetime
RPC = "https://base-rpc.publicnode.com"
USDC = "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"
T = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
pad = lambda a: "0x" + a[2:].lower().rjust(64, "0")
def rpc(m, p):
    for k in range(8):
        try:
            r = urllib.request.Request(RPC, json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode(), {"Content-Type": "application/json", "User-Agent": "coldread-audit"})
            d = json.load(urllib.request.urlopen(r, timeout=40))
            if "error" in d: raise RuntimeError(d["error"])
            return d["result"]
        except Exception as e:
            err = e; time.sleep(2 + 2 * k)
    raise err
def logs(frm, to, topics, step=40000):
    out, b = [], frm
    while b <= to:
        e = min(b + step - 1, to); out += rpc("eth_getLogs", [{"address": USDC, "fromBlock": hex(b), "toBlock": hex(e), "topics": topics}]); b = e + 1; time.sleep(0.3)
    return out
pay_to = sys.argv[1].lower(); frm = int(sys.argv[2])
head = int(rpc("eth_blockNumber", []), 16)
to = head if len(sys.argv) < 4 or sys.argv[3] in ("latest", "--broad") else int(sys.argv[3])
inb = logs(frm, to, [T, None, pad(pay_to)])
ts = {}
def when(b):
    if b not in ts: ts[b] = int(rpc("eth_getBlockByNumber", [hex(b), False])["timestamp"], 16)
    return datetime.datetime.fromtimestamp(ts[b], datetime.timezone.utc).isoformat()
rows = [{"tx": l["transactionHash"], "block": int(l["blockNumber"], 16), "payer": "0x" + l["topics"][1][-40:], "usdc": int(l["data"], 16) / 1e6} for l in inb]
for r in rows: r["utc"] = when(r["block"])
per = collections.defaultdict(list)
for r in rows: per[r["payer"]].append(r)
payers = {}
for p, rs in per.items():
    bl = sorted(x["block"] for x in rs)
    payers[p] = {"transfers": len(rs), "usdc": round(sum(x["usdc"] for x in rs), 6), "first_block": bl[0], "last_block": bl[-1], "self": p == pay_to, "returned_after_1h": bl[-1] - bl[0] > 1800}
    if "--broad" in sys.argv:
        out = logs(max(bl[0] - 10000, 0), min(bl[0] + 10000, head), [T, pad(p)], step=20001)
        payers[p]["distinct_payees_pm10k"] = len({"0x" + l["topics"][2][-40:] for l in out})
print(json.dumps({"pay_to": pay_to, "chain": "base", "asset": USDC, "from_block": frm, "to_block": to, "rpc": RPC,
  "summary": {"transfers": len(rows), "usdc": round(sum(r["usdc"] for r in rows), 6), "distinct_payers": len(payers),
              "payers_2plus": sum(1 for v in payers.values() if v["transfers"] > 1), "returned_after_1h": sum(1 for v in payers.values() if v["returned_after_1h"])},
  "payers": payers, "transfers": sorted(rows, key=lambda r: r["block"])}, indent=1))
