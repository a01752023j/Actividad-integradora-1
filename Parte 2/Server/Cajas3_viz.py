from Cajas3 import *
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer

def agent_portrayal(agent):


    portrayalCircle = {"Shape": "circle",
                  "Filled": "false",
                  "Layer": 0,
                  "r": 0.5}
    
    portrayalRect = {"Shape": "rect",
                 "w": 0.7,
                 "h": 0.7,
                 "Filled": "true",
                 "Layer": 0}


    portrayalRectMid = {"Shape": "rect",
                 "w": 0.5,
                 "h": 0.5,
                 "Filled": "true",
                 "Layer": 0}
    

    portrayalRectFull = {"Shape": "rect",
                 "w": 1,
                 "h": 1,
                 "Filled": "true",
                 "Layer": 0}

    

    if agent.agent == "robotOrg":
        portrayalCircle["Color"] = "lightblue"
        return portrayalCircle
    elif isinstance (agent, RobotOrg) and agent.agent == "robotCaja":
        portrayalCircle["Color"] = "red"
        return portrayalCircle
    elif agent.agent == "stack":
        portrayalRect["Color"] = "grey"
        return portrayalRect
    elif agent.agent == "celdacaja":
        portrayalRectMid["Color"] = "brown"
        return portrayalRectMid
    elif agent.agent == "pared":
        portrayalRectFull["Color"] = "black"
        return portrayalRectFull
    elif agent.agent == "fullStack":
        portrayalRectFull["Color"] = "red"
        return portrayalRectFull
    elif agent.agent == "puerta":
        portrayalRectMid["Color"] = "green"
        return portrayalRectMid
    else:
        portrayalCircle["Color"] = "white"
        return portrayalCircle

ancho = 20
alto = 20
robots = 5
cajas = 20
pasos = 5000000
grid = CanvasGrid(agent_portrayal, ancho, alto, 750, 750)
server = ModularServer(BOXboolCollector,
                       [grid],
                       "BOXbool Collector",
                       {"width":ancho, "height":alto, "agents": robots, "BOXbooles": cajas, "steps": pasos})
server.port = 8521 # The default
server.launch()