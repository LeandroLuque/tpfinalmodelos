import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from threading import Thread

# Constantes para el graficador
HISTOGRAMA="Histograma"
DIAGRAMA_TORTA="Diagrama de torta"


class Graficador(object):
	""" Graficador generico que grafica histogramas y graficos de torta"""

	def __init__(self,plt):
		self.plt = plt
		self.indice = 0
		self.figure=self.axis=None
		# La clave es el numero del grafico y el array son los datos necesarios
		# para hacer el grafico
		# { 1: { "tipo":HISTOGRAMA,"titulo":"Nombre 111",
		#	"label_x":"Tiempos promedios", "label_y":"Frecuencia" ,
		#	"datos_x":[1,2,3,4,5] }, "datos_y":[1,2,3,4,5] },
		#	 ...
		#	}
		self.dic_datos_graficos = {}

	def get_plt(self):
		return self.plt

	def siguiente(self, event):   
		self.indice += 1
		if self.indice > len(self.dic_datos_graficos):
			self.indice=1
		print "Cambio self.indice: %s" % self.indice
		print ""
		self.graficar_diagrama()

	def anterior(self, event):
		self.indice -= 1
		if self.indice < 1:
			self.indice=len(self.dic_datos_graficos)
		print "Cambio self.indice: %s" % self.indice
		print ""
		self.graficar_diagrama()


	def inicializar_ventana(self):
		#Se configura el subplot que contiene los botones de la GUI
		self.figure,self.axis = self.plt.subplots()
		self.plt.subplots_adjust(bottom=0.2)
		# Se establecen las posiciones de los graficos estadisticos
		axprev = self.plt.axes([0.62,0.08, 0.1, 0.075])
		axnext = self.plt.axes([0.8, 0.08, 0.1, 0.075])
		# Se crea el objeto indice que maneja los eventos y el redibujado
		# de los inicializar_ventana().
		bnext=Button(axnext,"Siguiente")
		bnext.on_clicked(self.siguiente)
		bprev = Button(axprev,"Anterior")
		bprev.on_clicked(self.anterior)

		#Sei dibuja el diagrama actual segun el nro de indice
		self.graficar_diagrama()
		#Se muestra la venta
		self.plt.show()
		print "Ventana inicializada !"
		print ""

	#Se agrega un grafico a la coleccion de graficos
	def agregar_grafico(self,datos):
		nuevo_indice=len(self.dic_datos_graficos)+1
		self.dic_datos_graficos[nuevo_indice]=datos
		self.indice=nuevo_indice
		print "nuevo indice agregado a la ventana: %s " % self.indice
		print ""

	#Funcion auxiliar que hace los graficos de torta con los porcentajes del informe
	def make_autopct(self,values):
		def my_autopct(pct):
			return '{p:.2f}% '.format(p=pct)
		return my_autopct

	def graficar_diagrama(self):
		print "Graficando histograma actual en self.indice: %s " % self.indice
		print "..."
		# Se accede al primer subplot creado anteriormente
		if self.dic_datos_graficos[self.indice]["tipo"] == HISTOGRAMA:
			self.plt.clf()
			self.figure.add_subplot(111)
			#Se configura el subplot que contiene los botones de la GUI	
			self.plt.title(self.dic_datos_graficos[self.indice]["titulo"])
			self.plt.xlabel(self.dic_datos_graficos[self.indice]["label_x"]) 
			self.plt.ylabel(self.dic_datos_graficos[self.indice]["label_y"])
			#[minX,minY,maxX,maxY]
			self.plt.axis(self.dic_datos_graficos[self.indice]["limites_histograma"])

			self.plt.hist(self.dic_datos_graficos[self.indice]["datos_x"],
				50, facecolor='blue',range=(1,100), alpha=0.75)
			
			self.figure.add_subplot(111)
			self.figure.subplots_adjust(bottom=0.3)

			# Se establecen las posiciones de los graficos estadisticos
			axprev = self.plt.axes([0.62,0.08, 0.1, 0.075])
			axnext = self.plt.axes([0.8, 0.08, 0.1, 0.075])
			# Se crea el objeto indice que maneja los eventos y el redibujado
			# de los inicializar_ventana().
			bnext=Button(axnext,"Siguiente")
			bnext.on_clicked(self.siguiente)
			bprev = Button(axprev,"Anterior")
			bprev.on_clicked(self.anterior)
			# Se dibujan los cambios en el grafico
			self.plt.draw()
			# Se redibujan todos los elementos de la interfaz grafica
			self.plt.show()

		elif self.dic_datos_graficos[self.indice]["tipo"] == DIAGRAMA_TORTA:
			#Se borran todos los labels del grafico anterior
			self.plt.clf()
			self.figure.add_subplot(111)
			self.plt.title(self.dic_datos_graficos[self.indice]["titulo"])
			self.plt.pie(self.dic_datos_graficos[self.indice]["datos"],
				labels = self.dic_datos_graficos[self.indice]["labels"],
				explode = self.dic_datos_graficos[self.indice]["explode"],
				labeldistance=.2,
				shadow=True,
				autopct=self.make_autopct(
							self.dic_datos_graficos[self.indice]["porcentajes"]) )
				
			self.figure.add_subplot(111)
			self.figure.subplots_adjust(bottom=0.3)

			# Se establecen las posiciones de los graficos estadisticos
			axprev = self.plt.axes([0.62,0.08, 0.1, 0.075])
			axnext = self.plt.axes([0.8, 0.08, 0.1, 0.075])
			# Se crea el objeto indice que maneja los eventos y el redibujado
			# de los inicializar_ventana().
			bnext=Button(axnext,"Siguiente")
			bnext.on_clicked(self.siguiente)
			bprev = Button(axprev,"Anterior")
			bprev.on_clicked(self.anterior)

			self.plt.draw()
			self.plt.show()




	# BACKUP!
	# def graficar_diagrama(self):
	# 	print "Graficando histograma actual en self.indice: %s " % self.indice
	# 	print "..."
	# 	# Se accede al primer subplot creado anteriormente
	# 	self.plt.subplot(111)
	# 	if self.dic_datos_graficos[self.indice]["tipo"] == HISTOGRAMA:
	# 		self.plt.clf()
	# 		#Se configura el subplot que contiene los botones de la GUI	
	# 		self.plt.title(self.dic_datos_graficos[self.indice]["titulo"])
	# 		self.plt.xlabel(self.dic_datos_graficos[self.indice]["label_x"]) 
	# 		self.plt.ylabel(self.dic_datos_graficos[self.indice]["label_y"])
	# 		#[minX,minY,maxX,maxY]
	# 		self.plt.axis(self.dic_datos_graficos[self.indice]["limites_histograma"])

	# 		self.plt.hist(self.dic_datos_graficos[self.indice]["datos_x"],
	# 			50, facecolor='blue',range=(1,100), alpha=0.75)

	# 	elif self.dic_datos_graficos[self.indice]["tipo"] == DIAGRAMA_TORTA:
	# 		self.plt.subplot(111)
	# 		self.plt.cla()
	# 		self.plt.title(self.dic_datos_graficos[self.indice]["titulo"])
	# 		self.plt.pie(self.dic_datos_graficos[self.indice]["datos"],
	# 			labels = self.dic_datos_graficos[self.indice]["labels"],
	# 			explode = self.dic_datos_graficos[self.indice]["explode"],
	# 			labeldistance=.2,
	# 			shadow=True,
	# 			autopct=self.make_autopct(
	# 						self.dic_datos_graficos[self.indice]["porcentajes"]) )
			
		
	# 	self.plt.draw()


def main():
	g = Graficador(plt)
	d={
		"tipo":HISTOGRAMA,
		"titulo":"Histogama de prueba",
		"label_x":"Valores de tiempo",
		"label_y":"Frecuencias de tiempo",
		"datos_x":np.random.normal(50,5,1000),
		#[minX,minY,maxX,maxY]
		"limites_histograma":[20,100, 0, 200]
	}

	d2= {
		"tipo":DIAGRAMA_TORTA,
		"titulo": "Prueba de torta",
		"labels":["Tiempo usado del quirofano","Tiempo ocioso del quirofano"],
		"datos":[87,13],
		"explode":[0.2,0],
		"porcentajes":[10,20]
	}

	# Se inicializa la ventana y se muestra una vez que se cargan los datos
	g.agregar_grafico(d)
	g.agregar_grafico(d2)
	g.inicializar_ventana()

main()

