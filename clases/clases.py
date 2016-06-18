__author__ = 'leandro'


from collections import deque
import numpy as np

class Evento(object):

    def __init__(self, tipo, tiempo):
        self.tipo = tipo
        self.tiempo = tiempo

    @property
    def tipo(self):
        return self._tipo

    @tipo.setter
    def tipo(self, tipo):
        self._tipo = tipo

    @property
    def tiempo(self):
        return self._tiempo

    @tiempo.setter
    def tiempo(self, tiempo):
        self._tiempo = tiempo

    def __str__(self):
        return "El tipo de evento es: %s - El tiempo es: %d" % (self.tipo, self.tiempo)


class Reloj(object):

    TIEMPO_INICIAL = 60 * 8

    def __init__(self):
        self.tiempo = Reloj.TIEMPO_INICIAL

    @property
    def tiempo(self):
        return self._tiempo

    @tiempo.setter
    def tiempo(self, tiempo):
        if tiempo >= 0:
            self._tiempo = tiempo


class Paciente(object):

    nro_paciente = 0

    def __init__(self):
        Paciente.nro_paciente = self.nro_paciente = Paciente.nro_paciente + 1
        self.tiempo_internacion = np.random.exponential(2)
        self.quirofano = np.random.choice([True,False])

    @property
    def tiempo_internacion(self):
        return self.__tiempo_internacion

    @tiempo_internacion.setter
    def tiempo_internacion(self,x):
        self.__tiempo_internacion = x

    @property
    def quirofano(self):
        return self.__quirofano

    @quirofano.setter
    def quirofano(self,x):
        self.__quirofano = x


class Hospital(object):

    def __init__(self, cantidad_camas):
        self.camas = {x:None for x in range(1, cantidad_camas+1)}
        self.cola_espera_internacion = deque([])
        self.cola_atencion = deque([])
        self.sala_operatoria = SalaOperatoria()

    @property
    def camas(self):
        return self.__camas

    @camas.setter
    def camas(self,x):
        self.__camas = x

    def agregar_paciente_a_espera(self):
        """
            Obtiene el proximo paciente que esta en
            la cola de inte
        """
        return self.cola_espera_internacion.popleft()

    def sacar_paciente_de_espera(self,paciente):
        """
            Agrega paciente a la cola de espera
            para internacion
        """
        self.cola_espera_internacion.append(paciente)

    def internar(self,paciente):
        """
            En este punto hay que hacer la
            internacion del paciente. Asignacion de
            cama y encolarlo para operarlo, si es que
            tiene orden para quirofano
        """
        pass

    def alta_paciente(self,paciente):
        """
            Se tiene que liberar la cama en la que
            estaba el paciente.
        """
        pass


class SalaOperatoria:

    def __init__(self):
        self.cola_operacion = []
        self.quirofano1 = False
        self.quirofano2 = False
        self.cerrado = False


    @property
    def cerrado(self):
        return self.__cerrado

    @cerrado.setter
    def cerrado(self, x):
        self.__cerrado = x

    def comenzar_operacion(self,paciente):
        """
            Aca hay que dejar pasar el tiempo de
            operacion para el paciente dado
        """
        pass

    def finalizar_operacion(self,paciente):
        """
            Finaliza la operacion de curso
            para un paciente dado
        """
        pass


class FEL(object):

    def __init__(self):
        self.lista = deque([])

    @property
    def lista(self):
        return self._lista

    @lista.setter
    def lista(self, lista):
        self._lista = lista

    def agregar_evento(self,evento):
        self.lista.append(evento)
        self.lista = deque(sorted(self.lista, key= lambda ev: ev.tiempo))

    def vacia(self):
        """
            Indica si todavia quedan elementos
            por procesar
        :return:
        """
        if not self.lista:
            return True
        else:
            return False

    def extraer(self):
        """
            Devuelve el proximo evento a
            procesar en el sistema
        :return:
        """
        return self.lista.popleft()

    def mostrar_eventos(self):
        #TODO Borrar este metodo cuando la simulacion sea exitosa
        for evento in self.lista:
            print(evento)

    def sumar_tiempo(self):
        conta = 0
        for evento in self.lista:
            conta += evento.tiempo
        return conta