__author__ = 'leandro'

import numpy as np

from clases import Reloj
from clases import Evento
from clases import FEL
from clases import Paciente
from clases import Hospital

"""
    Constantes para la simulacion del sistema
"""
CANT_PACIENTES_INICIAL = 10
CANT_EXPERIMENTO = 1 # years
CANT_CORRIDAS = 30# DIAS

MAX_COLA_ESPERA_INTERNACION = 250
cantidad_dias = 0
#Variables de salida
#Se utiliza este arreglo para guardar los tiempos promedios de cada paciente
# y calcular el tiempo promedio
tiempos_de_espera_pacientes = []
cantidad_pacientes_atendidos = 0
cantidad_pacientes_no_atendidos = 0
pacientes_para_operacion = 0
pacientes_sin_opearacion = 0
tiempo_uso_sala_operaciones = 0



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

    global pacientes_sin_opearacion
    global pacientes_para_operacion

    if len(hospital.cola_espera_internacion) < MAX_COLA_ESPERA_INTERNACION:
        paciente = Paciente(reloj.tiempo)
        if paciente.quirofano:
            pacientes_para_operacion +=1
        else:
            pacientes_sin_opearacion +=1
        hospital.agregar_paciente_a_espera(paciente)
        if (hospital.tiene_cama_libre()):
            ## TODO El tiempo de espera promedio para internar un paciente es siempre 1!!
            # Corregir!
            e = Evento("Paciente Internado",reloj.tiempo+1,paciente)
            FEL.agregar_evento(e)


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
    t = round(np.random.exponential(1 * 60))
    if reloj.tiempo + t < paciente.tiempo_fin_espera_internacion + paciente.tiempo_internacion:
        e = Evento("Paciente Sale de Quirofano",reloj.tiempo+t,paciente)
        FEL.agregar_evento(e)
        # Se marca un quirofano como ocupado.
        hospital.sala_operatoria.marcar_quirofano_ocupado()
        # Se establece el tiempo de inicio y de fin de uso quirofano.
        tiempo_uso_sala_operaciones += t
    


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
    #Se verifica si la cant. de operaciones es mayor a cero, hay que planificar el prox. evento
    # de entrada a quirofano para el sig. paciente
    hospital.mostrar_cola_espera_operacion()
    p = hospital.sacar_de_cola_espera_operacion()
    a = hospital.sala_operatoria.cant_cirugias_restantes_diarias
    if hospital.sala_operatoria.cant_cirugias_restantes_diarias>0 and p is not None:
        e=Evento("Paciente Entra a Quirofano",reloj.tiempo+1,p)
        #Se marca un quirofano como libre
        hospital.sala_operatoria.marcar_quirofano_libre()
        FEL.agregar_evento(e)
        # cantidad_pacientes_atendidos+=1


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

    tiempos_arribos = [round(np.random.exponential(100)) for value in range(1,CANT_PACIENTES_INICIAL + 1)]
    for tiempo in tiempos_arribos:
        evento = Evento("Arribo de Paciente",tiempo + reloj.tiempo)
        FEL.agregar_evento(evento)


def imprimir_estadisticas(tiempos_espera,porc_uso_quirofano,
                                pac_operados,pac_no_operados,pacientes_para_operacion,
                                pacientes_sin_operacion):
    print ("======================================================================================")
    print ("")
    print ("- Tiempo de espera promedio para internacion(TEI): %d " % int(np.average(tiempos_espera)))
    print ("- Porcentaje del tiempo total de uso de la sala de operaciones (PTUS): %s " % porc_uso_quirofano)
    print ("- Cantidad de pacientes que logran ser operados (CPLO): %s " % pac_operados)
    print ("- Cantidad de pacientes que no logran ser operados (CPNO): %s " %  pac_no_operados)
    print ("- Cantidad de pacientes para operacion: %d " %  pacientes_para_operacion)
    print ("- Cantidad de pacientes sin operacion %d" %  pacientes_sin_operacion)
    print ("")



if __name__ == '__main__':

    FEL = FEL()
    reloj = Reloj()
    hospital = Hospital(250,2)
    inicializar_simulacion(FEL, reloj)
    #global cantidad_pacientes_atendidos
    #global cantidad_pacientes_no_atendidos
    while (cantidad_dias < CANT_CORRIDAS):
        print("========DIA %d=============" % cantidad_dias)
        FEL.mostrar_eventos()
        print("============================")
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
            #agregar_nuevos_pacientes(FEL)

    #print(hospital.cola_espera_internacion)
    #print(hospital.cola_espera_operacion)
    print ("cantidad_pacientes_no_atendidos: %s" % cantidad_pacientes_no_atendidos)
    print ("cantidad_pacientes_atendidos: %s" % cantidad_pacientes_atendidos)
    print ("tiempos_de_espera_pacientes: %s" % tiempos_de_espera_pacientes)
    imprimir_estadisticas(tiempos_de_espera_pacientes,tiempo_uso_sala_operaciones,
                            cantidad_pacientes_atendidos,
                            cantidad_pacientes_no_atendidos,pacientes_para_operacion,pacientes_sin_opearacion)

