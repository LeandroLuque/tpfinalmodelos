import time
import pygame
import sys
#from pygame.locals import *


#Constantes de estado de quirofano
ESTADO_ABIERTO=1
ESTADO_CERRADO=0
ORIGEN_X=ORIGEN_Y=0

#Dimensiones de la pantalla
SCREEN_WIDTH=1300
SCREEN_HEIGHT=700

#CONSTANTE_INCREMENTO_DECREMENTO paso de la barra de personas en la cola
CONSTANTE_INCREMENTO_DECREMENTO=1

#Constantes para modificar iconos cargados
TAMANIO_ESCALA=.15



class Canvas:

	def __init__(self,pygame):
		self.simulacionTerminada=False
		self.posicion=Posicion(100,100)
		self.ancho=SCREEN_WIDTH
		self.alto=SCREEN_HEIGHT
		self.pygame=pygame
		self.pantalla=None
		self.fondo=None
		self.imagen="vista/fondo1.jpg"
		self.inicializar()
		#Quirofano(nombre,X,Y,pygame)
		self.q1=Quirofano("Quirofano Q1","vista/quirofanoImg.png",700,100,self.pygame)
		self.q2=Quirofano("Quirofano Q2","vista/quirofanoImg.png",700,550,self.pygame)

		self.q2.agregarPropiedad("porcent","Porcentaje actual de uso ",700,650)
		#ColaEspera(Nombre,X,Y,pygame)
		self.colaEsperaEntradaPacientes=ColaEspera("Pacientes esperando internacion",
			"vista/pacientesEsperando.jpg",50,200,pygame)

		self.colaEsperaParaCirugia=ColaEspera("Pacientes esperando cirugia",
			"vista/esperandoCirugia.png",400,200,pygame)
		self.redibujar()

	def getColaEspera(self):
		return self.colaEsperaEntradaPacientes

	def getColaEsperaOperacion(self):
		return self.colaEsperaParaCirugia
		
	# Metodos getters y setters de Quirofano
	def getQuirofano1(self):
		return self.q1

	def getQuirofano2(self):
		return self.q2

	# Se dibujan los componentes GUI en el canvas de pygame
	def inicializar(self):
		self.pygame.init()
		# creamos la ventana y le indicamos un titulo
		#pygame.display.set_mode() retorna un objeto Surface
		self.pantalla = self.pygame.display.set_mode((self.ancho, self.alto))
		self.pygame.display.set_caption("Simulacion de Hospital")
		#Se obtiene un objeto Surface para la imagen de forndo
		self.fondo = self.pygame.image.load(self.imagen).convert()
		
	#Este metodo redibuja todos los componetnes de la GUI
	def redibujar(self):
		self.pantalla.blit(self.fondo, (ORIGEN_X,ORIGEN_Y))
		# Redibujamos todos los elementos de la pantalla

        #Se pasa la referencia al Surface (pantalla de pygame)
		self.q1.actualizar(self.pantalla)
		self.q2.actualizar(self.pantalla)

		self.colaEsperaEntradaPacientes.actualizar(self.pantalla)
		self.colaEsperaParaCirugia.actualizar(self.pantalla)
		
		# Se muestran lo cambios en pantalla
		self.pygame.display.flip()


	def estaSimulacionTerminada(self):
		return self.simulacionTerminada


	def terminar_simulacion(self):
		self.simulacionTerminada = True

	#Bucle infinito que muestra la ventana de pygame
	def mostrar(self):
		contadorColaLlegada=0
		contadorColaCirugia=100
		# contadorColaLlegada=200
		while not self.estaSimulacionTerminada():
			# Posibles entradas del teclado y mouse
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					print ("Cerrando la ventana ...")
					print ("")
					sys.exit()
			self.redibujar()
			# self.probarQuirofanos(contadorColaLlegada)
			# contadorColaLlegada=self.probarColaLlegadaPositiva(contadorColaLlegada)
			# contadorColaCirugia=self.probarColaCirugiaNegativa(contadorColaCirugia)
			# contador=self.probarColaLlegadaNegativa(contadorColaLlegada)
			# print "--------------------------------"
			
	def actualizar_porcentaje_quirofano(self,porcentaje):
		self.q2.actualizarPropiedad("porcent",porcentaje)

	# def probarQuirofanos(self,cont):
	# 	#time.sleep(1)
	# 	self.getQuirofano1().actualizarEstado()
	# 	self.getQuirofano2().actualizarEstado()
	# 	self.getQuirofano2().actualizarPropiedad("porcent",str(cont)+" %")

	# def probarColaLlegadaPositiva(self,contador):
	# 	aux=contador+1
	# 	self.colaEsperaEntradaPacientes.incrementar(contador)
	# 	time.sleep(.2)
	# 	return aux

	# def probarColaLlegadaNegativa(self,contador):
	# 	aux=contador-1
	# 	self.colaEsperaEntradaPacientes.decrementar(contador)
	# 	time.sleep(.3)
	# 	return aux

	# def probarColaCirugiaPositiva(self,contador):
	# 	aux=contador+1
	# 	self.colaEsperaParaCirugia.incrementar(contador)
	# 	time.sleep(.2)
	# 	return aux

	# def probarColaCirugiaNegativa(self,contador):
	# 	aux=contador-1
	# 	self.colaEsperaParaCirugia.decrementar(contador)
	# 	time.sleep(.3)
	# 	return aux


class Quirofano(pygame.sprite.Sprite):
	def __init__(self,nombre,pathImagen,x,y,pygame):
		# Call the parent class (Sprite) constructor
		pygame.sprite.Sprite.__init__(self)
		self.nombre=nombre
		self.estado=ESTADO_ABIERTO
		self.posicion=Posicion(x,y)
		self.rutaImagen=pathImagen
		# Create an image of the block, and fill it with a color.
		self.image = pygame.image.load(self.rutaImagen).convert()
		#Se obtienen las propiedades de la imagen y se la escala
		ancho,alto= self.image.get_size()
		self.image=pygame.transform.scale(self.image,(int(TAMANIO_ESCALA*ancho),
			int(TAMANIO_ESCALA*alto)) )
		#Se establece supDisponibilidad, que dibuja un rectangulo de color transparente
		#sobre el icono del quirofano, indicando si esta disponible u ocupado
		self.pygame=pygame
		self.supDisponibilidad=None
		#Se configura el label con el nombre del quirofano
		self.font=pygame.font.Font(None,26)

		#Diccionario de lables para agregar a la cola de espera
		self.labels={}


	def getEstado(self):
		return self.estado

	#Agrega una propiedad tipo cadena  a la interfaz grafica del componente
	def agregarPropiedad(self,nombreLabel,texto,x,y):
		p=Posicion(x,y)
		#Se configura el label con el nombre del quirofano
		font=self.pygame.font.Font(None,26)		
		self.labels[nombreLabel]={ "cadenaLabel":texto,"valor":0, "font":font, "pos": p}


	#Actualiza el valor numerico de una propiedad(como el porcentaje de uso)
	def actualizarPropiedad(self,nombre,valor):
		self.labels[nombre]["valor"]=valor


	def actualizarEstado(self):
		if self.estado==ESTADO_ABIERTO:
			self.estado=ESTADO_CERRADO
		elif self.estado==ESTADO_CERRADO:
			self.estado=ESTADO_ABIERTO
		print "Actualizado estado del quirofano"

	#Este metodo redibuja el componente del quirofano a un nuevo color indicando estado.
	def actualizar(self,surface):
		color=(0,0,0)
		alpha=200
		# if self.estado==ESTADO_ABIERTO:
		# 	color=(0,0,255)
		# else:
		# 	color=(255,0,0)

		#Se asigna un rectangulo encima de Surface "self.image" que sea transparente
		ancho,alto=self.image.get_size()
		# self.supDisponibilidad=self.pygame.draw.rect(surface,color,(self.posicion.getX(),
		# 			self.posicion.getY(),ancho,alto))
		self.image.set_alpha(alpha)
		#Se redibuja la letra
		fg = 0,0,0
		bg = 255, 255, 255
		textoRend= self.font.render(self.nombre,0,fg,bg)
		surface.blit(textoRend,(self.posicion.getX()-15,self.posicion.getY()-35 ))
		surface.blit(self.image, ( self.posicion.getX(), self.posicion.getY()) )

		#Se recorren las propiedades del quirofano
		for nombre,dicProps in self.labels.iteritems():
			cadenaNueva=self.labels[nombre]["cadenaLabel"]+": "+str(self.labels[nombre]["valor"])
			textoRend= dicProps["font"].render(cadenaNueva,0,fg,bg)
			surface.blit(textoRend,( dicProps["pos"].getX()-15,
				dicProps["pos"].getY() ))

						


class ColaEspera(pygame.sprite.Sprite):
	""" Clase que representa una cola de espera de pacientes."""
	def __init__(self,nombre,pathImagen,x,y,pygame,largo=200,ancho=20,tamanioColaMax=False):
		pygame.sprite.Sprite.__init__(self)
		self.pygame=pygame
		#Cantidad actual de personas en la cola
		self.cantPersonas=0
		#Se crea una posicion la colaDeEspera
		self.posicion=Posicion(x,y)
		self.nombre=nombre
		self.rutaImagen=pathImagen
		#Nota: La cola crece o decrece de largo solamente, y el valor Y de la barra variable 
		# NOTA:El topeSuperiorBarra es el tope de la pila que representa la barra
		# y el self.limiteInferiorBarra es el fondo de la pila que representa la barra. 
		# self.topeSuperiorBarra=self.limiteInferiorBarra=0
		# if tamanioColaMax:
		# 	self.topeSuperiorBarra=self.posicion.getY()
		# 	self.limiteInferiorBarra=largo
		# else:
		# 	self.topeSuperiorBarra=self.posicion.getY()+largo-1
		# 	self.limiteInferiorBarra=largo-self.posicion.getY()+1


		#BACKUP version vieja!
		# if tamanioCola > 0:
		# 	self.topeSuperiorBarra=self.posicion.getY()+tamanioCola
		# 	self.limiteInferiorBarra=largo-tamanioCola
		# else:
		# 	self.topeSuperiorBarra=self.posicion.getY()+largo-1
		# 	self.limiteInferiorBarra=largo-self.posicion.getY()+1

		#Medidas de la barra negra no variable
		# self.largoConstante=largo
		# self.ancho=ancho
		#Se configura el label con el nombre del quirofano
		self.font=pygame.font.Font(None,26)
		self.escalarImagen()


	#Escala la imagen que ilusta el tipo de la cola de espera
	def escalarImagen(self):
		self.image = self.pygame.image.load(self.rutaImagen).convert()
		#Se obtienen las propiedades de la imagen y se la escala
		ancho,alto= self.image.get_size()
		self.image=self.pygame.transform.scale(self.image,(int(TAMANIO_ESCALA*ancho),
			int(TAMANIO_ESCALA*alto)) )

	
	def getNombre(self):
		return self.nombre

	def getCantPersonas(self):
		return self.cantPersonas

	#Se incrementa el tamanio de la cola y se actualiza la cant. actual de personas.
	#(se decrementa la distancia del valor Y del eje de coordenadas)
	def incrementar(self,valor):
		# self.topeSuperiorBarra-=CONSTANTE_INCREMENTO_DECREMENTO
		# self.limiteInferiorBarra+=CONSTANTE_INCREMENTO_DECREMENTO
		# print "self.topeSuperiorBarra: %s ; self.limiteInferiorBarra: %s " % (self.topeSuperiorBarra,
		# 	self.limiteInferiorBarra)
		# print ""
		# if self.topeSuperiorBarra <= 200:
		# 	self.topeSuperiorBarra=200
		# 	self.limiteInferiorBarra=199
		self.cantPersonas = valor

	#Se decrementa el tamanio de la cola (se aumenta la distancia del valor Y
	# del eje de coordenadas)
	def decrementar(self,valor):
		# self.topeSuperiorBarra+=CONSTANTE_INCREMENTO_DECREMENTO
		# self.limiteInferiorBarra-=CONSTANTE_INCREMENTO_DECREMENTO
		# if self.limiteInferiorBarra<0:
		# 	self.limiteInferiorBarra=0
		# 	self.topeSuperiorBarra=self.posicion.getY()+self.largoConstante-2
		self.cantPersonas=valor

	#Se redibuja la barra que representa una cola de pacientes
	def actualizar(self,surface):
		#Barra exterior que contiene a la barra variable
		# (x,y,ancho,alto)
		# self.pygame.draw.rect(surface,(0,0,0),(self.posicion.getX(),
		# 			self.posicion.getY(),
		# 			self.ancho,
		# 			self.largoConstante),3 )

		# #Barra interior roja variable de la cola
		# self.pygame.draw.rect(surface,(255,0,0),(self.posicion.getX()+2,
		# 			self.topeSuperiorBarra,
		# 			self.ancho-4,
		# 			self.limiteInferiorBarra) )

		self.dibujarTextoCantidad(surface)
		self.dibujarLabel(surface)
		#Se dibuja la imagen 
		surface.blit(self.image, ( self.posicion.getX()+30, self.posicion.getY()+45) )




	#Se redibuja el texto de la cantidad de personas
	def dibujarTextoCantidad(self,surface):
		#Se redibuja la letra
		fg = 0,0,0
		bg = 255, 255, 255
		textoRend= self.font.render(str(self.cantPersonas),0,fg,bg)
		surface.blit(textoRend,(self.posicion.getX()-30, self.posicion.getY()+10 ))

	#Dibuja el Label encima de la cantidad de personas en la cola
	def dibujarLabel(self,surface):
		#Se redibuja la letra
		fg = 0,0,0
		bg = 255, 255, 255
		textoRend= self.font.render(str(self.nombre),0,fg,bg)
		surface.blit(textoRend,(self.posicion.getX()-40, self.posicion.getY()-25 ))		

class Posicion:

	def __init__(self,x,y):
		self.x=x
		self.y=y

	def getX(self):
		return self.x

	def setX(self,x):
		self.x=x

	def setY(self,y):
		self.y=y

	def getY(self):
		return self.y



 
# def main():
# 	c=Canvas(pygame)
# 	# c.mostrar()
# 	t = Thread(target=c.mostrar)
# 	# t.daemon = True
# 	t.start()
# 	print ("Despues de mostrar!!!")
# 	print ("")

# if __name__ == "__main__":
#     main()
