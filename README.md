# ArcSpace: Observatorio Estelar Arcade

**Proyecto Educativo e Institucional** *Desarrollado para la Tecnicatura Superior en Desarrollo de Software* **Público Objetivo:** Niños de 6, 7 y 8 años (Primer Ciclo de la Escuela Primaria).  
**Tecnologías:** Python 3 + Pygame.

---

## 🌌 Propósito del Proyecto y Enfoque Pedagógico

**ArcSpace** es un videojuego educativo e interactivo en 2D que fusiona la emoción de las mecánicas arcade clásicas con la divulgación científica astronómica. El software sitúa al niño en el rol de un explorador espacial que, equipado con un telescopio digital, debe registrar de forma fotográfica los diversos astros del universo.

### Adaptación para la Infancia (6 a 8 años)
Teniendo en cuenta el desarrollo cognitivo y motriz del rango de edad objetivo, el diseño del software implementa las siguientes pautas:
- **Gamificación Dinámica sin Frustración:** El juego utiliza un sistema de "Intermisiones" narrativas y pausas guiadas. Si el tiempo de juego expira, el niño no "pierde" de forma punitiva, sino que avanza hacia la estación de revelado para interactuar con lo descubierto.
- **Estimulación Visomotora:** El control de la mira telescópica mediante movimientos suaves entrena el reconocimiento espacial, la precisión analógica y la coordinación ojo-mano.
- **Refuerzo Positivo Coleccionable:** La transición al "Álbum de Fotos" digital fomenta el sentido de pertenencia y logro a través de la gamificación permanente, invitando a la rejugabilidad para completar las páginas de descubrimientos.

---

## 🛠️ Arquitectura de Software y Conceptos Técnicos

Para cumplir con los estándares académicos de la Tecnicatura, el código fuente fue desarrollado bajo sólidos principios de ingeniería de software para entornos 2D:

### 1. Máquina de Estados Finitos (FSM)
El flujo completo de las pantallas y transiciones del videojuego está estructurado mediante un motor de estados centralizado. Esto desacopla de manera limpia las responsabilidades visuales y lógicas a través de las siguientes fases:
- `ESTADO_MENU`: Pantalla de bienvenida e inicialización.
- `ESTADOS_INTERMISION` (1 al 4 + Pausas/Mejoras): Bloques narrativos interactivos y de transición lúdica que controlan el hilo conductor de la partida.
- `ESTADO_JUGANDO`: Núcleo del gameplay, renderizado de sprites dinámicos y captura visomotora.
- `ESTADO_REPORTE`: Fase analítica donde se procesa, escala y revela el material fotográfico obtenido en la sesión.
- `ESTADO_ALBUM_PUNTAJES` y `ESTADO_PUNTAJES`: Módulos encargados de mostrar las métricas lúdicas e históricas.

### 2. Persistencia de Datos local (JSON)
El juego no pierde el progreso del estudiante al cerrarse. Cuenta con un sistema de serialización de datos nativo que administra el archivo de guardado `album.json`.
- **Estructura del Almacenamiento:** Registra de manera persistente las fotos ya desbloqueadas (evitando duplicaciones vacías en el álbum permanente) y el historial de puntajes máximos con su respectiva marca de tiempo (`datetime`).

### 3. Animación Matemática y Transformaciones de Matriz
- **Revelado Polar Analógico:** En la pantalla de reporte, el juego simula el revelado físico de una fotografía Polaroid mediante transformaciones de escala dinámicas (`pygame.transform.scale`) animadas en base a giros polares y reducciones progresivas que aportan un efecto de profundidad visual fluido.
- **Cálculo Cinemático de Visores:** Las coordenadas visuales y los límites del zoom se gestionan a través de vectores bidimensionales (`pygame.Vector2`), optimizando el rendimiento de las colisiones en pantalla.

### 4. Algoritmo Procedural Anti-Superposición
Para garantizar un mapa de juego limpio y equilibrado en cada nivel, se implementó un algoritmo dinámico de **generación de posiciones válidas por radio de seguridad decreciente**. El sistema busca de manera iterativa coordenadas aleatorias para cada astro en el plano de `1280x720`, asegurándose mediante álgebra vectorial que ningún cuerpo celeste tape o solape visualmente a otro. Si el mapa se satura, el radio se comprime de forma controlada para asegurar el despliegue del 100% de los elementos requeridos por el nivel.

##  Tecnologías Utilizadas
- **Python:** Lenguaje principal.
- **Pygame:** Librería para la lógica del juego y renderizado gráfico.
- **JSON:** Formato de almacenamiento para los datos de los astros y el sistema de puntajes.
- **OpenCode** Para refinar estados y animaciones.
- **Claude** Para refinar el estado del codigo en general y hacerlo más legible.