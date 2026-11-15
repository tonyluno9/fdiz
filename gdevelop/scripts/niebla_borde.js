// El sprite puede pasar por delante del borde, aunque la sala siga tapada.
const nieblas = runtimeScene.getLayer("NieblaSalas").isVisible()
  ? runtimeScene.getObjects("Niebla").filter(niebla => !niebla.isHidden() && niebla.getOpacity() > 0)
  : [];

for (const superviviente of runtimeScene.getObjects("Sup")) {
  const piesX = superviviente.getX();
  const piesY = superviviente.getY();
  const izquierda = superviviente.getDrawableX();
  const arriba = superviviente.getDrawableY();
  const derecha = izquierda + superviviente.getWidth();
  const abajo = arriba + superviviente.getHeight();
  let cruzaBorde = false;

  for (const niebla of nieblas) {
    const x = niebla.getX();
    const y = niebla.getY();
    const finX = x + niebla.getWidth();
    const finY = y + niebla.getHeight();
    if (x <= piesX && piesX < finX && y <= piesY && piesY < finY) {
      cruzaBorde = false;
      break;
    }
    if (izquierda < finX && x < derecha && arriba < finY && y < abajo) {
      cruzaBorde = true;
    }
  }

  const capa = cruzaBorde ? "SupervivientesBorde" : "Juego";
  if (superviviente.getLayer() !== capa) {
    superviviente.setLayer(capa);
  }
}
