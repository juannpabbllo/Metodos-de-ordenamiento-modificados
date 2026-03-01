import pygame
import heapq
import time

# --- CONFIGURACIÓN DE COLORES (Paleta Moderna) ---
BG_COLOR = (18, 18, 18)      # Gris casi negro
NODE_COLOR = (45, 45, 45)    # Gris oscuro
TEXT_COLOR = (240, 240, 240) # Blanco roto
HIGHLIGHT = (255, 215, 0)    # Dorado (Procesando)
VISITED = (0, 120, 215)      # Azul Windows (Visitado)
PATH_COLOR = (0, 255, 127)   # Verde neón (Ruta final)
LINE_COLOR = (60, 60, 60)    # Líneas base

class SimuladorCETI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((900, 600))
        pygame.display.set_caption("Dijkstra Navigator: Misión CETI")
        self.font = pygame.font.SysFont("Segoe UI", 18, bold=True)
        self.clock = pygame.time.Clock()

        # Posiciones de los nodos (X, Y)
        self.nodos = {
            'Mi Casa': (100, 300),
            'Parada del camion': (300, 150),
            'Ciclovia': (300, 450),
            'Avenida Principal': (550, 150),
            'Atajo Callejones': (550, 450),
            'CETI Colomos': (800, 300)
        }

        # Grafo con pesos (minutos)
        self.grafo = {
            'Mi Casa': [('Parada del camion', 8), ('Ciclovia', 12)],
            'Parada del camion': [('Avenida Principal', 15), ('Atajo Callejones', 10)],
            'Ciclovia': [('Atajo Callejones', 5)],
            'Avenida Principal': [('CETI Colomos', 5)],
            'Atajo Callejones': [('Avenida Principal', 3), ('CETI Colomos', 12)],
            'CETI Colomos': []
        }

    def dibujar_grafo(self, estados, ruta_final=None):
        self.screen.fill(BG_COLOR)

        # 1. Dibujar Aristas (Líneas)
        for u, vecinos in self.grafo.items():
            for v, peso in vecinos:
                color = LINE_COLOR
                ancho = 2
                pygame.draw.line(self.screen, color, self.nodos[u], self.nodos[v], ancho)
                
                # Dibujar peso del vértice (minutos)
                mid_x = (self.nodos[u][0] + self.nodos[v][0]) // 2
                mid_y = (self.nodos[u][1] + self.nodos[v][1]) // 2
                txt = self.font.render(f"{peso} min", True, (150, 150, 150))
                self.screen.blit(txt, (mid_x, mid_y - 20))

        # 2. Dibujar Ruta Final si existe
        if ruta_final:
            for i in range(len(ruta_final)-1):
                u, v = ruta_final[i], ruta_final[i+1]
                pygame.draw.line(self.screen, PATH_COLOR, self.nodos[u], self.nodos[v], 6)

        # 3. Dibujar Nodos
        for nombre, pos in self.nodos.items():
            color = NODE_COLOR
            if nombre in estados['visitados']: color = VISITED
            if nombre == estados['actual']: color = HIGHLIGHT
            if ruta_final and nombre in ruta_final: color = PATH_COLOR

            # Sombra/Brillo del nodo
            pygame.draw.circle(self.screen, color, pos, 30)
            pygame.draw.circle(self.screen, TEXT_COLOR, pos, 30, 2) # Borde

            # Texto del nodo
            txt = self.font.render(nombre, True, TEXT_COLOR)
            self.screen.blit(txt, (pos[0] - txt.get_width()//2, pos[1] + 40))

        pygame.display.flip()

    def ejecutar(self):
        inicio = 'Mi Casa'
        fin = 'CETI Colomos'
        distancias = {n: float('inf') for n in self.nodos}
        distancias[inicio] = 0
        previos = {n: None for n in self.nodos}
        cola = [(0, inicio)]
        visitados = set()

        estados = {'actual': None, 'visitados': visitados}

        running = True
        paso_a_paso = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            if paso_a_paso and cola:
                d_u, u = heapq.heappop(cola)
                if u in visitados: continue

                estados['actual'] = u
                self.dibujar_grafo(estados)

                esperando = True
                while esperando:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                            esperando = False
                        elif event.type == pygame.QUIT:
                            pygame.quit()
                            return

                visitados.add(u)

                for v, peso in self.grafo[u]:
                    alt = distancias[u] + peso
                    if alt < distancias[v]:
                        distancias[v] = alt
                        previos[v] = u
                        heapq.heappush(cola, (alt, v))

                if u == fin:
                    paso_a_paso = False
                    # Reconstruir camino
                    ruta = []
                    curr = fin
                    while curr:
                        ruta.append(curr)
                        curr = previos[curr]
                    ruta = ruta[::-1]
                    self.dibujar_grafo(estados, ruta)

                    # Mostrar tiempo total
                    tiempo_total = distancias[fin]
                    texto_tiempo = self.font.render(f"Tiempo total: {tiempo_total} minutos", True, TEXT_COLOR)
                    self.screen.blit(texto_tiempo, (450 - texto_tiempo.get_width() // 2, 550))
                    pygame.display.flip()

            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    sim = SimuladorCETI()
    sim.ejecutar()