from flask import Flask, render_template, request, jsonify
import math

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/bayes', methods=['GET', 'POST'])
def bayes():
    resultado = None
    if request.method == 'POST':
        try:
            p1 = float(request.form.get('p1', 30)) / 100
            p2 = float(request.form.get('p2', 20)) / 100
            p3 = float(request.form.get('p3', 50)) / 100
            dp1 = float(request.form.get('dp1', 1)) / 100
            dp2 = float(request.form.get('dp2', 3)) / 100
            dp3 = float(request.form.get('dp3', 2)) / 100

            # Teorema de Bayes
            p_d = (p1 * dp1) + (p2 * dp2) + (p3 * dp3)
            
            post = [0, 0, 0]
            if p_d > 0:
                post[0] = (p1 * dp1) / p_d
                post[1] = (p2 * dp2) / p_d
                post[2] = (p3 * dp3) / p_d
            
            responsable = post.index(max(post)) + 1

            resultado = {
                'p_d': round(p_d * 100, 4),
                'p1': p1*100, 'p2': p2*100, 'p3': p3*100,
                'dp1': dp1*100, 'dp2': dp2*100, 'dp3': dp3*100,
                'post_p1': round(post[0] * 100, 2),
                'post_p2': round(post[1] * 100, 2),
                'post_p3': round(post[2] * 100, 2),
                'responsable': responsable
            }
        except Exception as e:
            resultado = {'error': str(e)}

    return render_template('bayes.html', resultado=resultado)

@app.route('/combinatoria', methods=['GET', 'POST'])
def combinatoria():
    resultado = None
    if request.method == 'POST':
        try:
            varones = int(request.form.get('varones', 2))
            chicas = int(request.form.get('chicas', 3))
            
            total_personas = varones + chicas
            
            # 1. Total de formas posibles sin restricciones (N!)
            total_permutaciones = math.factorial(total_personas)
            
            # 2. Casos prohibidos: Las 3 chicas juntas formando un solo bloque
            # Tratamos al bloque de chicas como 1 elemento + los varones
            elementos_con_bloque = varones + 1 
            formas_bloque_interno = math.factorial(chicas)
            formas_ordenar_bloque = math.factorial(elementos_con_bloque)
            
            casos_prohibidos = formas_ordenar_bloque * formas_bloque_interno
            
            # 3. Casos deseados (Total - Prohibidos)
            total = total_permutaciones - casos_prohibidos

            resultado = {
                'chicas': chicas,
                'varones': varones,
                'total_permutaciones': total_permutaciones,
                'casos_prohibidos': casos_prohibidos,
                'total': total
            }
        except Exception as e:
            resultado = {'error': str(e)}

    return render_template('combinatoria.html', resultado=resultado)

@app.route('/simulador')
def simulador():
    return render_template('simulador.html')

@app.route('/api/simulador/calcular', methods=['POST'])
def calcular_simulador():
    data = request.json
    k = data.get('k', 0) # numero de defectuosos en la muestra
    
    # Probabilidades a priori P(D=d)
    p_d0 = 0.60
    p_d1 = 0.30
    p_d2 = 0.10

    # Lote total N=20, Muestra n=2
    # Combinaciones totales C(20,2) = 190
    c20_2 = 190

    # P(K=k | D=d) - Probabilidades condicionales usando distribucion hipergeometrica
    # D=0
    pk_d0 = 1.0 if k == 0 else 0.0
    
    # D=1
    if k == 0:
        pk_d1 = (1 * 171) / 190 # C(1,0)*C(19,2)/C(20,2)
    elif k == 1:
        pk_d1 = (1 * 19) / 190  # C(1,1)*C(19,1)/C(20,2)
    else:
        pk_d1 = 0.0

    # D=2
    if k == 0:
        pk_d2 = (1 * 153) / 190 # C(2,0)*C(18,2)/C(20,2)
    elif k == 1:
        pk_d2 = (2 * 18) / 190  # C(2,1)*C(18,1)/C(20,2)
    elif k == 2:
        pk_d2 = (1 * 1) / 190   # C(2,2)*C(18,0)/C(20,2)
    else:
        pk_d2 = 0.0

    # Probabilidad Total P(K=k)
    p_k = (pk_d0 * p_d0) + (pk_d1 * p_d1) + (pk_d2 * p_d2)

    # Probabilidades a posteriori P(D=d | K=k) - Teorema de Bayes
    if p_k > 0:
        post_d0 = (pk_d0 * p_d0) / p_k
        post_d1 = (pk_d1 * p_d1) / p_k
        post_d2 = (pk_d2 * p_d2) / p_k
    else:
        post_d0 = post_d1 = post_d2 = 0.0

    # Texto paso a paso
    paso_a_paso = f"D = número de defectuosos en el lote.\nK = número de defectuosos en la muestra (K={k}).\n\n"
    paso_a_paso += "Probabilidades iniciales:\nP(D=0)=0.60; P(D=1)=0.30; P(D=2)=0.10\n\n"
    paso_a_paso += "Combinaciones C(n,r) = n! / (r! (n-r)!)\nMuestras posibles C(20,2) = 190.\n\n"
    paso_a_paso += f"P(K={k}|D=0) = {pk_d0:.4f}\n"
    paso_a_paso += f"P(K={k}|D=1) = {pk_d1:.4f}\n"
    paso_a_paso += f"P(K={k}|D=2) = {pk_d2:.4f}\n\n"
    paso_a_paso += f"P(K={k}) prob total = {p_k:.4f}\n\n"
    paso_a_paso += f"P(D=0|K={k}) = {post_d0:.4f} ({post_d0*100:.2f}%)\n"
    paso_a_paso += f"P(D=1|K={k}) = {post_d1:.4f} ({post_d1*100:.2f}%)\n"
    paso_a_paso += f"P(D=2|K={k}) = {post_d2:.4f} ({post_d2*100:.2f}%)\n"

    return jsonify({
        "condicionales": [round(pk_d0, 4), round(pk_d1, 4), round(pk_d2, 4)],
        "posteriores": [round(post_d0, 4), round(post_d1, 4), round(post_d2, 4)],
        "paso_a_paso": paso_a_paso
    })

#if __name__ == '__main__':
 #   app.run(debug=True)

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)