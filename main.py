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
        self.image = pygame.Surface((radio * 2, radio * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center = (ancho/2, alto/2))
        self.velocidad = 4
        self.limite_ancho = limite_ancho
        self.limite_alto = limite_alto
        pygame.draw.circle(self.image, color_borde, (radio, radio), radio, 3)
        pygame.draw.line(self.image, color_borde, (45, 50), (55, 50), 2)
        pygame.draw.line(self.image, color_borde, (50, 45), (50, 55), 2)

    def controlar_bordes(self):
        if self.rect.left < 0: 
            self.rect.left = 0
        if self.rect.right > self.limite_ancho: 
            self.rect.right = self.limite_ancho
        if self.rect.top < 0: 
            self.rect.top = 0
        if self.rect.bottom > self.limite_alto: 
            self.rect.bottom = self.limite_alto      

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
    ##texto_inicio = fuente_normal.render("Presione", False, (255,255,255))
    ##texto_inicio_rect = texto_inicio.get_rect(midbottom = tuple(a + b for a, b in zip(ancla, (250, -80))))
    ##texto_foto = fuente_normal.render("Para Jugar", False, (255,255,255))
    ##texto_foto_rect = texto_foto.get_rect(midbottom = tuple(a + b for a, b in zip(ancla, (250, -50)))) 
    
    for t in datos_teclas:
        ancla_flecha = tuple(a + b for a, b in zip(ancla, t["offset"]))
        rectangulo = t["img"].get_rect(center = ancla_flecha)
        pantalla.blit(t["img"], rectangulo)
    
    pantalla.blit(texto_mov, texto_mov_rect)
    ##pantalla.blit(texto_inicio, texto_inicio_rect)
    ##pantalla.blit(texto_foto, texto_foto_rect)

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
    tiempo_restante = 5 - int(tiempo_transcurrido)
    if tiempo_restante <= 0:
        return True
    return False

def tomar_foto():    
    colisiones = pygame.sprite.spritecollide(camara.sprite, astros_grupo, False)
    p = 0
    if colisiones:
        p = colisiones[0].puntos
        album.append(colisiones[0].nombre)
        colisiones[0].kill()
        return p
    else:
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

def mostrar_puntos_partida():
    bar_width = 20
    bar_height = int(alto * 0.6)
    x = ancho - 75
    y = (alto - bar_height) // 2

    texto_puntos = fuente_normal.render("PUNTOS", False, (255, 255, 255))
    texto_rect = texto_puntos.get_rect(center=(x + bar_width // 2, y - 20))
    pantalla.blit(texto_puntos, texto_rect)

    pygame.draw.rect(pantalla, (64, 64, 64), (x, y, bar_width, bar_height), 2, border_radius=10)

def generar_posiciones_validas(cantidad, radio_seguridad):
    posiciones = []
    intentos_maximos = 100
    
    # Agregamos la posición de la cámara para que nada nazca encima del jugador
    posiciones.append(pygame.Vector2(ancho // 2, alto // 2))

    for _ in range(cantidad):
        for _ in range(intentos_maximos):
            candidata = pygame.Vector2(randint(100, ancho - 100), randint(100, alto - 100))
            
            # Verificamos si está lo suficientemente lejos de todas las posiciones ya aceptadas
            es_valida = True
            for p in posiciones:
                if candidata.distance_to(p) < radio_seguridad:
                    es_valida = False
                    break
            
            if es_valida:
                posiciones.append(candidata)
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
# Estados posibles
ESTADO_MENU = "menu"
ESTADO_INTERMISION1 = "intermision1"
ESTADO_INTERMISION2 = "intermision2"
ESTADO_INTERMISION3 = "intermision3"
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
tiempo_inicial = 10
ticks_inicio_juego = 0
tiempo_inicio_intermision1 = 0
tiempo_inicio_intermision2 = 0
tiempo_inicio_intermision3 = 0
#Fotos tomadas
album = []

##niveles
nivel = 1

##Nombre jugador
nombre_jugador = ""

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
                        crear_astros()
                elif event.key == pygame.K_BACKSPACE:
                    nombre_jugador = nombre_jugador[:-1]
                else:
                    if len(nombre_jugador) < 10:
                        nombre_jugador += event.unicode
        

        elif estado_actual == 'intermision1':
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                estado_actual = ESTADO_INTERMISION2
                tiempo_inicio_intermision2 = pygame.time.get_ticks()
                camara.sprite.rect.center = (ancho/2, alto/2)
                

        elif estado_actual == 'intermision2':
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                estado_actual = ESTADO_INTERMISION3
                tiempo_inicio_intermision3 = pygame.time.get_ticks()

        elif estado_actual == 'intermision3':
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                estado_actual = ESTADO_JUGANDO
                ticks_inicio_juego = pygame.time.get_ticks()
                astros_grupo = pygame.sprite.Group()
                crear_astros()

        elif estado_actual == 'jugando':
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                fotos -= 1
                if fotos <= 0:
                    estado_actual = ESTADO_REPORTE
                    fotos = 5
                puntuacion += tomar_foto()

        elif estado_actual == 'reporte':
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                for astro in astros_grupo:
                    astro.kill()
                astros_grupo = pygame.sprite.Group()
                crear_astros()
                ticks_inicio_juego = pygame.time.get_ticks()
                estado_actual = ESTADO_JUGANDO

    pantalla.blit(fondo, (0,0))

    if estado_actual == 'menu':
        mostrar_menu()
    
    if estado_actual == "intermision1":
        dibujar_controles()
        camara.draw(pantalla)
        camara.sprite.automatico()
        pos_v = camara.sprite.rect.center
        for astro in astros_grupo:
            astro.update_visual(pos_v)
        astros_grupo.draw(pantalla)

        if asignar_tiempo_transicion(tiempo_inicio_intermision1):
            estado_actual = ESTADO_INTERMISION2
            tiempo_inicio_intermision2 = pygame.time.get_ticks()
            camara.sprite.rect.center = (ancho/2, alto/2)

    if estado_actual == "intermision2":
        for astro in astros_grupo:
            astro.kill()
        astros_grupo = pygame.sprite.Group()
        if asignar_tiempo_transicion(tiempo_inicio_intermision2):
            estado_actual = ESTADO_INTERMISION3
            tiempo_inicio_intermision3 = pygame.time.get_ticks()

    if estado_actual == "intermision3":
        if asignar_tiempo_transicion(tiempo_inicio_intermision3):
            estado_actual = ESTADO_JUGANDO
            ticks_inicio_juego = pygame.time.get_ticks()
            crear_astros()

    if estado_actual == 'jugando':
        camara.draw(pantalla)
        camara.update()

        tiempo_transcurrido = (pygame.time.get_ticks() - ticks_inicio_juego) / 1000
        tiempo_restante = tiempo_inicial - tiempo_transcurrido
        if tiempo_restante <= 0:
            estado_actual = ESTADO_REPORTE
        else:
            mostrar_tiempo(tiempo_restante)
            mostrar_puntos_partida()
        

        pos_v = camara.sprite.rect.center
        
        for astro in astros_grupo:
            astro.update_visual(pos_v) 

        astros_grupo.draw(pantalla)
        astro_actual = colision()


    if estado_actual == 'reporte':
        pantalla.fill("#000000")   
        
    pygame.display.update()
    clock.tick(60)