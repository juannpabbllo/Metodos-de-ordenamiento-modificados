import pygame
import sys
import time

# --- CONFIGURACIÓN DE COLORES ---
BG_COLOR = (18, 18, 18)
NODE_COLOR = (45, 45, 45)
TEXT_COLOR = (240, 240, 240)
CURRENT_NODE = (255, 215, 0)   # Dorado (Nodo explorando)
IN_MST = (0, 120, 215)         # Azul (Ya conectado a la red)
PATH_COLOR = (0, 255, 127)     # Verde neón (Tubería instalada)
LINE_BASE = (60, 60, 60)       # Conexiones posibles

class SimuladorPrim:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((950, 650))
        pygame.display.set_caption("Prim: Instalación de Red Hidráulica")
        self.font = pygame.font.SysFont("Segoe UI", 17, bold=True)
        self.title_font = pygame.font.SysFont("Segoe UI", 24, bold=True)
        self.clock = pygame.time.Clock()

        # Nodos: Puntos de suministro de agua
        self.nodos_nombres = ['Pozo Central', 'Torre A', 'Torre B', 'Área Común', 'Gimnasio']
        self.posiciones = {
            'Pozo Central': (150, 300),
            'Torre A': (400, 150),
            'Torre B': (400, 450),
            'Área Común': (700, 150),
            'Gimnasio': (700, 450)
        }

        # Matriz de adyacencia (Peso = metros de tubería)
        #                 Pozo, T.A, T.B, A.C, Gim
        self.matrix = [[0, 2, 0, 6, 0],   # Pozo
                       [2, 0, 3, 8, 5],   # Torre A
                       [0, 3, 0, 0, 7],   # Torre B
                       [6, 8, 0, 0, 9],   # Área Común
                       [0, 5, 7, 9, 0]]   # Gimnasio

    def dibujar_escena(self, mst_set, parent, u_actual=None, mensaje="", costo=0):
        self.screen.fill(BG_COLOR)
        
        # Títulos
        titulo = self.title_font.render("RED HIDRÁULICA: ALGORITMO DE PRIM", True, TEXT_COLOR)
        self.screen.blit(titulo, (50, 20))
        info_costo = self.font.render(f"Tubería total: {costo} metros", True, PATH_COLOR)
        self.screen.blit(info_costo, (50, 550))
        status = self.font.render(f"Estado: {mensaje}", True, (200, 200, 200))
        self.screen.blit(status, (50, 590))

        # 1. Dibujar conexiones posibles (Base)
        for i in range(len(self.matrix)):
            for j in range(i + 1, len(self.matrix)):
                if self.matrix[i][j] > 0:
                    p1 = self.posiciones[self.nodos_nombres[i]]
                    p2 = self.posiciones[self.nodos_nombres[j]]
                    pygame.draw.line(self.screen, LINE_BASE, p1, p2, 1)
                    # Dibujar peso
                    mid = ((p1[0]+p2[0])//2, (p1[1]+p2[1])//2)
                    txt = self.font.render(f"{self.matrix[i][j]}m", True, (100, 100, 100))
                    self.screen.blit(txt, mid)

        # 2. Dibujar Tuberías instaladas (MST)
        for i in range(1, len(self.nodos_nombres)):
            if parent[i] is not None:
                p1 = self.posiciones[self.nodos_nombres[i]]
                p2 = self.posiciones[self.nodos_nombres[parent[i]]]
                pygame.draw.line(self.screen, PATH_COLOR, p1, p2, 5)

        # 3. Dibujar Nodos
        for i, nombre in enumerate(self.nodos_nombres):
            pos = self.posiciones[nombre]
            color = NODE_COLOR
            if mst_set[i]: color = IN_MST
            if i == u_actual: color = CURRENT_NODE

            pygame.draw.circle(self.screen, color, pos, 25)
            pygame.draw.circle(self.screen, TEXT_COLOR, pos, 25, 2)
            
            label = self.font.render(nombre, True, TEXT_COLOR)
            self.screen.blit(label, (pos[0] - label.get_width()//2, pos[1] + 35))

        pygame.display.flip()

    def ejecutar(self):
        V = len(self.nodos_nombres)
        key = [sys.maxsize] * V
        parent = [None] * V
        mst_set = [False] * V
        key[0] = 0
        parent[0] = -1
        costo_total = 0

        running = True
        pasos_completados = 0

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

            if pasos_completados < V:
                # min_key logic
                min_val = sys.maxsize
                u = -1
                for v in range(V):
                    if key[v] < min_val and not mst_set[v]:
                        min_val = key[v]
                        u = v

                if u != -1:
                    # Visualizar expansión
                    nombre_u = self.nodos_nombres[u]
                    self.dibujar_escena(mst_set, parent, u, f"Conectando {nombre_u} a la red...", costo_total)

                    esperando = True
                    while esperando:
                        for event in pygame.event.get():
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_RETURN:
                                    esperando = False
                                elif event.key == pygame.K_ESCAPE:
                                    pygame.quit()
                                    return

                    mst_set[u] = True
                    if parent[u] != -1:
                        costo_total += self.matrix[u][parent[u]]

                    # Actualizar vecinos
                    for v in range(V):
                        if 0 < self.matrix[u][v] < key[v] and not mst_set[v]:
                            key[v] = self.matrix[u][v]
                            parent[v] = u
                            self.dibujar_escena(mst_set, parent, u, f"Nueva opción: {nombre_u} -> {self.nodos_nombres[v]}", costo_total)

                            esperando = True
                            while esperando:
                                for event in pygame.event.get():
                                    if event.type == pygame.KEYDOWN:
                                        if event.key == pygame.K_RETURN:
                                            esperando = False
                                        elif event.key == pygame.K_ESCAPE:
                                            pygame.quit()
                                            return

                pasos_completados += 1
            else:
                self.dibujar_escena(mst_set, parent, None, "Red hidráulica optimizada.", costo_total)

            self.clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    SimuladorPrim().ejecutar()