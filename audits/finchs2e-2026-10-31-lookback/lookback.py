"""Lookback: did any of the 3 in-window payers (Oct 28-30 audit) send Base USDC to the QuantX402 payTo BEFORE
Oct 28 00:00 UTC (block 53,178,000)? Read-only: USDC Transfer logs filtered by from=payer, to=payTo. Public RPC."""
import json, sys, time, urllib.request as u
RPC="https://base-rpc.publicnode.com"; USDC="0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
PAYTO="0x2b79541911a436a83074eb3a38a920042524db96"
PAYERS=["0xc4985c1ecaf9d7cc91727e32cf28bba1e002254a","0xc9c7b38c0942914fc8ea12063bc92dcd3b581670","0x3ed93a7b87832f04a91137cacb273d39295e430e"]
START,END,STEP=int(sys.argv[1]),53177999,50000
pad=lambda a:"0x"+a[2:].rjust(64,"0")
def rpc(m,p):
    for i in range(5):
        try:
            r=u.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),{"Content-Type":"application/json","User-Agent":"coldread-audit/1"})
            d=json.load(u.urlopen(r,timeout=60))
            if "error" in d: raise RuntimeError(d["error"])
            return d["result"]
        except Exception as e: time.sleep(2*(i+1)); err=e
    raise err
hits=[]; b=START
while b<=END:
    e=min(b+STEP-1,END)
    for l in rpc("eth_getLogs",[{"address":USDC,"fromBlock":hex(b),"toBlock":hex(e),"topics":[TRANSFER,[pad(p) for p in PAYERS],pad(PAYTO)]}]):
        blk=int(l["blockNumber"],16); ts=int(rpc("eth_getBlockByNumber",[hex(blk),False])["timestamp"],16)
        hits.append({"payer":"0x"+l["topics"][1][-40:],"block":blk,"utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(ts)),"usdc":int(l["data"],16)/1e6,"tx":l["transactionHash"]})
    b=e+1
out={"pay_to":PAYTO,"payers":PAYERS,"from_block":START,"to_block":END,"rpc":RPC,"hits":hits,
     "by_payer":{p:sum(1 for h in hits if h["payer"]==p) for p in PAYERS}}
print(json.dumps(out,indent=1))
