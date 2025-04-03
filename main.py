import os
import sys
import pygame
import time
import math

def cargar_imagenes(directorio):
    # Buscar archivos con extensión .JPG (sin distinguir mayúsculas/minúsculas)
    archivos = [f for f in os.listdir(directorio) if f.lower().endswith('.jpg')]
    archivos.sort()  # Ordenar alfabéticamente
    imagenes = [pygame.image.load(os.path.join(directorio, f)) for f in archivos]
    return imagenes, archivos

class Parametros:
    def __init__(self):
        self.initialStep=10
        self.totalSteps=2
        self.metralleta=20
        self.border=100

class Singular:
    def __init__(self, p,im, x, y):
        self.p=p
        self.im = im
        self.x = x
        self.y = y
        self.puntos = []
        self.promedio=0
        self.numeroPromedio=0
        for xy in self.kernelIncex():
        # for x in range(-5, 6, 1):
        #     for y in range(-5, 6, 1):
                x0 = self.x + xy[0]
                y0 = self.y + xy[1]
                if x0 < 0 or y0 < 0 or x0 >= self.im.get_width() or y0 >= self.im.get_height():
                    self.puntos.append(None)
                else:
                    self.puntos.append(self.im.get_at((x0, y0)))

        # error=0
        # num=0
        # for i in range(len(self.puntos)):
        #     for j in range(i+1,len(self.puntos)):
        #         p0=self.puntos[i]
        #         p1=self.puntos[j]
        #         if p0 is None or p1 is None:
        #             continue

        #         num+=1
        #         error+=(p0[0]-p1[0])**2+(p0[1]-p1[1])**2+(p0[2]-p1[2])**2
        # self.singular=error/num

    def add(self, error):
        self.promedio += error
        self.numeroPromedio += 1

    def kernelIncex(self):
        # def f():
        #     for i in range(-self.p.metralleta, self.p.metralleta+1, self.p.metralleta):
        #         for j in range(-self.p.metralleta, self.p.metralleta+1, self.p.metralleta):
        #             yield (i,j)

        # return f 
        pos=[(0,0)]
        # angle=0
        # module=1
        # for _ in range(20):
        #     angle+=math.pi/10
        #     module+=1
        #     x=module*math.cos(angle)
        #     y=module*math.sin(angle)
        #     pos.append((int(x),int(y)))


        # #
        step=self.p.initialStep
        for _ in range (self.p.totalSteps):
            for i in range(-step, step+1,step):
                for j in range(-step, step+1,step):
                    if i==0 and j==0:
                        continue
                    pos.append((i,j))
            step*=2

        return pos
    
    def compare(self, other):
        # Comparar los puntos de la imagen actual con los de la otra imagen
        error=0
        num=len(self.puntos)
        for i in range(len(self.puntos)):
            p0=self.puntos[i] 
            p1=other.puntos[i]
            if p0 is None or p1 is None:
                num-=1
            else:
                error+=(p0[0]-p1[0])**2+(p0[1]-p1[1])**2+(p0[2]-p1[2])**2

        error/=num
        #error+= -self.singular-other.singular
        # self.add(error)
        # other.add(error)
        return (error,self,other)

class MarcoMetralleta:
    def __init__(self, x0,xi,x1,y0,yi,y1):
        self.x0=x0
        self.xi=xi
        self.x1=x1
        self.y0=y0
        self.yi=yi
        self.y1=y1
    
    def cont(self):
        if self.x0>self.x1 or self.y0>self.y1:
            print("Error de lógica")
        if self.x0==self.x1:
            return False
        if self.y0==self.y1:
            return False
        return True
    
    def x(self):
        inc=int((self.x1-self.x0)/self.xi)
        return range(self.x0,self.x1+1,inc)
    
    def y(self):
        inc=int((self.y1-self.y0)/self.yi)
        return range(self.y0,self.y1+1,inc)
    
    def split(self, x, y):
        xi=self.xi #//2
        yi=self.yi #//2
        m0=MarcoMetralleta(self.x0,xi,x+self.xi,self.y0,yi,y+self.yi)
        m1=MarcoMetralleta(x-self.xi,xi,self.x1,y-self.yi,yi,self.y1)
        m2=MarcoMetralleta(self.x0,xi,x+self.xi,y-self.yi,yi,self.y1)
        m3=MarcoMetralleta(x-self.xi,xi,self.x1,self.y0,yi,y+self.yi)
        return [m0,m1,m2,m3]

class TranslationMatrix:
    def __init__(self,p):
        self.p=p

    
    def singualar2(self,im,m):
        s=[]
        for y in m.y():
            for x in m.x():
                aux=Singular(self.p,im,x,y)
                # if aux.singular>0:
                s.append(aux)
        return s
    
    def dist(self,x0,y0,x1,y1):
        return (x0-x1)**2+(y0-y1)**2
    
    def singular3(self,im0,m0, im1,m1, credit):
        pixels0=self.singualar2(im0,m0)
        pixels2=self.singualar2(im1,m1)

        comp=[]
        for i in range(1,len(pixels0)):
            p0=pixels0[i]
            best=None
            for j in range(len(pixels2)):
                cand=p0.compare(pixels2[j])
                if best is None or best[0]>cand[0]:
                    best=cand
            comp.append(best)
        return [((x[1].x, x[1].y), (x[2].x, x[2].y)) for x in comp ]

        #comp.sort(key=lambda x: x[0]+x[1].promedio/x[1].numeroPromedio+x[2].promedio/x[2].numeroPromedio) # *self.dist(x[1].x,x[1].y,x[2].x,x[2].y)
        comp.sort(key=lambda x: x[0])
        mejor=comp[0]

        if credit>0:
            # Recursividad con borde.
            split0=m0.split(mejor[1].x, mejor[1].y)
            split1=m1.split(mejor[2].x, mejor[2].y)

            r=[]
            for i in range(len(split0)):
                for r2 in self.singular3(im0,split0[i],im1,split1[i], credit-1):
                    r.append(r2)
            return r
        else:
            print("Mejor coincidencia:", mejor[1].x, mejor[1].y, "con", mejor[2].x, mejor[2].y, " con ", mejor[0])
            return [((mejor[1].x, mejor[1].y), (mejor[2].x, mejor[2].y))]

    def singular(self,im0, im1):
        start=time.time()

        m0=MarcoMetralleta(self.p.border,self.p.metralleta,im0.get_width()-self.p.border*2-1,self.p.border,self.p.metralleta,im0.get_height()-self.p.border*2-1)
        m1=MarcoMetralleta(self.p.border,self.p.metralleta,im1.get_width()-self.p.border*2-1,self.p.border,self.p.metralleta,im1.get_height()-self.p.border*2-1)
        credit=0
        r=self.singular3(im0,m0,im1,m1,credit)


        print("Size:",im0.get_size())
        print("Tiempo de ejecución (s):", time.time() - start)
        return r
        


    def step(self, im0, im1):
        start=time.time()
        ancho, alto = im0.get_size()
        for y in range(alto):
            for x in range(ancho):
                pixel = im0.get_at((x, y))
                # Desempaquetar el color (R, G, B, A)
                r, g, b, a = pixel
        print("Tiempo de ejecución (ms):", time.time() - start)
def main():
    pygame.init()
    
    # Directorio actual
    directorio = '100JVCSO_coche'
    imagenes, archivos = cargar_imagenes(directorio)
    
    if not imagenes:
        print("No se encontraron imágenes con extensión .JPG en el directorio actual.")
        pygame.quit()
        sys.exit()
    
    # Tamaño de la imagen y definir altura de la barra de control
    ancho, alto = imagenes[0].get_size()
    control_bar_height = 50  # Altura de la barra inferior de botones
    
    # Crear ventana con espacio para la imagen y la barra de control
    pantalla = pygame.display.set_mode((ancho, alto + control_bar_height))
    pygame.display.set_caption("Presentación de imágenes")
    
    # Definir rectángulos para los botones
    button_width = 150
    button_height = 40
    margin = 10
    btn_anterior_rect = pygame.Rect(margin, alto + (control_bar_height - button_height) // 2, button_width, button_height)
    btn_siguiente_rect = pygame.Rect(ancho - button_width - margin, alto + (control_bar_height - button_height) // 2, button_width, button_height)
    
    # Fuente para el texto de los botones
    font = pygame.font.SysFont(None, 24)
    
    indice_actual = 0
    total_imagenes = len(imagenes)
    reloj = pygame.time.Clock()

    pygame.event.set_allowed(None)  # Bloquea todo
    pygame.event.set_allowed([pygame.QUIT, pygame.MOUSEBUTTONDOWN])

    firstTime = True
    ejecutando = True

    p=Parametros()
    t=TranslationMatrix(p)
    singular_1=None

    while ejecutando:
        evento = pygame.event.wait()

        if not firstTime and  not evento.type in [pygame.MOUSEBUTTONDOWN, pygame.QUIT]:
            reloj.tick(30)
            continue

        firstTime = False
        #for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos = evento.pos
            if btn_anterior_rect.collidepoint(pos):
                indice_actual = (indice_actual - 1) % total_imagenes
            elif btn_siguiente_rect.collidepoint(pos):
                indice_actual = (indice_actual + 1) % total_imagenes
        
        r=t.singular(imagenes[indice_actual], imagenes[(indice_actual + 1) % total_imagenes])

        # Dibujar la imagen en la parte superior
        pantalla.fill((0, 0, 0))
        pantalla.blit(imagenes[indice_actual], (0, 0))
        
        # Dibujar la barra de control en la parte inferior
        control_bar_rect = pygame.Rect(0, alto, ancho, control_bar_height)
        pygame.draw.rect(pantalla, (50, 50, 50), control_bar_rect)

        # draw line on singular
        for r0,r1 in r:
            pygame.draw.line(pantalla, (255, 0, 0), r0, r1, 1)
        singular_1=r

        # Dibujar los botones
        pygame.draw.rect(pantalla, (200, 200, 200), btn_anterior_rect)
        pygame.draw.rect(pantalla, (200, 200, 200), btn_siguiente_rect)
        
        # Renderizar y posicionar el texto en cada botón
        text_anterior = font.render("Anterior", True, (0, 0, 0))
        text_siguiente = font.render("Siguiente", True, (0, 0, 0))
        pantalla.blit(text_anterior, (btn_anterior_rect.x + (button_width - text_anterior.get_width()) // 2,
                                      btn_anterior_rect.y + (button_height - text_anterior.get_height()) // 2))
        pantalla.blit(text_siguiente, (btn_siguiente_rect.x + (button_width - text_siguiente.get_width()) // 2,
                                       btn_siguiente_rect.y + (button_height - text_siguiente.get_height()) // 2))
        
        pygame.display.flip()
        #reloj.tick(30)
    
    pygame.quit()
    sys.exit()

def main2():
    import time
    import cv2
    import numpy as np

    img1 = cv2.imread("100JVCSO_coche/PIC_0760.JPG")
    img2 = cv2.imread("100JVCSO_coche/PIC_0761.JPG")
    prev_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    hsv = np.zeros_like(img1)
    hsv[..., 1] = 255

    # Medir el tiempo de ejecución
    start = time.time()
    flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 
                                        0.5, 3, 15, 3, 5, 1.2, 0)
    end = time.time()

    print("Tiempo de ejecución: {:.2f} ms".format((end - start) * 1000))


if __name__ == "__main__":
    main2()
