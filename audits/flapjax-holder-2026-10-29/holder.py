import json,urllib.request,sys,time
R=["https://bsc-rpc.publicnode.com","https://bsc-rpc.publicnode.com"]
def rpc(m,p,i=0):
    for k in range(6):
        try:
            r=urllib.request.Request(R[(i+k)%2],json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),{"Content-Type":"application/json","User-Agent":"curl/8"})
            d=json.load(urllib.request.urlopen(r,timeout=30))
            if "error" in d: raise Exception(d["error"])
            return d["result"]
        except Exception as e:
            err=e; time.sleep(3)
    raise err
TOK="0x90c8889f428F9Ebb77BB8f15CAD3a50a9aC680df"; TRE="0xAbc2C3DAfFa4c1963299DA225c25f2aa7d4ddf62"; POOL=""
T="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
pad=lambda a:"0x"+a[2:].lower().rjust(64,"0")
head=int(rpc("eth_blockNumber",[]),16); print("head",head)
print("owner()",rpc("eth_call",[{"to":TOK,"data":"0x8da5cb5b"},"latest"]))
print("treasury bal",int(rpc("eth_call",[{"to":TOK,"data":"0x70a08231"+pad(TRE)[2:]},"latest"]),16)/1e18)
print("treasury code len",len(rpc("eth_getCode",[TRE,"latest"])))
days=float(sys.argv[1]) if len(sys.argv)>1 else 1
start=int(sys.argv[1]); step=int(sys.argv[2]) if len(sys.argv)>2 else 5000
out=[];inn=[]
b=start
while b<=head:
    e=min(b+step-1,head)
    out+=rpc("eth_getLogs",[{"address":TOK,"fromBlock":hex(b),"toBlock":hex(e),"topics":[T,pad(TRE)]}])
    inn+=rpc("eth_getLogs",[{"address":TOK,"fromBlock":hex(b),"toBlock":hex(e),"topics":[T,None,pad(TRE)]}])
    b=e+1; time.sleep(0.15)
json.dump({"head":head,"start":start,"out":out,"in":inn},open(f"bai_logs.json","w"))
print("window",start,head,"out",len(out),"in",len(inn))
