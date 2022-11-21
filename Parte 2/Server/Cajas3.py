from mesa import Agent, Model 
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
import numpy as np
from mesa.datacollection import DataCollector
'''
def _init_(self, unique_id, model):
        super()._init_(unique_id, model)
'''

#Creación del Agente que representará las cajas.
class Caja(Agent):

    #Constructor de las cajas
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.agent = "celdacaja"

#Creación del Agente que representará las pilas de cajas.
class Stack(Agent):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.agent = "stack"
        self.max = 0

#Creación del Agente que representará la pared.
class Pared(Agent):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.agent = "pared"

#Creación del Agente que representará la puerta.

class Puerta(Agent):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.agent = "puerta"


#Creación del Agente que representará los robots.
class RobotOrg(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.agent = "robotOrg"
        self.BOXbool = False
        self.movimientos = 0
        self.cajasRestantes = self.model.cajas

    def Prefabs(self):

        #Union con los modelos (prefabs) en Unity.
        cellmates = self.model.grid.get_cell_list_contents([self.pos])

        if len(cellmates) != 0:
            for i in cellmates:
                if i.agent == "celdacaja" and self.agent == "robotOrg":
                    self.BOXbool = True
                    self.agent = "robotCaja"
                    i.agent = "vacio"

                elif i.agent == "stack":
                    if self.agent == "robotCaja":
                        self.agent = "robotOrg"
                        self.BOXbool = False

                elif i.agent == "fullStack" and self.BOXbool == True:
                    self.BOXbool = True
                    self.agent = "robotCaja"
                    i.agent = "fullStack"


    def Movimiento(self):
        
        #El agente se mueve de manera aleatoria.
        possibleSteps = self.model.grid.get_neighborhood(
            self.pos,
            moore=False,
            include_center=False,
            radius=1)
        new_position = self.random.choice(possibleSteps)
        cellmatesNewPos = self.model.grid.get_cell_list_contents([new_position])

        if len(cellmatesNewPos) == 1:
            if cellmatesNewPos[0].agent != "robotOrg" and \
                cellmatesNewPos[0].agent != "robotCaja" and \
                cellmatesNewPos[0].agent != "pared" and \
                cellmatesNewPos[0].agent != "stack" and \
                cellmatesNewPos[0].agent != "fullStack" and \
                cellmatesNewPos[0].agent != "puerta":
                self.model.grid.move_agent(self, new_position)
                self.movimientos += 1

        elif len(cellmatesNewPos) == 0:
            self.model.grid.move_agent(self, new_position)
            self.movimientos += 1


    def irPila(self):
        
        #Una vez cuenta con una caja, el agente se dirige a una pila.

        diffX = self.pos[0] - self.model.posicionesPilas[0][0]
        diffY = self.pos[1] - self.model.posicionesPilas[0][1]
        
        if diffX > 0:
            newPos = (self.pos[0] - 1, self.pos[1])
            cellmatesNewPos = self.model.grid.get_cell_list_contents([newPos])

            if len(cellmatesNewPos) == 1:
                if cellmatesNewPos[0].agent != "robotOrg" and \
                cellmatesNewPos[0].agent != "robotCaja" and \
                cellmatesNewPos[0].agent != "pared" and \
                cellmatesNewPos[0].agent != "puerta":
                    self.model.grid.move_agent(self, newPos)
                    self.movimientos += 1
            elif len(cellmatesNewPos) == 0:
                self.model.grid.move_agent(self, newPos)
                self.movimientos += 1

        elif diffX < 0:
            newPos = (self.pos[0] + 1, self.pos[1])
            cellmatesNewPos = self.model.grid.get_cell_list_contents([newPos])

            if len(cellmatesNewPos) == 1:
                if cellmatesNewPos[0].agent != "robotOrg" and \
                cellmatesNewPos[0].agent != "robotCaja" and \
                cellmatesNewPos[0].agent != "pared" and \
                cellmatesNewPos[0].agent != "puerta":
                    self.model.grid.move_agent(self, newPos)
                    self.movimientos += 1
            elif len(cellmatesNewPos) == 0:
                self.model.grid.move_agent(self, newPos)
                self.movimientos += 1

        elif diffY > 0:
            newPos = (self.pos[0], self.pos[1] - 1)
            cellmatesNewPos = self.model.grid.get_cell_list_contents([newPos])

            if len(cellmatesNewPos) == 1:
                if cellmatesNewPos[0].agent != "robotOrg" and \
                cellmatesNewPos[0].agent != "robotCaja" and \
                cellmatesNewPos[0].agent != "pared" and \
                cellmatesNewPos[0].agent != "puerta":
                    self.model.grid.move_agent(self, newPos)
                    self.movimientos += 1
            elif len(cellmatesNewPos) == 0:
                self.model.grid.move_agent(self, newPos)
                self.movimientos += 1

        elif diffY < 0:
            newPos = (self.pos[0], self.pos[1] + 1)
            cellmatesNewPos = self.model.grid.get_cell_list_contents([newPos])

            if len(cellmatesNewPos) == 1:
                if cellmatesNewPos[0].agent != "robotOrg" and \
                cellmatesNewPos[0].agent != "robotCaja" and \
                cellmatesNewPos[0].agent != "pared" and \
                cellmatesNewPos[0].agent != "puerta":
                    self.model.grid.move_agent(self, newPos)
                    self.movimientos += 1
            elif len(cellmatesNewPos) == 0:
                self.model.grid.move_agent(self, newPos)
                self.movimientos += 1


    def step(self):
        self.cajasRestantes = self.model.cajas
        self.Prefabs()

        if self.model.pasosTotales > 0 and self.model.cajas > 0:
            if self.BOXbool == True:
                self.irPila()
                self.model.pasosTotales -= 1
            else:
                self.Movimiento()
                self.model.pasosTotales -= 1
            cellmates = self.model.grid.get_cell_list_contents([self.pos])

            for i in cellmates:
                if i.agent == "fullStack":
                    if self.BOXbool == True:
                        self.irPila()
                        self.model.pasosTotales -= 1
                elif i.agent == "stack":
                    if self.BOXbool == True:
                        if i.max == 4:
                            i.max = 5
                            print(f'PILA llena: {i.max} cajas')
                            i.agent = "fullStack"
                            posLlena = [i.pos[0], i.pos[1]]
                            self.model.posicionesPilas.remove(posLlena)
                            self.agent = "robotOrg"
                            self.BOXbool = False
                            self.model.cajas -= 1
                        elif i.max < 4:
                            i.max += 1
                            print(f'Numero de cajas PILA: {i.max}')
                            self.agent = "robotOrg"
                            self.BOXbool = False
                            self.model.cajas -= 1
                    



class BOXboolCollector(Model):
   
   #Modelación del comportamiento de todos los agentes.

    def __init__(self, width, height, agents, BOXbooles, steps):
        self.ancho = width
        self.alto = height
        self.agentes = agents
        self.cajas = BOXbooles
        self.pasosTotales = steps * agents
        self.grid = MultiGrid(width, height, True)
        self.schedule = SimultaneousActivation(self)
        self.running = True
        celdas = []
        self.pilas = (BOXbooles // 5) + 1
        self.posicionesPilas = []
        self.dataCollectorMovements = DataCollector(
            model_reporters={"Total Movements":BOXboolCollector.calculateMovements},
            agent_reporters={}
        )
        self.dataCollectorBOXbooles = DataCollector(
            model_reporters={"BOXbooles Left":BOXboolCollector.calculateBOXbooles},
            agent_reporters={}
        )

        # Guarda posiciones de celdas para poder actualizar su disponibilidad.
        for (content, x, y) in self.grid.coord_iter():
            celdas.append([x, y])

        # Paredes en y
        for i in range(0, height):
            a = Pared(i, self)
            self.grid.place_agent(a, (0, i))
            self.grid.place_agent(a, (width - 1, i))
            pos = [0, i]
            pos2 = [width - 1, i]
            celdas.remove(pos)
            celdas.remove(pos2)

        # Pared en x (superior)
        for i in range(1, width - 1):
            a = Pared(i, self)
            self.grid.place_agent(a, (i, height - 1))
            pos = [i, height - 1]
            celdas.remove(pos)

        # Pared en x (inferior parte izquierda)
        for i in range(1, (width // 2)):
            a = Pared(i, self)
            self.grid.place_agent(a, (i, 0))
            pos = [i, 0]
            celdas.remove(pos)

        # Hace puerta entre muro abajo
        a = Puerta(1, self)
        self.grid.place_agent(a, ((width // 2), 0))
        pos = [(width // 2), 0]
        celdas.remove(pos)

        # Pared en x (inferior parte derecha)
        for i in range((width // 2) + 1, width - 1):
            a = Pared(i, self)
            self.grid.place_agent(a, (i, 0))
            pos = [i, 0]
            celdas.remove(pos)

        # Creación de las pilas.
        for i in range(self.pilas):
            a = Stack(i, self)
            pos = self.random.choice(celdas)
            self.grid.place_agent(a, (pos[0], pos[1]))
            self.posicionesPilas.append(pos)
            celdas.remove(pos)

        # Creación de los robots.
        for i in range(self.agentes):
            a = RobotOrg(i, self)
            self.schedule.add(a)
            pos = self.random.choice(celdas)
            self.grid.place_agent(a, (pos[0], pos[1]))
            celdas.remove(pos)
        
        # Creación de las cajas.
        for i in range(self.cajas):
            a = Caja(i, self)
            pos = self.random.choice(celdas)
            self.grid.place_agent(a, (pos[0], pos[1])) 
            celdas.remove(pos)

    def calculateMovements(model):
        totalMovements = 0
        movementsReport = [agent.movimientos for agent in model.schedule.agents]
        for x in movementsReport:
            totalMovements += x
        return totalMovements

    def calculateBOXbooles(model):
        #Indica las cajas por acomodar en cada step.
        BOXboolesReport = [agent.cajasRestantes for agent in model.schedule.agents]
        for x in BOXboolesReport:
            return x 

    def step(self):
        self.schedule.step()
        self.dataCollectorMovements.collect(self)
        self.dataCollectorBOXbooles.collect(self)
        print("Cajas en el grid: ", self.cajas)
        print(" ")