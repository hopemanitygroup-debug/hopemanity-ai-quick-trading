"""Read-only Binance public market data. No credentials or orders."""
import json
import time
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from multi_agent_v4 import decide

def get(path, **params):
    for attempt in range(3):
        try:
            with urlopen("https://api.binance.com/api/v3/"+path+"?"+urlencode(params), timeout=5) as r:
                return json.load(r)
        except HTTPError as exc:
            if exc.code not in (500, 502, 503, 504) or attempt == 2:
                raise
        except (URLError, TimeoutError):
            if attempt == 2:
                raise
        time.sleep(2**attempt)

def sign(x):
    return int(x>0)-int(x<0)

def snapshot(fee_bps, slippage_bps, notional=10000, max_positions=5):
    start=time.monotonic()
    try:
        candles=get("klines",symbol="BTCUSDT",interval="1m",limit=61)[:-1]
        closes=[float(c[4]) for c in candles]
        depth=get("depth",symbol="BTCUSDT",limit=20)
        bids=sum(float(q) for p,q in depth["bids"])
        asks=sum(float(q) for p,q in depth["asks"])
        trades=get("aggTrades",symbol="BTCUSDT",limit=100)
        recent=[t for t in trades if t["T"]>=trades[-1]["T"]-5000]
        flow=sum(float(t["q"])*(-1 if t["m"] else 1) for t in recent)
        trend=sign(sum(closes[-10:])/10-sum(closes[-50:])/50)
        scalp=sign(float(recent[-1]["p"])-float(recent[0]["p"]))
        pattern=1 if closes[-1]>max(closes[-11:-1]) else -1 if closes[-1]<min(closes[-11:-1]) else 0
        # Historical range proxy, not a calibrated forecast.
        move=sum(abs(b-a)/a*10000 for a,b in zip(closes[-11:-1],closes[-10:]))/10
        result=decide(trend=trend,scalp=scalp,volume=sign(flow),book=sign(bids-asks),
            pattern=pattern,news=0,age_seconds=max(time.monotonic()-start,time.time()-trades[-1]["T"]/1000),
            notional=notional,expected_move_bps=move,fee_bps=fee_bps,slippage_bps=slippage_bps,
            open_positions=0,max_positions=max_positions,drawdown_pct=0)
        result.update(price=float(trades[-1]["p"]),news_status="unavailable",mode="SIGNAL_ONLY")
        return result
    except HTTPError as exc:
        return dict(signal="WAIT",mode="SIGNAL_ONLY",reason=str(exc),http_status=exc.code,feed_status="RESTRICTED" if exc.code==451 else "UNAVAILABLE")
    except Exception as exc:
        return dict(signal="WAIT",mode="SIGNAL_ONLY",reason=str(exc),feed_status="UNAVAILABLE")

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--fee-bps",type=float,required=True)
    p.add_argument("--slippage-bps",type=float,required=True)
    args=p.parse_args()
    print(json.dumps(snapshot(args.fee_bps,args.slippage_bps),indent=2))
