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



    for i in range(2, len(df)):
        if df['color'][i-2] == df['color'][i-1] and df['color'][i] != df['color'][i-1]:
            if usar_rsi and not (40 <= df['RSI'][i] <= 60):
                entradas_filtradas_por_rsi += 1
                entradas_filtradas_idx.append(i)  # Guardamos el índice de esta oportunidad ignorada
                continue


            entradas += 1
            entradas_idx.append(i)  # ← nuevo: guardar punto de entrada real
            ciclo = 0
            apuesta = saldo * stake_pct
            real = df['color'][i]
            prediccion = 'verde' if df['color'][i-1] == 'roja' else 'roja'
            acierto = prediccion == real

            while not acierto and ciclo < ciclos_max - 1:
                saldo -= apuesta
                apuesta *= martingala
                ciclo += 1
                acierto = prediccion == real

            ganancia = apuesta * payout if acierto else -apuesta
            saldo += ganancia
            aciertos += 1 if acierto else 0
            ciclos_totales.append(ciclo + 1)
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
        'entradas_filtradas_idx': entradas_filtradas_idx
    }
