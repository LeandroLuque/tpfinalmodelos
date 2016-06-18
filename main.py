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
CANT_EXPERIMENTO = 1
CANT_CORRIDAS = 30
MAX_COLA_ESPERA_INTERNACION = 250
cantidad_dias = 0


def inicializar_simulacion(FEL, reloj):

    ## Obtener el evento de cierre de sala de operaciones y agregarlo a la FEL
    ## Cargar los diez pacientes con distribucion exponencial

    tiempos_arribos = [round(np.random.exponential(100)) for value in range(1,CANT_PACIENTES_INICIAL + 1)]
    for tiempo in tiempos_arribos:
        evento = Evento("Arribo de Paciente",tiempo + reloj.tiempo)
        FEL.agregar_evento(evento)
    evento = Evento("Cierre de Sala de Operaciones",1200)
    FEL.agregar_evento(evento)
    evento = Evento("Fin Dia",1440)
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
    paciente = Paciente(reloj.tiempo)
    if len(hospital.cola_espera_internacion) < MAX_COLA_ESPERA_INTERNACION:
        hospital.agregar_paciente_a_espera(paciente)
        if (hospital.tiene_cama_libre()):
            e = Evento("Paciente Internado",reloj.tiempo+1)
            FEL.agregar_evento(e)


def procesar_internacion(reloj, FEL):
    pass

def procesar_fin_internacion(reloj, FEL):
    pass

def procesar_entrada_quirofano(reloj, FEL):
    pass

def procesar_salida_quirofano(reloj, FEL):
    pass

def procesar_apertura_so(reloj, FEL):
    pass

def procesar_cierre_so(reloj, FEL):
    pass


if __name__ == '__main__':

    FEL = FEL()
    reloj = Reloj()
    hospital = Hospital(250,2)
    inicializar_simulacion(FEL, reloj)

    while (not FEL.vacia()):
        FEL.mostrar_eventos()
        print("============================")
        ##TODO reemplazar por la cantidad de dias
        evento = FEL.extraer()
        reloj.tiempo = evento.tiempo

        if evento.tipo == "Arribo de Paciente":
            procesar_arribo(reloj, hospital, FEL)

        elif evento.tipo == "Paciente Internado":
            procesar_internacion(reloj, FEL)

        elif evento.tipo == "Fin Paciente Internado":
            procesar_fin_internacion(reloj, FEL)

        elif evento.tipo == "Paciente Entra a Quirofano":
            procesar_entrada_quirofano(reloj, FEL)

        elif evento.tipo == "Paciente Sale de Quirofano":
            procesar_salida_quirofano(reloj, FEL)

        elif evento.tipo == "Apertura de Sala de Operaciones":
            procesar_apertura_so(reloj, FEL)

        elif evento.tipo == "Cierre de Sala de Operaciones":
            procesar_cierre_so(reloj, FEL)



