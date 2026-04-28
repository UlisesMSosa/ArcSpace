# ArcSpace
Observatorio Estelar Arcade

Este proyecto es una herramienta educativa diseñada para niños de nivel primario (7-8 años), desarrollada como parte de la Tecnicatura en Desarrollo de Software. El objetivo es enseñar conceptos básicos de **astronomía** y **lógica de programación**, utilizando la **probabilidad** como puente entre la ciencia y el software.

##  Descripción del Proyecto
El juego simula un observatorio digital donde los estudiantes asumen el rol de astrónomos. Utilizando un visor de telescopio/camara, deben explorar el cielo nocturno en busca de astros ocultos. La experiencia combina mecánicas de juegos arcade (tiempo limitado e intentos) con el descubrimiento de información científica real.

###  Conceptos Aplicados

- **Astronomía:** Reconocimiento de los objetos del Sistema Solar.
- **Probabilidad:** El azar influye en la "calidad del revelado" de las fotografías y en la aparición de eventos astronómicos raros (cometas o eclipses), simulando los desafíos reales de la observación atmosférica.
- **Programación y Gestión:** - Gestión de datos persistentes mediante archivos **JSON**.
  - Lógica de detección de colisiones y manejo de estados de software.
  - Estructuración de un ranking de puntajes para fomentar la participación.

##  Mecánica del Juego
1. **Registro:** El estudiante ingresa su nombre y grado para participar del ranking.
2. **Exploración:** Controla el visor del telescopio/camara con las flechas del teclado. El lente dará señales visuales al estar cerca de un hallazgo.
3. **Captura:** El jugador tiene intentos limitados para tomar "fotos" espaciales.
4. **Reporte de Misión:** Al finalizar el tiempo, se muestra una galería con imágenes reales de los objetos capturados y datos curiosos sobre cada uno.

##  Tecnologías Utilizadas
- **Python:** Lenguaje principal.
- **Pygame:** Librería para la lógica del juego y renderizado gráfico.
- **JSON:** Formato de almacenamiento para los datos de los astros y el sistema de puntajes.