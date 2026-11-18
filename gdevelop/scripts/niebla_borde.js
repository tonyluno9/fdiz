// El sprite puede pasar por delante del borde, aunque la sala siga tapada.
const nieblas = runtimeScene.getLayer("NieblaSalas").isVisible()
  ? runtimeScene.getObjects("Niebla").filter(niebla => !niebla.isHidden() && niebla.getOpacity() > 0)
  : [];

const zonasTapadas = nieblas.map(niebla => {
  const x = niebla.getX();
  const y = niebla.getY();
  return { x, y, finX: x + niebla.getWidth(), finY: y + niebla.getHeight() };
});
const nombres = ["Sup", "Profe", "ZNormal", "ZCorredor", "ZGriton", "ZGordo", "ZConserje", "ZCurado", "ZJoel", "ZJustino", "ZCanepa"];

for (const personaje of nombres.flatMap(nombre => runtimeScene.getObjects(nombre))) {
  const piesX = personaje.getX();
  const piesY = personaje.getY();
  const izquierda = personaje.getDrawableX();
  const arriba = personaje.getDrawableY();
  const derecha = izquierda + personaje.getWidth();
  const abajo = arriba + personaje.getHeight();
  let cruzaBorde = false;

  for (const { x, y, finX, finY } of zonasTapadas) {
    if (x <= piesX && piesX < finX && y <= piesY && piesY < finY) {
      cruzaBorde = false;
      break;
    }
    if (izquierda < finX && x < derecha && arriba < finY && y < abajo) {
      cruzaBorde = true;
    }
  }

  const capa = cruzaBorde ? "SupervivientesBorde" : "Juego";
  if (personaje.getLayer() !== capa) {
    personaje.setLayer(capa);
  }
}
