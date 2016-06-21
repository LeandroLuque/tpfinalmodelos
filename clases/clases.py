__author__ = 'leandro'


from collections import deque
import numpy as np

#from vista import Posicion

class Evento(object):

    def __init__(self, tipo, tiempo,nro_paciente = None,tiempo_max_internacion=None):
        self.tipo = tipo
        self.tiempo = tiempo
        self.nro_paciente = nro_paciente
        self.tiempo_maximo_de_internacion=tiempo_max_internacion

    @property
    def tipo(self):
        return self._tipo

    @tipo.setter
    def tipo(self, tipo):
        self._tipo = tipo


    @property
    def tiempo_maximo_de_internacion(self):
        return self.__tiempo_maximo_de_internacion

    @tiempo_maximo_de_internacion.setter
    def tiempo_maximo_de_internacion(self, tipo):
        self.__tiempo_maximo_de_internacion = tipo

    @property
    def tiempo(self):
        return self._tiempo

    @tiempo.setter
    def tiempo(self, tiempo):
        self._tiempo = tiempo


    @property
    def paciente(self):
        return self._nro_paciente

    @tipo.setter
    def paciente(self, p):
        self._nro_paciente = p


    def __str__(self):
        return "Nro paciente: %s - El tipo de evento es: %s - El tiempo es: %d" % (
            self.nro_paciente,self.tipo, self.tiempo)


class Reloj(object):

    # TIEMPO_INICIAL = 60 * 8
    TIEMPO_INICIAL = 0

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

    def __init__(self, tiempo_llegada):
        Paciente.nro_paciente = self.nro_paciente = Paciente.nro_paciente + 1
        self.tiempo_internacion = round(np.random.exponential(2) * 24 * 60)
        self.quirofano = np.random.choice([True,False])
        ## Esto dos tiempos se usan para calcular el tiempo que
        ## espera un paciente para ser internado
        self.tiempo_inicio_espera_internacion = tiempo_llegada
        self.tiempo_fin_espera_internacion = 0

        self.tiempo_maximo_de_internacion=0

    @property
    def tiempo_maximo_de_internacion(self):
        return self.__tiempo_maximo_de_internacion

    @tiempo_maximo_de_internacion.setter
    def tiempo_maximo_de_internacion(self,x):
        self.__tiempo_maximo_de_internacion = x




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


    @property
    def tiempo_inicio_espera_internacion(self):
        return self.__tiempo_inicio_espera_internacion

    @quirofano.setter
    def tiempo_inicio_espera_internacion(self,t):
        self.__tiempo_inicio_espera_internacion = t


    @property
    def tiempo_fin_espera_internacion(self):
        return self.__tiempo_fin_espera_internacion

    @quirofano.setter
    def tiempo_fin_espera_internacion(self,t):
        self.__tiempo_fin_espera_internacion = t


    def tiempo_espera(self):
        """
            Devuelve el tiempo que espera un paciente
            para ser internado
        :return Tiempo (en minutos):
        """
        return self.__tiempo_fin_espera_internacion - self.__tiempo_inicio_espera_internacion


    def tiene_turno_quirofano(self):
        """ Determina si un paciente tiene turno de quirofano o no.
        :return Boolean
        """
        return self.quirofano


class Hospital(object):

    def __init__(self, cantidad_camas, cantidad_quirofanos):
        self.camas = {x:None for x in range(1, cantidad_camas+1)}
        self.cola_espera_internacion = deque([])
        self.cola_espera_operacion = deque([])
        self.sala_operatoria = SalaOperatoria(cantidad_quirofanos)

    @property
    def camas(self):
        return self.__camas

    @camas.setter
    def camas(self,x):
        self.__camas = x

    @property
    def sala_operatoria(self):
        return self.__sala_opearatoria

    @sala_operatoria.setter
    def sala_operatoria(self,x):
        self.__sala_opearatoria = x

    def agregar_paciente_a_espera(self,paciente):
        """
            Agrega paciente a la cola de espera
            para internacion
        """
        self.cola_espera_internacion.append(paciente)

    def sacar_paciente_de_espera(self):
        """
            Obtiene el proximo paciente que esta en
            la cola de intenacion
        """
        return self.cola_espera_internacion.popleft()
        # if len(self.cola_espera_internacion) == 0:
        #     return None
        # else:
        #     return self.cola_espera_internacion.popleft()


    def agregar_a_cola_espera_operacion(self,paciente):
        """
            Agrega paciente a la cola de operacion
        """
        self.cola_espera_operacion.append(paciente)

    def sacar_de_cola_espera_operacion(self):
        """
            Obtiene el proximo paciente que esta en
            la cola de intenacion
        :return:Retorno el proximo paciente a operar. Si no hay,
                devuelve None.
        """
        if len(self.cola_espera_operacion) == 0:
            return None
        else:
            return self.cola_espera_operacion.popleft()


    def abrir_sala_operaciones(self):
        self.sala_operatoria.cerrada = False


    def internar(self,paciente):
        """
            En este punto hay que hacer la
            internacion del paciente. Asignacion de
            cama y encolarlo para operarlo, si es que
            tiene orden para quirofano
        """
        for c in self.camas:
            if (self.camas[c] is None):
                self.camas[c]=paciente
                if paciente.quirofano:
                    self.cola_espera_operacion.append(paciente)
                break

    def alta_paciente(self,nro_paciente):
        """
            Se tiene que liberar la cama en la que
            estaba el paciente.
        """
        for c in self.camas:
            if ( (self.camas[c] is not None) and
                    self.camas[c].nro_paciente == nro_paciente):
                self.camas[c]=None
                break

    def tiene_cama_libre(self):
        """
            Indica si hay una cama libre
        :return Boolean:
        """

        for cama in self.camas:
            if  self.camas[cama] == None:
                return True
        return False

    # Calcula la cant. de cirugias diarias que se pueden hacer agregar_paciente_a_espera
    def calcular_cirugias_diarias(self):
        self.sala_operatoria.calcular_cirugias_diarias()

    #Actualiza el estado de los quirofanos
    def cerrar_quirofanos(self):
        self.sala_operatoria.cerrar_quirofanos()

    def mostrar_cola_espera_operacion(self):
        print "Pacientes en cola_espera_operacion actualmente:"
        if len(self.cola_espera_operacion) == 0:
            print "- 0;"
            return 
        for p in self.cola_espera_operacion:
            print "- %s;" % p.nro_paciente


class SalaOperatoria:

    def __init__(self, cantidad_quirofanos):
        self.cola_operacion = []
        self.quirofanos = [ Quirofano() , Quirofano() ]
        self.cerrado = False
        #
        self.cant_cirugias_restantes_diarias = 0



    @property
    def quirofanos(self):
        return self.__quirofanos

    @quirofanos.setter
    def quirofanos(self,x):
        self.__quirofanos = x

    @property
    def cerrado(self):
        return self.__cerrado

    @cerrado.setter
    def cerrado(self, x):
        self.__cerrado = x


    @property
    def cant_cirugias_restantes_diarias(self):
        return self.__cant_cirugias_restantes_diarias

    @cerrado.setter
    def cant_cirugias_restantes_diarias(self, x):
        self.__cant_cirugias_restantes_diarias = x

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

    def calcular_cirugias_diarias(self):
        self.cant_cirugias_restantes_diarias = round(np.random.poisson(10))

    def marcar_quirofano_ocupado(self):
        for q in self.quirofanos:
            if not q.esta_ocupado:
                q.esta_ocupado=True
                break

    def marcar_quirofano_libre(self):
        for q in self.quirofanos:
            if q.esta_ocupado:
                q.esta_ocupado=False
                break

class Quirofano(object):

    def __init__(self):
        self.ocupado = False
    #     self.posicion= Posicion(x,y)

    @property
    def ocupado(self):
        return self.__ocupado

    @ocupado.setter
    def ocupado(self, x):
        self.__ocupado = x

    def esta_ocupado(self):
        return self.ocupado

    # def getX(self):
    #     return self.posicion.getX()

    # def getY(self):
    #     return self.posicion.getY()


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