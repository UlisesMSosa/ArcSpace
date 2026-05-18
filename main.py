import pygame
import json
from sys import exit
from random import randint
import math

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
    global nombre_jugador
    titulo = fuente_titulo.render("ArcSpace", False, (255,255,255))
    titulo_rect = titulo.get_rect(center = (ancho / 2, alto / 8))
    scores_title = fuente_normal.render("Puntajes", False, (255,0,0))
    scores_title_rect = scores_title.get_rect(midleft = (ancho / 1.31 , alto / 7))

    ancla = (ancho / 1.38, alto / 14)
    offset = (0, 50)
    posicion_final = tuple(a + b for a, b in zip(ancla, offset))

    for score in scores:
        posicion_final = tuple(a + b for a, b in zip(posicion_final, offset))
        score_surf = fuente_normal.render(f"{score["nombre"]}: {score["puntos"]}", False, (255, 0, 0))
        score_rect = score_surf.get_rect(topleft = posicion_final)
        pantalla.blit(score_surf, score_rect)

    pantalla.blit(titulo, titulo_rect)
    pantalla.blit(scores_title, scores_title_rect)

    input_label = fuente_media.render("INGRESA TU NOMBRE", False, (255,255,255))
    input_label_rect = input_label.get_rect(center = (ancho / 2, alto / 2))
    pantalla.blit(input_label, input_label_rect)

    nombre_ingresado = fuente_titulo.render(nombre_jugador, False, (150, 50, 200))
    nombre_ingresado_rect = nombre_ingresado.get_rect(center = (ancho / 2, alto / 2 + 70))
    pantalla.blit(nombre_ingresado, nombre_ingresado_rect)

    instruccion = fuente_media.render("PRESIONE ESPACIO PARA INICIAR", False, (255,255,255))
    instruccion_rect = instruccion.get_rect(center = (ancho / 2, alto / 2 + 140))
    pantalla.blit(instruccion, instruccion_rect)

def crear_astros():
    global nivel
    astros_nivel = [a for a in astros if a.get("nivel") == nivel]
    total_cantidad = sum(a.get("cantidad", 1) for a in astros_nivel)
    posiciones_listas = generar_posiciones_validas(total_cantidad, 120)
    for i, dato_astro in enumerate(astros_nivel):
        cantidad = dato_astro.get("cantidad", 1)
        for j in range(cantidad):
            pos_index = i + j
            if pos_index < len(posiciones_listas):
                pos = posiciones_listas[pos_index]
            else:
                pos = (randint(0, ancho), randint(0, alto))
            nuevo_astro = Astro(dato_astro, pos)
            astros_grupo.add(nuevo_astro)

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

def mostrar_reporte():
    global nivel
    rect_ancho = int(ancho * 0.9)
    rect_alto = 200
    x = (ancho - rect_ancho) // 2
    y = 20
    pygame.draw.rect(pantalla, (48, 39, 38), (x, y, rect_ancho, rect_alto), border_radius=20)

    if album:
        tamano_foto = 120
        espacio = 20
        total_fotos = len(album)
        ancho_total = total_fotos * tamano_foto + (total_fotos - 1) * espacio
        inicio_x = x + (rect_ancho - ancho_total) // 2
        y_foto = y + (rect_alto - tamano_foto) // 2
        
        for i, item in enumerate(album):
            img = assets_astros.get(item["nombre"])
            if img:
                img_redim = pygame.transform.scale(img, (tamano_foto, tamano_foto))
                pos_x = inicio_x + i * (tamano_foto + espacio)
                pygame.draw.rect(pantalla, (212, 193, 190), (pos_x - 6, y_foto - 6, tamano_foto + 12, tamano_foto + 12), border_radius=2)
                pygame.draw.rect(pantalla, (0, 0, 0), (pos_x - 6, y_foto - 6, tamano_foto + 12, tamano_foto + 12), 3, border_radius=2)
                pantalla.blit(img_redim, (pos_x, y_foto))

    if puntuacion >= objetivo:
        texto = fuente_normal.render("Avanzar al siguiente nivel", False, (255, 215, 0))
    else:
        texto = fuente_normal.render("Intentar de nuevo", False, (255, 0, 0))
    texto_rect = texto.get_rect(center=(ancho // 2, alto // 2))
    pantalla.blit(texto, texto_rect)
    img_space_rect = img_space.get_rect(center=(ancho // 2, alto // 2 + 50))
    pantalla.blit(img_space, img_space_rect)
    texto_menu = fuente_pequena.render("Volver al menu", False, (255, 255, 255))
    texto_rect = texto_menu.get_rect(left=20, centery=alto - 30)
    pantalla.blit(texto_menu, texto_rect)
    img_m_redim = pygame.transform.scale(img_m, (30, 30))
    img_m_rect = img_m_redim.get_rect(left=texto_rect.right + 10, centery=alto - 30)
    pantalla.blit(img_m_redim, img_m_rect)

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

pygame.init()
ancho = 1280
alto = 720
centro = (ancho //2, alto // 2)
pantalla = pygame.display.set_mode((ancho,alto))
pygame.display.set_caption("ArcSpace")
clock = pygame.time.Clock()
fuente_titulo = pygame.font.Font("assets/Fonts/Silkscreen/Silkscreen-Regular.ttf", 80)
fuente_normal = pygame.font.Font("assets/Fonts/Silkscreen/Silkscreen-Regular.ttf", 30)
fuente_media = pygame.font.Font("assets/Fonts/Silkscreen/Silkscreen-Regular.ttf", 50)
fuente_pequena = pygame.font.Font("assets/Fonts/Silkscreen/Silkscreen-Regular.ttf", 20)

img_camara = pygame.transform.scale(pygame.image.load("assets/Graphics/Camara.png").convert_alpha(), (60, 60))
# Estados posibles
ESTADO_MENU = "menu"
ESTADO_INTERMISION1 = "intermision1"
ESTADO_INTERMISION2 = "intermision2"
ESTADO_INTERMISION3 = "intermision3"
ESTADO_INTERMISION4 = "intermision4"
ESTADO_JUGANDO = "jugando"
ESTADO_REPORTE = "reporte"

# Estado inicial
estado_actual = ESTADO_MENU

#Menu
fondo = pygame.transform.scale(pygame.image.load("assets/Graphics/fondo.png").convert(), (ancho,alto))
img_up = pygame.image.load("assets/Graphics/Keyboard & Mouse/Default/keyboard_arrow_up.png").convert_alpha()
img_down = pygame.image.load("assets/Graphics/Keyboard & Mouse/Default/keyboard_arrow_down.png").convert_alpha()
img_left = pygame.image.load("assets/Graphics/Keyboard & Mouse/Default/keyboard_arrow_left.png").convert_alpha()
img_right = pygame.image.load("assets/Graphics/Keyboard & Mouse/Default/keyboard_arrow_right.png").convert_alpha()
img_space = pygame.image.load("assets/Graphics/Keyboard & Mouse/Double/keyboard_space.png").convert_alpha()
img_m = pygame.image.load("assets/Graphics/Keyboard & Mouse/Default/keyboard_m.png").convert_alpha()
datos_teclas = [
    {"img": img_up, "offset": (0, -50)},   
    {"img": img_down, "offset": (0, 0)},  
    {"img": img_left, "offset": (-50, 0)},  
    {"img": img_right, "offset": (50, 0)} 
    ]

#Mostrar jugadores
scores = []
with open('data/scores.json', 'r') as f:
    datos = json.load(f)
    for item in datos["top_scores"]:
        scores.append(item)

#Juego
fotos = 5
camara = pygame.sprite.GroupSingle()
camara.add(Camara(ancho, alto))

#Astros
assets_astros = {
    "Luna": pygame.transform.scale(pygame.image.load("assets/Graphics/Astros/Luna.png").convert_alpha(), (140, 140)),
    "Venus": pygame.transform.scale(pygame.image.load("assets/Graphics/Astros/Venus.png").convert_alpha(), (120, 120)),
    "Mercurio": pygame.transform.scale(pygame.image.load("assets/Graphics/Astros/Mercurio.png").convert_alpha(), (100, 100)),
    "Marte": pygame.transform.scale(pygame.image.load("assets/Graphics/Astros/Marte.png").convert_alpha(), (90, 90)),
    "Estacion": pygame.transform.scale(pygame.image.load("assets/Graphics/Astros/Estacion.png").convert_alpha(), (80, 80)),
    "Jupiter": pygame.transform.scale(pygame.image.load("assets/Graphics/Astros/Jupiter.png").convert_alpha(), (70, 70)),
    "Saturno": pygame.transform.scale(pygame.image.load("assets/Graphics/Astros/Saturno.png").convert_alpha(), (100, 60)),
    "Urano": pygame.transform.scale(pygame.image.load("assets/Graphics/Astros/Urano.png").convert_alpha(), (50, 50)),
    "Neptuno": pygame.transform.scale(pygame.image.load("assets/Graphics/Astros/Neptuno.png").convert_alpha(), (45, 45)),
    "Estrella": pygame.transform.scale(pygame.image.load("assets/Graphics/Astros/Estrella.png").convert_alpha(), (45, 45)),
    }

astros = []
with open("data/astros.json", "r") as f:
    datos = json.load(f)
    for item in datos["astros"]:
        astros.append(item)


#Puntuacion
puntuacion = 0

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

##niveles
nivel = 1

##Objetivo
objetivo = 500

##Nombre jugador
nombre_jugador = ""

##Flash
flash_activo = False
flash_tiempo = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        
        if estado_actual == 'menu':
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if nombre_jugador:
                        tiempo_inicio_intermision1 = pygame.time.get_ticks()
                        estado_actual = ESTADO_INTERMISION1
                        astros_grupo = pygame.sprite.Group()
                        puntuacion = 0
                        tipo_pausa = ""
                        fotos_tutorial = 5
                        crear_astros()
                elif event.key == pygame.K_BACKSPACE:
                    nombre_jugador = nombre_jugador[:-1]
                else:
                    if len(nombre_jugador) < 10:
                        nombre_jugador += event.unicode
        

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
                puntuacion += tomar_foto()
                if puntuacion >= objetivo:
                    tiempo_pausado = True
                    tipo_pausa = "objetivo"
                    tiempo_fotos_agotadas = pygame.time.get_ticks()
                elif fotos <= 0:
                    tiempo_pausado = True
                    tipo_pausa = "fotos"
                    tiempo_fotos_agotadas = pygame.time.get_ticks()

        elif estado_actual == 'reporte':
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
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
                    album.clear()
                    coleccion.clear()
                    nivel = 1
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
                estado_actual = ESTADO_JUGANDO
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                album.clear()
                coleccion.clear()
                nivel = 1
                nombre_jugador = ""
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
        
    pygame.display.update()
    clock.tick(60)