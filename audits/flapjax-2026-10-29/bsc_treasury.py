#!/usr/bin/env python3
"""Re-derive FlapJax treasury token flows on BSC from public RPC only (read-only, no keys).
usage: bsc_treasury.py [fromBlock=130000000] [toBlock=130407620]
Writes treasury_flows.json: owner() of the token, treasury balance at toBlock, every FLAPJAX Transfer out of and
into the treasury in the window (tx, block, COT time, counterparty, amount, whether the counterparty is the pool,
and the counterparty's code type), plus per-COT-day totals. publicnode serves ~3.5 days of logs without an archive token."""
import json, sys, time, urllib.request, datetime, collections
RPC = "https://bsc-rpc.publicnode.com"
TOKEN = "0x90c8889f428f9ebb77bb8f15cad3a50a9ac680df"      # FLAPJAX (BEP-20, 18 decimals)
TREASURY = "0x7c34e9e21ee28a49ff0b84b61774119e6633359f"   # as named in FlapJax's own task posts
POOL = "0xca93ec685b8623688e6b236f9068034b298c2150"       # PancakeSwap V3 FLAPJAX/WBNB, as named by FlapJax
T = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
pad = lambda a: "0x" + a[2:].lower().rjust(64, "0")
COT = datetime.timezone(datetime.timedelta(hours=-5))
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
frm = int(sys.argv[1]) if len(sys.argv) > 1 else 130000000
to = int(sys.argv[2]) if len(sys.argv) > 2 else 130407620
def logs(topics):
    out, b = [], frm
    while b <= to:
        e = min(b + 4999, to); out += rpc("eth_getLogs", [{"address": TOKEN, "fromBlock": hex(b), "toBlock": hex(e), "topics": topics}]); b = e + 1; time.sleep(0.15)
    return out
ts, code = {}, {}
def when(b):
    if b not in ts: ts[b] = int(rpc("eth_getBlockByNumber", [hex(b), False])["timestamp"], 16)
    return datetime.datetime.fromtimestamp(ts[b], COT).isoformat()
def kind(a):
    if a not in code:
        c = rpc("eth_getCode", [a, "latest"])
        code[a] = "eoa" if c == "0x" else ("eip7702_delegated_eoa" if c.startswith("0xef0100") else "contract")
    return code[a]
rows = []
for direction, topics in (("out", [T, pad(TREASURY)]), ("in", [T, None, pad(TREASURY)])):
    for l in logs(topics):
        b = int(l["blockNumber"], 16); cp = "0x" + l["topics"][2 if direction == "out" else 1][-40:]
        rows.append({"direction": direction, "tx": l["transactionHash"], "block": b, "time_cot": when(b), "counterparty": cp, "counterparty_type": kind(cp), "is_pool": cp == POOL, "amount": int(l["data"], 16) / 1e18})
rows.sort(key=lambda r: (r["block"], r["tx"]))
days = collections.defaultdict(lambda: {"out_transfers": 0, "out_amount": 0.0, "out_recipients": set(), "in_transfers": 0, "in_amount": 0.0})
for r in rows:
    d = days[r["time_cot"][:10]]
    if r["direction"] == "out": d["out_transfers"] += 1; d["out_amount"] += r["amount"]; d["out_recipients"].add(r["counterparty"])
    else: d["in_transfers"] += 1; d["in_amount"] += r["amount"]
res = {"rpc": RPC, "token": TOKEN, "treasury": TREASURY, "pool": POOL, "from_block": frm, "to_block": to,
       "from_time_cot": when(frm), "to_time_cot": when(to),
       "owner_at_to_block": rpc("eth_call", [{"to": TOKEN, "data": "0x8da5cb5b"}, hex(to)]),
       "treasury_balance_at_to_block": int(rpc("eth_call", [{"to": TOKEN, "data": "0x70a08231" + pad(TREASURY)[2:]}, hex(to)]), 16) / 1e18,
       "treasury_code_type": kind(TREASURY),
       "by_cot_day": {k: {**v, "out_recipients": len(v["out_recipients"])} for k, v in sorted(days.items())},
       "outflows_to_pool": sum(1 for r in rows if r["direction"] == "out" and r["is_pool"]),
       "outflow_recipient_types": dict(collections.Counter(r["counterparty_type"] for r in rows if r["direction"] == "out")),
       "transfers": rows}
json.dump(res, open("treasury_flows.json", "w"), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != "transfers"}, indent=1))
