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
const gridIdCuadriculaX = document.querySelector("#gridIdX");
const espaciadoXCuadriculaX = document.querySelector("#espaciadoX");
//  --- EJE Y
const gridIdCuadriculaY = document.querySelector("#gridIdY");
const espaciadoYCuadriculaY = document.querySelector("#espaciadoY");

// ----- NODES 
const buttonSave = document.querySelector(".grabar-container");

const buttonPlusCuadriculaX = document.querySelector(".btn_plus_cuadricula-x");
const buttonMinusCuadriculaX = document.querySelector(".btn_minus_cuadricula-x");

const buttonPlusCuadriculaY = document.querySelector(".btn_plus_cuadricula-y");
const buttonMinusCuadriculaY = document.querySelector(".btn_minus_cuadricula-y");

// FUNCTIONS
function guardarDatos() {
    console.log({
        analisiSismico: [capacidadPortante.value, factorUso.value, factorZona.value, factorSuelo.value]
    });
}

function agregarLineaX() {
    const campoAdcional = document.createElement("input");
    campoAdcional.classList.add("gridIdX");
    campoAdcional.setAttribute("type");
}

function eliminarLineaX() {

}

function agregarLineaY() {

}

function eliminarLineaY() {

}


buttonPlusCuadriculaX.addEventListener("click", agregarLineaX);
buttonMinusCuadriculaX.addEventListener("click", eliminarLineaX);

buttonPlusCuadriculaY.addEventListener("click", agregarLineaY);
buttonMinusCuadriculaY.addEventListener("click", eliminarLineaY);

buttonSave.addEventListener("click", guardarDatos)

console.log(capacidadPortante);