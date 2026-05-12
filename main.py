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
          
    def update(self):
        self.movimiento()

class Astro(pygame.sprite.Sprite):
    def __init__(self, astro, posicion):
        super().__init__()
        self.nombre = astro["nombre"]
        self.puntos = astro["puntos"]
        self.image = assets_astros[self.nombre].copy() # Usamos copy por si modificamos el alpha
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
                False
        else:
            self.image.set_alpha(0)
            self.seleccionado = False
    

    def update(self):
        pass
        

def dibujar_controles():
    ancla = (ancho / 2.5, alto / 1.2)
    texto_mov = fuente_normal.render("Movimiento", False, (255,255,255))
    texto_mov_rect = texto_mov.get_rect(midbottom = tuple(a + b for a, b in zip(ancla, (0, -80))))
    texto_inicio = fuente_normal.render("Presione", False, (255,255,255))
    texto_inicio_rect = texto_inicio.get_rect(midbottom = tuple(a + b for a, b in zip(ancla, (250, -80))))
    texto_foto = fuente_normal.render("Para Jugar", False, (255,255,255))
    texto_foto_rect = texto_foto.get_rect(midbottom = tuple(a + b for a, b in zip(ancla, (250, -50)))) 
    
    for t in datos_teclas:
        ancla_flecha = tuple(a + b for a, b in zip(ancla, t["offset"]))
        rectangulo = t["img"].get_rect(center = ancla_flecha)
        pantalla.blit(t["img"], rectangulo)
    
    pantalla.blit(texto_mov, texto_mov_rect)
    pantalla.blit(texto_inicio, texto_inicio_rect)
    pantalla.blit(texto_foto, texto_foto_rect)

def mostrar_menu():
    pantalla.fill((0,0,0))
    nombre = fuente_titulo.render("ArcSpace", False, (255,255,255))
    nombre_rect = nombre.get_rect(center = (ancho / 2, alto / 8))
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

    pantalla.blit(nombre, nombre_rect)
    pantalla.blit(scores_title, scores_title_rect)
    dibujar_controles()

def tomar_foto():    
    colisiones = pygame.sprite.spritecollide(camara.sprite, astros_grupo, False)
    p = 0
    if colisiones:
        p = colisiones[0].puntos
        album.append(colisiones[0].nombre)
        colisiones[0].kill()
        return p

def colision():
        colisiones = pygame.sprite.spritecollide(camara.sprite, astros_grupo, False)
        if colisiones:
            return colisiones[0]
        else:
            return None

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
# Estados posibles
ESTADO_MENU = "menu"
ESTADO_JUGANDO = "jugando"
ESTADO_REPORTE = "reporte"

# Estado inicial
estado_actual = ESTADO_MENU

#Menu
img_up = pygame.image.load("assets/Graphics/Keyboard & Mouse/Default/keyboard_arrow_up.png").convert_alpha()
img_down = pygame.image.load("assets/Graphics/Keyboard & Mouse/Default/keyboard_arrow_down.png").convert_alpha()
img_left = pygame.image.load("assets/Graphics/Keyboard & Mouse/Default/keyboard_arrow_left.png").convert_alpha()
img_right = pygame.image.load("assets/Graphics/Keyboard & Mouse/Default/keyboard_arrow_right.png").convert_alpha()
img_space = pygame.image.load("assets/Graphics/Keyboard & Mouse/Double/keyboard_space.png").convert_alpha()
datos_teclas = [
    {"img": img_up, "offset": (0, -50)},   
    {"img": img_down, "offset": (0, 0)},  
    {"img": img_left, "offset": (-50, 0)},  
    {"img": img_right, "offset": (50, 0)},
    {"img": img_space, "offset": (250, -5)}   
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
    "Luna": pygame.transform.scale(pygame.image.load("assets/Graphics/Astros/Luna.png").convert_alpha(), (105, 105)),
    "Marte": pygame.transform.scale(pygame.image.load("assets/Graphics/Astros/Marte.png").convert_alpha(), (105, 105)),
    "Mercurio": pygame.transform.scale(pygame.image.load("assets/Graphics/Astros/Mercurio.png").convert_alpha(), (70, 70)),
    "Venus": pygame.transform.scale(pygame.image.load("assets/Graphics/Astros/Venus.png").convert_alpha(), (105, 105)),
    "Jupiter": pygame.transform.scale(pygame.image.load("assets/Graphics/Astros/Jupiter.png").convert_alpha(), (154, 154)),
    "Saturno": pygame.transform.scale(pygame.image.load("assets/Graphics/Astros/Saturno.png").convert_alpha(), (175, 105)),
    "Urano": pygame.transform.scale(pygame.image.load("assets/Graphics/Astros/Urano.png").convert_alpha(), (112, 112)),
    "Neptuno": pygame.transform.scale(pygame.image.load("assets/Graphics/Astros/Neptuno.png").convert_alpha(), (112, 112)),
    "Estacion": pygame.transform.scale(pygame.image.load("assets/Graphics/Astros/Estacion.png").convert_alpha(), (84, 84)),
    }

astros = []
with open("data/astros.json", "r") as f:
    datos = json.load(f)
    for item in datos["astros"]:
        astros.append(item)

astro_en_foco = None
astro_actual = None

#Puntuacion
puntuacion = 0

#Fotos tomadas
album = []

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        
        if estado_actual == 'menu':
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                estado_actual = ESTADO_JUGANDO
                astros_grupo = pygame.sprite.Group()
                
                posiciones_listas = generar_posiciones_validas(len(astros), 120) # 120px de distancia mín.
                for i, dato_astro in enumerate(astros):
                    # Si no hay suficientes posiciones válidas, usamos una por defecto para no romper el juego
                    if i < len(posiciones_listas):
                        pos = posiciones_listas[i]
                    else:
                        pos = (randint(0, ancho), randint(0, alto))
                    
                    nuevo_astro = Astro(dato_astro, pos)
                    astros_grupo.add(nuevo_astro)
        
        elif estado_actual == 'jugando':
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                fotos -= 1
                if fotos <= 0:
                    estado_actual = ESTADO_REPORTE
                    fotos = 5
                puntuacion += tomar_foto()


    if estado_actual == 'menu':
        mostrar_menu()
    
    if estado_actual == 'jugando':
        pantalla.fill((11, 9, 28))
        camara.draw(pantalla)
        camara.update()

        pos_v = camara.sprite.rect.center
        for astro in astros_grupo:
            astro.update_visual(pos_v)
        
        astros_grupo.draw(pantalla)
        astro_actual = colision()

        # if astro_actual != astro_en_foco:   
        #     if astro_en_foco is not None:
        #         astro_en_foco.seleccionado = False
            
        #     if astro_actual is not None:
        #         astro_actual.seleccionado = True
        #         print(f"Enfocando: {astro_actual.nombre}")
        #     astro_en_foco = astro_actual

    if estado_actual == 'reporte':
        pantalla.fill("#000000")   
        
    pygame.display.update()
    clock.tick(60)