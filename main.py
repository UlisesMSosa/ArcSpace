import pygame
import json
from sys import exit
from random import randint
import math
import datetime

class Camara(pygame.sprite.Sprite):
    def __init__(self, limite_ancho, limite_alto):
        super().__init__()
        radio = 50
        color_borde = (0, 255, 0)
        self.image = pygame.Surface((radio * 2, radio * 2 + 20), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center = (ancho/2, alto/2))
        self.velocidad = 4
        self.limite_ancho = limite_ancho
        self.limite_alto = limite_alto
        pygame.draw.circle(self.image, color_borde, (radio, radio), radio, 3)
        pygame.draw.line(self.image, color_borde, (45, 50), (55, 50), 2)
        pygame.draw.line(self.image, color_borde, (50, 45), (50, 55), 2)
        pygame.draw.rect(self.image, (255, 255, 255), (15, 100, 70, 25))
        if hasattr(self, 'mostrar_texto_foto') and self.mostrar_texto_foto:
            fuente = pygame.font.Font("assets/Fonts/Silkscreen/Silkscreen-Regular.ttf", 12)
            texto = fuente.render("FOTO", False, (0, 0, 0))
            texto_rect = texto.get_rect(center=(50, 112))
            self.image.blit(texto, texto_rect)

    def controlar_bordes(self):
        if self.rect.left < -80: 
            self.rect.left = -80
        if self.rect.right > self.limite_ancho + 80: 
            self.rect.right = self.limite_ancho + 80
        if self.rect.top < -70: 
            self.rect.top = -70
        if self.rect.bottom > self.limite_alto + 70: 
            self.rect.bottom = self.limite_alto + 70      

    def movimiento(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.velocidad
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.velocidad
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.velocidad
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.velocidad
        
        self.controlar_bordes()

    def automatico(self):
        if not hasattr(self, 'dir_auto'):
            self.dir_auto = 0
            self.cambio_dir = 0
        
        self.cambio_dir += 1
        if self.cambio_dir > 60:
            self.dir_auto = randint(0, 3)
            self.cambio_dir = 0
        
        if self.dir_auto == 0 and self.rect.x - self.velocidad >= 0:
            self.rect.x -= self.velocidad
        elif self.dir_auto == 1 and self.rect.x + self.velocidad <= ancho - self.rect.width:
            self.rect.x += self.velocidad
        elif self.dir_auto == 2 and self.rect.y - self.velocidad >= 0:
            self.rect.y -= self.velocidad
        elif self.dir_auto == 3 and self.rect.y + self.velocidad <= alto - self.rect.height:
            self.rect.y += self.velocidad

    def update(self):
        if estado_actual not in (ESTADO_INTERMISION1, ESTADO_INTERMISION2, ESTADO_INTERMISION3, ESTADO_INTERMISION4):
            self.movimiento()
        radio = 50
        self.image = pygame.Surface((radio * 2 + 100, radio * 2 + 80), pygame.SRCALPHA)
        color_borde = (0, 255, 0)
        pygame.draw.circle(self.image, color_borde, (100, 70), radio, 3)
        pygame.draw.line(self.image, color_borde, (95, 70), (105, 70), 2)
        pygame.draw.line(self.image, color_borde, (100, 65), (100, 75), 2)
        if estado_actual == ESTADO_JUGANDO:
            if hasattr(self, 'mostrar_texto_foto') and self.mostrar_texto_foto:
                if pygame.time.get_ticks() - self.tiempo_foto > 500:
                    self.mostrar_texto_foto = False
                else:
                    fuente = pygame.font.Font("assets/Fonts/Silkscreen/Silkscreen-Regular.ttf", 32)
                    texto = fuente.render(self.texto_foto, False, self.color_texto_foto)
                    texto_rect = texto.get_rect(center=(100, 140))
                    self.image.blit(texto, texto_rect)

class Astro(pygame.sprite.Sprite):
    def __init__(self, astro, posicion):
        super().__init__()
        self.nombre = astro["nombre"]
        self.puntos = astro["puntos"]
        self.image = assets_astros[self.nombre].copy()
        self.rect = self.image.get_rect(center = posicion)
        self.seleccionado = False
        self.radio_deteccion = 150
        self.image.set_alpha(0)
    
    def update_visual(self, pos_visor):
        distancia = math.dist(self.rect.center, pos_visor)

        if distancia < self.radio_deteccion:
            proporcion = 1 - (distancia / self.radio_deteccion)            
            nuevo_alpha = int(proporcion * 255)
            self.image.set_alpha(nuevo_alpha)
            
            if proporcion > 0.8:
                self.seleccionado = True 
            else:
                self.seleccionado = False
        else:
            self.image.set_alpha(0)
            self.seleccionado = False
    
    def update(self):
        pass


class FotoReporte(pygame.sprite.Sprite):
    def __init__(self, clave_astro, texto_astro, rect_miniatura, rect_destino, superficie_pixel, superficie_real):
        super().__init__()
        self.clave = clave_astro
        self.texto_astro = texto_astro
        self.rect_miniatura = rect_miniatura
        self.rect_destino = rect_destino
        self.superficie_pixel = superficie_pixel
        self.superficie_real = superficie_real
        self.estado = 'oculta_en_libro'
        self.angulo = 0.0
        self.hover = False
        pw, ph = superficie_pixel.get_size()
        escala = min(rect_destino.w / pw, rect_destino.h / ph)
        self.tamanio_normal = (int(pw * escala), int(ph * escala))
        self.tamanio_anim = (self.tamanio_normal[0] * 3, self.tamanio_normal[1] * 3)
        self.tamanio_relleno = (rect_destino.w, rect_destino.h)
        self.image = pygame.transform.scale(superficie_pixel, self.tamanio_normal)
        self.rect = self.image.get_rect(center=rect_miniatura.center)

    def update(self):
        if self.estado == 'girando':
            self.velocidad_angular = min(getattr(self, 'velocidad_angular', 0.02) + 0.003, 0.3)
            self.angulo += self.velocidad_angular
            seno = math.sin(self.angulo)
            factor_ancho = abs(seno)
            nuevo_ancho = max(int(self.tamanio_anim[0] * factor_ancho), 1)

            if seno >= 0:
                activa = self.superficie_pixel
            else:
                activa = pygame.transform.flip(self.superficie_pixel, True, False)

            self.image = pygame.transform.scale(activa, (nuevo_ancho, self.tamanio_anim[1]))
            self.rect = self.image.get_rect(center=(ancho // 2, alto // 2))

            if self.angulo >= 10 * math.pi and abs(seno) > 0.95:
                self.image = pygame.transform.scale(self.superficie_real, self.tamanio_anim)
                self.rect = self.image.get_rect(center=(ancho // 2, alto // 2))
                self.estado = 'revelada'

    def pegar(self):
        self.image = pygame.transform.scale(self.superficie_real, self.tamanio_relleno)
        self.rect = self.image.get_rect(center=self.rect_destino.center)
        self.estado = 'pegada'


def dibujar_controles():
    ancla = (ancho / 2, alto / 1.3)
    texto_mov = fuente_normal.render("MUEVE LA CAMARA Y ENCUENTRA LOS PLANETAS", False, (255,255,255))
    texto_mov_rect = texto_mov.get_rect(midbottom = tuple(a + b for a, b in zip(ancla, (0, -80))))
    
    for t in datos_teclas:
        ancla_flecha = tuple(a + b for a, b in zip(ancla, t["offset"]))
        rectangulo = t["img"].get_rect(center = ancla_flecha)
        pantalla.blit(t["img"], rectangulo)
    
    pantalla.blit(texto_mov, texto_mov_rect)

def dibujar_tomar_fotos():
    ancla = (ancho / 2, alto / 1.3)
    texto_foto = fuente_normal.render("TOMA FOTOS DEL ESPACIO", False, (255,255,255))
    texto_foto_rect = texto_foto.get_rect(midbottom = tuple(a + b for a, b in zip(ancla, (0, -80))))
    
    rect_espacio = img_space.get_rect(center = ancla)
    pantalla.blit(img_space, rect_espacio)
    
    pantalla.blit(texto_foto, texto_foto_rect)

def dibujar_objetivo():
    ancla = (ancho / 2, alto / 1.3)
    texto_obj = fuente_normal.render("CADA FOTO TE DA PUNTOS", False, (255,255,255))
    texto_obj_rect = texto_obj.get_rect(midbottom = tuple(a + b for a, b in zip(ancla, (0, -80))))
    pantalla.blit(texto_obj, texto_obj_rect)
    
    texto_obj2 = fuente_normal.render("COMPLETA EL OBJETIVO PARA PASAR DE NIVEL", False, (255,255,255))
    texto_obj2_rect = texto_obj2.get_rect(midbottom = tuple(a + b for a, b in zip(ancla, (0, -40))))
    pantalla.blit(texto_obj2, texto_obj2_rect)

def mostrar_menu():
    global nombre_jugador, boton_puntajes_rect
    titulo = fuente_titulo.render("ArcSpace", False, (255,255,255))
    titulo_rect = titulo.get_rect(center = (ancho / 2, alto / 8))

    pantalla.blit(titulo, titulo_rect)

    input_label = fuente_media.render("INGRESA TU NOMBRE", False, (255,255,255))
    input_label_rect = input_label.get_rect(center = (ancho / 2, alto / 2))
    pantalla.blit(input_label, input_label_rect)

    nombre_ingresado = fuente_titulo.render(nombre_jugador, False, (150, 50, 200))
    nombre_ingresado_rect = nombre_ingresado.get_rect(center = (ancho / 2, alto / 2 + 70))
    pantalla.blit(nombre_ingresado, nombre_ingresado_rect)

    instruccion = fuente_media.render("PRESIONE ESPACIO PARA INICIAR", False, (255,255,255))
    instruccion_rect = instruccion.get_rect(center = (ancho / 2, alto / 2 + 140))
    pantalla.blit(instruccion, instruccion_rect)

    boton_base = fuente_normal.render("PUNTAJES", False, (255, 255, 255))
    boton_base_rect = boton_base.get_rect()
    boton_base_rect.centery = titulo_rect.centery
    boton_base_rect.right = ancho - 20
    mouse_pos = pygame.mouse.get_pos()
    hover = boton_base_rect.inflate(20, 10).collidepoint(mouse_pos)
    if hover:
        escala = 1.1
        boton_puntajes = pygame.transform.scale(boton_base,
            (int(boton_base.get_width() * escala), int(boton_base.get_height() * escala)))
        boton_puntajes_rect = boton_puntajes.get_rect(center=boton_base_rect.center)
        padding = 12
        bg_rect = boton_puntajes_rect.inflate(padding * 2, padding)
    else:
        boton_puntajes = boton_base
        boton_puntajes_rect = boton_base_rect
        padding = 12
        bg_rect = boton_base_rect.inflate(padding * 2, padding)
    pygame.draw.rect(pantalla, (100, 0, 180), bg_rect, border_radius=8)
    pantalla.blit(boton_puntajes, boton_puntajes_rect)

    if nombre_erroneo:
        error_texto = fuente_pequena.render("YA EXISTE UN JUGADOR CON ESE NOMBRE", False, (255, 0, 0))
        error_rect = error_texto.get_rect(center=(ancho // 2, alto - 30))
        pantalla.blit(error_texto, error_rect)

def mostrar_puntajes():
    global boton_volver_rect, scroll_offset
    titulo = fuente_titulo.render("PUNTAJES", False, (255, 255, 255))
    titulo_rect = titulo.get_rect(center=(ancho // 2, 50))

    boton_base = fuente_normal.render("VOLVER (M)", False, (255, 255, 255))
    boton_base_rect = boton_base.get_rect()
    boton_base_rect.centery = titulo_rect.centery
    boton_base_rect.right = ancho - 20
    mouse_pos = pygame.mouse.get_pos()
    hover = boton_base_rect.inflate(20, 10).collidepoint(mouse_pos)
    if hover:
        escala = 1.1
        boton_volver = pygame.transform.scale(boton_base,
            (int(boton_base.get_width() * escala), int(boton_base.get_height() * escala)))
        boton_volver_rect = boton_volver.get_rect(center=boton_base_rect.center)
        padding = 12
        bg_rect = boton_volver_rect.inflate(padding * 2, padding)
    else:
        boton_volver = boton_base
        boton_volver_rect = boton_base_rect
        padding = 12
        bg_rect = boton_base_rect.inflate(padding * 2, padding)
    pygame.draw.rect(pantalla, (100, 0, 180), bg_rect, border_radius=8)
    pantalla.blit(boton_volver, boton_volver_rect)

    pantalla.blit(titulo, titulo_rect)

    y_inicio = 110
    alto_entrada = 80
    area_y = alto - y_inicio - 20
    total_alto = len(jugadores_ordenados) * alto_entrada
    max_scroll = max(0, total_alto - area_y)
    scroll_offset = min(scroll_offset, max_scroll)

    for i, (nombre, datos_jugador) in enumerate(jugadores_ordenados):
        y = y_inicio + i * alto_entrada - scroll_offset
        if y + alto_entrada < y_inicio or y > alto - 20:
            continue

        pts = datos_jugador["puntuacion_total"]
        nivel_max = datos_jugador["nivel_maximo"]
        astros = datos_jugador["astros_descubiertos"]
        cant_astros = len(astros)
        partidas = datos_jugador["cantidad_partidas"]

        fuente_actual = fuente_normal if i < 3 else fuente_pequena
        nombre_surf = fuente_actual.render(f"{nombre}", False, (255, 215, 0))
        pts_surf = fuente_actual.render(f"{pts} pts", False, (255, 215, 0))
        pantalla.blit(nombre_surf, (60, y))
        pantalla.blit(pts_surf, (60 + nombre_surf.get_width() + 20, y))
        info_surf = fuente_pequena.render(
            f"Nivel max: {nivel_max}  |  Astros: {cant_astros}  |  Partidas: {partidas}",
            False, (150, 50, 200)
        )
        pantalla.blit(info_surf, (60, y + (35 if i < 3 else 20)))

def crear_astros():
    global nivel
    astros_nivel = [a for a in astros if a.get("nivel") == nivel]
    total_cantidad = sum(a.get("cantidad", 1) for a in astros_nivel)
    posiciones_listas = generar_posiciones_validas(total_cantidad, 120)
    pos_index = 0
    for dato_astro in astros_nivel:
        cantidad = dato_astro.get("cantidad", 1)
        for _ in range(cantidad):
            if pos_index < len(posiciones_listas):
                pos = posiciones_listas[pos_index]
            else:
                pos = (randint(0, ancho), randint(0, alto))
            nuevo_astro = Astro(dato_astro, pos)
            astros_grupo.add(nuevo_astro)
            pos_index += 1

def asignar_tiempo_transicion(tiempo_inicio):
    tiempo_transcurrido = (pygame.time.get_ticks() - tiempo_inicio) / 1000
    tiempo_restante = 7 - int(tiempo_transcurrido)
    if tiempo_restante <= 0:
        return True
    return False

def tomar_foto():    
    colisiones = pygame.sprite.spritecollide(camara.sprite, astros_grupo, False)
    p = 0
    if colisiones:
        astro = colisiones[0]
        p = astro.puntos
        album.append({
            "nombre": astro.nombre,
            "puntos": astro.puntos
        })
        dx = (camara.sprite.rect.x + 100) - astro.rect.centerx
        dy = (camara.sprite.rect.y + 70) - astro.rect.centery
        distancia = math.sqrt(dx*dx + dy*dy)
        
        camara.sprite.mostrar_texto_foto = True
        camara.sprite.tiempo_foto = pygame.time.get_ticks()
        if distancia < 30:
            camara.sprite.texto_foto = "PERFECTO"
            camara.sprite.color_texto_foto = (128, 0, 128)
        else:
            camara.sprite.texto_foto = "BIEN"
            camara.sprite.color_texto_foto = (0, 255, 0)
        astro.kill()
        return p
    else:
        camara.sprite.mostrar_texto_foto = True
        camara.sprite.tiempo_foto = pygame.time.get_ticks()
        camara.sprite.texto_foto = "MAL"
        camara.sprite.color_texto_foto = (255, 0, 0)
        return p

def colision():
        colisiones = pygame.sprite.spritecollide(camara.sprite, astros_grupo, False)
        if colisiones:
            return colisiones[0]
        else:
            return None

def mostrar_tiempo(tiempo_restante):
    tiempo_maximo = tiempo_inicial
    bar_width = int(ancho * 0.8)
    bar_height = 20
    x = (ancho - bar_width) // 2
    y = alto - 40

    fill_width = int((tiempo_restante / tiempo_maximo) * bar_width)

    if tiempo_restante < tiempo_maximo * 0.2:
        color = (255, 0, 0)
    else:
        color = (255, 255, 255)

    texto_tiempo = fuente_normal.render("TIEMPO", False, (255, 255, 255))
    texto_rect = texto_tiempo.get_rect(center=(ancho // 2, y - 20))
    pantalla.blit(texto_tiempo, texto_rect)

    pygame.draw.rect(pantalla, (64, 64, 64), (x, y, bar_width, bar_height), 2, border_radius=10)
    pygame.draw.rect(pantalla, color, (x, y, fill_width, bar_height), border_radius=10)

def mostrar_camaras(cuantas=None):
    if cuantas is None:
        cuantas = fotos
    texto_fotos = fuente_normal.render("FOTOS", False, (255, 255, 255))
    texto_rect = texto_fotos.get_rect(topleft=(10, 5))
    pantalla.blit(texto_fotos, texto_rect)
    
    for i in range(cuantas):
        x = 10 + (i * 60)
        y = 35
        pantalla.blit(img_camara, (x, y))

def mostrar_puntos_partida(puntuacion_mostrar=None):
    if puntuacion_mostrar is None:
        puntuacion_mostrar = puntuacion
    bar_width = 20
    bar_height = int(alto * 0.6)
    x = ancho - 75
    y = (alto - bar_height) // 2

    texto_puntos = fuente_normal.render("PUNTOS", False, (255, 255, 255))
    texto_rect = texto_puntos.get_rect(center=(x + bar_width // 2, y - 20))
    pantalla.blit(texto_puntos, texto_rect)

    pygame.draw.rect(pantalla, (64, 64, 64), (x, y, bar_width, bar_height), 2, border_radius=10)
    
    if objetivo > 0:
        proporcion = min(puntuacion_mostrar / objetivo, 1)
        fill_height = int(bar_height * proporcion)
        fill_y = y + bar_height - fill_height
        pygame.draw.rect(pantalla, (255, 215, 0), (x, fill_y, bar_width, fill_height), border_radius=10)

def mostrar_flash():
    global flash_activo, flash_tiempo
    if flash_activo:
        flash_surface = pygame.Surface((ancho, alto))
        flash_surface.fill((220, 220, 220))
        alpha = max(0, 200 - int((pygame.time.get_ticks() - flash_tiempo) * 5))
        flash_surface.set_alpha(alpha)
        pantalla.blit(flash_surface, (0, 0))
        if alpha <= 0:
            flash_activo = False

def dibujar_rect_punteado(superficie, color, rect, dash=8):
    x, y, w, h = rect
    for i in range(0, w, dash * 2):
        pygame.draw.line(superficie, color, (x + i, y), (min(x + i + dash, x + w), y))
    for i in range(0, w, dash * 2):
        pygame.draw.line(superficie, color, (x + i, y + h), (min(x + i + dash, x + w), y + h))
    for i in range(0, h, dash * 2):
        pygame.draw.line(superficie, color, (x, y + i), (x, min(y + i + dash, y + h)))
    for i in range(0, h, dash * 2):
        pygame.draw.line(superficie, color, (x + w, y + i), (x + w, min(y + i + dash, y + h)))

def mostrar_reporte():
    global nivel, pagina_actual
    cargar_assets_reales()
    rect_ancho = int(ancho * 0.9)
    rect_alto = 110
    x = (ancho - rect_ancho) // 2
    y = 0
    pygame.draw.rect(pantalla, (48, 39, 38), (x, y, rect_ancho, rect_alto), border_radius=20)
    texto_fotos_nuevas = fuente_media.render("fotos nuevas:", False, (180, 180, 180))
    pantalla.blit(texto_fotos_nuevas, (x + 10, y + (rect_alto - texto_fotos_nuevas.get_height()) // 2))

    tamano_foto = 80
    espacio = 20

    rec_w, rec_h = 130, 130
    gap = 30
    group_w = 2 * rec_w + gap
    group_h = 2 * rec_h + gap
    sep = 150
    total_w = 2 * group_w + sep
    start_x = (ancho - total_w) // 2
    start_y = 275

    posiciones_pagina = {}
    page0_slots = []
    for i in range(8):
        group = i // 4
        idx = i % 4
        r = idx // 2
        c = idx % 2
        rx = start_x + group * (group_w + sep) + c * (rec_w + gap)
        ry = start_y + r * (rec_h + gap)
        page0_slots.append(pygame.Rect(rx, ry, rec_w, rec_h))
    posiciones_pagina[0] = page0_slots

    if astros_sin_pos:
        page1_extra_pages = (len(astros_sin_pos) - 1) // 8 + 1
        for p in range(1, page1_extra_pages + 1):
            posiciones_pagina[p] = [pygame.Rect(r.x, r.y, r.w, r.h) for r in page0_slots]

    if pagina_actual >= len(posiciones_pagina):
        pagina_actual = 0
    posiciones_fotos_reales = posiciones_pagina[pagina_actual]

    if album and not fotos_reporte_instancias:
        total_fotos = len(album)
        ancho_total = total_fotos * tamano_foto + (total_fotos - 1) * espacio
        min_inicio_x = x + 10 + texto_fotos_nuevas.get_width() + 20
        inicio_x = max(min_inicio_x, x + (rect_ancho - ancho_total) // 2)
        y_foto = y + (rect_alto - tamano_foto) // 2
        claves_agregadas = set()
        for idx_album, item in enumerate(album):
            clave = item["nombre"]
            rect_min = pygame.Rect(inicio_x + idx_album * (tamano_foto + espacio), y_foto, tamano_foto, tamano_foto)
            if clave in claves_agregadas:
                continue
            claves_agregadas.add(clave)
            if clave in {c for c, _, _ in fotos_pegadas_permanentes}:
                continue
            astro_data = next((a for a in astros if a["nombre"] == clave), None)
            if astro_data is None:
                continue
            pos = astro_data.get("posicion")
            pixel_img = assets_astros.get(clave)
            real_img = assets_reales.get(clave)
            if not (pixel_img and real_img):
                continue
            astro_texto = astro_data["texto"] if astro_data else ""
            if pos is not None and 0 <= pos < len(posiciones_pagina[0]):
                rect_dest = posiciones_pagina[0][pos]
                pagina = 0
            else:
                try:
                    idx_sin = next(i for i, a in enumerate(astros_sin_pos) if a["nombre"] == clave)
                    target_page = 1 + idx_sin // 8
                    target_slot = idx_sin % 8
                    if target_page in posiciones_pagina and target_slot < len(posiciones_pagina[target_page]):
                        rect_dest = posiciones_pagina[target_page][target_slot]
                        pagina = target_page
                    else:
                        continue
                except StopIteration:
                    continue
            foto = FotoReporte(clave, astro_texto, rect_min, rect_dest, pixel_img, real_img)
            foto.pagina = pagina
            fotos_reporte_instancias.append(foto)

    for f in fotos_reporte_instancias:
        f.update()

    if album:
        claves_pegadas = {f.clave for f in fotos_reporte_instancias if f.estado == 'pegada'}
        claves_pegadas |= {c for c, _, _ in fotos_pegadas_permanentes}
        total_fotos = len(album)
        ancho_total = total_fotos * tamano_foto + (total_fotos - 1) * espacio
        min_inicio_x = x + 10 + texto_fotos_nuevas.get_width() + 20
        inicio_x = max(min_inicio_x, x + (rect_ancho - ancho_total) // 2)
        y_foto = y + (rect_alto - tamano_foto) // 2
        for idx_album, item in enumerate(album):
            clave = item["nombre"]
            if clave in claves_pegadas:
                continue
            pos_x = inicio_x + idx_album * (tamano_foto + espacio)
            pygame.draw.rect(pantalla, (212, 193, 190), (pos_x - 6, y_foto - 6, tamano_foto + 12, tamano_foto + 12), border_radius=2)
            pygame.draw.rect(pantalla, (0, 0, 0), (pos_x - 6, y_foto - 6, tamano_foto + 12, tamano_foto + 12), 3, border_radius=2)
            img = assets_astros.get(clave)
            if img:
                pantalla.blit(pygame.transform.scale(img, (tamano_foto, tamano_foto)), (pos_x, y_foto))

    img_uibook_rect = img_uibook.get_rect(center=(ancho // 2, 420))
    pantalla.blit(img_uibook, img_uibook_rect)

    for i, rect in enumerate(posiciones_fotos_reales):
        dibujar_rect_punteado(pantalla, (0, 0, 0), (rect.x, rect.y, rec_w, rec_h), 8)
        num_surf = fuente_normal.render(str(i + pagina_actual * 8 + 1), False, (180, 180, 180))
        num_rect = num_surf.get_rect(center=rect.center)
        pantalla.blit(num_surf, num_rect)

    for clave, pag, slot_idx in fotos_pegadas_permanentes:
        if pag == pagina_actual and pag in posiciones_pagina and slot_idx < len(posiciones_pagina[pag]):
            real_img = assets_reales.get(clave)
            if real_img:
                img_pegada = pygame.transform.scale(real_img, (rec_w, rec_h))
                pantalla.blit(img_pegada, posiciones_pagina[pag][slot_idx])

    for f in fotos_reporte_instancias:
        if f.estado == 'pegada' and f.pagina == pagina_actual:
            pantalla.blit(f.image, f.rect)

    todas_pegadas = all(f.estado == 'pegada' for f in fotos_reporte_instancias)
    hay_revelada = any(f.estado == 'revelada' for f in fotos_reporte_instancias)
    hay_girando = any(f.estado == 'girando' for f in fotos_reporte_instancias)
    if not todas_pegadas and not hay_girando:
        t = (pygame.time.get_ticks() % 3000) / 3000
        if t < 1/3:
            lt = t * 3
            r = int(255 - lt * 127)
            g = int(165 - lt * 165)
            b = int(0 + lt * 128)
        elif t < 2/3:
            lt = (t - 1/3) * 3
            r = int(128 - lt * 128)
            g = int(0 + lt * 0)
            b = int(128 + lt * 127)
        else:
            lt = (t - 2/3) * 3
            r = int(0 + lt * 255)
            g = int(0 + lt * 165)
            b = int(255 - lt * 255)
        color_texto = (r, g, b)
    if todas_pegadas:
        if puntuacion >= objetivo:
            texto = fuente_normal.render("Avanzar al siguiente nivel", False, (255, 215, 0))
        else:
            texto = fuente_normal.render("Intentar de nuevo", False, (255, 0, 0))
    elif hay_girando:
        texto = None
    elif hay_revelada:
        texto = fuente_normal.render("Haz click sobre la imagen para pegarla en el album", False, color_texto)
    else:
        texto = fuente_normal.render("Haz click sobre las fotos para revelarlas", False, color_texto)
    if texto is not None:
        if todas_pegadas:
            img_space_peq = pygame.transform.scale(img_space, (96, 42))
            total_w = texto.get_width() + 8 + img_space_peq.get_width()
            start_x = (ancho - total_w) // 2
            texto_rect = texto.get_rect(left=start_x, centery=140)
            img_space_rect = img_space_peq.get_rect(left=start_x + texto.get_width() + 8, centery=140)
            pantalla.blit(texto, texto_rect)
            pantalla.blit(img_space_peq, img_space_rect)
        else:
            texto_rect = texto.get_rect(center=(ancho // 2, 140))
            pantalla.blit(texto, texto_rect)
            img_mouse_peq = pygame.transform.scale(img_mouse_left, (30, 38))
            img_mouse_rect = img_mouse_peq.get_rect(midright=(texto_rect.left - 10, texto_rect.centery))
            pantalla.blit(img_mouse_peq, img_mouse_rect)
    texto_menu = fuente_pequena.render("Volver al menu", False, (255, 255, 255))
    texto_rect = texto_menu.get_rect(left=20, centery=alto - 30)
    pantalla.blit(texto_menu, texto_rect)
    img_m_redim = pygame.transform.scale(img_m, (30, 30))
    img_m_rect = img_m_redim.get_rect(left=texto_rect.right + 10, centery=alto - 30)
    pantalla.blit(img_m_redim, img_m_rect)

    for f in fotos_reporte_instancias:
        if f.estado == 'girando':
            pantalla.blit(f.image, f.rect)

    for f in fotos_reporte_instancias:
        if f.estado == 'revelada':
            pantalla.blit(f.image, f.rect)
            nombre_surf = fuente_normal.render(f.clave.upper(), False, (255, 255, 255))
            ancho_max = 260
            palabras = f.texto_astro.split()
            lineas = []
            linea_actual = ""
            for p in palabras:
                prueba = linea_actual + (" " if linea_actual else "") + p
                if fuente_pequena.size(prueba)[0] <= ancho_max:
                    linea_actual = prueba
                else:
                    if linea_actual:
                        lineas.append(linea_actual)
                    linea_actual = p
            if linea_actual:
                lineas.append(linea_actual)
            textos_surf = [fuente_pequena.render(l, False, (200, 200, 200)) for l in lineas]
            panel_w = max(nombre_surf.get_width(), ancho_max) + 20
            panel_h = nombre_surf.get_height() + len(textos_surf) * fuente_pequena.get_height() + 20
            margen = 10
            lado_derecho = f.rect.right + margen + panel_w < ancho - margen
            if lado_derecho:
                panel_x = f.rect.right + margen
            else:
                panel_x = f.rect.left - margen - panel_w
            panel_y = max(margen, min(f.rect.centery - panel_h // 2, alto - margen - panel_h))
            pygame.draw.rect(pantalla, (20, 20, 20), (panel_x, panel_y, panel_w, panel_h), border_radius=6)
            pantalla.blit(nombre_surf, (panel_x + 10, panel_y + 6))
            y_offset = panel_y + 10 + nombre_surf.get_height()
            for s in textos_surf:
                pantalla.blit(s, (panel_x + 10, y_offset))
                y_offset += fuente_pequena.get_height()
            if f.hover:
                pygame.draw.rect(pantalla, (192, 192, 192), f.rect, 3, border_radius=2)

    tam_flecha = 50
    margen_book = 12
    flecha_izq_img = pygame.transform.scale(img_left, (tam_flecha, tam_flecha))
    flecha_der_img = pygame.transform.scale(img_right, (tam_flecha, tam_flecha))
    libro_bottom = 670
    if pagina_actual > 0:
        pantalla.blit(flecha_izq_img, (ancho // 2 - 415 + margen_book + 30, libro_bottom - margen_book - tam_flecha - 40))
    if pagina_actual < len(posiciones_pagina) - 1:
        pantalla.blit(flecha_der_img, (ancho // 2 + 415 - margen_book - tam_flecha - 30, libro_bottom - margen_book - tam_flecha - 40))

def generar_posiciones_validas(cantidad, radio_seguridad, posiciones_extras=None):
    posiciones = []
    intentos_maximos = 100
    
    # Agregamos la posición de la cámara para que nada nazca encima del jugador
    posiciones.append(pygame.Vector2(ancho // 2, alto // 2))
    
    # Agregamos posiciones extras si se proporcionan (como astros existentes)
    if posiciones_extras:
        for pos in posiciones_extras:
            posiciones.append(pygame.Vector2(pos))

    for _ in range(cantidad):
        for _ in range(intentos_maximos):
            candidatura = pygame.Vector2(randint(350, ancho - 120), randint(80, alto - 100))
            
            # Verificamos si está lo suficientemente lejos de todas las posiciones ya aceptadas
            es_valida = True
            for p in posiciones:
                if candidatura.distance_to(p) < radio_seguridad:
                    es_valida = False
                    break
            
            if es_valida:
                posiciones.append(candidatura)
                break
                
    # Quitamos la posición de la cámara antes de devolver la lista
    return posiciones[1:]

def guardar_puntuacion():
    global scores
    astros_descubiertos = list(set(
        [a["nombre"] for a in album] +
        [a["nombre"] for a in coleccion]
    ))
    ahora = datetime.datetime.now()
    fecha_hora = ahora.strftime("%Y-%m-%d %H:%M:%S")
    punt_total = puntuacion_total_partida + puntuacion
    try:
        with open('data/scores.json', 'r') as f:
            datos = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        datos = {"jugadores": {}, "partidas": [], "top_scores": []}
    if nombre_jugador not in datos["jugadores"]:
        datos["jugadores"][nombre_jugador] = {
            "puntuacion_total": 0,
            "nivel_maximo": 0,
            "astros_descubiertos": [],
            "fecha_hora": "",
            "cantidad_partidas": 0
        }
    player = datos["jugadores"][nombre_jugador]
    player["cantidad_partidas"] += 1
    if punt_total > player["puntuacion_total"]:
        player["puntuacion_total"] = punt_total
        player["nivel_maximo"] = nivel
        player["astros_descubiertos"] = astros_descubiertos
        player["fecha_hora"] = fecha_hora
    datos["partidas"].append({
        "nombre": nombre_jugador,
        "puntuacion_total": punt_total,
        "nivel_maximo": nivel,
        "astros_descubiertos": astros_descubiertos,
        "fecha_hora": fecha_hora
    })
    sorted_players = sorted(datos["jugadores"].items(), key=lambda x: x[1]["puntuacion_total"], reverse=True)
    datos["top_scores"] = [{"nombre": k, "puntos": v["puntuacion_total"]} for k, v in sorted_players]
    with open('data/scores.json', 'w') as f:
        json.dump(datos, f, indent=4)
    scores = datos["top_scores"]

pygame.init()
ancho = 1280
alto = 720
centro = (ancho //2, alto // 2)
pantalla = pygame.display.set_mode((ancho,alto))
pygame.display.set_caption("ArcSpace")
clock = pygame.time.Clock()

pantalla.fill((0, 0, 0))
pygame.display.flip()

fuente_titulo = pygame.font.Font("assets/Fonts/Silkscreen/Silkscreen-Regular.ttf", 80)
fuente_normal = pygame.font.Font("assets/Fonts/Silkscreen/Silkscreen-Regular.ttf", 30)
fuente_media = pygame.font.Font("assets/Fonts/Silkscreen/Silkscreen-Regular.ttf", 50)
fuente_pequena = pygame.font.Font("assets/Fonts/Silkscreen/Silkscreen-Regular.ttf", 20)

texto_carga = fuente_normal.render("Cargando...", False, (255, 255, 255))
pantalla.blit(texto_carga, (ancho // 2 - texto_carga.get_width() // 2, alto // 2 - texto_carga.get_height() // 2))
pygame.display.flip()
pygame.event.pump()

def cargar_imagen(ruta, escala=None):
    img = pygame.image.load(ruta).convert_alpha()
    if escala:
        img = pygame.transform.scale(img, escala)
    return img

img_camara = cargar_imagen("assets/Graphics/Camara.png", (60, 60))
# Estados posibles
ESTADO_MENU = "menu"
ESTADO_INTERMISION1 = "intermision1"
ESTADO_INTERMISION2 = "intermision2"
ESTADO_INTERMISION3 = "intermision3"
ESTADO_INTERMISION4 = "intermision4"
ESTADO_JUGANDO = "jugando"
ESTADO_REPORTE = "reporte"
ESTADO_PUNTAJES = "puntajes"

# Estado inicial
estado_actual = ESTADO_MENU

#Menu
fondo = cargar_imagen("assets/Graphics/fondo.png", (ancho, alto))
pantalla.blit(texto_carga, (ancho // 2 - texto_carga.get_width() // 2, alto // 2 - texto_carga.get_height() // 2))
pygame.display.flip()
pygame.event.pump()
img_up = cargar_imagen("assets/Graphics/Keyboard & Mouse/Default/keyboard_arrow_up.png")
img_down = cargar_imagen("assets/Graphics/Keyboard & Mouse/Default/keyboard_arrow_down.png")
img_left = cargar_imagen("assets/Graphics/Keyboard & Mouse/Default/keyboard_arrow_left.png")
img_right = cargar_imagen("assets/Graphics/Keyboard & Mouse/Default/keyboard_arrow_right.png")
img_space_raw = cargar_imagen("assets/Graphics/Keyboard & Mouse/Double/keyboard_space.png")
img_space = img_space_raw.subsurface((0, 36, 128, 56)).copy()
img_m = cargar_imagen("assets/Graphics/Keyboard & Mouse/Default/keyboard_m.png")
img_mouse_left = cargar_imagen("assets/Graphics/Keyboard & Mouse/Default/mouse_left.png")
img_uibook = cargar_imagen("assets/Graphics/UIBook.png", (830, 500))
datos_teclas = [
    {"img": img_up, "offset": (0, -50)},   
    {"img": img_down, "offset": (0, 0)},  
    {"img": img_left, "offset": (-50, 0)},  
    {"img": img_right, "offset": (50, 0)} 
    ]

#Mostrar jugadores
scores = []
nombres_existentes = set()
with open('data/scores.json', 'r') as f:
    datos = json.load(f)
    for item in datos["top_scores"]:
        scores.append(item)
    if "jugadores" in datos:
        nombres_existentes = {k.lower() for k in datos["jugadores"]}

#Juego
fotos = 5
camara = pygame.sprite.GroupSingle()
camara.add(Camara(ancho, alto))

#Astros
assets_astros = {
    "Luna": cargar_imagen("assets/Graphics/Astros/Luna.png", (140, 140)),
    "Venus": cargar_imagen("assets/Graphics/Astros/Venus.png", (140, 140)),
    "Mercurio": cargar_imagen("assets/Graphics/Astros/Mercurio.png", (140, 140)),
    "Marte": cargar_imagen("assets/Graphics/Astros/Marte.png", (140, 140)),
    "Estacion": cargar_imagen("assets/Graphics/Astros/Estacion.png", (80, 80)),
    "Jupiter": cargar_imagen("assets/Graphics/Astros/Jupiter.png", (140, 140)),
    "Saturno": cargar_imagen("assets/Graphics/Astros/Saturno.png", (140, 140)),
    "Urano": cargar_imagen("assets/Graphics/Astros/Urano.png", (140, 140)),
    "Neptuno": cargar_imagen("assets/Graphics/Astros/Neptuno.png", (140, 140)),
    "Estrella": cargar_imagen("assets/Graphics/Astros/Estrella.png", (45, 45)),
    }

assets_reales = {}
def cargar_assets_reales():
    if assets_reales:
        return
    nombres_reales = ["Luna", "Venus", "Mercurio", "Marte", "Estacion", "Jupiter", "Saturno", "Urano", "Neptuno", "Estrella"]
    archivos_reales = {
        "Luna": "Luna-Real.png", "Venus": "Venus-Real.png", "Mercurio": "Mercurio-Real.png",
        "Marte": "Marte-Real.png", "Estacion": "Estacion-Real.png", "Jupiter": "Jupiter-Real.png",
        "Saturno": "Saturno-Real.png", "Urano": "Urano-Real.png", "Neptuno": "Neptuno-Real.png",
        "Estrella": "Estrella-Real.png",
    }
    for nombre in nombres_reales:
        assets_reales[nombre] = cargar_imagen(f"assets/Graphics/Reales/{archivos_reales[nombre]}")

astros = []
with open("data/astros.json", "r") as f:
    datos = json.load(f)
    for item in datos["astros"]:
        astros.append(item)

astros_sin_pos = [a for a in astros if "posicion" not in a]
total_paginas = 1 + (len(astros_sin_pos) + 7) // 8 if astros_sin_pos else 1
pagina_actual = 0


#Puntuacion
puntuacion = 0
puntuacion_total_partida = 0

#Tiempo
ticks_inicio = pygame.time.get_ticks()
tiempo_inicial = 30
ticks_inicio_juego = 0
tiempo_inicio_intermision1 = 0
tiempo_pausado = False
tiempo_fotos_agotadas = 0
tipo_pausa = ""
tiempo_inicio_intermision2 = 0
tiempo_inicio_intermision3 = 0
tiempo_inicio_intermision4 = 0
fotos_tutorial = 5
#Fotos tomadas
album = []
coleccion = []
fotos_reporte_instancias = []
fotos_pegadas_permanentes = []  # [(clave, pos_idx)] astros pegados en niveles anteriores

##niveles
nivel = 1

##Objetivo
objetivo = 500

##Nombre jugador
nombre_jugador = ""
nombre_erroneo = False

##Puntajes
scroll_offset = 0
jugadores_ordenados = []
boton_puntajes_rect = pygame.Rect(0, 0, 0, 0)
boton_volver_rect = pygame.Rect(0, 0, 0, 0)

##Flash
flash_activo = False
flash_tiempo = 0

pantalla.fill((0, 0, 0))
pygame.display.flip()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if nombre_jugador:
                guardar_puntuacion()
                nombres_existentes.add(nombre_jugador.lower())
            pygame.quit()
            exit()
        
        if estado_actual == 'menu':
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if nombre_jugador and nombre_jugador.lower() not in nombres_existentes:
                        tiempo_inicio_intermision1 = pygame.time.get_ticks()
                        estado_actual = ESTADO_INTERMISION1
                        astros_grupo = pygame.sprite.Group()
                        puntuacion = 0
                        puntuacion_total_partida = 0
                        tipo_pausa = ""
                        fotos_tutorial = 5
                        crear_astros()
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
                    with open('data/scores.json', 'r') as f:
                        datos = json.load(f)
                    jugadores_ordenados = sorted(
                        datos["jugadores"].items(),
                        key=lambda x: x[1]["puntuacion_total"],
                        reverse=True
                    )
                    scroll_offset = 0
                    estado_actual = ESTADO_PUNTAJES

        elif estado_actual == 'puntajes':
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m or event.key == pygame.K_ESCAPE:
                    estado_actual = ESTADO_MENU
                elif event.key == pygame.K_UP:
                    scroll_offset = max(0, scroll_offset - 50)
                elif event.key == pygame.K_DOWN:
                    scroll_offset += 50
            if event.type == pygame.MOUSEWHEEL:
                scroll_offset -= event.y * 40
                scroll_offset = max(0, scroll_offset)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if boton_volver_rect.collidepoint(event.pos):
                    estado_actual = ESTADO_MENU
        

        elif estado_actual == 'intermision1':
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                for astro in astros_grupo:
                    astro.kill()
                estado_actual = ESTADO_INTERMISION2
                tiempo_inicio_intermision2 = pygame.time.get_ticks()
                camara.sprite.rect.center = (ancho/2, alto/2)
                

        elif estado_actual == 'intermision2':
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                for astro in astros_grupo:
                    astro.kill()
                camara.sprite.rect.center = (ancho // 2, alto // 2)
                camara.sprite.fotos_tutorial = 5
                if hasattr(camara.sprite, 'iniciado_tutorial'):
                    delattr(camara.sprite, 'iniciado_tutorial')
                if hasattr(camara.sprite, 'astros_demo'):
                    delattr(camara.sprite, 'astros_demo')
                if hasattr(camara.sprite, 'indice_astro'):
                    delattr(camara.sprite, 'indice_astro')
                if hasattr(camara.sprite, 'foto_tomada'):
                    delattr(camara.sprite, 'foto_tomada')
                estado_actual = ESTADO_INTERMISION3
                tiempo_inicio_intermision3 = pygame.time.get_ticks()

        elif estado_actual == 'intermision3':
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                for astro in astros_grupo:
                    astro.kill()
                camara.sprite.rect.center = (ancho // 2, alto // 2)
                fotos = 5
                if hasattr(camara.sprite, 'iniciado_tutorial3'):
                    delattr(camara.sprite, 'iniciado_tutorial3')
                if hasattr(camara.sprite, 'indice_astro3'):
                    delattr(camara.sprite, 'indice_astro3')
                if hasattr(camara.sprite, 'puntuacion_tutorial'):
                    delattr(camara.sprite, 'puntuacion_tutorial')
                if hasattr(camara.sprite, 'foto_tomada3'):
                    delattr(camara.sprite, 'foto_tomada3')
                if hasattr(camara.sprite, 'astros_demo3'):
                    delattr(camara.sprite, 'astros_demo3')
                tiempo_inicio_intermision4 = pygame.time.get_ticks()
                estado_actual = ESTADO_INTERMISION4

        elif estado_actual == 'intermision4':
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                fotos = 5
                camara.sprite.rect.center = (ancho // 2, alto // 2)
                estado_actual = ESTADO_JUGANDO
                ticks_inicio_juego = pygame.time.get_ticks()
                crear_astros()

        elif estado_actual == 'jugando':
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not tiempo_pausado:
                fotos -= 1
                flash_activo = True
                flash_tiempo = pygame.time.get_ticks()
                p = tomar_foto()
                puntuacion += p
                puntuacion_total_partida += p
                if puntuacion >= objetivo:
                    tiempo_pausado = True
                    tipo_pausa = "objetivo"
                    tiempo_fotos_agotadas = pygame.time.get_ticks()
                elif fotos <= 0:
                    tiempo_pausado = True
                    tipo_pausa = "fotos"
                    tiempo_fotos_agotadas = pygame.time.get_ticks()

        elif estado_actual == 'reporte':
            todas_pegadas = all(f.estado == 'pegada' for f in fotos_reporte_instancias)
            if event.type == pygame.MOUSEBUTTONDOWN:
                pegando = False
                for f in fotos_reporte_instancias:
                    if f.estado == 'revelada' and f.rect.collidepoint(event.pos):
                        f.pegar()
                        pegando = True
                        pos_idx = next((a.get("posicion") for a in astros if a["nombre"] == f.clave), None)
                        if pos_idx is not None:
                            pag_peg = 0
                            slot_peg = pos_idx
                        else:
                            try:
                                idx_sin = next(i for i, a in enumerate(astros_sin_pos) if a["nombre"] == f.clave)
                                pag_peg = 1 + idx_sin // 8
                                slot_peg = idx_sin % 8
                            except StopIteration:
                                pag_peg = None
                        if pag_peg is not None and (f.clave, pag_peg, slot_peg) not in fotos_pegadas_permanentes:
                            fotos_pegadas_permanentes.append((f.clave, pag_peg, slot_peg))
                        break
                if not pegando:
                    clicked_arrow = False
                    libro_bottom = 670
                    margen_book = 12
                    tam_flecha = 50
                    if pagina_actual > 0:
                        izq_rect = pygame.Rect(ancho // 2 - 415 + margen_book + 30, libro_bottom - margen_book - tam_flecha - 40, tam_flecha, tam_flecha)
                        if izq_rect.collidepoint(event.pos):
                            pagina_actual -= 1
                            clicked_arrow = True
                    if not clicked_arrow and pagina_actual < total_paginas - 1:
                        der_rect = pygame.Rect(ancho // 2 + 415 - margen_book - tam_flecha - 30, libro_bottom - margen_book - tam_flecha - 40, tam_flecha, tam_flecha)
                        if der_rect.collidepoint(event.pos):
                            pagina_actual += 1
                            clicked_arrow = True
                    if not clicked_arrow:
                        for f in fotos_reporte_instancias:
                            if f.estado == 'oculta_en_libro' and f.rect_miniatura.collidepoint(event.pos):
                                f.estado = 'girando'
                                break
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                for f in fotos_reporte_instancias:
                    if f.estado == 'revelada':
                        f.hover = f.rect.collidepoint(mouse_pos)
                    else:
                        f.hover = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if todas_pegadas:
                    if puntuacion >= objetivo:
                        nivel += 1
                        coleccion.extend(album)
                        album.clear()
                        astros_nivel_nuevo = [a for a in astros if a.get("nivel") == nivel]
                        total_cantidad = sum(a.get("cantidad", 1) for a in astros_nivel_nuevo)
                        posiciones_astros_existentes = [astro.rect.center for astro in astros_grupo]
                        posiciones_listas = generar_posiciones_validas(total_cantidad, 200, posiciones_astros_existentes)
                        for i, dato_astro in enumerate(astros_nivel_nuevo):
                            cantidad = dato_astro.get("cantidad", 1)
                            for j in range(cantidad):
                                idx = len(posiciones_listas) - total_cantidad + i + j
                                if 0 <= idx < len(posiciones_listas):
                                    pos = posiciones_listas[idx]
                                else:
                                    pos = (ancho // 2, alto // 2)
                                nuevo_astro = Astro(dato_astro, pos)
                                astros_grupo.add(nuevo_astro)
                    else:
                        fotos_pegadas_permanentes.clear()
                        album.clear()
                        coleccion.clear()
                        nivel = 1
                        puntuacion_total_partida = 0
                        for astro in astros_grupo:
                            astro.kill()
                        astros_grupo = pygame.sprite.Group()
                        crear_astros()
                    puntuacion = 0
                    tipo_pausa = ""
                    fotos_tutorial = 5
                    fotos = 5
                    camara.sprite.rect.center = (ancho // 2, alto // 2)
                    ticks_inicio_juego = pygame.time.get_ticks()
                    fotos_reporte_instancias.clear()
                    estado_actual = ESTADO_JUGANDO
                else:
                    for f in fotos_reporte_instancias:
                        if f.estado == 'oculta_en_libro':
                            f.estado = 'girando'
                            break
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m and todas_pegadas:
                guardar_puntuacion()
                nombres_existentes.add(nombre_jugador.lower())
                fotos_pegadas_permanentes.clear()
                album.clear()
                coleccion.clear()
                nivel = 1
                puntuacion_total_partida = 0
                nombre_jugador = ""
                fotos_reporte_instancias.clear()
                estado_actual = ESTADO_MENU

    pantalla.blit(fondo, (0,0))

    if estado_actual == 'menu':
        mostrar_menu()
    
    if estado_actual == "intermision1":
        dibujar_controles()
        camara.sprite.update()
        camara.draw(pantalla)
        camara.sprite.automatico()
        pos_v = camara.sprite.rect.center
        for astro in astros_grupo:
            astro.update_visual(pos_v)
        astros_grupo.draw(pantalla)

        if asignar_tiempo_transicion(tiempo_inicio_intermision1):
            for astro in astros_grupo:
                astro.kill()
            estado_actual = ESTADO_INTERMISION2
            tiempo_inicio_intermision2 = pygame.time.get_ticks()
            camara.sprite.rect.center = (ancho/2, alto/2)

    if estado_actual == "intermision2":
        tiempo_actual = pygame.time.get_ticks()
        
        if not hasattr(camara.sprite, 'iniciado_tutorial'):
            camara.sprite.iniciado_tutorial = True
            camara.sprite.indice_astro = 0
            camara.sprite.fotos_tutorial = 5
            
            astros_demo = []
            posiciones = [
                (ancho // 2 + 200, alto // 2),
                (ancho // 2 + 200, alto // 2 - 150),
                (ancho // 2 - 100, alto // 2 - 50)
            ]
            nombres = ["Luna", "Venus", "Mercurio"]
            
            for i, (pos, nombre) in enumerate(zip(posiciones, nombres)):
                astro_demo = pygame.sprite.Sprite()
                astro_demo.image = assets_astros[nombre].copy()
                astro_demo.rect = astro_demo.image.get_rect(center = pos)
                astros_grupo.add(astro_demo)
                astros_demo.append(astro_demo)
            
            camara.sprite.astros_demo = astros_demo
        
        astros_demo = camara.sprite.astros_demo
        indice = camara.sprite.indice_astro
        
        for astro in astros_demo:
            if astro.alive():
                astro.image.set_alpha(255)
        
        if indice < len(astros_demo):
            astro = astros_demo[indice]
            
            dx = astro.rect.centerx - camara.sprite.rect.centerx
            dy = astro.rect.centery - camara.sprite.rect.centery
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > 10:
                if abs(dx) > abs(dy):
                    if dx < 0:
                        camara.sprite.rect.x -= 2
                    else:
                        camara.sprite.rect.x += 2
                else:
                    if dy < 0:
                        camara.sprite.rect.y -= 2
                    else:
                        camara.sprite.rect.y += 2
            else:
                if not hasattr(camara.sprite, 'foto_tomada'):
                    camara.sprite.foto_tomada = True
                    flash_activo = True
                    flash_tiempo = tiempo_actual
                    fotos_tutorial -= 1
                    camara.sprite.indice_astro += 1
                    camara.sprite.fotos_tutorial -= 1
                    astro.kill()
                    if hasattr(camara.sprite, 'foto_tomada'):
                        delattr(camara.sprite, 'foto_tomada')
        
        fotos_tutorial = camara.sprite.fotos_tutorial
        
        astros_grupo.draw(pantalla)
        camara.sprite.update()
        camara.draw(pantalla)
        dibujar_tomar_fotos()
        
        mostrar_camaras(fotos_tutorial)
        mostrar_flash()
        
        if fotos_tutorial == 0 or asignar_tiempo_transicion(tiempo_inicio_intermision2):
            fotos = 5
            for astro in astros_grupo:
                astro.kill()
            if hasattr(camara.sprite, 'iniciado_tutorial'):
                delattr(camara.sprite, 'iniciado_tutorial')
            if hasattr(camara.sprite, 'indice_astro'):
                delattr(camara.sprite, 'indice_astro')
            if hasattr(camara.sprite, 'fotos_tutorial'):
                delattr(camara.sprite, 'fotos_tutorial')
            if hasattr(camara.sprite, 'foto_tomada'):
                delattr(camara.sprite, 'foto_tomada')
            if hasattr(camara.sprite, 'astros_demo'):
                delattr(camara.sprite, 'astros_demo')
            estado_actual = ESTADO_INTERMISION3
            tiempo_inicio_intermision3 = pygame.time.get_ticks()
        else:
            tiempo_restante = 7 - int((tiempo_actual - tiempo_inicio_intermision2) / 1000)

    if estado_actual == "intermision3":
        tiempo_actual = pygame.time.get_ticks()
        
        if not hasattr(camara.sprite, 'iniciado_tutorial3'):
            camara.sprite.iniciado_tutorial3 = True
            camara.sprite.indice_astro3 = 0
            camara.sprite.puntuacion_tutorial = 0
            
            astros_demo3 = []
            posiciones3 = [
                (ancho // 2 + 200, alto // 2),
                (ancho // 2 - 150, alto // 2 - 80),
                (ancho // 2 + 100, alto // 2 - 120)
            ]
            nombres3 = ["Luna", "Marte", "Venus"]
            
            for pos, nombre in zip(posiciones3, nombres3):
                astro_demo3 = pygame.sprite.Sprite()
                astro_demo3.image = assets_astros[nombre].copy()
                astro_demo3.rect = astro_demo3.image.get_rect(center = pos)
                astro_demo3.radio_deteccion = 150
                astro_demo3.image.set_alpha(0)
                astros_grupo.add(astro_demo3)
                astros_demo3.append(astro_demo3)
            
            camara.sprite.astros_demo3 = astros_demo3
        
        astros_demo3 = camara.sprite.astros_demo3
        indice3 = camara.sprite.indice_astro3
        
        if indice3 < len(astros_demo3):
            astro = astros_demo3[indice3]
            
            distancia = math.dist(astro.rect.center, camara.sprite.rect.center)
            if distancia < astro.radio_deteccion:
                proporcion = 1 - (distancia / astro.radio_deteccion)            
                nuevo_alpha = int(proporcion * 255)
                astro.image.set_alpha(nuevo_alpha)
            else:
                astro.image.set_alpha(0)
            
            dx = astro.rect.centerx - camara.sprite.rect.centerx
            dy = astro.rect.centery - camara.sprite.rect.centery
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > 10:
                if abs(dx) > abs(dy):
                    camara.sprite.rect.x += 2 if dx > 0 else -2
                else:
                    camara.sprite.rect.y += 2 if dy > 0 else -2
            else:
                if not hasattr(camara.sprite, 'foto_tomada3'):
                    camara.sprite.foto_tomada3 = True
                    flash_activo = True
                    flash_tiempo = tiempo_actual
                    camara.sprite.puntuacion_tutorial += 100
                    camara.sprite.indice_astro3 += 1
                    astro.kill()
                    delattr(camara.sprite, 'foto_tomada3')
        
        astros_grupo.draw(pantalla)
        camara.sprite.update()
        camara.draw(pantalla)
        
        mostrar_puntos_partida(camara.sprite.puntuacion_tutorial)
        dibujar_objetivo()
        mostrar_flash()
        
        if asignar_tiempo_transicion(tiempo_inicio_intermision3):
            for astro in astros_grupo:
                astro.kill()
            fotos = 5
            if hasattr(camara.sprite, 'iniciado_tutorial3'):
                delattr(camara.sprite, 'iniciado_tutorial3')
            if hasattr(camara.sprite, 'indice_astro3'):
                delattr(camara.sprite, 'indice_astro3')
            if hasattr(camara.sprite, 'puntuacion_tutorial'):
                delattr(camara.sprite, 'puntuacion_tutorial')
            if hasattr(camara.sprite, 'foto_tomada3'):
                delattr(camara.sprite, 'foto_tomada3')
            if hasattr(camara.sprite, 'astros_demo3'):
                delattr(camara.sprite, 'astros_demo3')
            tiempo_inicio_intermision4 = pygame.time.get_ticks()
            estado_actual = ESTADO_INTERMISION4

    if estado_actual == "intermision4":
        tiempo_transcurrido = (pygame.time.get_ticks() - tiempo_inicio_intermision4) / 1000
        
        if tiempo_transcurrido < 1:
            texto = fuente_titulo.render("PREPARATE", False, (255, 255, 255))
        elif tiempo_transcurrido < 2:
            texto = fuente_titulo.render("3", False, (255, 255, 255))
        elif tiempo_transcurrido < 3:
            texto = fuente_titulo.render("2", False, (255, 255, 255))
        elif tiempo_transcurrido < 4:
            texto = fuente_titulo.render("1", False, (255, 255, 255))
        elif tiempo_transcurrido < 5:
            texto = fuente_titulo.render("A JUGAR", False, (0, 255, 0))
        else:
            fotos = 5
            camara.sprite.rect.center = (ancho // 2, alto // 2)
            estado_actual = ESTADO_JUGANDO
            ticks_inicio_juego = pygame.time.get_ticks()
            crear_astros()
        
        if estado_actual == "intermision4":
            texto_rect = texto.get_rect(center=(ancho // 2, alto // 2))
            pantalla.blit(texto, texto_rect)

    if estado_actual == 'jugando':
        mostrar_puntos_partida()
        
        if tiempo_pausado:
            delay = 2000
            if pygame.time.get_ticks() - tiempo_fotos_agotadas > delay:
                fotos_reporte_instancias.clear()
                pagina_actual = 0
                estado_actual = ESTADO_REPORTE
                fotos = 5
                tiempo_pausado = False
            else:
                if tipo_pausa == "objetivo":
                    texto_fotos = fuente_titulo.render("OBJETIVO CUMPLIDO", False, (255, 215, 0))
                else:
                    texto_fotos = fuente_titulo.render("FOTOS AGOTADAS", False, (255, 0, 0))
                texto_rect = texto_fotos.get_rect(center = (ancho // 2, alto // 2))
                pantalla.blit(texto_fotos, texto_rect)
        else:
            camara.update()

            tiempo_transcurrido = (pygame.time.get_ticks() - ticks_inicio_juego) / 1000
            tiempo_restante = tiempo_inicial - tiempo_transcurrido
            if tiempo_restante <= 0:
                fotos_reporte_instancias.clear()
                pagina_actual = 0
                estado_actual = ESTADO_REPORTE
            else:
                mostrar_tiempo(tiempo_restante)
                mostrar_camaras()
        

        pos_v = camara.sprite.rect.center
        
        for astro in astros_grupo:
            astro.update_visual(pos_v) 

        astros_grupo.draw(pantalla)
        astro_actual = colision()
        if not tiempo_pausado:
            camara.draw(pantalla)
        mostrar_flash()


    if estado_actual == 'reporte':
        mostrar_reporte()

    if estado_actual == 'puntajes':
        mostrar_puntajes()

    pygame.display.update()
    clock.tick(60)