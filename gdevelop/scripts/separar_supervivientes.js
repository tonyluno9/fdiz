// Los pies conservan su máscara del mapa. Entre supervivientes de pie se deja
// más espacio en perspectiva para que sus cuerpos no se apilen en una fila.
if (runtimeScene.getGame().getVariables().get("NetRol").getAsNumber() === 2) return;

const jugadores = runtimeScene.getObjects("Sup").filter(
  jugador => jugador.getVariables().get("Estado").getAsString() === "normal"
);
const control = jugador => jugador.getVariables().get("Control").getAsNumber();
const ancho = 46;
const fondo = 86;
let obstaculos;

function desplazar(jugador, dx, dy) {
  if (control(jugador) === -2) return false;
  if (!obstaculos) {
    obstaculos = ["Muro", "ChoqueMueble", "Puerta", "Objetivo", "Contenedor"]
      .flatMap(nombre => runtimeScene.getObjects(nombre))
      .map(objeto => ({ objeto, caja: objeto.getAABB() }));
  }
  const x = jugador.getX();
  const y = jugador.getY();
  jugador.setPosition(x + dx, y + dy);
  const caja = jugador.getAABB();
  const bloqueado = obstaculos.some(({ objeto, caja: limite }) =>
    caja.min[0] < limite.max[0] && limite.min[0] < caja.max[0] &&
    caja.min[1] < limite.max[1] && limite.min[1] < caja.max[1] &&
    gdjs.RuntimeObject.collisionTest(jugador, objeto, true)
  );
  if (bloqueado) jugador.setPosition(x, y);
  else jugador.setZOrder(jugador.getY());
  return !bloqueado;
}

for (let i = 0; i < jugadores.length; i++) {
  for (let j = i + 1; j < jugadores.length; j++) {
    let a = jugadores[i];
    let b = jugadores[j];
    // Los bots ceden primero, para que el jugador pueda pasar por un acceso.
    if (control(a) === -1 && control(b) !== -1) [a, b] = [b, a];
    const dx = b.getX() - a.getX();
    const dy = b.getY() - a.getY();
    const faltaX = ancho - Math.abs(dx);
    const faltaY = fondo - Math.abs(dy);
    if (faltaX <= 0 || faltaY <= 0) continue;

    const x = Math.sign(dx || 1) * Math.min(faltaX, 10);
    const y = Math.sign(dy || 1) * Math.min(faltaY, 10);
    const ejes = faltaX < faltaY ? [[x, 0], [0, y]] : [[0, y], [x, 0]];
    for (const [mx, my] of ejes) {
      if (desplazar(b, mx, my) || desplazar(a, -mx, -my)) break;
    }
  }
}
