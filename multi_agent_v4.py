"""Paper-only deterministic signal engine. No exchange order execution."""
from math import isfinite

def decide(*, trend, scalp, volume, book, pattern, news, age_seconds,
           notional, expected_move_bps, fee_bps, slippage_bps,
           open_positions, max_positions, drawdown_pct, target=1):
    votes = dict(trend=trend, scalp=scalp, volume=volume, book=book,
                 pattern=pattern, news=news)
    values = [age_seconds, notional, expected_move_bps, fee_bps,
              slippage_bps, drawdown_pct, target]
    valid = all(isinstance(x,(int,float)) and isfinite(x) and x>=0 for x in values)
    if not valid or any(v not in (-1,0,1) for v in votes.values()):
        return dict(signal="WAIT", reason="invalid data")
    net = notional*(expected_move_bps-2*(fee_bps+slippage_bps))/10000
    score = sum(votes.values())
    risk = (age_seconds<=5 and notional>0 and max_positions in (5,10,30)
            and 0<=open_positions<max_positions and drawdown_pct<2
            and 1<=target<=10 and net>=target)
    signal = "WAIT"
    if risk and trend==1 and score>=4:
        signal="LONG"
    elif risk and trend==-1 and score<=-4:
        signal="SHORT"
    return dict(signal=signal, agents=votes, risk=risk, score=score,
                estimated_net=round(net,4),
                regime={1:"bull",-1:"bear",0:"uncertain_or_range"}[trend],
                mode="PAPER", reason="consensus" if signal!="WAIT" else "risk or consensus filter")

if __name__=="__main__":
    sample=dict(trend=1,scalp=1,volume=1,book=1,pattern=0,news=0,
                age_seconds=1,notional=10000,expected_move_bps=15,
                fee_bps=4,slippage_bps=1,open_positions=0,max_positions=5,
                drawdown_pct=0)
    assert decide(**sample)["signal"]=="LONG"
    assert decide(**dict(sample,age_seconds=6))["signal"]=="WAIT"
    assert decide(**dict(sample,fee_bps=10))["signal"]=="WAIT"
    assert decide(**dict(sample,open_positions=5))["signal"]=="WAIT"
    assert decide(**dict(sample,drawdown_pct=2))["signal"]=="WAIT"
    assert decide(**dict(sample,trend=-1,scalp=-1,volume=-1,book=-1))["signal"]=="SHORT"
    print("6 smoke checks passed")
