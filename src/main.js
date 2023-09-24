//  VALORES 
// ------ ANALISIS SISMICO - VALORES
const capacidadPortante = document.querySelector("#capacidadPortante");
const factorUso = document.querySelector("#factorUso");
const factorZona = document.querySelector("#factorZona");
const factorSuelo = document.querySelector("#factorSuelo");

//  --------- DIMENSIONES DE TERRENO - VALORES
const largoY = document.querySelector("#largoY");
const anchoX = document.querySelector("#anchoX");

// ---------- DATOS DE CUADRICULA - VALORES
//  --- EJE X
const gridIdCuadriculaX = document.querySelectorAll(".gridIdX");
const espaciadoXCuadriculaX = document.querySelectorAll(".espaciadoX");
//  --- EJE Y
const gridIdCuadriculaY = document.querySelectorAll(".gridIdY");
const espaciadoYCuadriculaY = document.querySelectorAll(".espaciadoY");

// ----- BUTTONS 
const buttonPlusCuadriculaX = document.querySelector(".btn_plus_cuadricula-x");
const buttonMinusCuadriculaX = document.querySelector(".btn_minus_cuadricula-x");

const buttonPlusCuadriculaY = document.querySelector(".btn_plus_cuadricula-y");
const buttonMinusCuadriculaY = document.querySelector(".btn_minus_cuadricula-y");

const buttonSave = document.querySelector(".grabar-container");

// -----NODES
const contanierIdX = document.querySelector(".cuadricula_id-x");
const contanierEspaciadoX = document.querySelector(".cuadricula_espaciado-x");

const contanierIdY = document.querySelector(".cuadricula_id-y");
const contanierEspaciadoY = document.querySelector(".cuadricula_espaciado-y");

// FUNCTIONS
function guardarDatos() {
    console.log({
        analisiSismico: [capacidadPortante.value, factorUso.value, factorZona.value, factorSuelo.value]
    });
}

function agregarLineaX() {
    const campoAdcionalId = document.createElement("input");
    campoAdcionalId.classList.add("gridIdX");
    campoAdcionalId.setAttribute("type", "text");

    const campoAdcionalEspaciado = document.createElement("input");
    campoAdcionalEspaciado.classList.add("espaciadoX");
    campoAdcionalEspaciado.setAttribute("type", "number");

    contanierIdX.appendChild(campoAdcionalId);
    contanierEspaciadoX.appendChild(campoAdcionalEspaciado)
}

function eliminarLineaX() {
    console.log("here");
    const gridX = Array.from(gridIdCuadriculaX);
    console.log(gridX);
    gridX.pop();
    const cuadriculaX = Array.from(espaciadoXCuadriculaX);
    cuadriculaX.pop();

    const gridY = Array.from(gridIdCuadriculaY);
    gridY.pop();
    const cuadriculaY = Array.from(espaciadoYCuadriculaY);
    cuadriculaY.pop();
}

function agregarLineaY() {
    const campoAdcionalId = document.createElement("input");
    campoAdcionalId.classList.add("gridIdY");
    campoAdcionalId.setAttribute("type", "text");

    const campoAdcionalEspaciado = document.createElement("input");
    campoAdcionalEspaciado.classList.add("espaciadoY");
    campoAdcionalEspaciado.setAttribute("type", "number");

    contanierIdY.appendChild(campoAdcionalId);
    contanierEspaciadoY.appendChild(campoAdcionalEspaciado)


}

function eliminarLineaY() {

}


buttonPlusCuadriculaX.addEventListener("click", agregarLineaX);
buttonMinusCuadriculaX.addEventListener("click", eliminarLineaX);

buttonPlusCuadriculaY.addEventListener("click", agregarLineaY);
buttonMinusCuadriculaY.addEventListener("click", eliminarLineaY);

buttonSave.addEventListener("click", guardarDatos)

console.log(capacidadPortante);
var trace1 = {
    x: [],
    y: [],
    type: 'scatter'
  };
  
  var trace2 = {
    x: [],
    y: [],
    type: 'scatter'
  };
  
  var data = [trace1, trace2];
  
  var layout = {
    xaxis: {
      type: 'log',
      autorange: true
    },
    yaxis: {
      type: 'log',
      autorange: true
    }
  };
  
  Plotly.newPlot('myDiv', data, layout);