
let lote = [];
let seleccionados = [];
let totalDefectuosos = 0;
let revelado = false;

function iniciarLote() {
    // Determinar cantidad de defectuosos según probabilidad (60%, 30%, 10%)
    const rand = Math.random();
    if (rand < 0.6) totalDefectuosos = 0;
    else if (rand < 0.9) totalDefectuosos = 1;
    else totalDefectuosos = 2;

    lote = Array(20).fill('bueno');
    // Asignar defectuosos al azar
    let asignados = 0;
    while(asignados < totalDefectuosos) {
        let idx = Math.floor(Math.random() * 20);
        if(lote[idx] === 'bueno') {
            lote[idx] = 'malo';
            asignados++;
        }
    }
    seleccionados = [];
    revelado = false;
    dibujarLote();
    resetUI();
}

function dibujarLote() {
    const grid = document.getElementById('grid-componentes');
    grid.innerHTML = '';
    for(let i=0; i<20; i++) {
        const div = document.createElement('div');
        div.className = 'componente';
        if(seleccionados.includes(i)) div.classList.add('comp-muestra');
        
        let texto = (i+1) + '<br>';
        if(revelado || seleccionados.includes(i)) {
            if(lote[i] === 'bueno') {
                div.classList.add('comp-bueno');
                texto += 'B';
            } else {
                div.classList.add('comp-malo');
                texto += 'D';
            }
        } else {
            texto += '?';
        }
        div.innerHTML = texto;
        grid.appendChild(div);
    }
}

function extraerYProbar() {
    if(seleccionados.length > 0) return; // ya se extrajo
    while(seleccionados.length < 2) {
        let idx = Math.floor(Math.random() * 20);
        if(!seleccionados.includes(idx)) seleccionados.push(idx);
    }
    dibujarLote();
    
    // Contar defectuosos en la muestra
    let k = 0;
    if(lote[seleccionados[0]] === 'malo') k++;
    if(lote[seleccionados[1]] === 'malo') k++;

    // Llamar a Flask para hacer el cálculo
    fetch('/api/simulador/calcular', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ k: k })
    })
    .then(r => r.json())
    .then(data => {
        // Actualizar Tabla
        for(let i=0; i<3; i++) {
            document.getElementById(`cond-${i}`).innerText = data.condicionales[i].toFixed(4);
            let post = data.posteriores[i];
            document.getElementById(`post-${i}`).innerText = post.toFixed(4);
            
            // Actualizar barras
            let bar = document.getElementById(`bar-${i}`);
            let percent = (post * 100).toFixed(2);
            bar.style.width = percent + '%';
            bar.innerText = percent + '%';
        }
        // Actualizar texto
        document.getElementById('consola-pasos').value = data.paso_a_paso;
    });
}

function revelarLote() {
    revelado = true;
    dibujarLote();
}

function resetUI() {
    for(let i=0; i<3; i++) {
        document.getElementById(`cond-${i}`).innerText = "Sin muestra";
        document.getElementById(`post-${i}`).innerText = "Sin muestra";
        let bar = document.getElementById(`bar-${i}`);
        let initProbs = [60, 30, 10];
        bar.style.width = initProbs[i] + '%';
        bar.innerText = initProbs[i].toFixed(2) + '%';
    }
    document.getElementById('consola-pasos').value = "Extrae y prueba dos componentes para aplicar Bayes.\nCada nuevo lote inicia un experimento independiente.";
}

document.addEventListener('DOMContentLoaded', iniciarLote);
