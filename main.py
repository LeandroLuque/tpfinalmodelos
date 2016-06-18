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

#Se utiliza este arreglo para guardar los tiempos promedios de cada paciente
# y calcular el tiempo promedio
tiempos_de_espera_pacientes=[]


def inicializar_simulacion(FEL, reloj):

    ## Obtener el evento de cierre de sala de operaciones y agregarlo a la FEL
    ## Cargar los diez pacientes con distribucion exponencial

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
    paciente = Paciente(reloj.tiempo)
    if len(hospital.cola_espera_internacion) < MAX_COLA_ESPERA_INTERNACION:
        hospital.agregar_paciente_a_espera(paciente)
        if (hospital.tiene_cama_libre()):
            e = Evento("Paciente Internado",reloj.tiempo+1,paciente.nro_paciente)
            FEL.agregar_evento(e)


def procesar_internacion(reloj, hospital, FEL):
    """ """
    paciente = hospital.sacar_paciente_de_espera()
    paciente.tiempo_fin_espera_internacion = reloj.tiempo
    e = Evento("Fin Paciente Internado",reloj.tiempo + paciente.tiempo_internacion,
        paciente.nro_paciente)
    #Asignar cama
    hospital.internar(paciente)
    FEL.agregar_evento(e)
    tiempos_de_espera_pacientes.append(paciente.tiempo_espera())
    
def procesar_fin_internacion(reloj, hospital, FEL,nro_paciente):
    hospital.alta_paciente(nro_paciente)
    if len(hospital.cola_espera_internacion) > 0:
        paciente= hospital.sacar_paciente_de_espera()
        e =  Evento("Paciente Internado",reloj.tiempo+1,paciente.nro_paciente)
        FEL.agregar_evento(e)

def procesar_entrada_quirofano(reloj, hospital, FEL,nro_paciente):
    t = round(np.random.exponential(1 * 60))
    e = Evento("Paciente Sale de Quirofano",reloj.tiempo+t,nro_paciente)
    FEL.agregar_evento(e)
    #Se marca un quirofano como ocupado
    self.hospital.sala_operatoria.marcar_quirofano_ocupado()
    self.hospital.sala_operatoria.cant_cirugias_restantes_diarias-=1


def procesar_salida_quirofano(reloj, hospital, FEL,nro_paciente):
    #Se verifica si la cant. de operaciones es mayor a cero, hay que planificar el prox. evento
    # de entrada a quirofano
    if self.hospital.sala_operatoria.cant_cirugias_restantes_diarias>0:
        e=Evento("Paciente Entra a Quirofano",reloj.tiempo+1,nro_paciente)
        FEL.agregar_evento(e)
        #Se marca un quirofano como libre
        self.hospital.sala_operatoria.marcar_quirofano_libre()



def procesar_apertura_so(reloj, hospital, FEL):
    e = Evento("Cierre de Sala de Operaciones",reloj.tiempo+12*60)
    FEL.agregar_evento(e)
    hospital.abrir_sala_operaciones()
    hospital.calcular_cirugias_diarias()

    #TODO: Cambiar el atributo quirofanos de la sala operatoria por un arreglo de quirofanos
    quirofanos = hospital.sala_operatoria.quirofanos
    for q in quirofanos:
        if (not quirofanos[q].esta_ocupado ):
            p = hospital.sacar_de_cola_espera_operacion()
            e = Evento("Paciente Entra a Quirofano",reloj.tiempo+1,)
            FEL.agregar_evento(e)


def procesar_cierre_so(reloj, hospital, FEL):
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
            procesar_internacion(reloj, hospital, FEL)

        elif evento.tipo == "Fin Paciente Internado":
            procesar_fin_internacion(reloj, hospital, FEL,evento.nro_paciente)

        elif evento.tipo == "Paciente EPaciente Entra a Quirofano":
            procesar_entrada_quirofano(reloj, hospital, FEL, evento.nro_paciente)

        elif evento.tipo == "Paciente Sale de Quirofano":
            procesar_salida_quirofano(reloj, hospital, FEL,evento.nro_paciente)

        elif evento.tipo == "Apertura de Sala de Operaciones":
            procesar_apertura_so(reloj, hospital, FEL)

        elif evento.tipo == "Cierre de Sala de Operaciones":
            procesar_cierre_so(reloj, hospital, FEL)

        elif evento.tipo == "Inicio Dia":
            evento = Evento("Inicio Dia",reloj.tiempo+ 1440)
            FEL.agregar_evento(evento)


