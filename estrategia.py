def simular_sesion(df, payout, stake_pct, martingala, ciclos_max, tp_pct, sl_pct, usar_rsi):
    saldo = 100
    historial = []
    entradas = 0
    aciertos = 0
    ciclos_totales = []
    saldo_max = saldo
    saldo_min = saldo
    entradas_idx = []  # ← nuevo: guardar posiciones reales de entrada
    entradas_filtradas_idx = []
    entradas_filtradas_por_rsi = 0



    for i in range(2, len(df) - ciclos_max):  # aseguramos que no salimos del índice
        if df['color'][i-2] == df['color'][i-1] and df['color'][i] != df['color'][i-1]:
            if usar_rsi and not (40 <= df['RSI'][i] <= 60):
                entradas_filtradas_por_rsi += 1
                entradas_filtradas_idx.append(i)
                continue
    
            entradas += 1
            entradas_idx.append(i)
    
            prediccion = 'verde' if df['color'][i-1] == 'roja' else 'roja'
            ciclo = 0
            apuesta = saldo * stake_pct
            acierto = False
    
            while ciclo < ciclos_max:
                vela_idx = i + ciclo
                if vela_idx >= len(df):
                    break
    
                saldo -= apuesta
                real = df['color'][vela_idx]
                acierto = prediccion == real
    
                if acierto:
                    ganancia = apuesta * payout
                    #saldo -= apuesta
                    saldo += apuesta + (apuesta * payout)  # Reintegra lo apostado + ganancia
                    aciertos += 1
                    break
                else:
                    apuesta *= martingala
                    ciclo += 1
    
            if not acierto:
                # No se acierta en ningún ciclo
                aciertos += 0  # explícito
                ganancia = 0  # ya se descontó todo
    
            ciclos_totales.append(ciclo + 1 if acierto else ciclo)
            saldo_max = max(saldo_max, saldo)
            saldo_min = min(saldo_min, saldo)
            historial.append(saldo)
    
            if saldo >= 100 * (1 + tp_pct) or saldo <= 100 * (1 - sl_pct):
                break



    return {
        'entradas': entradas,
        'aciertos': aciertos,
        'prom_ciclos': sum(ciclos_totales)/len(ciclos_totales) if ciclos_totales else 0,
        'saldo_final': saldo,
        'drawdown_max': (saldo_max - saldo_min)/saldo_max * 100,
        'historial': historial,
        'entradas_idx': entradas_idx,  # ← nuevo: devuelve los índices
        'entradas_filtradas_idx': entradas_filtradas_idx,
        'entradas_filtradas_rsi': entradas_filtradas_por_rsi,
        'ciclos_por_entrada': ciclos_totales
    }
