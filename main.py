__author__ = 'leandro'

import numpy as np
import time
import os

from clases import Reloj
from clases import Evento
from clases import FEL
from clases import Paciente
from clases import Hospital
# from clases import Observable

from utilidades.utilidades import *
#from vista.vistaV2 import *
import sys
import math

"""
    Constantes para la simulacion del sistema
"""
CANT_PACIENTES_INICIAL = 10
CANT_EXPERIMENTO = 30 # years
CANT_CORRIDAS = 365 # DIAS * MESES
CANTIDAD_CAMAS = 250

MAX_COLA_ESPERA_INTERNACION = 300
cantidad_dias = 0

#=================================================================================================
#====================================== Variables de salida ======================================
#=================================================================================================
#
#Se utiliza este arreglo para guardar los tiempos promedios de cada paciente
# y calcular el tiempo promedio
tiempos_de_espera_pacientes = []
#Nota: Los pacientes atendidos/no atendidos, son los que entraron/no entraron al quirofano.
cantidad_pacientes_atendidos = 0
cantidad_pacientes_no_atendidos = 0
pacientes_para_operacion = 0
pacientes_sin_operacion = 0
tiempo_uso_sala_operaciones = 0

#=================================================================================================
#====================================== Variables de estado ======================================
#=================================================================================================
total_pacientes_ingresaron_hospital = 0

#=================================================================================================
#====================================== Variables para datos estadisticos ======================================
#=================================================================================================
tiempos_de_arribos = []

# Variables usadas para los acumulados anuales de tiempo de uso de quirofano, tiempos de espera
# de pacientes, pacientes operados y no operados, que se resetean anualmente.
# 
acumulado_anual_uso_sala_operaciones = 0
tiempos_anuales_sala_operaciones = []

pacientes_anuales_operados = []
acumulado_anual_pacientes_operados=0

pacientes_anuales_no_operados = []
acumulado_anual_pacientes_no_operados=0

tiempos_anuales_espera_pacientes= []
acumulado_anual_tiempos_espera = 0



#TODOS PENDIENTES
# -AGREGAR CONTADOR PARA CALCULAR LA CANTIDAD DE PACIENTES QUE ENTRARON AL HOSPITAL --> OK
# -CALCULAR EL PORCENTAJE DE USO DE LA SALA DE OPERACIONES PARA MOSTRAR EN IMPIRMIR_ESTADISTICAS --> OK
# -CORREGIR EL TIEMPO DE ESPERA DE LOS PACIENTES (TODOS UNOS!!) --> OK
# -AGREGAR MAS QUIROFANOS PARA VER SI DISMINUYE LA CANTIDAD DE PACIENTES


def inicializar_simulacion(FEL, reloj):

    ## Obtener el evento de cierre de sala de operaciones y agregarlo a la FEL
    ## Cargar los diez pacientes con distribucion exponencial

    # #print ("Tiempo de reloj en inicializar_simulacion(): %s" % reloj.tiempo)

    tiempos_arribos = [round(np.random.exponential(100)) for value in range(1,CANT_PACIENTES_INICIAL + 1)]
    for tiempo in tiempos_arribos:
        evento = Evento("Arribo de Paciente",tiempo + reloj.tiempo)
        FEL.agregar_evento(evento)

    evento = Evento("Inicio Dia",0)
    FEL.agregar_evento(evento)
    evento = Evento("Apertura de Sala de Operaciones",60*8)
    FEL.agregar_evento(evento)


def procesar_arribo(reloj, hospital, FEL):
    """
        Este metodo sirve para procesar el arribo de
        un paciente. Se crea el paciente y se lo agrega a la
        cola de espera para internacion del hospital
    :param reloj:
    :param hospital
    :return:
    """
    global pacientes_sin_operacion
    global pacientes_para_operacion
    global total_pacientes_ingresaron_hospital 
    if len(hospital.cola_espera_internacion) < MAX_COLA_ESPERA_INTERNACION:
        paciente = Paciente(reloj.tiempo)
        #print ("En procesar_arribo() ...")
        #print ("Paciente numero: %s instanciado! El tiempo de llegada del paciente es: %s" % (paciente.nro_paciente,
            # paciente.tiempo_inicio_espera_internacion))
        #print ("Cola espera internacion inicial: ")
        # hospital.mostrar_cola_espera_internacion()
        #print ("")
        total_pacientes_ingresaron_hospital += 1
        if paciente.quirofano:
            pacientes_para_operacion += 1
        else:
            pacientes_sin_operacion += 1
        # hospital.agregar_paciente_a_espera(paciente)

        #print ("Cola espera internacion actualizada: ")
        # hospital.mostrar_cola_espera_internacion()
        #print ("")

        # if (hospital.tiene_cama_libre()):
        #     e = Evento("Paciente Internado",reloj.tiempo+1,paciente)
        #     FEL.agregar_evento(e)
        #     #print ("Se interno al paciente %s en tiempo evento: %s!" % (paciente.nro_paciente,
        #         reloj.tiempo+1))
        #     #print ("")
        e = Evento("Paciente Internado",reloj.tiempo+1,paciente)
        FEL.agregar_evento(e)
        #print ("Se interno al paciente %s en tiempo evento: %s!" % (paciente.nro_paciente,
            # reloj.tiempo+1))
        #print ("")
        #print ("Fin de procesar_arribo()")
        #print ("")

def procesar_internacion(reloj, hospital, FEL,evento):
    global acumulado_anual_tiempos_espera
    # #print ("En procesar_internacion() ...")
    # #print ("")
    # #print ("hospital.cola_espera_internacion longitud: %s" % len(hospital.cola_espera_internacion))
    # #print ("Pacientes en cola espera internacion: ")
    # hospital.mostrar_cola_espera_internacion()
    # #print ("")

    paciente = evento.paciente
    if (hospital.tiene_cama_libre()):        
        # #print ("Se saco al pacinete %s de la cola espera internacion!!!" % paciente.nro_paciente)
        # #print ("El paciente a internar es: %s " % paciente.nro_paciente)
        # #print ("")
        # Se establece el tiempo maximo de internacion segun el reloj y el tiempo de internacion del paciente.
        # Este valor se usa despues en el evento "Entra a Quirofano", para determinar si un paciente
        # puede ser operado dentro del rango de los dias que esta operado.
        paciente.tiempo_fin_espera_internacion = reloj.tiempo

        # Se asigna la cama y si el paciente tiene turno de quirofano, se lo pone en
        # la cola de pacientes para operacion
        hospital.internar(paciente)
        # #print ("Se agrego al paciente a la cola de espera operacion, la nueva cola es: ")
        # hospital.mostrar_cola_espera_operacion()
        # #print ("")
        # Se establece el tiempo max. de internacion de paciente. Se usa para la cantidad
        # de pacientes no operados.
        e = Evento("Fin Paciente Internado",(reloj.tiempo + paciente.tiempo_internacion),
                paciente)
        FEL.agregar_evento(e)

        #print ("Se produjo el evento de Fin paciente Internado con paciente: %s y tiempo evento: %s" % (paciente.nro_paciente,
            # e.tiempo))

        tiempos_de_espera_pacientes.append(paciente.tiempo_espera())
        if paciente.tiempo_espera() == 0:
            #print ("ERROR!! TIEMPOS DE ESPERA NULOOOOOOOOOOOOOOOOOOOS!!!! ")
            #print ("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            #print ("")
            sys.exit(1)
        acumulado_anual_tiempos_espera += paciente.tiempo_espera()
    else:
        # #print ("El paciente nro %s no tiene cama libre " % paciente.nro_paciente)
        # #print ("")
        hospital.agregar_paciente_a_espera(paciente)
    
    #Primero procesas los pacientes en la cola
    # if len(hospital.cola_espera_internacion) > 0:
    # #print ("Los pacientes en la cola de internacion para internar son: ")
    # hospital.mostrar_cola_espera_internacion()
    # #print ("")
    # while hospital.tiene_cama_libre() and (len(hospital.cola_espera_internacion) > 0):
    #     paciente = hospital.sacar_paciente_de_espera()
    #     paciente.tiempo_fin_espera_internacion = reloj.tiempo

    #     # Se asigna la cama y si el paciente tiene turno de quirofano, se lo pone en
    #     # la cola de pacientes para operacion
    #     hospital.internar(paciente)
    #     # Se establece el tiempo max. de internacion de paciente. Se usa para la cantidad
    #     # de pacientes no operados.
    #     e = Evento("Fin Paciente Internado",(reloj.tiempo + paciente.tiempo_internacion),
    #             paciente)
    #     FEL.agregar_evento(e)

    #     #print ("Se produjo el evento de Fin paciente Internado con paciente: %s y tiempo evento: %s" % (paciente.nro_paciente,
    #         e.tiempo))

    #     tiempos_de_espera_pacientes.append(paciente.tiempo_espera())
    #     if paciente.tiempo_espera() == 0:
    #         #print ("ERROR!! TIEMPOS DE ESPERA NULOOOOOOOOOOOOOOOOOOOS!!!! ")
    #         #print ("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    #         #print ("")
    #         sys.exit(1)
    #     acumulado_anual_tiempos_espera += paciente.tiempo_espera()

    # #print ("Los pacientes que quedaron en la cola de internacion pendientes son: ")
    # hospital.mostrar_cola_espera_internacion()
    # #print ("")



def procesar_fin_internacion(reloj, hospital, FEL,paciente):
    global cantidad_pacientes_no_atendidos
    global acumulado_anual_pacientes_no_operados
    hospital.alta_paciente(paciente.nro_paciente)
    if not paciente.atendido():
        cantidad_pacientes_no_atendidos += 1
        #Para estadisticas se usa este valor!
        acumulado_anual_pacientes_no_operados += 1
    if len(hospital.cola_espera_internacion) > 0:
        p= hospital.sacar_paciente_de_espera()
        e =  Evento("Paciente Internado",reloj.tiempo+1,p)
        FEL.agregar_evento(e)

def procesar_entrada_quirofano(reloj, hospital, FEL,paciente):

    global tiempo_uso_sala_operaciones
    global acumulado_anual_uso_sala_operaciones

    t = round(np.random.exponential(1 * 60))
    p = None
    paciente_alcanza_a_operarse = False

    #print ("En procesar_entrada_quirofano() para paciente %s ..." % paciente.nro_paciente)
    #print ("El paciente %s se alcanza a operar? : %s" % (paciente.nro_paciente,
        # (reloj.tiempo + t < paciente.tiempo_fin_espera_internacion + paciente.tiempo_internacion) ) )
    #print ("")

    if reloj.tiempo + t < paciente.tiempo_fin_espera_internacion + paciente.tiempo_internacion:
        e = Evento("Paciente Sale de Quirofano",reloj.tiempo+t,paciente)
        FEL.agregar_evento(e)
        # Se marca un quirofano como ocupado.
        hospital.sala_operatoria.marcar_quirofano_ocupado()
        # Se establece el tiempo de inicio y de fin de uso quirofano.
        tiempo_uso_sala_operaciones += t
        # #print ("Paciente %s se puede operar, ingresando a quirofano ..." % paciente.nro_paciente)
        # #print ("Cantidad de pacientes en cola espera operacion: %s" % 
                    # len(hospital.cola_espera_operacion))
        
        #Se recolectan los tiempos anuales 
        acumulado_anual_uso_sala_operaciones += t
                    
    else:
        #Si el paciente pasado por parametro no es valido, se continuan sacando pacientes
        # hasta que alguno pueda ser operado o hasta que la cola de espera de operacion
        # se acabe
        p = hospital.sacar_de_cola_espera_operacion()
        # #print ("Paciente %s sacado de cola de espera." % p.nro_paciente)
        # #print ("El paciente %s se alcanza a operar? : %s" % (p.nro_paciente,
        #         (reloj.tiempo + t < p.tiempo_fin_espera_internacion + p.tiempo_internacion) ) )
        # #print ("")

        while len(hospital.cola_espera_operacion) > 0 and not paciente_alcanza_a_operarse:
            if reloj.tiempo + t < p.tiempo_fin_espera_internacion + p.tiempo_internacion:
                e = Evento("Paciente Sale de Quirofano",reloj.tiempo+t,p)
                FEL.agregar_evento(e)
                # Se marca un quirofano como ocupado.
                hospital.sala_operatoria.marcar_quirofano_ocupado()
                # Se establece el tiempo de inicio y de fin de uso quirofano.
                tiempo_uso_sala_operaciones += t
                #Se recolectan los tiempos anuales 
                acumulado_anual_uso_sala_operaciones += t
                paciente_alcanza_a_operarse = True
                #print ("Paciente %s se puede operar, ingresando a quirofano ..." % p.nro_paciente)
                #print ("Cantidad de pacientes en cola espera operacion: %s" % 
                            # len(hospital.cola_espera_operacion))
            else:
                p = hospital.sacar_de_cola_espera_operacion()


    # #print ("Duracion de paciente sale de quirofano: %s; reloj.tiempo: %s" %
    #  (float(reloj.tiempo + t),reloj.tiempo))
    # #print ("Cola de operacion actualizada!")
    # #print ("")
    # hospital.mostrar_cola_espera_operacion()



def procesar_salida_quirofano(reloj, hospital, FEL, paciente):
    """
        Metodo que procesa el evento de Salida de Quirofano
    :param reloj:
    :param hospital:
    :param FEL:
    :param paciente:
    :return:
    """
    global cantidad_pacientes_atendidos
    global acumulado_anual_pacientes_operados
    hospital.decrementar_cirugias_diarias()
    paciente.operado = True
    cantidad_pacientes_atendidos += 1
    #Este valor se usa para estadisticas
    acumulado_anual_pacientes_operados += 1
    # #print ("En procesar_salida_quirofano() para paciente %s ..." % paciente.nro_paciente)
    # #print ("cantidad_pacientes_atendidos: %s" % cantidad_pacientes_atendidos)
    # #print ("")
    #Se verifica si la cant. de operaciones es mayor a cero, hay que planificar el prox. evento
    # de entrada a quirofano para el sig. paciente
    # hospital.mostrar_cola_espera_operacion()
    p = hospital.sacar_de_cola_espera_operacion()
    
    #Se marca un quirofano como libre
    # #print ("Quirofano liberado!")
    hospital.sala_operatoria.marcar_quirofano_libre()

    # #print ("hospital.sala_operatoria.cant_cirugias_restantes_diarias: %s" % hospital.sala_operatoria.cant_cirugias_restantes_diarias)
    # #print ("")
    if hospital.sala_operatoria.cant_cirugias_restantes_diarias>0 and p is not None:
        # #print ("Entrando al nuevo paciente %s al quirofano en tiempo %s" % 
        #             (paciente.nro_paciente,reloj.tiempo+1) )
        # #print ("")
        e=Evento("Paciente Entra a Quirofano",reloj.tiempo+1,p)
        FEL.agregar_evento(e)


def procesar_apertura_so(reloj, hospital, FEL):
    """
        Metodo que controla la apertura de la Sala de Operaciones
    :param reloj:
    :param hospital:
    :param FEL:
    :return:
    """
    #print ("Cola inicial del dia %s es -->" % (cantidad_dias) )
    # hospital.mostrar_cola_espera_operacion()
    #print ("")
    e = Evento("Cierre de Sala de Operaciones",reloj.tiempo+12*60)
    FEL.agregar_evento(e)
    hospital.abrir_sala_operaciones()
    hospital.calcular_cirugias_diarias()
    # #print ("Cantidad de cirugias diarias para el dia %s son: %s" % (cantidad_dias,hospital.sala_operatoria.cant_cirugias_restantes_diarias))
    quirofanos = hospital.sala_operatoria.quirofanos
    # #print ("Pacientes restantes en hospital.cola_espera_operacion: %s" %
    #             len(hospital.cola_espera_operacion))
    # #print ("")
    if (len(hospital.cola_espera_operacion) > 0):
        hospital.sala_operatoria.mostrar_quirofanos(estado_ocupado=True)
        for q in quirofanos:
            if (not q.ocupado):
                p = hospital.sacar_de_cola_espera_operacion()
                q.ocupado = True
                e = Evento("Paciente Entra a Quirofano",reloj.tiempo+1,p)
                FEL.agregar_evento(e)


def procesar_cierre_so(reloj, hospital, FEL):
    hospital.sala_operatoria.cerrado = True
    e = Evento("Apertura de Sala de Operaciones", reloj.tiempo+12*60)
    FEL.agregar_evento(e)


# Agrega los pacientes del nuevo dia, cuando encuentra en la FEL el evento
# de inicio de dia
def agregar_nuevos_pacientes(self):

    tiempos_arribos = [round(np.random.exponential(100)) for value in range(1,np.random.poisson(100))]
    for tiempo in tiempos_arribos:
        evento = Evento("Arribo de Paciente",tiempo + reloj.tiempo)
        FEL.agregar_evento(evento)


def imprimir_estadisticas(tiempos_espera,porc_uso_quirofano,
                                pac_operados,pac_no_operados,pacientes_para_operacion,
                                pacientes_sin_operacion,
                                total_pacientes_ingresaron_hospital,
                                cantidad_pacientes_para_internar,
                                cantidad_pacientes_para_operar,
                                cantidad_pacientes_FEL):
    print ("======================================================================================")
    print ("")
    print ("- Tiempo de espera promedio para internacion(TEI): %s " % float(np.average(tiempos_espera)))
    print ("- Porcentaje del tiempo total de uso de la sala de operaciones (PTUS): %s " % porc_uso_quirofano)
    print ("---------------------------------------------------------------------------------")
    print ("- Cantidad de pacientes que logran ser operados (CPLO): %s " % pac_operados)
    print ("- Cantidad de pacientes que no logran ser operados (CPNO): %s " %  pac_no_operados)
    print ("- Cantidad de pacientes para operacion(con turno quirofano): %d " %  pacientes_para_operacion)
    print ("- Cantidad de pacientes sin operacion(sin turno quirofano): %d" %  pacientes_sin_operacion)
    print ("---------------------------------------------------------------------------------")
    print ("- Cantidad de pacientes en cola de internacion: %d" %  cantidad_pacientes_para_internar)
    print ("- Cantidad de pacientes en cola de operacion: %d" %  cantidad_pacientes_para_operar)
    print ("---------------------------------------------------------------------------------")
    print ("- Cantidad de eventos que quedaron planificados en la FEL: %s" % cantidad_pacientes_FEL )
    FEL.mostrar_cant_tipo_evento("Arribo de Paciente")
    FEL.mostrar_cant_tipo_evento("Paciente Internado")
    FEL.mostrar_cant_tipo_evento("Fin Paciente Internado",verificar_paciente_con_turno=True)
    FEL.mostrar_cant_tipo_evento("Paciente Entra a Quirofano")
    FEL.mostrar_cant_tipo_evento("Paciente Sale de Quirofano")
    FEL.mostrar_cant_tipo_evento("Apertura de Sala de Operaciones")
    print ("---------------------------------------------------------------------------------")
    print ("- Total pacientes que ingresaron al hospital: %d" %  total_pacientes_ingresaron_hospital)
    print ("")


def calcular_fin_anio(anio):
    return anio * 365

# Guarda tiempos de uso estadisticos 
def recolectar_tiempos_uso_sala_operaciones():
    global tiempos_anuales_sala_operaciones
    global acumulado_anual_uso_sala_operaciones
    #print ("En recolectar_tiempos_uso_sala_operaciones()")
    #print ("")
    #print ("acumulado_anual_uso_sala_operaciones: %s" % acumulado_anual_uso_sala_operaciones)
    tiempos_anuales_sala_operaciones.append(acumulado_anual_uso_sala_operaciones)
    #print ("tiempos_anuales_sala_operaciones: %s" % tiempos_anuales_sala_operaciones)
    acumulado_anual_uso_sala_operaciones = 0
    #print ("Paso un anio!! dia: %s" % cantidad_dias)
    #print ("")

#Recolecta la cantidad de pacientes anual que fueron operados y los que no en dos arreglos
def recolectar_pacientes():
    global pacientes_anuales_operados
    global pacientes_anuales_no_operados
    global acumulado_anual_pacientes_operados
    global acumulado_anual_pacientes_no_operados
    pacientes_anuales_operados.append(acumulado_anual_pacientes_operados)
    pacientes_anuales_no_operados.append(acumulado_anual_pacientes_no_operados)
    # acumulado_anual_pacientes_operados = 0
    # acumulado_anual_pacientes_no_operados=0

def recolectar_tiempos_espera():
    global acumulado_anual_tiempos_espera
    global tiempos_anuales_espera_pacientes
    global acumulado_anual_pacientes_operados
    global acumulado_anual_pacientes_no_operados
    tiempos_anuales_espera_pacientes.append(
        acumulado_anual_tiempos_espera/(acumulado_anual_pacientes_no_operados+acumulado_anual_pacientes_operados))
    acumulado_anual_tiempos_espera = 0
    acumulado_anual_pacientes_operados = 0
    acumulado_anual_pacientes_no_operados = 0




def generar_diagramas(porcentaje_uso_so):
    #print ("En generar_diagramas()")
    #print ("tiempos_anuales_espera_pacientes: %s"  % tiempos_anuales_espera_pacientes)
    #print ("tiempos_anuales_sala_operaciones: %s"  % tiempos_anuales_sala_operaciones)
    #print ("pacientes_anuales_operados: %s"  % pacientes_anuales_operados)
    #print ("pacientes_anuales_no_operados: %s"  % pacientes_anuales_no_operados)
    #print ("")
    g = Graficador(plt)
    histograma_tiempos_espera={
        "tipo":HISTOGRAMA,
        "titulo":"Histogama tiempos de espera de pacientes",
        "label_x":"Valores de tiempo",
        "label_y":"Frecuencias de tiempo",
        # "datos_x":tiempos_de_espera_pacientes,
        "datos_x":tiempos_anuales_espera_pacientes,
        #[minX,minY,maxX,maxY]
        "limites_histograma":[0,0, 3, 5],
        #El paso tiene que ver con la cantidad de valores que se 
        #mostraran en la escala de x o y.
        "paso_x": 1,
        "paso_y": 1
    }

    histograma_tiempos_uso_sala_operaciones={
        "tipo":HISTOGRAMA,
        "titulo":"Histogama uso de sala de operaciones",
        "label_x":"Valores de tiempo",
        "label_y":"Frecuencias de tiempo",
        "datos_x":tiempos_anuales_sala_operaciones,
        #[minX,minY,maxX,maxY]
        "limites_histograma":[200000,0, 300000, 10],
        #El paso tiene que ver con la cantidad de valores que se 
        #mostraran en la escala de x o y.
        "paso_x": 20000,
        "paso_y": 1
    }
    histograma_pacientes_atendidos= {
        "tipo":HISTOGRAMA,
        "titulo":"Histogama de pacientes operados",
        "label_x":"Valores de tiempo",
        "label_y":"Frecuencias de tiempo",
        "datos_x":pacientes_anuales_operados,
        #[minX,minY,maxX,maxY]
        "limites_histograma":[3800,0, 4400, 10],
        #El paso tiene que ver con la cantidad de valores que se 
        #mostraran en la escala de x o y.
        "paso_x": 100,
        "paso_y": 1   
    }
    histograma_pacientes_no_atendidos= {
        "tipo":HISTOGRAMA,
        "titulo":"Histogama de pacientes no operados",
        "label_x":"Valores de tiempo",
        "label_y":"Frecuencias de tiempo",
        "datos_x":pacientes_anuales_no_operados,
        #[minX,minY,maxX,maxY]
        "limites_histograma":[11000,0, 14000, 10],
        #El paso tiene que ver con la cantidad de valores que se 
        #mostraran en la escala de x o y.
        "paso_x": 1000,
        "paso_y": 1   
    }

    #print ("El porcentaje de uso de la sala de operaciones es: %s" %  porcentaje_uso_so)
    diagrama_torta= {
        "tipo":DIAGRAMA_TORTA,
        "titulo": "Uso de la sala de operaciones",
        "labels":["Tiempo usado del quirofano","Tiempo ocioso del quirofano"],
        "datos":[porcentaje_uso_so,(100-porcentaje_uso_so)],
        "explode":[0.2,0],
        "porcentajes":[porcentaje_uso_so,(100-porcentaje_uso_so)]
    }
    g.agregar_grafico(histograma_tiempos_espera)
    g.agregar_grafico(histograma_tiempos_uso_sala_operaciones)
    g.agregar_grafico(histograma_pacientes_atendidos)
    g.agregar_grafico(histograma_pacientes_no_atendidos)
    g.agregar_grafico(diagrama_torta)
    # # Se inicializa la ventana y se muestra una vez que se cargan los datos
    g.inicializar_ventana()

def calcular_intervalo_confianza(tiempos_anuales_espera_pacientes):
    prom = np.mean(tiempos_anuales_espera_pacientes)
    desvio_std = math.sqrt(np.var(tiempos_anuales_espera_pacientes))
    intervalo_confianza=1.96 # 95% de confianza
    
    str_promedio = "El promedio anual de los tiempos de espera de pacientes es: %s " % prom
    str_intervalo_confianza_calculo = "El intervalo de confianza de los tiempos de espera se encuentra definido entre los valores: %s - 2.57 * %s <= %s <= %s + 2.57 * %s" %( ( prom, desvio_std,prom,prom,desvio_std ))

    str_intervalo_confianza_numeros = "El intervalo de confianza de los tiempos de espera se encuentra definido entre: %s <= %s <= %s" %((prom - 2.57* desvio_std),(prom),(prom + 2.57* desvio_std) )

    #print ("")
    #print ("========================================================")
    #print (str_promedio)
    #print (str_intervalo_confianza_calculo)
    #print (str_intervalo_confianza_numeros)
    #print ("========================================================")
    root = Tk()
    # labels_estadisticos=["El promedio de tiempos de espera es: 12",
    # "El intervalo de confianza se encuentra definido entre: 2.3<= 2.5 <=2.6"]
    ex = VentanaResultados(root,[   str_promedio,
                                    str_intervalo_confianza_calculo,
                                    str_intervalo_confianza_numeros
                                ])
    ex.mostrar()




if __name__ == '__main__':

    FEL = FEL()
    reloj = Reloj()
    hospital = Hospital(CANTIDAD_CAMAS,2)
    inicializar_simulacion(FEL, reloj)
    #global cantidad_pacientes_atendidos
    #global cantidad_pacientes_no_atendidos
    global cantidad_dias
    global tiempos_anuales_espera_pacientes

    cantidad_experimentos = 1
    while (cantidad_experimentos <= CANT_EXPERIMENTO):
        #print ("Cantidad de experimentos actual %s" % cantidad_experimentos)
        #print ("")
        print ("--> NUEVO EXPERIMENTO: %s" % cantidad_experimentos)
        while (cantidad_dias <= CANT_CORRIDAS):
            # print ("========DIA %d=============" % cantidad_dias)
            # FEL.mostrar_eventos()
            #print("============================")

            evento = FEL.extraer()
            #print ("Evento extraido de la FEL: %s" % evento)
            #print ("")
            # if evento.paciente is not None:
                #print ("El paciente relacionado al evento es: %s" % evento.paciente.nro_paciente)
            
            #print ("")
            reloj.tiempo = evento.tiempo
            #print ("Reloj cambiado a: %s" % reloj.tiempo)
            #print ("")
            if evento.tipo == "Arribo de Paciente":
                #print ("Procesando arribo de paciente nuevo con tiempo de evento: %s , valor reloj: %s..." % 
                    # (evento.tiempo, reloj.tiempo))
                procesar_arribo(reloj, hospital, FEL)

            elif evento.tipo == "Paciente Internado":
                procesar_internacion(reloj, hospital, FEL,evento)

            elif evento.tipo == "Fin Paciente Internado":
                procesar_fin_internacion(reloj, hospital, FEL,evento.paciente)

            elif evento.tipo == "Paciente Entra a Quirofano":
                procesar_entrada_quirofano(reloj, hospital, FEL, evento.paciente)

            elif evento.tipo == "Paciente Sale de Quirofano":
                #print ("Evento Paciente Sale de quirofano con paciente %s en tiempo %s" %
                    # (evento.paciente.nro_paciente,evento.tiempo))
                procesar_salida_quirofano(reloj, hospital, FEL, evento.paciente)

            elif evento.tipo == "Apertura de Sala de Operaciones":
                procesar_apertura_so(reloj, hospital, FEL)

            elif evento.tipo == "Cierre de Sala de Operaciones":
                procesar_cierre_so(reloj, hospital, FEL)

            elif evento.tipo == "Inicio Dia":
                fines_anio = map(calcular_fin_anio,range(1,CANT_EXPERIMENTO+1))
                #print ("Dia actual: %s; Los fines de anio son los dias numero: %s" %
                            # (cantidad_dias , fines_anio) )
                #print ("")
                # Si se llego al final de un anio se recolecta
                if cantidad_dias in fines_anio:
                    #print ("Entre al fin de anio en el dia %s" % cantidad_dias)
                    #Se verifica si cambia de anio para recoger tiempos de uso del quirofano anuales
                    recolectar_tiempos_uso_sala_operaciones()
                    recolectar_pacientes()
                    recolectar_tiempos_espera()

                evento = Evento("Inicio Dia",reloj.tiempo+ 1440)
                cantidad_dias += 1
                FEL.agregar_evento(evento)
                agregar_nuevos_pacientes(FEL)
                #print ("Nuevo dia! La cantidad de dias actual es: %s" % cantidad_dias)
                #print ("Tiempo del nuevo dia: %s" % int(reloj.tiempo+1440) )
                hospital.sala_operatoria.mostrar_quirofanos(estado_ocupado=True)
                # for q in hospital.sala_operatoria.quirofanos:
                    #print (q)
                #print ("")

        cantidad_dias = 0
        cantidad_experimentos += 1

    #Se obtienen las varaibles de estado de las colas de espera de internacion y operacion
    cantidad_pacientes_para_internar = 0
    cantidad_pacientes_para_operar = 0

    cantidad_pacientes_para_internar = len(hospital.cola_espera_internacion)
    cantidad_pacientes_para_operar = len(hospital.cola_espera_operacion)
    cantidad_pacientes_FEL = FEL.calcular_tamanio()

    #print ("cantidad_pacientes_no_atendidos: %s" % cantidad_pacientes_no_atendidos)
    #print ("cantidad_pacientes_atendidos: %s" % cantidad_pacientes_atendidos)
    # #print ("tiempos_de_espera_pacientes: %s" % tiempos_de_espera_pacientes)
    #print ("longitud tiempos_de_espera_pacientes: %s" % len(tiempos_de_espera_pacientes))
    imprimir_estadisticas(tiempos_de_espera_pacientes,(tiempo_uso_sala_operaciones/reloj.tiempo)*100,
                            cantidad_pacientes_atendidos,
                            cantidad_pacientes_no_atendidos,pacientes_para_operacion,
                            pacientes_sin_operacion,
                            total_pacientes_ingresaron_hospital,
                            cantidad_pacientes_para_internar,
                            cantidad_pacientes_para_operar,
                            cantidad_pacientes_FEL)
    
    #print (" ********************************************************************* ")
    #print ("tiempos de uso anuales de sala operaciones : %s" % tiempos_anuales_sala_operaciones)
    #print ("pacientes anuales operados: %s " % pacientes_anuales_operados)
    #print ("pacientes anuales no operados: %s " % pacientes_anuales_no_operados)
    #print ("")
    # generar_diagramas((tiempo_uso_sala_operaciones/reloj.tiempo)*100
    #Hijo
    if os.fork() == 0:
        generar_diagramas((tiempo_uso_sala_operaciones/reloj.tiempo)*100)
    else:
        calcular_intervalo_confianza(tiempos_anuales_espera_pacientes)

