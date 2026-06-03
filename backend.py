FIGURAS = {
    "Triângulo": [
        (0.0,  1.5),
        (-1.3, -0.75),
        (1.3, -0.75),
    ],
    "Quadrado": [
        (-1.0,  1.0),
        ( 1.0,  1.0),
        ( 1.0, -1.0),
        (-1.0, -1.0),
    ],
    "Pentágono": [
        (0.0,  1.2),
        (1.14, 0.37),
        (0.69, -0.97),
        (-0.69, -0.97),
        (-1.14, 0.37),
    ],
}


def aplicar_matriz(mat, vertice):
    ax, ay = vertice
    rx = mat[0][0] * ax + mat[0][1] * ay
    ry = mat[1][0] * ax + mat[1][1] * ay
    return (round(rx, 6), round(ry, 6))

def transformar_figura(mat, vertices):
    return [aplicar_matriz(mat, v) for v in vertices]

def multiplicar_matriz_vetor(mat, vec):
    resultado = []
    passos = []
    for r in range(2):
        termos = []
        soma = 0.0
        for c in range(2):
            a = mat[r][c]
            x = vec[c]
            soma += a * x
            termos.append((a, x, c, round(soma, 6)))
        resultado.append(round(soma, 6))
        passos.append({
            "tipo": "linha",
            "linha": r,
            "termos": termos,
            "resultado": round(soma, 6),
        })
    passos.append({"tipo": "pronto", "resultado": resultado})
    return resultado, passos

def fmt(v):
    n = round(float(v), 4)
    return f"({n})" if n < 0 else str(n)
