#---------------------------
# Libraries importation
#---------------------------
import pandas as pd
import numpy as np
from alpaca_trade_api import REST
from datetime import datetime

#---------------------------
# API 
#---------------------------
API_KEY = "PKRXT5FDOY66J2QLADBCZM56UR"
API_SECRET = "AVUxxopGAbhtz4xUaz6dAFERNJWxmXhsQNfQqcow76Tj"
BASE_URL = "https://paper-api.alpaca.markets"
api = REST(API_KEY, API_SECRET, BASE_URL)


#---------------------------
# Def function
#---------------------------
def submit_whole_order(symbol, side, notional=1000):
    """
    Convert a notional amount into whole shares (int)
    and send a valid Alpaca order (compatible with shorting).
    """
    price = api.get_latest_trade(symbol).price
    qty = int(notional // price)

    if qty <= 0:
        print(f"[SKIP] qty for {symbol} would be 0 (price too high)")
        return None

    print(f"Submitting {side} order for {symbol} — qty {qty} @ ~{price} (notional {notional})")

    return api.submit_order(
        symbol=symbol,
        qty=qty,
        side=side,
        type="market",
        time_in_force="day"
    )

#---------------------------
# sym1, sym2, avg_range, std_range, upper_bound, lower_bound in results
#---------------------------
results = [
    ('HBAN', 'TFC', np.float64(0.9830744337125339), np.float64(0.03691857065950266), np.float64(1.0199930043720364), np.float64(0.9461558630530312)), 
    ('GS', 'MS', np.float64(1.5733629073979698), np.float64(0.033524158918637186), np.float64(1.606887066316607), np.float64(1.5398387484793326)), 
    ('MA', 'V', np.float64(0.4819913271965817), np.float64(0.02881133415805173), np.float64(0.5108026613546335), np.float64(0.45317999303853)), 
    ('MET', 'PRU', np.float64(0.2905207625112272), np.float64(0.02628865252031276), np.float64(0.31680941503154), np.float64(0.26423210999091445)), 
    ('FITB', 'USB', np.float64(0.09217660170557691), np.float64(0.02121942514683352), np.float64(0.11339602685241043), np.float64(0.0709571765587434)), 
    ('HD', 'LOW', np.float64(0.4726003468396616), np.float64(0.0184390456446125), np.float64(0.49103939248427414), np.float64(0.4541613011950491)), 
    ('MTB', 'PNC', np.float64(0.02245077128569019), np.float64(0.016698425985391136), np.float64(0.03914919727108133), np.float64(0.0057523453002990554))
]

#---------------------------
# Lauch Trade
#---------------------------
positions = api.list_positions()
current_positions = {p.symbol: p for p in positions}

for sym1, sym2, avg_range, std_range, upper_bound, lower_bound in results:
    print("--------------------------------")
    print(f"\nPair Trading for {sym1} and {sym2}\n")

    # Sécurité anti double-entrée si l'ordre précédent n'est pas encore exécuté
    open_orders = api.list_orders(status='open')
    if any(o.symbol in (sym1, sym2) for o in open_orders):
        print(f"Order still pending for {sym1}/{sym2}, skipping")
        continue


    # Gerer les erreurs de download
    try:
        current1 = api.get_latest_trade(sym1).price
        print(f"Tried to fetch prices for {sym1} : {current1}")
        current2 = api.get_latest_trade(sym2).price
        print(f"Tried to fetch prices for {sym2} : {current2}")
    except Exception as e:
        print(f"Error fetching prices for {sym1}/{sym2}: {e}")
        continue
    
    if current1 is None or current2 is None:
        print(f"⏸️ No data available for {sym1} or {sym2} — maybe market closed?")
        continue

    # Calculer le spread
    log1 = np.log(current1)
    log2 = np.log(current2)

    last_spread = log1 - log2
    print(f"last spread : {last_spread}")

    # Check les positions actuelles
    if sym1 in current_positions:
        qty1 = float(current_positions[sym1].qty)
    else:
        qty1 = 0.0

    if sym2 in current_positions:
        qty2 = float(current_positions[sym2].qty)
    else:
        qty2 = 0.0
    print(f"Nombre de position pour {sym1} : {qty1}")
    print(f"Nombre de position pour {sym2} : {qty2}")

    # Passer les ordres
    try:
        # Spread classique -> on vend les positions
        if upper_bound >= last_spread >= lower_bound:
            if qty1 != 0 or qty2 != 0:
                print(f"\n=> Closing position for {sym1}-{sym2} (spread normalized)\n")
                if qty1 != 0:
                    api.submit_order(
                        symbol=sym1,
                        qty=abs(int(qty1)),
                        side="buy" if qty1 < 0 else "sell",
                        type="market",
                        time_in_force="day"
                    )
                if qty2 != 0:
                    api.submit_order(
                        symbol=sym2,
                        qty=abs(int(qty2)),
                        side="buy" if qty2 < 0 else "sell",
                        type="market",
                        time_in_force="day"
                    )
                
                continue
            else :
                print(f"\n=> Spread Classique, aucune position a ajuster\n")
                continue
        
        # Check si la position est déjà en cours
        elif qty1 != 0 or qty2 != 0:
            print(f"\n=> Already traded for {sym1}/{sym2}\n")
            continue         

        # Spread trop large -> on parie sur convergence
        elif last_spread > upper_bound:
            if current1 > current2:
                print(f"\n=> {sym1} overvalued, selling {sym1}, buying {sym2}\n")
                submit_whole_order(sym1, "sell")
                submit_whole_order(sym2, "buy")
            else:
                print(f"\n=> {sym2} overvalued, selling {sym2}, buying {sym1}\n")
                submit_whole_order(sym1, "buy")
                submit_whole_order(sym2, "sell")
            continue

        # Spread trop faible -> on parie sur divergence
        elif last_spread < lower_bound:
            if current1 > current2:
                print(f"\n=> {sym1} undervalued, buying {sym1}, selling {sym2}\n")
                submit_whole_order(sym1, "buy")
                submit_whole_order(sym2, "sell")
            else:
                print(f"\n=> {sym2} undervalued, buying {sym2}, selling {sym1}\n")
                submit_whole_order(sym1, "sell")
                submit_whole_order(sym2, "buy")
            continue 

    # Check pour des Exception    
    except Exception as e:
        print(f"\n=> Error on pair {sym1}-{sym2}: {e}\n")

print("--------------------------------")
time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
print(f"End - {time}")