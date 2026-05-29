import pygame
import json
import math
import datetime
from sys import exit
import random

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
ANCHO, ALTO = 1280, 720

ESTADO_MENU              = "menu"
ESTADO_INTERMISION1      = "intermision1"
ESTADO_INTERMISION2      = "intermision2"
ESTADO_INTERMISION3      = "intermision3"
ESTADO_INTERMISION4      = "intermision4"
ESTADO_INTERMISION_MEJORA = "intermision_mejora"
ESTADO_INTERMISION_PAUSA  = "intermision_pausa"
ESTADO_JUGANDO           = "jugando"
ESTADO_REPORTE           = "reporte"
ESTADO_PUNTAJES          = "puntajes"
ESTADO_ALBUM_PUNTAJES    = "album_puntajes"
ESTADO_FELICITACION      = "felicitacion"

ESTADOS_INTERMISION = (
    ESTADO_INTERMISION1, ESTADO_INTERMISION2,
    ESTADO_INTERMISION3, ESTADO_INTERMISION4,
    ESTADO_INTERMISION_MEJORA, ESTADO_INTERMISION_PAUSA,
)

OBJETIVOS_POR_NIVEL = {1: 500, 2: 1000, 3: 2000, 4: 3500, 5: 5000}
TIEMPO_INICIAL      = 120


def objetivo_nivel5():
    fotografiados = set(a["nombre"] for a in album) | set(a["nombre"] for a in coleccion)
    return sum(a["puntos"] * a.get("cantidad", 1) for a in astros if a["nombre"] not in fotografiados)


def objetivo_actual():
    return objetivo_nivel5() if nivel == 5 else OBJETIVOS_POR_NIVEL[nivel]

FOTOS_INICIALES     = 5

# 24 posiciones fijas (6×4) sin solapamiento y sin cubrir HUD
POSICIONES_FIJAS = [
    (x, y)
    for y in (165, 305, 445, 585)
    for x in (100, 307, 514, 721, 928, 1135)
]

# Layout del álbum (compartido por reporte, album_puntajes y carga de scores)
REC_W, REC_H = 130, 130
GAP          = 30
SEP          = 150
GROUP_W      = 2 * REC_W + GAP
START_Y      = 275

# Posiciones del libro de flechas
LIBRO_BOTTOM  = 670
MARGEN_BOOK   = 12
TAM_FLECHA    = 50
FLECHA_IZQ_X  = ANCHO // 2 - 415 + MARGEN_BOOK + 30
FLECHA_DER_X  = ANCHO // 2 + 415 - MARGEN_BOOK - TAM_FLECHA - 30
FLECHA_Y      = LIBRO_BOTTOM - MARGEN_BOOK - TAM_FLECHA - 40

# ---------------------------------------------------------------------------
# Utilidades gráficas
# ---------------------------------------------------------------------------

def escalar_proporcional(image, target_w, target_h):
    iw, ih = image.get_size()
    escala = min(target_w / iw, target_h / ih)
    return pygame.transform.scale(image, (int(iw * escala), int(ih * escala)))


def escalar_rellenar(image, target_w, target_h):
    iw, ih = image.get_size()
    escala = max(target_w / iw, target_h / ih)
    nw, nh = int(iw * escala), int(ih * escala)
    scaled = pygame.transform.scale(image, (nw, nh))
    cx, cy = (nw - target_w) // 2, (nh - target_h) // 2
    return scaled.subsurface((cx, cy, target_w, target_h)).copy()


def render_gradiente_texto(fuente, texto, color1, color2):
    surf = fuente.render(texto, True, (255, 255, 255))
    w, h = surf.get_size()
    grad = pygame.Surface((w, h), pygame.SRCALPHA)
    for x in range(w):
        t = x / max(w - 1, 1)
        r = int(color1[0] * (1 - t) + color2[0] * t)
        g = int(color1[1] * (1 - t) + color2[1] * t)
        b = int(color1[2] * (1 - t) + color2[2] * t)
        pygame.draw.line(grad, (r, g, b), (x, 0), (x, h))
    grad.blit(surf, (0, 0), None, pygame.BLEND_RGBA_MULT)
    return grad


def cargar_imagen(ruta, escala=None):
    img = pygame.image.load(ruta)
    try:
        has_alpha = img.get_flags() & pygame.SRCALPHA
    except AttributeError:
        has_alpha = False
    img = img.convert_alpha() if has_alpha else img.convert()
    if escala:
        img = pygame.transform.scale(img, escala)
    return img


def dibujar_rect_punteado(superficie, color, rect, dash=8):
    x, y, w, h = rect
    for i in range(0, w, dash * 2):
        pygame.draw.line(superficie, color, (x + i, y), (min(x + i + dash, x + w), y))
        pygame.draw.line(superficie, color, (x + i, y + h), (min(x + i + dash, x + w), y + h))
    for i in range(0, h, dash * 2):
        pygame.draw.line(superficie, color, (x, y + i), (x, min(y + i + dash, y + h)))
        pygame.draw.line(superficie, color, (x + w, y + i), (x + w, min(y + i + dash, y + h)))


def dibujar_boton(pantalla, fuente, texto, rect_base, y_center, right_edge=None,
                  color_fondo=(100, 0, 180), left_edge=None):
    """Dibuja un botón con hover y glow. Devuelve el rect final del botón."""
    surf_base = fuente.render(texto, False, (255, 255, 255))
    if left_edge is not None:
        r = surf_base.get_rect(left=left_edge, centery=y_center)
    else:
        r = surf_base.get_rect(right=right_edge, centery=y_center)
    hover = r.inflate(20, 10).collidepoint(pygame.mouse.get_pos())
    if hover:
        surf = pygame.transform.scale(surf_base, (int(surf_base.get_width() * 1.1), int(surf_base.get_height() * 1.1)))
        btn_rect = surf.get_rect(center=r.center)
        # Glow: halo semitransparente detrás del botón
        pulse = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() / 200)
        glow_alpha = int(60 + 40 * pulse)
        glow_rect  = btn_rect.inflate(36, 18)
        glow_surf  = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (180, 80, 255, glow_alpha),
                         (0, 0, glow_rect.width, glow_rect.height), border_radius=12)
        pantalla.blit(glow_surf, glow_rect)
    else:
        surf, btn_rect = surf_base, r
    bg = btn_rect.inflate(24, 12)
    pygame.draw.rect(pantalla, color_fondo, bg, border_radius=8)
    pantalla.blit(surf, btn_rect)
    return btn_rect


def wrap_text(texto, fuente, ancho_max):
    """Divide texto en líneas que caben dentro de ancho_max."""
    palabras = texto.split()
    lineas, actual = [], ""
    for p in palabras:
        prueba = (actual + " " + p).strip()
        if fuente.size(prueba)[0] <= ancho_max:
            actual = prueba
        else:
            if actual:
                lineas.append(actual)
            actual = p
    if actual:
        lineas.append(actual)
    return lineas


def calcular_slots_album():
    """Calcula los 8 rects de slots del álbum (layout fijo)."""
    total_w = 2 * GROUP_W + SEP
    start_x = (ANCHO - total_w) // 2
    slots = []
    for i in range(8):
        group = i // 4
        idx   = i % 4
        r, c  = idx // 2, idx % 2
        rx = start_x + group * (GROUP_W + SEP) + c * (REC_W + GAP)
        ry = START_Y + r * (REC_H + GAP)
        slots.append(pygame.Rect(rx, ry, REC_W, REC_H))
    return slots


def calcular_posiciones_pagina(astros_data):
    """Devuelve {pagina: [slots]} para todas las páginas necesarias."""
    slots_base = calcular_slots_album()
    posiciones = [a["posicion"] for a in astros_data if "posicion" in a]
    max_pos    = max(posiciones) if posiciones else 0
    total_pags = (max_pos // 8) + 1
    return {p: [pygame.Rect(s.x, s.y, s.w, s.h) for s in slots_base]
            for p in range(total_pags)}


def obtener_pagina_slot(pos):
    return pos // 8, pos % 8


def color_pulsante():
    """Devuelve un color que cicla suavemente entre naranja → morado → naranja."""
    t = (pygame.time.get_ticks() % 3000) / 3000
    if t < 1/3:
        lt = t * 3
        return (int(255 - lt * 127), int(165 - lt * 165), int(lt * 128))
    elif t < 2/3:
        lt = (t - 1/3) * 3
        return (int(128 - lt * 128), 0, int(128 + lt * 127))
    else:
        lt = (t - 2/3) * 3
        return (int(lt * 255), int(lt * 165), int(255 - lt * 255))


# ---------------------------------------------------------------------------
# Sprites
# ---------------------------------------------------------------------------

class Camara(pygame.sprite.Sprite):
    RADIO = 50

    def __init__(self, limite_ancho, limite_alto):
        super().__init__()
        self.limite_ancho = limite_ancho
        self.limite_alto  = limite_alto
        self.velocidad    = 4
        self.rect         = pygame.Rect(0, 0, self.RADIO * 2 + 100, self.RADIO * 2 + 80)
        self.rect.center  = (limite_ancho // 2, limite_alto // 2)

        # Atributos de feedback visual (deben estar antes de _render)
        self.mostrar_texto_foto  = False
        self.texto_foto          = ""
        self.color_texto_foto    = (255, 255, 255)
        self.tiempo_foto         = 0

        self.image = self._render()

    # -- Dibujo --

    def _render(self):
        r = self.RADIO
        surf = pygame.Surface((r * 2 + 100, r * 2 + 80), pygame.SRCALPHA)
        color = (0, 255, 0)
        cx, cy = 100, 70

        # Anillos de sonar que se expanden y desvanecen
        t = pygame.time.get_ticks() / 1000
        for i in range(3):
            phase = (t * 0.6 + i / 3) % 1.0
            ring_r = int(r + phase * 45)
            alpha  = int(180 * (1 - phase))
            if alpha > 0:
                ring_surf = pygame.Surface((ring_r * 2 + 4, ring_r * 2 + 4), pygame.SRCALPHA)
                pygame.draw.circle(ring_surf, (0, 255, 0, alpha),
                                   (ring_r + 2, ring_r + 2), ring_r, 1)
                surf.blit(ring_surf, (cx - ring_r - 2, cy - ring_r - 2))

        pygame.draw.circle(surf, color, (cx, cy), r, 3)
        pygame.draw.line(surf, color, (cx - 5, cy), (cx + 5, cy), 2)
        pygame.draw.line(surf, color, (cx, cy - 5), (cx, cy + 5), 2)

        if self.mostrar_texto_foto:
            if pygame.time.get_ticks() - self.tiempo_foto > 500:
                self.mostrar_texto_foto = False
            else:
                fuente = pygame.font.Font("assets/Fonts/Silkscreen/Silkscreen-Regular.ttf", 32)
                texto  = fuente.render(self.texto_foto, False, self.color_texto_foto)
                surf.blit(texto, texto.get_rect(center=(cx, cy + 90)))
        return surf

    # -- Movimiento --

    def _controlar_bordes(self):
        self.rect.left   = max(self.rect.left,   -80)
        self.rect.right  = min(self.rect.right,   self.limite_ancho + 80)
        self.rect.top    = max(self.rect.top,    -70)
        self.rect.bottom = min(self.rect.bottom,  self.limite_alto  + 70)

    def movimiento(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.rect.x -= self.velocidad
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.rect.x += self.velocidad
        if keys[pygame.K_UP]    or keys[pygame.K_w]: self.rect.y -= self.velocidad
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: self.rect.y += self.velocidad
        self._controlar_bordes()

    def automatico(self):
        if not hasattr(self, '_dir_auto'):
            self._dir_auto    = 0
            self._cambio_dir  = 0
        self._cambio_dir += 1
        if self._cambio_dir > 60:
            self._dir_auto   = random.randint(0, 3)
            self._cambio_dir = 0
        v = self.velocidad
        if   self._dir_auto == 0 and self.rect.x - v >= 0:                          self.rect.x -= v
        elif self._dir_auto == 1 and self.rect.x + v <= ANCHO - self.rect.width:    self.rect.x += v
        elif self._dir_auto == 2 and self.rect.y - v >= 0:                          self.rect.y -= v
        elif self._dir_auto == 3 and self.rect.y + v <= ALTO  - self.rect.height:   self.rect.y += v

    def mover_hacia(self, target_center, velocidad=2):
        """Mueve la cámara automáticamente hacia un punto (tutoriales)."""
        dx = target_center[0] - self.rect.centerx
        dy = target_center[1] - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist > 10:
            if abs(dx) >= abs(dy):
                self.rect.x += velocidad if dx > 0 else -velocidad
            else:
                self.rect.y += velocidad if dy > 0 else -velocidad
            return False
        return True  # llegó

    def update(self):
        self.image = self._render()
        if estado_actual not in ESTADOS_INTERMISION:
            self.movimiento()


class Astro(pygame.sprite.Sprite):
    ASTROS_REDUCIDOS = {"CometaHalley", "AgujeroNegro", "Nebulosa", "Galaxia", "Agujero De Gusano"}

    def __init__(self, data, posicion):
        super().__init__()
        self.nombre          = data["nombre"]
        self.puntos          = data["puntos"]
        self.image           = assets_astros[self.nombre].copy()
        if self.nombre in self.ASTROS_REDUCIDOS:
            w = int(self.image.get_width() * 0.7)
            h = int(self.image.get_height() * 0.7)
            self.image = pygame.transform.scale(self.image, (w, h))
        self.rect            = self.image.get_rect(center=posicion)
        self.seleccionado    = False
        self.radio_deteccion = 150
        self.image.set_alpha(0)

    def update_visual(self, pos_visor):
        distancia  = math.dist(self.rect.center, pos_visor)
        if distancia < self.radio_deteccion:
            proporcion = 1 - distancia / self.radio_deteccion
            self.image.set_alpha(int(proporcion * 255))
            self.seleccionado = proporcion > 0.8
        else:
            self.image.set_alpha(0)
            self.seleccionado = False

    def update(self):
        pass


class FotoReporte(pygame.sprite.Sprite):
    def __init__(self, clave, texto, rect_miniatura, rect_destino, surf_pixel, surf_real, nombre_mostrar=None):
        super().__init__()
        self.clave          = clave
        self.nombre_mostrar = nombre_mostrar or clave
        self.texto_astro    = texto
        self.rect_miniatura = rect_miniatura
        self.rect_destino   = rect_destino
        self.superficie_pixel = surf_pixel
        self.superficie_real  = surf_real
        self.estado   = 'oculta_en_libro'
        self.angulo   = 0.0
        self.hover    = False
        self.pagina   = 0

        pw, ph = surf_pixel.get_size()
        escala = min(rect_destino.w / pw, rect_destino.h / ph)
        self.tamanio_normal  = (int(pw * escala), int(ph * escala))
        self.tamanio_anim    = (self.tamanio_normal[0] * 3, self.tamanio_normal[1] * 3)
        self.tamanio_relleno = (rect_destino.w, rect_destino.h)

        self.image = pygame.transform.scale(surf_pixel, self.tamanio_normal)
        self.rect  = self.image.get_rect(center=rect_miniatura.center)

    def update(self):
        if self.estado == 'girando':
            self._animar_giro()
        elif self.estado == 'pegando':
            self._animar_pegado()

    def _animar_giro(self):
        self.velocidad_angular = min(getattr(self, 'velocidad_angular', 0.02) + 0.003, 0.3)
        self.angulo += self.velocidad_angular
        seno         = math.sin(self.angulo)
        factor_ancho = abs(seno)
        nuevo_ancho  = max(int(self.tamanio_anim[0] * factor_ancho), 1)

        activa = self.superficie_pixel if seno >= 0 else pygame.transform.flip(self.superficie_pixel, True, False)
        self.image = pygame.transform.scale(activa, (nuevo_ancho, self.tamanio_anim[1]))
        self.rect  = self.image.get_rect(center=(ANCHO // 2, ALTO // 2))

        if self.angulo >= 10 * math.pi and abs(seno) > 0.95:
            # La imagen real aparece de golpe; guardamos el momento para el flash
            self._flash_inicio = pygame.time.get_ticks()
            self.image = escalar_rellenar(self.superficie_real, *self.tamanio_anim)
            self.rect  = self.image.get_rect(center=(ANCHO // 2, ALTO // 2))
            self.estado = 'revelada'

    def pegar(self, instantaneo=False):
        if instantaneo:
            self.image  = escalar_rellenar(self.superficie_real, *self.tamanio_relleno)
            self.rect   = self.image.get_rect(center=self.rect_destino.center)
            self.estado = 'pegada'
            return
        self._pegando_inicio      = pygame.time.get_ticks()
        self._pegando_duracion    = 500
        self._pegando_start_center = (ANCHO // 2, ALTO // 2)
        self._pegando_end_center   = self.rect_destino.center
        self._pegando_start_size   = self.tamanio_anim
        self._pegando_end_size     = self.tamanio_relleno
        self.estado = 'pegando'

    def _animar_pegado(self):
        elapsed = pygame.time.get_ticks() - self._pegando_inicio
        t = min(elapsed / self._pegando_duracion, 1.0)

        ease = 1 - (1 - t) ** 3
        if t > 0.8:
            bt = (t - 0.8) / 0.2
            ease += 0.08 * math.sin(bt * math.pi * 3) * (1 - bt)
        ease = min(ease, 1.0)

        cx = self._pegando_start_center[0] + (self._pegando_end_center[0] - self._pegando_start_center[0]) * ease
        cy = self._pegando_start_center[1] + (self._pegando_end_center[1] - self._pegando_start_center[1]) * ease
        w  = max(int(self._pegando_start_size[0] + (self._pegando_end_size[0] - self._pegando_start_size[0]) * ease), 1)
        h  = max(int(self._pegando_start_size[1] + (self._pegando_end_size[1] - self._pegando_start_size[1]) * ease), 1)

        if t >= 1.0:
            self.image  = escalar_rellenar(self.superficie_real, *self.tamanio_relleno)
            self.rect   = self.image.get_rect(center=self._pegando_end_center)
            self.estado = 'pegada'
        else:
            self.image = pygame.transform.scale(self.superficie_real, (w, h))
            self.rect  = self.image.get_rect(center=(int(cx), int(cy)))

    def revelar_ampliado(self):
        self.image  = pygame.transform.scale(self.superficie_real, self.tamanio_anim)
        self.rect   = self.image.get_rect(center=(ANCHO // 2, ALTO // 2))
        self.estado = 'revelada'


# ---------------------------------------------------------------------------
# Lógica de juego
# ---------------------------------------------------------------------------

def crear_astros():
    global objetivo_nivel5_inicial
    if nivel == 5:
        objetivo_nivel5_inicial = objetivo_nivel5()
    astros_nivel = [a for a in astros if a.get("nivel") == nivel]
    total        = sum(a.get("cantidad", 1) for a in astros_nivel)
    ocupadas     = {a.rect.center for a in astros_grupo}
    disponibles  = [p for p in POSICIONES_FIJAS if p not in ocupadas]
    posiciones   = random.sample(disponibles, total)
    for dato in astros_nivel:
        for _ in range(dato.get("cantidad", 1)):
            astros_grupo.add(Astro(dato, posiciones.pop(0)))


def tomar_foto():
    global flash_activo, flash_tiempo, puntos_flotantes
    flash_activo = True
    flash_tiempo = pygame.time.get_ticks()

    colisiones = pygame.sprite.spritecollide(camara.sprite, astros_grupo, False)
    if not colisiones:
        camara.sprite.mostrar_texto_foto  = True
        camara.sprite.tiempo_foto         = flash_tiempo
        camara.sprite.texto_foto          = "MAL"
        camara.sprite.color_texto_foto    = (255, 0, 0)
        return 0

    visor_center = (camara.sprite.rect.x + 100, camara.sprite.rect.y + 70)
    astro = min(colisiones, key=lambda a: math.dist(a.rect.center, visor_center))
    dx = visor_center[0] - astro.rect.centerx
    dy = visor_center[1] - astro.rect.centery
    perfecto = math.hypot(dx, dy) < 30

    camara.sprite.mostrar_texto_foto = True
    camara.sprite.tiempo_foto        = flash_tiempo
    camara.sprite.texto_foto         = "PERFECTO" if perfecto else "BIEN"
    camara.sprite.color_texto_foto   = (128, 0, 128) if perfecto else (0, 255, 0)

    puntos_flotantes.append({"puntos": astro.puntos, "centro": astro.rect.center, "tiempo": flash_tiempo})
    album.append({"nombre": astro.nombre, "puntos": astro.puntos})
    astro.kill()
    return astro.puntos


def colision_camara():
    hits = pygame.sprite.spritecollide(camara.sprite, astros_grupo, False)
    return hits[0] if hits else None


def asignar_tiempo_transicion(tiempo_inicio, duracion=7):
    return (pygame.time.get_ticks() - tiempo_inicio) / 1000 >= duracion


def limpiar_atributos_tutorial(camara_sprite, *attrs):
    for a in attrs:
        if hasattr(camara_sprite, a):
            delattr(camara_sprite, a)


# ---------------------------------------------------------------------------
# Persistencia
# ---------------------------------------------------------------------------

def cargar_scores():
    try:
        with open('data/scores.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"jugadores": {}, "partidas": [], "top_scores": []}


def guardar_puntuacion():
    global scores
    datos    = cargar_scores()
    ahora    = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    punt_total = puntuacion_total_partida + puntuacion
    descubiertos = list(set(a["nombre"] for a in album) | set(a["nombre"] for a in coleccion))

    if nombre_jugador not in datos["jugadores"]:
        datos["jugadores"][nombre_jugador] = {
            "puntuacion_total": 0, "nivel_maximo": 0,
            "astros_descubiertos": [], "fecha_hora": "", "cantidad_partidas": 0,
        }
    p = datos["jugadores"][nombre_jugador]
    p["cantidad_partidas"] += 1
    if punt_total > p["puntuacion_total"]:
        p["puntuacion_total"]     = punt_total
        p["nivel_maximo"]         = nivel
        p["astros_descubiertos"]  = descubiertos
        p["fecha_hora"]           = ahora

    datos["partidas"].append({
        "nombre": nombre_jugador, "puntuacion_total": punt_total,
        "nivel_maximo": nivel, "astros_descubiertos": descubiertos, "fecha_hora": ahora,
    })
    sorted_p = sorted(datos["jugadores"].items(), key=lambda x: x[1]["puntuacion_total"], reverse=True)
    datos["top_scores"] = [{"nombre": k, "puntos": v["puntuacion_total"]} for k, v in sorted_p]

    with open('data/scores.json', 'w') as f:
        json.dump(datos, f, indent=4)
    scores = datos["top_scores"]


def cargar_assets_reales():
    if assets_reales:
        return
    for astro in astros:
        nombre, archivo = astro["nombre"], astro.get("real")
        if not archivo:
            continue
        for ext in ("png", "jpeg"):
            try:
                img = cargar_imagen(f"assets/Graphics/Reales/{archivo}.{ext}")
                w, h = img.get_size()
                max_lado = 800
                if w > max_lado or h > max_lado:
                    sc = max_lado / max(w, h)
                    img = pygame.transform.smoothscale(img, (int(w * sc), int(h * sc)))
                assets_reales[nombre] = img
                break
            except FileNotFoundError:
                pass


def construir_fotos_album(astros_clave_list):
    """Crea instancias de FotoReporte ya pegadas para la vista de álbum de puntajes."""
    posiciones_pagina = calcular_posiciones_pagina(astros)
    fotos = []
    for clave in astros_clave_list:
        astro_data = next((a for a in astros if a["nombre"] == clave), None)
        if astro_data is None:
            continue
        pos       = astro_data.get("posicion")
        pixel_img = assets_astros.get(clave)
        real_img  = assets_reales.get(clave)
        if not (pixel_img and real_img and pos is not None):
            continue
        pagina, slot = obtener_pagina_slot(pos)
        if pagina not in posiciones_pagina or slot >= len(posiciones_pagina[pagina]):
            continue
        foto = FotoReporte(clave, astro_data.get("texto", ""),
                           pygame.Rect(0, 0, 1, 1),
                           posiciones_pagina[pagina][slot],
                           pixel_img, real_img,
                           nombre_mostrar=astro_data.get("nombre_mostrar", clave))
        foto.pagina = pagina
        foto.pegar(instantaneo=True)
        fotos.append(foto)
    return fotos


# ---------------------------------------------------------------------------
# Dibujo: HUD y elementos compartidos
# ---------------------------------------------------------------------------

def mostrar_flash():
    global flash_activo
    if not flash_activo:
        return
    alpha = max(0, 200 - int((pygame.time.get_ticks() - flash_tiempo) * 5))
    if alpha <= 0:
        flash_activo = False
        return
    surf = pygame.Surface((ANCHO, ALTO))
    surf.fill((220, 220, 220))
    surf.set_alpha(alpha)
    pantalla.blit(surf, (0, 0))


def mostrar_camaras(cuantas=None):
    if cuantas is None:
        cuantas = fotos
    texto = fuente_normal.render("FOTOS", False, (255, 255, 255))
    pantalla.blit(texto, texto.get_rect(topleft=(10, 5)))
    for i in range(cuantas):
        pantalla.blit(img_camara, (10 + i * 60, 35))


def mostrar_tiempo(tiempo_restante):
    bar_w, bar_h = int(ANCHO * 0.8), 20
    x = (ANCHO - bar_w) // 2
    y = ALTO - 40
    fill_w = int((tiempo_restante / TIEMPO_INICIAL) * bar_w)
    color  = (255, 0, 0) if tiempo_restante < TIEMPO_INICIAL * 0.2 else (255, 255, 255)

    texto = fuente_normal.render("TIEMPO", False, (255, 255, 255))
    pantalla.blit(texto, texto.get_rect(center=(ANCHO // 2, y - 20)))
    pygame.draw.rect(pantalla, (64, 64, 64), (x, y, bar_w, bar_h), 2, border_radius=10)
    pygame.draw.rect(pantalla, color, (x, y, fill_w, bar_h), border_radius=10)


def mostrar_puntos_partida(pts=None):
    if pts is None:
        pts = puntuacion
    bar_w, bar_h = 20, int(ALTO * 0.6)
    x = ANCHO - 75
    y = (ALTO - bar_h) // 2

    texto = fuente_normal.render("PUNTOS", False, (255, 255, 255))
    pantalla.blit(texto, texto.get_rect(center=(x + bar_w // 2, y - 20)))
    pygame.draw.rect(pantalla, (64, 64, 64), (x, y, bar_w, bar_h), 2, border_radius=10)

    objetivo = objetivo_nivel5_inicial if nivel == 5 else objetivo_actual()
    if objetivo > 0:
        fill_h = int(bar_h * min(pts / objetivo, 1))
        pygame.draw.rect(pantalla, (255, 215, 0), (x, y + bar_h - fill_h, bar_w, fill_h), border_radius=10)


def dibujar_panel_foto_revelada(pantalla_surf, f):
    """Dibuja el panel de info lateral de una FotoReporte revelada."""
    ancho_max   = 260
    nombre_lineas = wrap_text(f.nombre_mostrar.upper(), fuente_normal, ancho_max)
    nombre_surf = [fuente_normal.render(l, False, (255, 255, 255)) for l in nombre_lineas]
    lineas      = wrap_text(f.texto_astro, fuente_pequena, ancho_max)
    textos_surf = [fuente_pequena.render(l, False, (153, 81, 184)) for l in lineas]

    nombre_w = max(s.get_width() for s in nombre_surf)
    panel_w = max(nombre_w, ancho_max) + 20
    panel_h = len(nombre_surf) * fuente_normal.get_height() + len(textos_surf) * fuente_pequena.get_height() + 20
    margen  = 10

    if f.rect.right + margen + panel_w < ANCHO - margen:
        panel_x = f.rect.right + margen
    else:
        panel_x = f.rect.left - margen - panel_w
    panel_y = max(margen, min(f.rect.centery - panel_h // 2, ALTO - margen - panel_h))

    pygame.draw.rect(pantalla_surf, (0, 0, 0), (panel_x, panel_y, panel_w, panel_h), border_radius=6)
    y_off = panel_y + 6
    for s in nombre_surf:
        pantalla_surf.blit(s, (panel_x + 10, y_off))
        y_off += fuente_normal.get_height()
    y_off += 4
    for s in textos_surf:
        pantalla_surf.blit(s, (panel_x + 10, y_off))
        y_off += fuente_pequena.get_height()
    if f.hover:
        pygame.draw.rect(pantalla_surf, (192, 192, 192), f.rect, 3, border_radius=2)


def dibujar_flechas_album(pantalla_surf, pagina_actual, total_paginas):
    if pagina_actual > 0:
        pantalla_surf.blit(img_arrow_l, (FLECHA_IZQ_X, FLECHA_Y))
    if pagina_actual < total_paginas - 1:
        pantalla_surf.blit(img_arrow_r, (FLECHA_DER_X, FLECHA_Y))


def dibujar_slots_album(pantalla_surf, slots, offset_pagina=0):
    for i, rect in enumerate(slots):
        dibujar_rect_punteado(pantalla_surf, (0, 0, 0), (rect.x, rect.y, REC_W, REC_H), 8)
        num = fuente_normal.render(str(i + offset_pagina * 8 + 1), False, (180, 180, 180))
        pantalla_surf.blit(num, num.get_rect(center=rect.center))


# ---------------------------------------------------------------------------
# Pantallas: menú, puntajes, álbum de puntajes
# ---------------------------------------------------------------------------

def mostrar_menu():
    global boton_puntajes_rect, boton_salir_rect
    t = pygame.time.get_ticks() / 1000

    # Título flotante
    titulo = render_gradiente_texto(fuente_titulo_grande, "ArcSpace", (100, 0, 180), (255, 215, 0))
    float_y = int(ALTO // 8 + math.sin(t * 1.4) * 6)
    titulo_rect = titulo.get_rect(center=(ANCHO // 2, float_y))
    pantalla.blit(titulo, titulo_rect)

    label = fuente_media.render("INGRESA TU NOMBRE", False, (255, 255, 255))
    pantalla.blit(label, label.get_rect(center=(ANCHO // 2, ALTO // 2)))

    # Guiones vacíos debajo del nombre con letras superpuestas
    MAX_NOMBRE = 10
    char_w, char_h = fuente_titulo.size("_")
    gap = 18
    total_w = MAX_NOMBRE * char_w + (MAX_NOMBRE - 1) * gap
    start_x = (ANCHO - total_w) // 2
    center_y = ALTO // 2 + 70
    pulse = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() / 150)
    for i in range(MAX_NOMBRE):
        x = start_x + i * (char_w + gap)
        surf_g = fuente_titulo.render("_", False, (150, 50, 200))
        surf_g.set_alpha(int(80 + 175 * pulse))
        pantalla.blit(surf_g, (x, center_y - char_h // 2))
        if i < len(nombre_jugador):
            surf_l = fuente_titulo.render(nombre_jugador[i], False, (150, 50, 200))
            pantalla.blit(surf_l, (x, center_y - char_h // 2 - 6))

    # "PRESIONE ESPACIO" con pulso de escala
    pulse = 1.0 + 0.04 * math.sin(t * 3.0)
    base_surf = fuente_media.render("PRESIONE ESPACIO PARA INICIAR", False, (255, 255, 255))
    w, h = int(base_surf.get_width() * pulse), int(base_surf.get_height() * pulse)
    instruccion = pygame.transform.scale(base_surf, (w, h))
    pantalla.blit(instruccion, instruccion.get_rect(center=(ANCHO // 2, ALTO // 2 + 140)))

    boton_salir_rect = dibujar_boton(pantalla, fuente_normal, "SALIR (ESC)",
                                     None, titulo_rect.centery, ANCHO - 20)
    boton_puntajes_rect = dibujar_boton(pantalla, fuente_normal, "PUNTAJES",
                                        None, titulo_rect.centery, ANCHO - 20,
                                        left_edge=20)

    if nombre_erroneo:
        err = fuente_pequena.render("YA EXISTE UN JUGADOR CON ESE NOMBRE", False, (255, 0, 0))
        pantalla.blit(err, err.get_rect(center=(ANCHO // 2, ALTO - 30)))

    creado = fuente_pequena.render("Creado por Ulises Sosa", False, (150, 50, 200))
    cr = creado.get_rect(center=(ANCHO // 2, ALTO - 20))
    pantalla.blit(creado, cr)
    pantalla.blit(img_nacional, img_nacional.get_rect(left=cr.right + 8, centery=cr.centery))


def mostrar_puntajes():
    global boton_volver_rect, scroll_offset, puntajes_rects
    puntajes_rects = []

    titulo = fuente_titulo.render("PUNTAJES", False, (255, 255, 255))
    pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 50)))
    boton_volver_rect = dibujar_boton(pantalla, fuente_normal, "VOLVER (M)", None, 50, ANCHO - 20)

    y_inicio, alto_entrada = 110, 80
    area_y    = ALTO - y_inicio - 20
    total_alto = len(jugadores_ordenados) * alto_entrada
    max_scroll = max(0, total_alto - area_y)
    scroll_offset = min(scroll_offset, max_scroll)

    pantalla.set_clip(pygame.Rect(0, y_inicio, ANCHO, ALTO - y_inicio))
    mouse_pos = pygame.mouse.get_pos()

    for i, (nombre, datos_j) in enumerate(jugadores_ordenados):
        y = y_inicio + i * alto_entrada - scroll_offset
        if y + alto_entrada < y_inicio or y > ALTO - 20:
            continue

        fuente_actual = fuente_normal if i < 3 else fuente_pequena
        color_base    = (255, 215, 0)
        rank_s  = fuente_actual.render(f"{i+1} - ", False, color_base)
        nom_s   = fuente_actual.render(nombre, False, color_base)
        pts_s   = fuente_actual.render(f"{datos_j['puntuacion_total']} pts", False, color_base)

        entry_w = 60 + rank_s.get_width() + nom_s.get_width() + 20 + pts_s.get_width()
        entry_r = pygame.Rect(60, y, entry_w, fuente_actual.get_height())
        puntajes_rects.append({"nombre": nombre, "datos": datos_j, "rect": entry_r})

        color = (150, 50, 200) if entry_r.collidepoint(mouse_pos) else color_base
        rank_s = fuente_actual.render(f"{i+1} - ", False, color)
        nom_s  = fuente_actual.render(nombre, False, color)
        pts_s  = fuente_actual.render(f"{datos_j['puntuacion_total']} pts", False, color)

        pantalla.blit(rank_s, (60, y))
        pantalla.blit(nom_s,  (60 + rank_s.get_width(), y))
        pantalla.blit(pts_s,  (60 + rank_s.get_width() + nom_s.get_width() + 20, y))

        info = fuente_pequena.render(
            f"Nivel max: {datos_j['nivel_maximo']}  |  "
            f"Astros: {len(datos_j['astros_descubiertos'])}  |  "
            f"Partidas: {datos_j['cantidad_partidas']}",
            False, (150, 50, 200)
        )
        pantalla.blit(info, (60, y + (35 if i < 3 else 20)))

    pantalla.set_clip(None)


def mostrar_album_puntajes():
    global boton_volver_rect, pagina_actual_album, pag_slide_album_activa
    global pag_slide_album_inicio, pag_slide_album_captura, pag_slide_album_solicitada

    posiciones_pagina = calcular_posiciones_pagina(astros)
    total_paginas     = len(posiciones_pagina)

    # --- Iniciar animación de página si se solicitó ---
    if pag_slide_album_solicitada != 0 and not pag_slide_album_activa:
        old_page = pagina_actual_album
        pagina_actual_album += pag_slide_album_solicitada
        if pagina_actual_album < 0 or pagina_actual_album >= total_paginas:
            pagina_actual_album = max(0, min(total_paginas - 1, pagina_actual_album))
            pag_slide_album_solicitada = 0
        else:
            cap = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            cap.blit(img_uibook, img_uibook.get_rect(center=(ANCHO // 2, 420)))
            dibujar_slots_album(cap, posiciones_pagina[old_page], old_page)
            for f in fotos_album_puntajes:
                if f.estado == 'pegada' and f.pagina == old_page:
                    cap.blit(f.image, f.rect)
            dibujar_flechas_album(cap, old_page, total_paginas)
            pag_slide_album_captura = cap
            pag_slide_album_inicio = pygame.time.get_ticks()
            pag_slide_album_activa = True
            pag_slide_album_solicitada = 0

    if pagina_actual_album >= total_paginas:
        pagina_actual_album = 0

    titulo = fuente_titulo.render(f"Album de {album_puntajes_clave}", False, (255, 215, 0))
    pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 110)))
    boton_volver_rect = dibujar_boton(pantalla, fuente_normal, "VOLVER (M)", None, 40, ANCHO - 20)

    img_uibook_rect = img_uibook.get_rect(center=(ANCHO // 2, 420))
    pantalla.blit(img_uibook, img_uibook_rect)

    dibujar_slots_album(pantalla, posiciones_pagina[pagina_actual_album], pagina_actual_album)

    for f in fotos_album_puntajes:
        if f.estado == 'pegada' and f.pagina == pagina_actual_album:
            pantalla.blit(f.image, f.rect)

    for f in fotos_album_puntajes:
        if f.estado == 'girando':
            pantalla.blit(f.image, f.rect)

    for f in fotos_album_puntajes:
        if f.estado == 'revelada':
            pantalla.blit(f.image, f.rect)
            dibujar_panel_foto_revelada(pantalla, f)

    dibujar_flechas_album(pantalla, pagina_actual_album, total_paginas)

    # --- Overlay de animación de página ---
    if pag_slide_album_activa and pag_slide_album_captura is not None:
        elapsed = pygame.time.get_ticks() - pag_slide_album_inicio
        t = min(elapsed / PAG_SLIDE_DURACION, 1.0)
        if t >= 1.0:
            pag_slide_album_activa = False
            pag_slide_album_captura = None
        else:
            alpha = int(255 * (1 - t * t))
            pag_slide_album_captura.set_alpha(alpha)
            pantalla.blit(pag_slide_album_captura, (0, 0))


# ---------------------------------------------------------------------------
# Pantallas: reporte post-ronda
# ---------------------------------------------------------------------------

def mostrar_reporte():
    global nivel, pagina_actual, pag_slide_activa, pag_slide_inicio
    global pag_slide_captura, pag_slide_solicitada
    cargar_assets_reales()

    posiciones_pagina = calcular_posiciones_pagina(astros)
    total_pags = len(posiciones_pagina)

    # --- Iniciar animación de página si se solicitó ---
    if pag_slide_solicitada != 0 and not pag_slide_activa:
        old_page = pagina_actual
        pagina_actual += pag_slide_solicitada
        if pagina_actual < 0 or pagina_actual >= total_pags:
            pagina_actual = max(0, min(total_pags - 1, pagina_actual))
            pag_slide_solicitada = 0
        else:
            cap = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            cap.blit(img_uibook, img_uibook.get_rect(center=(ANCHO // 2, 420)))
            dibujar_slots_album(cap, posiciones_pagina[old_page], old_page)
            for f in fotos_permanentes_vista:
                if f.estado == 'pegada' and f.pagina == old_page:
                    cap.blit(f.image, f.rect)
            claves_perm = {f.clave for f in fotos_permanentes_vista}
            for f in fotos_reporte_instancias:
                if f.estado == 'pegada' and f.pagina == old_page and f.clave not in claves_perm:
                    cap.blit(f.image, f.rect)
            dibujar_flechas_album(cap, old_page, total_pags)
            pag_slide_captura = cap
            pag_slide_inicio = pygame.time.get_ticks()
            pag_slide_activa = True
            pag_slide_solicitada = 0

    if pagina_actual >= total_pags:
        pagina_actual = 0
    slots = posiciones_pagina[pagina_actual]

    # Inicializar fotos permanentes (rondas anteriores) la primera vez
    if fotos_pegadas_permanentes and not fotos_permanentes_vista:
        _inicializar_fotos_permanentes(posiciones_pagina)

    # Cabecera con fotos nuevas
    _dibujar_cabecera_reporte(posiciones_pagina)

    # Libro de fondo
    pantalla.blit(img_uibook, img_uibook.get_rect(center=(ANCHO // 2, 420)))

    # Slots vacíos
    dibujar_slots_album(pantalla, slots, pagina_actual)

    # Fotos permanentes de rondas anteriores (ahora son instancias interactivas)
    for f in fotos_permanentes_vista:
        if f.estado == 'pegada' and f.pagina == pagina_actual:
            pantalla.blit(f.image, f.rect)

    # Fotos de esta ronda (pegadas)
    claves_permanentes = {f.clave for f in fotos_permanentes_vista}
    for f in fotos_reporte_instancias:
        if f.estado == 'pegada' and f.pagina == pagina_actual and f.clave not in claves_permanentes:
            pantalla.blit(f.image, f.rect)

    # Animaciones (girando / pegando encima de todo)
    for f in fotos_reporte_instancias:
        if f.estado in ('girando', 'pegando'):
            f.update()
            pantalla.blit(f.image, f.rect)

    # Fotos reveladas (nuevas o permanentes) con overlay y flash de revelado
    for f in fotos_reporte_instancias + fotos_permanentes_vista:
        if f.estado == 'revelada':
            f.update()
            # Overlay oscuro para enfocar la foto
            overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            pantalla.blit(overlay, (0, 0))
            # Borde dorado sólido
            border_rect = f.rect.inflate(6, 6)
            pygame.draw.rect(pantalla, (255, 215, 0), border_rect, 3, border_radius=8)
            pantalla.blit(f.image, f.rect)
            # Flash blanco que se desvanece en 0.6s desde el momento del revelado
            if hasattr(f, '_flash_inicio'):
                elapsed = (pygame.time.get_ticks() - f._flash_inicio) / 1000
                if elapsed < 0.6:
                    fa = int(255 * (1 - elapsed / 0.6))
                    flash_s = pygame.Surface(f.rect.size, pygame.SRCALPHA)
                    flash_s.fill((255, 255, 255, fa))
                    pantalla.blit(flash_s, f.rect)
                else:
                    del f._flash_inicio
            dibujar_panel_foto_revelada(pantalla, f)
            break  # solo una foto revelada a la vez

    # Texto de instrucción inferior
    _dibujar_instruccion_reporte()

    dibujar_flechas_album(pantalla, pagina_actual, len(posiciones_pagina))

    # Botón volver al menú (siempre visible)
    txt_m = fuente_pequena.render("Volver al menu", False, (255, 255, 255))
    r_m   = txt_m.get_rect(left=20, centery=ALTO - 30)
    pantalla.blit(txt_m, r_m)
    m_img = img_m_icon
    pantalla.blit(m_img, m_img.get_rect(left=r_m.right + 10, centery=ALTO - 30))

    # --- Overlay de animación de página ---
    if pag_slide_activa and pag_slide_captura is not None:
        elapsed = pygame.time.get_ticks() - pag_slide_inicio
        t = min(elapsed / PAG_SLIDE_DURACION, 1.0)
        if t >= 1.0:
            pag_slide_activa = False
            pag_slide_captura = None
        else:
            alpha = int(255 * (1 - t * t))
            pag_slide_captura.set_alpha(alpha)
            pantalla.blit(pag_slide_captura, (0, 0))


def _dibujar_cabecera_reporte(posiciones_pagina):
    """Dibuja el rectángulo superior con las miniaturas de fotos nuevas."""
    rx = (ANCHO - int(ANCHO * 0.9)) // 2
    rect_ancho, rect_alto = int(ANCHO * 0.9), 110
    pygame.draw.rect(pantalla, (100, 0, 180), (rx, 0, rect_ancho, rect_alto), border_radius=16)
    # Borde blanco fino
    pygame.draw.rect(pantalla, (180, 120, 255), (rx, 0, rect_ancho, rect_alto), 2, border_radius=16)

    label = fuente_media.render("fotos nuevas:", False, (255, 255, 255))
    pantalla.blit(label, (rx + 18, (rect_alto - label.get_height()) // 2))

    if not album:
        return

    tamano, espacio = 80, 20
    label_w = 18 + label.get_width() + 20

    # Inicializar instancias de FotoReporte si todavía no existen
    if not fotos_reporte_instancias:
        _inicializar_fotos_reporte(posiciones_pagina, rx, rect_ancho, rect_alto, tamano, espacio)

    # Sólo contar y dibujar fotos que aún no están pegadas
    claves_pegadas = {f.clave for f in fotos_reporte_instancias if f.estado == 'pegada'}
    claves_pegadas |= {c for c, _, _ in fotos_pegadas_permanentes}
    items_dibujables = [item for item in album if item["nombre"] not in claves_pegadas]
    vistas, items_unicos = set(), []
    for item in items_dibujables:
        if item["nombre"] not in vistas:
            vistas.add(item["nombre"])
            items_unicos.append(item)

    total_fotos = len(items_unicos)
    if total_fotos == 0:
        return
    inicio_x = rx + (rect_ancho - total_fotos * tamano - (total_fotos - 1) * espacio) // 2
    inicio_x = max(inicio_x, rx + label_w)
    y_foto = (rect_alto - tamano) // 2

    # Actualizar rect_miniatura de instancias no pegadas para que el hit-test sea correcto
    instancia_por_clave = {f.clave: f for f in fotos_reporte_instancias if f.estado != 'pegada'}
    for draw_idx, item in enumerate(items_unicos):
        clave = item["nombre"]
        px = inicio_x + draw_idx * (tamano + espacio)
        if clave in instancia_por_clave:
            inst = instancia_por_clave[clave]
            inst.rect_miniatura = pygame.Rect(px, y_foto, tamano, tamano)
            if inst.estado == 'oculta_en_libro':
                inst.rect = inst.rect_miniatura.copy()

        pygame.draw.rect(pantalla, (212, 193, 190), (px - 6, y_foto - 6, tamano + 12, tamano + 12), border_radius=2)
        pygame.draw.rect(pantalla, (0, 0, 0),       (px - 6, y_foto - 6, tamano + 12, tamano + 12), 3, border_radius=2)
        img = assets_astros.get(clave)
        if img:
            if clave not in _thumb_cache:
                iw, ih = img.get_size()
                sc = min(tamano / iw, tamano / ih)
                _thumb_cache[clave] = pygame.transform.smoothscale(img, (int(iw * sc), int(ih * sc)))
            img_sc = _thumb_cache[clave]
            pantalla.blit(img_sc, (px + (tamano - img_sc.get_width()) // 2,
                                   y_foto + (tamano - img_sc.get_height()) // 2))


def _inicializar_fotos_reporte(posiciones_pagina, rx, rect_ancho, rect_alto, tamano, espacio):
    label_w         = 18 + fuente_media.size("fotos nuevas:")[0] + 20
    permanentes_claves = {c for c, _, _ in fotos_pegadas_permanentes}

    # Obtener items únicos dibujables (sin permanentes ni duplicados)
    vistas, items_unicos = set(), []
    for item in album:
        clave = item["nombre"]
        if clave not in vistas and clave not in permanentes_claves:
            vistas.add(clave)
            items_unicos.append(item)

    total = len(items_unicos)
    if total == 0:
        return
    inicio_x = rx + (rect_ancho - total * tamano - (total - 1) * espacio) // 2
    inicio_x = max(inicio_x, rx + label_w + 10)
    y_foto = (rect_alto - tamano) // 2

    for draw_idx, item in enumerate(items_unicos):
        clave = item["nombre"]
        astro_data = next((a for a in astros if a["nombre"] == clave), None)
        if astro_data is None:
            continue
        pos       = astro_data.get("posicion")
        pixel_img = assets_astros.get(clave)
        real_img  = assets_reales.get(clave)
        if not (pixel_img and real_img and pos is not None):
            continue

        pagina, slot = obtener_pagina_slot(pos)
        if pagina not in posiciones_pagina or slot >= len(posiciones_pagina[pagina]):
            continue

        rect_min  = pygame.Rect(inicio_x + draw_idx * (tamano + espacio), y_foto, tamano, tamano)
        rect_dest = posiciones_pagina[pagina][slot]
        foto = FotoReporte(clave, astro_data.get("texto", ""), rect_min, rect_dest, pixel_img, real_img,
                           nombre_mostrar=astro_data.get("nombre_mostrar", clave))
        foto.pagina = pagina
        fotos_reporte_instancias.append(foto)


def _inicializar_fotos_permanentes(posiciones_pagina):
    """Crea instancias FotoReporte (estado pegada) para fotos de rondas anteriores,
    permitiendo que sean interactivas en el reporte."""
    for clave, pag, slot_idx in fotos_pegadas_permanentes:
        # Evitar duplicados si se llama más de una vez
        if any(f.clave == clave for f in fotos_permanentes_vista):
            continue
        astro_data = next((a for a in astros if a["nombre"] == clave), None)
        if astro_data is None:
            continue
        pixel_img = assets_astros.get(clave)
        real_img  = assets_reales.get(clave)
        if not (pixel_img and real_img):
            continue
        if pag not in posiciones_pagina or slot_idx >= len(posiciones_pagina[pag]):
            continue
        rect_dest = posiciones_pagina[pag][slot_idx]
        foto = FotoReporte(clave, astro_data.get("texto", ""),
                           pygame.Rect(0, 0, 1, 1), rect_dest, pixel_img, real_img,
                           nombre_mostrar=astro_data.get("nombre_mostrar", clave))
        foto.pagina = pag
        foto.pegar(instantaneo=True)
        fotos_permanentes_vista.append(foto)


def _dibujar_instruccion_reporte():
    todas_pegadas = all(f.estado == 'pegada' for f in fotos_reporte_instancias)
    hay_revelada  = any(f.estado == 'revelada' for f in fotos_reporte_instancias)
    hay_girando   = any(f.estado == 'girando'  for f in fotos_reporte_instancias)
    hay_pegando   = any(f.estado == 'pegando'  for f in fotos_reporte_instancias)

    if hay_girando or hay_pegando:
        return

    if todas_pegadas:
        if (nivel == 5 and objetivo_actual() <= 0) or (nivel != 5 and puntuacion >= objetivo_actual()):
            texto = fuente_normal.render("Avanzar al siguiente nivel", False, (255, 215, 0))
        else:
            texto = fuente_normal.render("Intentar de nuevo", False, (255, 0, 0))
        img_sp = img_space_inst
        total_w  = texto.get_width() + 8 + img_sp.get_width()
        start_x  = (ANCHO - total_w) // 2
        pantalla.blit(texto, texto.get_rect(left=start_x, centery=140))
        pantalla.blit(img_sp, img_sp.get_rect(left=start_x + texto.get_width() + 8, centery=140))
    elif hay_revelada:
        texto = fuente_normal.render("Haz click sobre la imagen para pegarla en el album",
                                     False, color_pulsante())
        _blit_con_icono_mouse(texto)
    else:
        texto = fuente_normal.render("Haz click sobre las fotos para revelarlas",
                                     False, color_pulsante())
        _blit_con_icono_mouse(texto)


def _blit_con_icono_mouse(texto):
    r = texto.get_rect(center=(ANCHO // 2, 140))
    pantalla.blit(texto, r)
    icono = img_mouse_icon
    pantalla.blit(icono, icono.get_rect(midright=(r.left - 10, r.centery)))


# ---------------------------------------------------------------------------
# Pantallas: tutoriales
# ---------------------------------------------------------------------------

def dibujar_controles():
    ancla = (ANCHO // 2, int(ALTO / 1.3))
    texto = fuente_normal.render("MUEVE LA CAMARA Y ENCUENTRA LOS PLANETAS", False, (255, 255, 255))
    pantalla.blit(texto, texto.get_rect(midbottom=(ancla[0], ancla[1] - 80)))
    for t in datos_teclas:
        img_rect = t["img"].get_rect(center=(ancla[0] + t["offset"][0], ancla[1] + t["offset"][1]))
        pantalla.blit(t["img"], img_rect)


def dibujar_tomar_fotos():
    ancla = (ANCHO // 2, int(ALTO / 1.3))
    texto = fuente_normal.render("TOMA FOTOS DEL ESPACIO", False, (255, 255, 255))
    pantalla.blit(texto, texto.get_rect(midbottom=(ancla[0], ancla[1] - 80)))
    pantalla.blit(img_space, img_space.get_rect(center=ancla))


def dibujar_objetivo():
    ancla = (ANCHO // 2, int(ALTO / 1.3))
    for i, msg in enumerate(("CADA FOTO TE DA PUNTOS",
                              "COMPLETA EL OBJETIVO PARA PASAR DE NIVEL")):
        t = fuente_normal.render(msg, False, (255, 255, 255))
        pantalla.blit(t, t.get_rect(midbottom=(ancla[0], ancla[1] - 80 + i * 40)))


def _crear_astros_demo(nombres, posiciones):
    """Crea sprites demo simples (sin puntuación) y los agrega a astros_grupo."""
    demos = []
    for nombre, pos in zip(nombres, posiciones):
        s = pygame.sprite.Sprite()
        s.image           = assets_astros[nombre].copy()
        s.rect            = s.image.get_rect(center=pos)
        s.radio_deteccion = 150
        s.image.set_alpha(0)
        astros_grupo.add(s)
        demos.append(s)
    return demos


def actualizar_intermision2():
    """Lógica de renderizado del tutorial 2 (foto demo)."""
    global flash_activo, flash_tiempo, fotos_tutorial

    tiempo_actual = pygame.time.get_ticks()
    cam = camara.sprite

    if not hasattr(cam, '_t2_init'):
        cam._t2_init        = True
        cam._t2_indice      = 0
        cam._t2_fotos       = 5
        cam._t2_demos       = _crear_astros_demo(
            ["Luna", "Venus", "Mercurio"],
            [(ANCHO//2+200, ALTO//2), (ANCHO//2+200, ALTO//2-150), (ANCHO//2-100, ALTO//2-50)]
        )

    for a in cam._t2_demos:
        if a.alive():
            a.image.set_alpha(255)

    if cam._t2_indice < len(cam._t2_demos):
        astro = cam._t2_demos[cam._t2_indice]
        llegó = cam.mover_hacia(astro.rect.center)
        if llegó and not getattr(cam, '_t2_foto_tomada', False):
            cam._t2_foto_tomada = True
            flash_activo, flash_tiempo = True, tiempo_actual
            cam._t2_fotos -= 1
            cam._t2_indice += 1
            astro.kill()
            cam._t2_foto_tomada = False

    fotos_tutorial = cam._t2_fotos
    astros_grupo.draw(pantalla)
    cam.update()
    camara.draw(pantalla)
    dibujar_tomar_fotos()
    mostrar_camaras(fotos_tutorial)
    mostrar_flash()


def actualizar_intermision3():
    """Lógica de renderizado del tutorial 3 (objetivo demo)."""
    global flash_activo, flash_tiempo

    tiempo_actual = pygame.time.get_ticks()
    cam = camara.sprite

    if not hasattr(cam, '_t3_init'):
        cam._t3_init   = True
        cam._t3_indice = 0
        cam._t3_pts    = 0
        cam._t3_demos  = _crear_astros_demo(
            ["Luna", "Marte", "Venus"],
            [(ANCHO//2+200, ALTO//2), (ANCHO//2-150, ALTO//2-80), (ANCHO//2+100, ALTO//2-120)]
        )

    if cam._t3_indice < len(cam._t3_demos):
        astro = cam._t3_demos[cam._t3_indice]
        distancia = math.dist(astro.rect.center, cam.rect.center)
        astro.image.set_alpha(int((1 - distancia / astro.radio_deteccion) * 255)
                              if distancia < astro.radio_deteccion else 0)

        llegó = cam.mover_hacia(astro.rect.center)
        if llegó and not getattr(cam, '_t3_foto_tomada', False):
            cam._t3_foto_tomada = True
            flash_activo, flash_tiempo = True, tiempo_actual
            cam._t3_pts    += 100
            cam._t3_indice += 1
            astro.kill()
            cam._t3_foto_tomada = False

    astros_grupo.draw(pantalla)
    cam.update()
    camara.draw(pantalla)
    mostrar_puntos_partida(cam._t3_pts)
    dibujar_objetivo()
    mostrar_flash()


def limpiar_tutorial2(cam):
    limpiar_atributos_tutorial(cam, '_t2_init', '_t2_indice', '_t2_fotos',
                                    '_t2_demos', '_t2_foto_tomada')


def limpiar_tutorial3(cam):
    limpiar_atributos_tutorial(cam, '_t3_init', '_t3_indice', '_t3_pts',
                                    '_t3_demos', '_t3_foto_tomada')


# ---------------------------------------------------------------------------
# Manejo de eventos por estado
# ---------------------------------------------------------------------------

def eventos_menu(event):
    global estado_actual, nombre_jugador, nombre_erroneo
    global tiempo_inicio_intermision1, astros_grupo, puntuacion, puntuacion_total_partida
    global tipo_pausa, fotos_tutorial, jugadores_ordenados, scroll_offset
    global objetivo_completado, boton_salir_rect

    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            if nombre_jugador:
                guardar_puntuacion()
            pygame.quit()
            exit()
        if event.key in (pygame.K_SPACE, pygame.K_RETURN):
            if nombre_jugador and nombre_jugador.lower() not in nombres_existentes:
                tiempo_inicio_intermision1 = pygame.time.get_ticks()
                astros_grupo = pygame.sprite.Group()
                puntuacion = puntuacion_total_partida = 0
                tipo_pausa = ""
                fotos_tutorial = FOTOS_INICIALES
                objetivo_completado = True
                crear_astros()
                estado_actual = ESTADO_INTERMISION1
            elif nombre_jugador:
                nombre_erroneo = True
        elif event.key == pygame.K_BACKSPACE:
            nombre_jugador = nombre_jugador[:-1]
            nombre_erroneo = False
        else:
            if len(nombre_jugador) < 10:
                nombre_jugador += event.unicode
                nombre_erroneo = nombre_jugador.lower() in nombres_existentes

    if event.type == pygame.MOUSEBUTTONDOWN:
        if boton_puntajes_rect.collidepoint(event.pos):
            datos = cargar_scores()
            jugadores_ordenados = sorted(
                datos["jugadores"].items(),
                key=lambda x: x[1]["puntuacion_total"], reverse=True
            )
            scroll_offset = 0
            estado_actual = ESTADO_PUNTAJES
        if boton_salir_rect.collidepoint(event.pos):
            if nombre_jugador:
                guardar_puntuacion()
            pygame.quit()
            exit()


def eventos_puntajes(event):
    global estado_actual, scroll_offset, pagina_actual_album
    global album_puntajes_clave, fotos_album_puntajes

    if event.type == pygame.KEYDOWN:
        if event.key in (pygame.K_m, pygame.K_ESCAPE):
            estado_actual = ESTADO_MENU
        elif event.key == pygame.K_UP:
            scroll_offset = max(0, scroll_offset - 50)
        elif event.key == pygame.K_DOWN:
            scroll_offset += 50
    if event.type == pygame.MOUSEWHEEL:
        scroll_offset = max(0, scroll_offset - event.y * 40)
    if event.type == pygame.MOUSEBUTTONDOWN:
        if boton_volver_rect.collidepoint(event.pos):
            estado_actual = ESTADO_MENU
            return
        for entry in puntajes_rects:
            if entry["rect"].collidepoint(event.pos):
                cargar_assets_reales()
                album_puntajes_clave  = entry["nombre"]
                pagina_actual_album   = 0
                fotos_album_puntajes  = construir_fotos_album(entry["datos"]["astros_descubiertos"])
                pag_slide_album_activa = False
                pag_slide_album_solicitada = 0
                pag_slide_album_captura = None
                estado_actual         = ESTADO_ALBUM_PUNTAJES
                break


def eventos_album_puntajes(event):
    global estado_actual, pagina_actual_album, pag_slide_album_solicitada, pag_slide_album_activa

    hay_slide_album = pag_slide_album_activa or pag_slide_album_solicitada != 0

    if event.type == pygame.KEYDOWN:
        if event.key in (pygame.K_m, pygame.K_ESCAPE):
            estado_actual = ESTADO_PUNTAJES
        elif event.key == pygame.K_LEFT and not hay_slide_album:
            posiciones_pagina = calcular_posiciones_pagina(astros)
            if _solicitar_slide_pagina(-1, len(posiciones_pagina), pag_slide_album_solicitada, pagina_actual_album):
                pag_slide_album_solicitada = -1
        elif event.key == pygame.K_RIGHT and not hay_slide_album:
            posiciones_pagina = calcular_posiciones_pagina(astros)
            if _solicitar_slide_pagina(1, len(posiciones_pagina), pag_slide_album_solicitada, pagina_actual_album):
                pag_slide_album_solicitada = 1
    if event.type == pygame.MOUSEWHEEL:
        if not hay_slide_album:
            posiciones_pagina = calcular_posiciones_pagina(astros)
            total = len(posiciones_pagina)
            direccion = -1 if event.y > 0 else 1
            if _solicitar_slide_pagina(direccion, total, pag_slide_album_solicitada, pagina_actual_album):
                pag_slide_album_solicitada = direccion
    if event.type == pygame.MOUSEBUTTONDOWN:
        if boton_volver_rect.collidepoint(event.pos):
            estado_actual = ESTADO_PUNTAJES
            return
        pos = event.pos
        # Revelar / pegar fotos
        for f in fotos_album_puntajes:
            if f.estado == 'revelada' and f.rect.collidepoint(pos):
                f.pegar(instantaneo=True); return
        # Solo una foto despegada a la vez
        if not any(f.estado == 'revelada' for f in fotos_album_puntajes):
            for f in fotos_album_puntajes:
                if f.estado == 'pegada' and f.rect.collidepoint(pos) and f.pagina == pagina_actual_album:
                    f.revelar_ampliado(); return
        if hay_slide_album:
            return
        # Flechas
        if pagina_actual_album > 0:
            if pygame.Rect(FLECHA_IZQ_X, FLECHA_Y, TAM_FLECHA, TAM_FLECHA).collidepoint(pos):
                pag_slide_album_solicitada = -1; return
        if pygame.Rect(FLECHA_DER_X, FLECHA_Y, TAM_FLECHA, TAM_FLECHA).collidepoint(pos):
            pag_slide_album_solicitada = 1
    if event.type == pygame.MOUSEMOTION:
        for f in fotos_album_puntajes:
            f.hover = f.estado == 'revelada' and f.rect.collidepoint(event.pos)


def eventos_jugando(event):
    global fotos, flash_activo, flash_tiempo, puntuacion, puntuacion_total_partida
    global tiempo_pausado, tipo_pausa, tiempo_fotos_agotadas

    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not tiempo_pausado:
        fotos -= 1
        flash_activo, flash_tiempo = True, pygame.time.get_ticks()
        p = tomar_foto()
        puntuacion             += p
        puntuacion_total_partida += p
        if (nivel == 5 and objetivo_actual() <= 0) or (nivel != 5 and puntuacion >= objetivo_actual()):
            tiempo_pausado       = True
            tipo_pausa           = "objetivo"
            tiempo_fotos_agotadas = pygame.time.get_ticks()
        elif fotos <= 0:
            tiempo_pausado       = True
            tipo_pausa           = "fotos"
            tiempo_fotos_agotadas = pygame.time.get_ticks()


def _solicitar_slide_pagina(direccion, total_pags, slide_solicitada, pagina_actual_val):
    """Helper: solicita una animación de cambio de página si es válida."""
    if slide_solicitada != 0:
        return False
    nueva = pagina_actual_val + direccion
    if nueva < 0 or nueva >= total_pags:
        return False
    return True


def eventos_reporte(event):
    global estado_actual, nivel, puntuacion, puntuacion_total_partida
    global fotos, fotos_reporte_instancias, fotos_pegadas_permanentes
    global album, coleccion, nombre_jugador, pagina_actual
    global tiempo_inicio_intermision_mejora, tipo_pausa, fotos_tutorial
    global pag_slide_solicitada, pag_slide_activa

    todas_pegadas = all(f.estado == 'pegada' for f in fotos_reporte_instancias)
    todas_fotos = fotos_reporte_instancias + fotos_permanentes_vista
    hay_transicion = any(f.estado in ('girando', 'revelada', 'pegando') for f in todas_fotos)
    hay_slide = pag_slide_activa or pag_slide_solicitada != 0

    if event.type == pygame.MOUSEMOTION:
        for f in todas_fotos:
            f.hover = f.estado == 'revelada' and f.rect.collidepoint(event.pos)

    if event.type == pygame.MOUSEBUTTONDOWN:
        # Si hay foto revelada, cualquier click la pega (incluso durante transición)
        for f in todas_fotos:
            if f.estado == 'revelada':
                f.pegar()
                if f in fotos_reporte_instancias:
                    pos_idx = next((a.get("posicion") for a in astros if a["nombre"] == f.clave), None)
                    if pos_idx is not None:
                        pag, slot = obtener_pagina_slot(pos_idx)
                        entrada = (f.clave, pag, slot)
                        if entrada not in fotos_pegadas_permanentes:
                            fotos_pegadas_permanentes.append(entrada)
                        pagina_actual = pag
                return

        # Bloquear todo mientras hay animación en curso
        if hay_transicion or hay_slide:
            return

        pos = event.pos

        # Revelar foto oculta
        for f in fotos_reporte_instancias:
            if f.estado == 'oculta_en_libro' and f.rect_miniatura.collidepoint(pos):
                f.estado = 'girando'; return

        # Flechas de página
        total_paginas = len(calcular_posiciones_pagina(astros))
        if _solicitar_slide_pagina(-1, total_paginas, pag_slide_solicitada, pagina_actual):
            if pygame.Rect(FLECHA_IZQ_X, FLECHA_Y, TAM_FLECHA, TAM_FLECHA).collidepoint(pos):
                pag_slide_solicitada = -1; return
        if _solicitar_slide_pagina(1, total_paginas, pag_slide_solicitada, pagina_actual):
            if pygame.Rect(FLECHA_DER_X, FLECHA_Y, TAM_FLECHA, TAM_FLECHA).collidepoint(pos):
                pag_slide_solicitada = 1

    if event.type == pygame.KEYDOWN:
        if hay_transicion or hay_slide:
            return  # Bloquear teclado mientras hay animación

        if event.key == pygame.K_SPACE:
            if todas_pegadas:
                _avanzar_o_reiniciar()
            else:
                for f in fotos_reporte_instancias:
                    if f.estado == 'oculta_en_libro':
                        f.estado = 'girando'; break

        if event.key == pygame.K_m:
            guardar_puntuacion()
            nombres_existentes.add(nombre_jugador.lower())
            _resetear_partida_completa()
            estado_actual = ESTADO_MENU


def _avanzar_o_reiniciar():
    global nivel, puntuacion, puntuacion_total_partida, estado_actual
    global fotos, fotos_reporte_instancias, fotos_permanentes_vista
    global album, coleccion, fotos_pegadas_permanentes
    global fotos_tutorial, tipo_pausa, tiempo_inicio_intermision_mejora
    global puntos_flotantes
    global felicitacion_fotos, felicitacion_puntaje, felicitacion_ticks
    global objetivo_completado, astros_grupo

    if (nivel == 5 and objetivo_actual() <= 0) or (nivel != 5 and puntuacion >= objetivo_actual()):
        objetivo_completado = True
        if nivel == 5:
            # ¡Juego completo! Mostrar pantalla de felicitación
            felicitacion_fotos   = len(set(a["nombre"] for a in album)) + len(set(a["nombre"] for a in coleccion))
            felicitacion_puntaje = puntuacion_total_partida + puntuacion
            felicitacion_ticks   = pygame.time.get_ticks()
            guardar_puntuacion()
            nombres_existentes.add(nombre_jugador.lower())
            estado_actual = ESTADO_FELICITACION
            return
        else:
            nivel += 1
        coleccion.extend(album)
        album.clear()
        # Mantener astros no fotografiados, crear_astros() en INTERMISION4 agregará los del nuevo nivel
    else:
        objetivo_completado = False
        fotos_pegadas_permanentes.clear()
        album.clear()
        coleccion.clear()
        nivel = 1
        puntuacion_total_partida = 0
        astros_grupo = pygame.sprite.Group()

    puntuacion  = 0
    tipo_pausa  = ""
    fotos = fotos_tutorial = FOTOS_INICIALES
    camara.sprite.rect.center = (ANCHO // 2, ALTO // 2)
    fotos_reporte_instancias.clear()
    fotos_permanentes_vista.clear()
    puntos_flotantes.clear()
    tiempo_inicio_intermision_mejora = pygame.time.get_ticks()
    estado_actual = ESTADO_INTERMISION_MEJORA


def _resetear_partida_completa():
    global nivel, puntuacion, puntuacion_total_partida, fotos, fotos_tutorial
    global fotos_reporte_instancias, fotos_permanentes_vista
    global fotos_pegadas_permanentes, album, coleccion
    global nombre_jugador, tipo_pausa, objetivo_completado
    global puntos_flotantes

    fotos_pegadas_permanentes.clear()
    album.clear()
    coleccion.clear()
    fotos_reporte_instancias.clear()
    fotos_permanentes_vista.clear()
    puntos_flotantes.clear()
    nivel = 1
    puntuacion = puntuacion_total_partida = 0
    fotos = fotos_tutorial = FOTOS_INICIALES
    nombre_jugador = ""
    tipo_pausa = ""
    objetivo_completado = True
    objetivo_nivel5_inicial = 0


# ---------------------------------------------------------------------------
# Inicialización de pygame
# ---------------------------------------------------------------------------

pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("ArcSpace")
clock = pygame.time.Clock()
pantalla.fill((0, 0, 0))
pygame.display.flip()

fuente_titulo_grande = pygame.font.Font("assets/Fonts/Silkscreen/Silkscreen-Regular.ttf", 110)
fuente_titulo        = pygame.font.Font("assets/Fonts/Silkscreen/Silkscreen-Regular.ttf", 80)
fuente_media         = pygame.font.Font("assets/Fonts/Silkscreen/Silkscreen-Regular.ttf", 50)
fuente_normal        = pygame.font.Font("assets/Fonts/Silkscreen/Silkscreen-Regular.ttf", 30)
fuente_pequena       = pygame.font.Font("assets/Fonts/Silkscreen/Silkscreen-Regular.ttf", 20)
fuente_puntos        = pygame.font.Font("assets/Fonts/Lato/Lato-Thin.ttf", 20)

# Pantalla de carga
carga = fuente_normal.render("Cargando...", False, (255, 255, 255))
pantalla.blit(carga, carga.get_rect(center=(ANCHO // 2, ALTO // 2)))
pygame.display.flip()
pygame.event.pump()

# ---------------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------------

img_camara       = cargar_imagen("assets/Graphics/Camara.png", (60, 60))
fondo            = cargar_imagen("assets/Graphics/fondo.png", (ANCHO, ALTO))
img_up           = cargar_imagen("assets/Graphics/Keyboard & Mouse/Default/keyboard_arrow_up.png")
img_down         = cargar_imagen("assets/Graphics/Keyboard & Mouse/Default/keyboard_arrow_down.png")
img_left         = cargar_imagen("assets/Graphics/Keyboard & Mouse/Default/keyboard_arrow_left.png")
img_right        = cargar_imagen("assets/Graphics/Keyboard & Mouse/Default/keyboard_arrow_right.png")
img_m            = cargar_imagen("assets/Graphics/Keyboard & Mouse/Default/keyboard_m.png")
img_mouse_left   = cargar_imagen("assets/Graphics/Keyboard & Mouse/Default/mouse_left.png")
img_uibook       = cargar_imagen("assets/Graphics/UIBook.png", (830, 500))
img_nacional     = escalar_proporcional(cargar_imagen("assets/Graphics/Nacional.png"), 32, 32)

_space_raw       = cargar_imagen("assets/Graphics/Keyboard & Mouse/Double/keyboard_space.png")
img_space        = _space_raw.subsurface((0, 36, 128, 56)).copy()

img_arrow_l      = pygame.transform.scale(img_left, (50, 50))
img_arrow_r      = pygame.transform.scale(img_right, (50, 50))
img_m_icon       = pygame.transform.scale(img_m, (30, 30))
img_mouse_icon   = pygame.transform.scale(img_mouse_left, (30, 38))
img_space_inst   = pygame.transform.scale(img_space, (96, 42))
img_camara_icon  = pygame.transform.scale(img_camara, (50, 50))

datos_teclas = [
    {"img": img_up,    "offset": (0, -50)},
    {"img": img_down,  "offset": (0,   0)},
    {"img": img_left,  "offset": (-50, 0)},
    {"img": img_right, "offset": (50,  0)},
]

assets_astros = {
    "Luna":            cargar_imagen("assets/Graphics/Astros/Luna.png",         (140, 140)),
    "Venus":           cargar_imagen("assets/Graphics/Astros/Venus.png",        (140, 140)),
    "Mercurio":        cargar_imagen("assets/Graphics/Astros/Mercurio.png",     (140, 140)),
    "Marte":           cargar_imagen("assets/Graphics/Astros/Marte.png",        (140, 140)),
    "Estacion":        cargar_imagen("assets/Graphics/Astros/Estacion.png",     (80,   80)),
    "Jupiter":         cargar_imagen("assets/Graphics/Astros/Jupiter.png",      (140, 140)),
    "Saturno":         cargar_imagen("assets/Graphics/Astros/Saturno.png",      (140,  84)),
    "Urano":           cargar_imagen("assets/Graphics/Astros/Urano.png",        (140, 140)),
    "Neptuno":         cargar_imagen("assets/Graphics/Astros/Neptuno.png",      (140, 140)),
    "Estrella":        cargar_imagen("assets/Graphics/Astros/Estrella.png",     (45,   45)),
    "CometaHalley":    cargar_imagen("assets/Graphics/Astros/Cometa.png",       (140, 140)),
    "AgujeroNegro":    cargar_imagen("assets/Graphics/Astros/Agujero.png",      (140,  76)),
    "Nebulosa":        cargar_imagen("assets/Graphics/Astros/Nebulosa.png",     (140, 140)),
    "Galaxia":         cargar_imagen("assets/Graphics/Astros/Galaxia.png",      (140, 140)),
    "Agujero De Gusano": cargar_imagen("assets/Graphics/Astros/Gusano.png",     (140, 140)),
    "Ovni":            cargar_imagen("assets/Graphics/Astros/Ovni.png",         (140, 140)),
}
assets_reales = {}
_thumb_cache = {}  # clave -> surface escalada a 80×80 (proporcional)

# Datos
astros = []
with open("data/astros.json", "r") as f:
    for item in json.load(f)["astros"]:
        astros.append(item)

# ---------------------------------------------------------------------------
# Estado global del juego
# ---------------------------------------------------------------------------

estado_actual = ESTADO_MENU

fotos          = FOTOS_INICIALES
fotos_tutorial = FOTOS_INICIALES
puntuacion     = 0
puntuacion_total_partida = 0
nivel          = 1
objetivo_completado = True

album                    = []
coleccion                = []
fotos_reporte_instancias  = []
fotos_permanentes_vista   = []   # instancias FotoReporte para fotos de rondas anteriores
fotos_pegadas_permanentes = []
puntos_flotantes          = []  # {"puntos", "centro", "tiempo"}

# Animación de cambio de página (reporte)
pag_slide_activa      = False
pag_slide_inicio      = 0
pag_slide_captura     = None
pag_slide_solicitada  = 0   # -1 izquierda, 1 derecha

# Animación de cambio de página (album_puntajes)
pag_slide_album_activa      = False
pag_slide_album_inicio      = 0
pag_slide_album_captura     = None
pag_slide_album_solicitada  = 0

PAG_SLIDE_DURACION = 200  # ms
objetivo_nivel5_inicial = 0  # snapshot del objetivo al comenzar nivel 5

felicitacion_fotos   = 0
felicitacion_puntaje = 0
felicitacion_ticks   = 0
felicitacion_boton_jugar_rect = pygame.Rect(0, 0, 0, 0)
felicitacion_boton_menu_rect  = pygame.Rect(0, 0, 0, 0)

flash_activo = False
flash_tiempo = 0

tiempo_pausado        = False
tiempo_fotos_agotadas = 0
tipo_pausa            = ""
ticks_inicio_juego    = 0

tiempo_inicio_intermision1     = 0
tiempo_inicio_intermision2     = 0
tiempo_inicio_intermision3     = 0
tiempo_inicio_intermision4     = 0
tiempo_inicio_intermision_mejora = 0
tiempo_inicio_intermision_pausa  = 0

nombre_jugador  = ""
nombre_erroneo  = False
scroll_offset   = 0
jugadores_ordenados = []
boton_puntajes_rect = pygame.Rect(0, 0, 0, 0)
boton_salir_rect    = pygame.Rect(0, 0, 0, 0)
boton_volver_rect   = pygame.Rect(0, 0, 0, 0)
puntajes_rects      = []

pagina_actual        = 0
pagina_actual_album  = 0
album_puntajes_clave = ""
fotos_album_puntajes = []

total_paginas = len(calcular_posiciones_pagina(astros))

scores = []
nombres_existentes = set()
datos_scores = cargar_scores()
scores = datos_scores.get("top_scores", [])
if "jugadores" in datos_scores:
    nombres_existentes = {k.lower() for k in datos_scores["jugadores"]}

astros_grupo = pygame.sprite.Group()
camara       = pygame.sprite.GroupSingle()
camara.add(Camara(ANCHO, ALTO))

# ---------------------------------------------------------------------------
# Pantalla: Felicitación final (nivel 5 completado)
# ---------------------------------------------------------------------------

def mostrar_felicitacion():
    """Pantalla de celebración al completar el nivel 5."""
    global felicitacion_boton_jugar_rect, felicitacion_boton_menu_rect
    t     = pygame.time.get_ticks() / 1000
    since = pygame.time.get_ticks() - felicitacion_ticks

    # --- Fondo: destellos de estrellas ---
    if not hasattr(mostrar_felicitacion, '_stars'):
        import random as _rnd
        mostrar_felicitacion._stars = [
            (_rnd.randint(0, ANCHO), _rnd.randint(0, ALTO),
             _rnd.uniform(0.5, 2.5), _rnd.uniform(0, math.pi * 2))
            for _ in range(120)
        ]
    for sx, sy, spd, phase in mostrar_felicitacion._stars:
        a = int(120 + 120 * math.sin(t * spd + phase))
        sz = max(1, int(1 + math.sin(t * spd + phase + 1)))
        c = (255, 215, 0) if (sx + sy) % 3 == 0 else (200, 150, 255) if (sx + sy) % 3 == 1 else (255, 255, 255)
        star_s = pygame.Surface((sz * 2, sz * 2), pygame.SRCALPHA)
        pygame.draw.circle(star_s, (*c, a), (sz, sz), sz)
        pantalla.blit(star_s, (sx - sz, sy - sz))

    # --- Título con gradiente y flotación ---
    float_y = int(ALTO // 6 + math.sin(t * 1.2) * 8)
    if not hasattr(mostrar_felicitacion, '_titulo'):
        mostrar_felicitacion._titulo = render_gradiente_texto(
            fuente_titulo_grande, "¡FELICIDADES!", (255, 215, 0), (200, 80, 255))
        mostrar_felicitacion._sub = fuente_media.render("Completaste el album", False, (255, 255, 255))
    titulo = mostrar_felicitacion._titulo
    # Halo con alpha variable (se crea cada frame, un solo ellipse es barato)
    halo_a = int(60 + 40 * math.sin(t * 2))
    halo = pygame.Surface((titulo.get_width() + 60, titulo.get_height() + 30), pygame.SRCALPHA)
    pygame.draw.ellipse(halo, (255, 215, 0, halo_a), halo.get_rect())
    pantalla.blit(halo, halo.get_rect(center=(ANCHO // 2, float_y)))
    pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, float_y)))

    # --- Subtítulo ---
    sub = mostrar_felicitacion._sub
    pantalla.blit(sub, sub.get_rect(center=(ANCHO // 2, float_y + 90)))

    # --- Panel central de estadísticas ---
    if not hasattr(mostrar_felicitacion, '_panel'):
        mostrar_felicitacion._panel_w, mostrar_felicitacion._panel_h = 760, 200
        panel_surf = pygame.Surface((mostrar_felicitacion._panel_w, mostrar_felicitacion._panel_h), pygame.SRCALPHA)
        for px_ in range(mostrar_felicitacion._panel_w):
            gt = px_ / max(mostrar_felicitacion._panel_w - 1, 1)
            pr = int(40 + gt * 60)
            pg = int(0)
            pb = int(80 + gt * 80)
            pygame.draw.line(panel_surf, (pr, pg, pb, 210), (px_, 0), (px_, mostrar_felicitacion._panel_h))
        mostrar_felicitacion._panel = panel_surf
    panel_w, panel_h = mostrar_felicitacion._panel_w, mostrar_felicitacion._panel_h
    panel_x = (ANCHO - panel_w) // 2
    panel_y = ALTO // 2 - 60
    panel_surf = mostrar_felicitacion._panel.copy()
    pulse_b = 0.5 + 0.5 * math.sin(t * 2.5)
    ba = int(160 + 80 * pulse_b)
    pygame.draw.rect(panel_surf, (255, 215, 0, ba), (0, 0, panel_w, panel_h), 3, border_radius=20)
    pygame.draw.rect(panel_surf, (0, 0, 0, 0), (0, 0, panel_w, panel_h), border_radius=20)
    pantalla.blit(panel_surf, (panel_x, panel_y))

    # Ícono cámara + fotos tomadas
    cam_icon = img_camara_icon
    pantalla.blit(cam_icon, (panel_x + 70, panel_y + panel_h // 2 - 50))
    lbl_fotos = fuente_normal.render("FOTOS", False, (200, 200, 255))
    val_fotos = fuente_titulo.render(str(felicitacion_fotos), False, (255, 215, 0))
    pantalla.blit(lbl_fotos, (panel_x + 140, panel_y + 30))
    pantalla.blit(val_fotos, (panel_x + 140, panel_y + 65))

    # Separador vertical
    pygame.draw.line(pantalla, (255, 215, 0, 120),
                     (panel_x + panel_w // 2, panel_y + 20),
                     (panel_x + panel_w // 2, panel_y + panel_h - 20), 2)

    # Estrella + puntaje (dibujada con polígonos: la fuente Silkscreen no incluye ★)
    cx_star = panel_x + panel_w // 2 + 70
    cy_star = panel_y + panel_h // 2 - 25
    star_size = 28
    puntos_estrella = []
    for i in range(10):
        ang = math.radians(-90 + i * 36)
        r = star_size if i % 2 == 0 else star_size * 0.4
        puntos_estrella.append((cx_star + r * math.cos(ang), cy_star + r * math.sin(ang)))
    pygame.draw.polygon(pantalla, (255, 215, 0), puntos_estrella)
    lbl_pts = fuente_normal.render("PUNTAJE", False, (200, 200, 255))
    val_pts = fuente_titulo.render(str(felicitacion_puntaje), False, (255, 215, 0))
    pantalla.blit(lbl_pts, (panel_x + panel_w // 2 + 110, panel_y + 30))
    pantalla.blit(val_pts, (panel_x + panel_w // 2 + 110, panel_y + 65))

    # --- Botones ---
    btn_y = panel_y + panel_h + 60
    mouse  = pygame.mouse.get_pos()

    def _btn_felicit(texto, cx, highlight):
        pulse2 = 0.5 + 0.5 * math.sin(t * 3 + cx)
        surf_t = fuente_normal.render(texto, False, (255, 255, 255))
        r = surf_t.get_rect(center=(cx, btn_y))
        bg = r.inflate(30, 16)
        hover = bg.collidepoint(mouse)
        color_bg = (180, 80, 255) if hover else (100, 0, 200)
        if hover:
            glow_s = pygame.Surface((bg.width + 20, bg.height + 20), pygame.SRCALPHA)
            ga2 = int(60 + 40 * pulse2)
            pygame.draw.rect(glow_s, (200, 100, 255, ga2),
                             (0, 0, bg.width + 20, bg.height + 20), border_radius=14)
            pantalla.blit(glow_s, (bg.x - 10, bg.y - 10))
        pygame.draw.rect(pantalla, color_bg, bg, border_radius=10)
        pygame.draw.rect(pantalla, (255, 215, 0) if highlight else (200, 100, 255), bg, 2, border_radius=10)
        pantalla.blit(surf_t, r)
        return bg

    felicitacion_boton_jugar_rect = _btn_felicit("JUGAR DE NUEVO", ANCHO // 2 - 170, True)
    felicitacion_boton_menu_rect  = _btn_felicit("VOLVER AL MENU", ANCHO // 2 + 170, False)

    # --- Hint de teclado ---
    hint = fuente_pequena.render("ESPACIO = Jugar de nuevo   |   M = Menú", False, (180, 180, 180))
    pantalla.blit(hint, hint.get_rect(center=(ANCHO // 2, ALTO - 30)))


def eventos_felicitacion(event):
    global estado_actual
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE:
            _iniciar_nueva_partida_felicit()
        elif event.key in (pygame.K_m, pygame.K_ESCAPE):
            _resetear_partida_completa()
            estado_actual = ESTADO_MENU
    if event.type == pygame.MOUSEBUTTONDOWN:
        pos = event.pos
        if felicitacion_boton_jugar_rect.collidepoint(pos):
            _iniciar_nueva_partida_felicit()
        elif felicitacion_boton_menu_rect.collidepoint(pos):
            _resetear_partida_completa()
            estado_actual = ESTADO_MENU


def _iniciar_nueva_partida_felicit():
    global estado_actual, nivel, puntuacion, puntuacion_total_partida
    global fotos, fotos_tutorial, fotos_reporte_instancias, fotos_permanentes_vista
    global fotos_pegadas_permanentes, album, coleccion, tipo_pausa
    global nombre_jugador, tiempo_inicio_intermision1, objetivo_completado

    fotos_pegadas_permanentes.clear()
    album.clear()
    coleccion.clear()
    fotos_reporte_instancias.clear()
    fotos_permanentes_vista.clear()
    nivel = 1
    puntuacion = puntuacion_total_partida = 0
    fotos = fotos_tutorial = FOTOS_INICIALES
    tipo_pausa = ""
    nombre_jugador = ""
    objetivo_completado = True
    if hasattr(mostrar_felicitacion, '_stars'):
        del mostrar_felicitacion._stars
    estado_actual = ESTADO_MENU


# ---------------------------------------------------------------------------
# Bucle principal
# ---------------------------------------------------------------------------

while True:
    # ---- Eventos ----
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if nombre_jugador:
                guardar_puntuacion()
            pygame.quit()
            exit()

        if   estado_actual == ESTADO_MENU:             eventos_menu(event)
        elif estado_actual == ESTADO_PUNTAJES:         eventos_puntajes(event)
        elif estado_actual == ESTADO_ALBUM_PUNTAJES:   eventos_album_puntajes(event)
        elif estado_actual == ESTADO_JUGANDO:          eventos_jugando(event)
        elif estado_actual == ESTADO_REPORTE:          eventos_reporte(event)
        elif estado_actual == ESTADO_FELICITACION:     eventos_felicitacion(event)

        # Tutoriales: saltar con ESPACIO
        elif estado_actual == ESTADO_INTERMISION1:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                for a in astros_grupo: a.kill()
                camara.sprite.rect.center = (ANCHO // 2, ALTO // 2)
                tiempo_inicio_intermision2 = pygame.time.get_ticks()
                estado_actual = ESTADO_INTERMISION2

        elif estado_actual == ESTADO_INTERMISION2:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                for a in astros_grupo: a.kill()
                camara.sprite.rect.center = (ANCHO // 2, ALTO // 2)
                limpiar_tutorial2(camara.sprite)
                tiempo_inicio_intermision3 = pygame.time.get_ticks()
                estado_actual = ESTADO_INTERMISION3

        elif estado_actual == ESTADO_INTERMISION3:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                for a in astros_grupo: a.kill()
                camara.sprite.rect.center = (ANCHO // 2, ALTO // 2)
                limpiar_tutorial3(camara.sprite)
                fotos = FOTOS_INICIALES
                tiempo_inicio_intermision4 = pygame.time.get_ticks()
                estado_actual = ESTADO_INTERMISION4

        elif estado_actual == ESTADO_INTERMISION4:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                fotos = FOTOS_INICIALES
                camara.sprite.rect.center = (ANCHO // 2, ALTO // 2)
                ticks_inicio_juego = pygame.time.get_ticks()
                crear_astros()
                estado_actual = ESTADO_JUGANDO

        elif estado_actual == ESTADO_INTERMISION_MEJORA:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                tiempo_inicio_intermision4 = pygame.time.get_ticks()
                estado_actual = ESTADO_INTERMISION4

        elif estado_actual == ESTADO_INTERMISION_PAUSA:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                fotos_reporte_instancias.clear()
                pagina_actual = 0
                fotos = FOTOS_INICIALES
                estado_actual = ESTADO_REPORTE

    # ---- Dibujo ----
    pantalla.blit(fondo, (0, 0))

    if estado_actual == ESTADO_MENU:
        mostrar_menu()

    elif estado_actual == ESTADO_INTERMISION1:
        dibujar_controles()
        camara.sprite.update()
        camara.sprite.automatico()
        pos_v = camara.sprite.rect.center
        for a in astros_grupo:
            a.update_visual(pos_v)
        astros_grupo.draw(pantalla)
        camara.draw(pantalla)
        if asignar_tiempo_transicion(tiempo_inicio_intermision1):
            for a in astros_grupo: a.kill()
            camara.sprite.rect.center = (ANCHO // 2, ALTO // 2)
            tiempo_inicio_intermision2 = pygame.time.get_ticks()
            estado_actual = ESTADO_INTERMISION2

    elif estado_actual == ESTADO_INTERMISION2:
        actualizar_intermision2()
        if camara.sprite._t2_fotos == 0 or asignar_tiempo_transicion(tiempo_inicio_intermision2):
            for a in astros_grupo: a.kill()
            limpiar_tutorial2(camara.sprite)
            fotos = FOTOS_INICIALES
            tiempo_inicio_intermision3 = pygame.time.get_ticks()
            estado_actual = ESTADO_INTERMISION3

    elif estado_actual == ESTADO_INTERMISION3:
        actualizar_intermision3()
        if asignar_tiempo_transicion(tiempo_inicio_intermision3):
            for a in astros_grupo: a.kill()
            limpiar_tutorial3(camara.sprite)
            fotos = FOTOS_INICIALES
            tiempo_inicio_intermision4 = pygame.time.get_ticks()
            estado_actual = ESTADO_INTERMISION4

    elif estado_actual == ESTADO_INTERMISION4:
        t = (pygame.time.get_ticks() - tiempo_inicio_intermision4) / 1000
        textos_cuenta = {0: ("PREPARATE", (255,255,255)), 1: ("3",(255,255,255)),
                         2: ("2",(255,255,255)), 3: ("1",(255,255,255)), 4: ("A JUGAR",(0,255,0))}
        idx_t = int(t) if t < 5 else None
        if idx_t is None:
            fotos = FOTOS_INICIALES
            camara.sprite.rect.center = (ANCHO // 2, ALTO // 2)
            ticks_inicio_juego = pygame.time.get_ticks()
            crear_astros()
            estado_actual = ESTADO_JUGANDO
        else:
            msg, col = textos_cuenta[min(idx_t, 4)]
            txt = fuente_titulo.render(msg, False, col)
            pantalla.blit(txt, txt.get_rect(center=(ANCHO // 2, ALTO // 2)))

    elif estado_actual == ESTADO_INTERMISION_MEJORA:
        t = (pygame.time.get_ticks() - tiempo_inicio_intermision_mejora) / 1000
        if t < 3:
            if objetivo_completado:
                t1 = fuente_media.render("Camara mejorada", False, (255, 215, 0))
                t2 = fuente_normal.render("Ahora puedes ver mas lejos", False, (255, 255, 255))
            else:
                t1 = fuente_media.render("INTENTA DE NUEVO", False, (255, 100, 100))
                t2 = fuente_normal.render("Vuelve a intentar el nivel", False, (255, 255, 255))
            pantalla.blit(t1, t1.get_rect(center=(ANCHO // 2, ALTO // 2 - 20)))
            pantalla.blit(t2, t2.get_rect(center=(ANCHO // 2, ALTO // 2 + 30)))
        else:
            tiempo_inicio_intermision4 = pygame.time.get_ticks()
            estado_actual = ESTADO_INTERMISION4

    elif estado_actual == ESTADO_INTERMISION_PAUSA:
        t = (pygame.time.get_ticks() - tiempo_inicio_intermision_pausa) / 1000
        if tipo_pausa == "objetivo":
            color = (255, 215, 0)
            linea1 = "OBJETIVO COMPLETADO"
            linea2 = f"{puntuacion} / {objetivo_nivel5_inicial if nivel == 5 else objetivo_actual()} puntos"
        elif tipo_pausa == "fotos":
            color = (255, 100, 100)
            linea1 = "FOTOS AGOTADAS"
            linea2 = "Has usado todas las fotos"
        else:
            color = (255, 100, 100)
            linea1 = "TIEMPO AGOTADO"
            linea2 = "Se acabo el tiempo"
        txt1 = fuente_titulo.render(linea1, False, color)
        txt2 = fuente_normal.render(linea2, False, (255, 255, 255))
        pantalla.blit(txt1, txt1.get_rect(center=(ANCHO // 2, ALTO // 2 - 30)))
        pantalla.blit(txt2, txt2.get_rect(center=(ANCHO // 2, ALTO // 2 + 30)))
        if t >= 2.5:
            fotos_reporte_instancias.clear()
            pagina_actual = 0
            fotos = FOTOS_INICIALES
            pag_slide_activa = False
            pag_slide_solicitada = 0
            pag_slide_captura = None
            estado_actual = ESTADO_REPORTE

    elif estado_actual == ESTADO_JUGANDO:
        mostrar_puntos_partida()

        if tiempo_pausado:
            tiempo_inicio_intermision_pausa = pygame.time.get_ticks()
            tiempo_pausado = False
            estado_actual = ESTADO_INTERMISION_PAUSA
        else:
            camara.update()
            t_transcurrido = (pygame.time.get_ticks() - ticks_inicio_juego) / 1000
            tiempo_restante = TIEMPO_INICIAL - t_transcurrido
            if tiempo_restante <= 0:
                tipo_pausa = "tiempo"
                tiempo_inicio_intermision_pausa = pygame.time.get_ticks()
                estado_actual = ESTADO_INTERMISION_PAUSA
            else:
                mostrar_tiempo(tiempo_restante)
                mostrar_camaras()

        pos_v = camara.sprite.rect.center
        for a in astros_grupo:
            a.update_visual(pos_v)
        astros_grupo.draw(pantalla)
        ahora = pygame.time.get_ticks()
        puntos_flotantes[:] = [e for e in puntos_flotantes if ahora - e["tiempo"] < 2000]
        for e in puntos_flotantes:
            txt = fuente_puntos.render(f"+{e['puntos']}", False, (255, 215, 0))
            tw, th = txt.get_size()
            cx, cy = e["centro"]
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx or dy:
                        pantalla.blit(txt, (cx - tw // 2 + dx, cy - th // 2 + dy))
            pantalla.blit(txt, (cx - tw // 2, cy - th // 2))
        if estado_actual == ESTADO_JUGANDO:
            camara.draw(pantalla)
        mostrar_flash()

    elif estado_actual == ESTADO_REPORTE:
        mostrar_reporte()

    elif estado_actual == ESTADO_PUNTAJES:
        mostrar_puntajes()

    elif estado_actual == ESTADO_ALBUM_PUNTAJES:
        mostrar_album_puntajes()

    elif estado_actual == ESTADO_FELICITACION:
        mostrar_felicitacion()

    pygame.display.update()
    clock.tick(60)
