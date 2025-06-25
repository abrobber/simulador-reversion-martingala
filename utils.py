def calcular_rsi(colores, periodo=6):
    import numpy as np
    delta = [1 if colores[i] != colores[i-1] else -1 for i in range(1, len(colores))]
    delta = [0] * (len(colores) - len(delta)) + delta
    rsi = []
    for i in range(len(delta)):
        if i < periodo:
            rsi.append(50)
        else:
            sub = delta[i-periodo+1:i+1]
            gains = sum(d for d in sub if d > 0)
            losses = abs(sum(d for d in sub if d < 0))
            rs = gains / losses if losses != 0 else 1
            rsi.append(100 - (100 / (1 + rs)))
    return rsi
