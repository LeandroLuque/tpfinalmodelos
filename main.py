__author__ = 'leandro'

import numpy as np
from clases import Reloj
from clases import Evento
from clases import FEL


"""
    Constantes para la simulacion del sistema
"""
CANT_PACIENTES_INICIAL = 10
CANT_EXPERIMENTO = 1
CANT_CORRIDAS = 30


def inicializar_simulacion(FEL, reloj):

    ## Obtener el evento de cierre de sala de operaciones y agregarlo a la FEL
    ## Cargar los diez pacientes con distribucion exponencial

    tiempos_arribos = [round(np.random.exponential(100)) for value in range(1,CANT_PACIENTES_INICIAL + 1)]
    for tiempo in tiempos_arribos:
        evento = Evento("Arribo de Paciente",tiempo)
        FEL.agregar_evento(evento)
    evento = Evento("Cierre de Sala de Operaciones",1200)
    FEL.agregar_evento(evento)
    evento = Evento("Fin Dia",1440)
    FEL.agregar_evento(evento)



if __name__ == '__main__':

    FEL = FEL()
    reloj = Reloj()
    inicializar_simulacion(FEL, reloj)
    FEL.mostrar_eventos()

    while (not FEL.vacia()):
        evento = FEL.extraer()
        if evento.tipo == "Arribo de Paciente":
            reloj.tiempo = evento.tiempo
        elif evento.tipo == "Paciente Internado":
            pass
        elif evento.tipo == "Fin Paciente Internado":
            pass
        elif evento.tipo == "Paciente Entra a Quirofano":
            pass
        elif evento.tipo == "Paciente Sale de Quirofano":
            pass
        elif evento.tipo == "Apertura de Sala de Operaciones":
            pass
        elif evento.tipo == "Cierre de Sala de Operaciones":
            pass