import pygame
import time

# --- CONFIGURACIÓN DE COLORES ---
BG_COLOR = (18, 18, 18)      # Fondo oscuro
NODE_COLOR = (45, 45, 45)    # Nodo base
TEXT_COLOR = (240, 240, 240) # Texto
EVALUATING = (255, 140, 0)   # Naranja (Analizando arista)
ACCEPTED = (0, 255, 127)     # Verde Neón (Conexión exitosa)
REJECTED = (220, 20, 60)     # Carmesí (Ciclo detectado)
LINE_BASE = (60, 60, 60)     # Líneas del mapa original

class UnionFind:
    def __init__(self, nodes):
        self.parent = {node: node for node in nodes}
        self.rank = {node: 0 for node in nodes}

    def find(self, i):
        if self.parent[i] == i:
            return i
        self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, i, j):
        root_i = self.find(i)
        root_j = self.find(j)
        if root_i != root_j:
            if self.rank[root_i] < self.rank[root_j]:
                self.parent[root_i] = root_j
            elif self.rank[root_i] > self.rank[root_j]:
                self.parent[root_j] = root_i
            else:
                self.parent[root_j] = root_i
                self.rank[root_i] += 1
            return True
        return False

class SimuladorKruskal:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((950, 650))
        pygame.display.set_caption("Kruskal: Instalación de Fibra Óptica")
        self.font = pygame.font.SysFont("Segoe UI", 17, bold=True)
        self.title_font = pygame.font.SysFont("Segoe UI", 24, bold=True)
        self.clock = pygame.time.Clock()

        # Coordenadas de puntos clave en la colonia
        self.nodos_pos = {
            'Central': (475, 300),
            'Sector Norte': (475, 100),
            'Zona Residencial': (150, 200),
            'Parque Tecnológico': (150, 450),
            'Centro Comercial': (800, 200),
            'Gimnasio Municipal': (800, 450)
        }

        # Aristas: (U, V, Costo en miles de pesos)
        self.aristas = [
            ('Central', 'Sector Norte', 4), ('Central', 'Zona Residencial', 5),
            ('Central', 'Centro Comercial', 6), ('Sector Norte', 'Zona Residencial', 8),
            ('Sector Norte', 'Centro Comercial', 2), ('Zona Residencial', 'Parque Tecnológico', 7),
            ('Parque Tecnológico', 'Gimnasio Municipal', 3), ('Centro Comercial', 'Gimnasio Municipal', 9),
            ('Central', 'Parque Tecnológico', 10), ('Central', 'Gimnasio Municipal', 12)
        ]

    def dibujar_escena(self, aristas_mst, arista_actual=None, estado_actual="", costo_total=0):
        self.screen.fill(BG_COLOR)
        
        # Título e información
        titulo = self.title_font.render("OPTIMIZACIÓN DE RED: FIBRA ÓPTICA", True, TEXT_COLOR)
        self.screen.blit(titulo, (50, 20))
        
        info_costo = self.font.render(f"Inversión Total: ${costo_total}k USD", True, ACCEPTED)
        self.screen.blit(info_costo, (50, 70))

        # Dibujar todas las conexiones posibles (base)
        for u, v, w in self.aristas:
            pygame.draw.line(self.screen, LINE_BASE, self.nodos_pos[u], self.nodos_pos[v], 1)
            # Dibujar el peso de la arista
            mid_x = (self.nodos_pos[u][0] + self.nodos_pos[v][0]) // 2
            mid_y = (self.nodos_pos[u][1] + self.nodos_pos[v][1]) // 2
            peso_txt = self.font.render(f"{w}k", True, TEXT_COLOR)
            self.screen.blit(peso_txt, (mid_x - peso_txt.get_width() // 2, mid_y - 10))

        # Dibujar Aristas aceptadas en el MST
        for u, v, w in aristas_mst:
            pygame.draw.line(self.screen, ACCEPTED, self.nodos_pos[u], self.nodos_pos[v], 5)

        # Dibujar Arista evaluándose en este momento
        if arista_actual:
            u, v, w = arista_actual
            color = EVALUATING
            if "Rechazada" in estado_actual: color = REJECTED
            pygame.draw.line(self.screen, color, self.nodos_pos[u], self.nodos_pos[v], 7)

        # Dibujar Nodos (Puntos de conexión)
        for nombre, pos in self.nodos_pos.items():
            pygame.draw.circle(self.screen, NODE_COLOR, pos, 25)
            pygame.draw.circle(self.screen, TEXT_COLOR, pos, 25, 2)
            
            label = self.font.render(nombre, True, TEXT_COLOR)
            self.screen.blit(label, (pos[0] - label.get_width()//2, pos[1] + 40))

        # Mostrar estado y controles al final de la pantalla
        status_txt = self.font.render(f"Estado: {estado_actual}", True, TEXT_COLOR)
        self.screen.blit(status_txt, (50, 550))

        instrucciones = self.font.render("Presiona ENTER para continuar o ESC para salir", True, TEXT_COLOR)
        self.screen.blit(instrucciones, (50, 590))

        pygame.display.flip()

    def ejecutar(self):
        # Ordenar por costo (Mínimo)
        aristas_ordenadas = sorted(self.aristas, key=lambda x: x[2])
        uf = UnionFind(self.nodos_pos.keys())
        mst = []
        costo_total = 0

        running = True
        index = 0
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

            if index < len(aristas_ordenadas):
                u, v, w = aristas_ordenadas[index]
                
                # Paso 1: Mostramos que estamos evaluando
                self.dibujar_escena(mst, (u,v,w), f"Evaluando conexión {u} - {v} (${w}k)...", costo_total)

                esperando = True
                while esperando:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_RETURN:
                                esperando = False
                            elif event.key == pygame.K_ESCAPE:
                                pygame.quit()
                                return

                # Paso 2: Lógica de Unión-Find
                if uf.union(u, v):
                    mst.append((u, v, w))
                    costo_total += w
                    self.dibujar_escena(mst, (u,v,w), "¡Conexión Aceptada!", costo_total)
                else:
                    self.dibujar_escena(mst, (u,v,w), "Rechazada: Genera un bucle innecesario.", costo_total)

                esperando = True
                while esperando:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_RETURN:
                                esperando = False
                            elif event.key == pygame.K_ESCAPE:
                                pygame.quit()
                                return

                index += 1
            else:
                self.dibujar_escena(mst, None, "Optimización finalizada con éxito.", costo_total)

            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    SimuladorKruskal().ejecutar()