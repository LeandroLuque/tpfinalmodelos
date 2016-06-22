__author__ = 'leandro'

import numpy as np

from clases import Reloj
from clases import Evento
from clases import FEL
from clases import Paciente
from clases import Hospital

from utilidades.utilidades import *
from vista.vistaV2 import *

"""
    Constantes para la simulacion del sistema
"""
CANT_PACIENTES_INICIAL = 10
CANT_EXPERIMENTO = 1 # years
CANT_CORRIDAS = 10 * 1# DIAS

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

tiempo_acumulado_sala_operaciones = 0
tiempos_anuales_sala_operaciones = []




#TODOS PENDIENTES
# -AGREGAR CONTADOR PARA CALCULAR LA CANTIDAD DE PACIENTES QUE ENTRARON AL HOSPITAL --> OK
# -CALCULAR EL PORCENTAJE DE USO DE LA SALA DE OPERACIONES PARA MOSTRAR EN IMPIRMIR_ESTADISTICAS --> OK
# -CORREGIR EL TIEMPO DE ESPERA DE LOS PACIENTES (TODOS UNOS!!)
# -AGREGAR MAS QUIROFANOS PARA VER SI DISMINUYE LA CANTIDAD DE PACIENTES


def inicializar_simulacion(FEL, reloj):

    ## Obtener el evento de cierre de sala de operaciones y agregarlo a la FEL
    ## Cargar los diez pacientes con distribucion exponencial

    print ("Tiempo de reloj en inicializar_simulacion(): %s" % reloj.tiempo)

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
        total_pacientes_ingresaron_hospital += 1
        if paciente.quirofano:
            pacientes_para_operacion += 1
        else:
            pacientes_sin_operacion += 1
        hospital.agregar_paciente_a_espera(paciente)
        if (hospital.tiene_cama_libre()):
            e = Evento("Paciente Internado",reloj.tiempo+1,paciente)
            FEL.agregar_evento(e)
        

        #TODO SACAR ESTE METODO UNA VEZ QUE ANDE LA SIMULACION!
        hospital.mostrar_cant_camas_libres()

# BACKUP!
# def procesar_arribo(reloj, hospital, FEL):
#     """
#         Este metodo sirve para procesar el arribo de
#         un paciente. Se crea el paciente y se lo agrega a la
#         cola de espera para internacion del hospital
#     :param reloj:
#     :param hospital
#     :return:
#     """
#     global pacientes_sin_operacion
#     global pacientes_para_operacion
#     global total_pacientes_ingresaron_hospital 
#     if len(hospital.cola_espera_internacion) < MAX_COLA_ESPERA_INTERNACION:
#         paciente = Paciente(reloj.tiempo)
#         total_pacientes_ingresaron_hospital += 1
#         if paciente.quirofano:
#             pacientes_para_operacion += 1
#         else:
#             pacientes_sin_operacion += 1
#         hospital.agregar_paciente_a_espera(paciente)
#         if (hospital.tiene_cama_libre()):
#             e = Evento("Paciente Internado",reloj.tiempo+1,paciente)
#             FEL.agregar_evento(e)
        



    
def procesar_internacion(reloj, hospital, FEL):

    if len(hospital.cola_espera_internacion) > 0:
        paciente = hospital.sacar_paciente_de_espera()
        # Se establece el tiempo maximo de internacion segun el reloj y el tiempo de internacion del paciente.
        # Este valor se usa despues en el evento "Entra a Quirofano", para determinar si un paciente
        # puede ser operado dentro del rango de los dias que esta operado.
        paciente.tiempo_fin_espera_internacion = reloj.tiempo

        # Se asigna la cama y si el paciente tiene turno de quirofano, se lo pone en
        # la cola de pacientes para operacion
        hospital.internar(paciente)
        # Se establece el tiempo max. de internacion de paciente. Se usa para la cantidad
        # de pacientes no operados.
        e = Evento("Fin Paciente Internado",(reloj.tiempo + paciente.tiempo_internacion),
                paciente)
        FEL.agregar_evento(e)
        tiempos_de_espera_pacientes.append(paciente.tiempo_espera())
    

def procesar_fin_internacion(reloj, hospital, FEL,paciente):
    global cantidad_pacientes_no_atendidos
    hospital.alta_paciente(paciente.nro_paciente)
    if not paciente.atendido():
        cantidad_pacientes_no_atendidos += 1
    if len(hospital.cola_espera_internacion) > 0:
        p= hospital.sacar_paciente_de_espera()
        e =  Evento("Paciente Internado",reloj.tiempo+1,p)
        FEL.agregar_evento(e)

def procesar_entrada_quirofano(reloj, hospital, FEL,paciente):
    global tiempo_uso_sala_operaciones
    global tiempo_acumulado_sala_operaciones
    t = round(np.random.exponential(1 * 60))
    if reloj.tiempo + t < paciente.tiempo_fin_espera_internacion + paciente.tiempo_internacion:
        e = Evento("Paciente Sale de Quirofano",reloj.tiempo+t,paciente)
        FEL.agregar_evento(e)
        # Se marca un quirofano como ocupado.
        hospital.sala_operatoria.marcar_quirofano_ocupado()
        # Se establece el tiempo de inicio y de fin de uso quirofano.
        tiempo_uso_sala_operaciones += t

        tiempo_acumulado_sala_operaciones += tiempo_uso_sala_operaciones
        # Si estoy en el ultimo dia del anio
        print ("En procesar_entrada_quirofano() dia: %s" % cantidad_dias)
        if (cantidad_dias % 360) == 0:
            tiempos_anuales_sala_operaciones.append(tiempo_acumulado_sala_operaciones)
            tiempo_acumulado_sala_operaciones = 0


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
    hospital.decrementar_cirugias_diarias()
    paciente.operado = True
    cantidad_pacientes_atendidos += 1
    print ("cantidad_pacientes_atendidos: %s" % cantidad_pacientes_atendidos)
    print ("")
    #Se verifica si la cant. de operaciones es mayor a cero, hay que planificar el prox. evento
    # de entrada a quirofano para el sig. paciente
    hospital.mostrar_cola_espera_operacion()
    p = hospital.sacar_de_cola_espera_operacion()
    a = hospital.sala_operatoria.cant_cirugias_restantes_diarias
    print ("hospital.sala_operatoria.cant_cirugias_restantes_diarias: %s" % hospital.sala_operatoria.cant_cirugias_restantes_diarias)
    print ("")
    if hospital.sala_operatoria.cant_cirugias_restantes_diarias>0 and p is not None:
        print ("Entrando al paciente %s al quirofano" % paciente.nro_paciente)
        print ("")
        e=Evento("Paciente Entra a Quirofano",reloj.tiempo+1,p)
        #Se marca un quirofano como libre
        hospital.sala_operatoria.marcar_quirofano_libre()
        FEL.agregar_evento(e)


def procesar_apertura_so(reloj, hospital, FEL):
    """
        Metodo que controla la apertura de la Sala de Operaciones
    :param reloj:
    :param hospital:
    :param FEL:
    :return:
    """
    e = Evento("Cierre de Sala de Operaciones",reloj.tiempo+12*60)
    FEL.agregar_evento(e)
    hospital.abrir_sala_operaciones()
    hospital.calcular_cirugias_diarias()
    print ("Cantidad de cirugias diarias para el dia %s son: %s" % (cantidad_dias,hospital.sala_operatoria.cant_cirugias_restantes_diarias))
    quirofanos = hospital.sala_operatoria.quirofanos
    if (len(hospital.cola_espera_operacion) > 0):
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



if __name__ == '__main__':

    FEL = FEL()
    reloj = Reloj()
    hospital = Hospital(120,2)
    inicializar_simulacion(FEL, reloj)
    #global cantidad_pacientes_atendidos
    #global cantidad_pacientes_no_atendidos
    global cantidad_dias

    while (cantidad_dias < CANT_CORRIDAS):
        # print("========DIA %d=============" % cantidad_dias)
        # FEL.mostrar_eventos()
        # print("============================")
        ##TODO reemplazar por la cantidad de dias
        evento = FEL.extraer()
        reloj.tiempo = evento.tiempo

        if evento.tipo == "Arribo de Paciente":
            procesar_arribo(reloj, hospital, FEL)

        elif evento.tipo == "Paciente Internado":
            procesar_internacion(reloj, hospital, FEL)

        elif evento.tipo == "Fin Paciente Internado":
            procesar_fin_internacion(reloj, hospital, FEL,evento.paciente)

        elif evento.tipo == "Paciente Entra a Quirofano":
            procesar_entrada_quirofano(reloj, hospital, FEL, evento.paciente)

        elif evento.tipo == "Paciente Sale de Quirofano":
            procesar_salida_quirofano(reloj, hospital, FEL, evento.paciente)

        elif evento.tipo == "Apertura de Sala de Operaciones":
            procesar_apertura_so(reloj, hospital, FEL)

        elif evento.tipo == "Cierre de Sala de Operaciones":
            procesar_cierre_so(reloj, hospital, FEL)

        elif evento.tipo == "Inicio Dia":
            evento = Evento("Inicio Dia",reloj.tiempo+ 1440)
            cantidad_dias += 1
            FEL.agregar_evento(evento)
            agregar_nuevos_pacientes(FEL)
            print ("Nuevo dia! La cantidad de dias actual es: %s" % cantidad_dias)

    #Se obtienen las varaibles de estado de las colas de espera de internacion y operacion
    cantidad_pacientes_para_internar = 0
    cantidad_pacientes_para_operar = 0

    cantidad_pacientes_para_internar = len(hospital.cola_espera_internacion)
    cantidad_pacientes_para_operar = len(hospital.cola_espera_operacion)
    cantidad_pacientes_FEL = FEL.calcular_tamanio()

    #print(hospital.cola_espera_internacion)
    #print(hospital.cola_espera_operacion)
    print ("cantidad_pacientes_no_atendidos: %s" % cantidad_pacientes_no_atendidos)
    print ("cantidad_pacientes_atendidos: %s" % cantidad_pacientes_atendidos)
    print ("tiempos_de_espera_pacientes: %s" % tiempos_de_espera_pacientes)
    print ("longitud tiempos_de_espera_pacientes: %s" % len(tiempos_de_espera_pacientes))
    imprimir_estadisticas(tiempos_de_espera_pacientes,(tiempo_uso_sala_operaciones/reloj.tiempo)*100,
                            cantidad_pacientes_atendidos,
                            cantidad_pacientes_no_atendidos,pacientes_para_operacion,
                            pacientes_sin_operacion,
                            total_pacientes_ingresaron_hospital,
                            cantidad_pacientes_para_internar,
                            cantidad_pacientes_para_operar,
                            cantidad_pacientes_FEL)
    
    print (" ********************************************************************* ")
    print ("tiempos de uso anuales del quirfano : %s" % tiempos_anuales_sala_operaciones)
    print ("")


    # g = Graficador(plt)
    # histograma_tiempos_espera={
    #     "tipo":HISTOGRAMA,
    #     "titulo":"Histogama de prueba",
    #     "label_x":"Valores de tiempo",
    #     "label_y":"Frecuencias de tiempo",
    #     "datos_x":tiempos_de_espera_pacientes,
    #     #[minX,minY,maxX,maxY]
    #     "limites_histograma":[20,100, 0, 100]
    # }
    # histograma_tiempos_uso_sala_operaciones={
    #     "tipo":HISTOGRAMA,
    #     "titulo":"Histogama de prueba",
    #     "label_x":"Valores de tiempo",
    #     "label_y":"Frecuencias de tiempo",
    #     "datos_x":tiempos_anuales_sala_operaciones,
    #     #[minX,minY,maxX,maxY]
    #     "limites_histograma":[20,100, 0, 100]
    # }

    # d2= {
    #     "tipo":DIAGRAMA_TORTA,
    #     "titulo": "Prueba de torta",
    #     "labels":["Tiempo usado del quirofano","Tiempo ocioso del quirofano"],
    #     "datos":[87,13],
    #     "explode":[0.2,0],
    #     "porcentajes":[10,20]
    # }
    # # Se inicializa la ventana y se muestra una vez que se cargan los datos
    # g.agregar_grafico(histograma_tiempos_espera)
    # g.agregar_grafico(d2)
    # g.inicializar_ventana()





