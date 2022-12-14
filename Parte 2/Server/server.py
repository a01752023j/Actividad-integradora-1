# TC2008B. Sistemas Multiagentes y Gráficas Computacionales
# Python flask server to interact with Unity. Based on the code provided by Sergio Ruiz.
# Octavio Navarro. October 2021

from flask import Flask, request, jsonify
from Cajas3 import *
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer


app = Flask("Traffic example")

@app.route('/init', methods=['POST', 'GET'])
def initModel():
    global currentStep, randomModel, number_agents, width, height

    if request.method == 'POST':
        number_agents = int(request.form.get('NAgents'))
        width = int(request.form.get('width'))
        height = int(request.form.get('height'))
        cajas = int(request.form.get('cajas'))
        pasos = int(request.form.get('pasos'))  
        currentStep = 0

        print(request.form)
        print(number_agents, width, height)
        randomModel = BOXboolCollector(width, height, number_agents, cajas, pasos)

        return jsonify({"message":"Parameters recieved, model initiated."})

@app.route('/getAgents', methods=['GET'])
def getAgents():
    global randomModel

    if request.method == 'GET':
        agentPositions = [{"id": str(agent.unique_id), "x": x, "y": 1, "z": z, "tieneCaja": bool(agent.BOXbool)} for (a, x, z) in randomModel.grid.coord_iter() for agent in a if isinstance(agent, RobotOrg)]

        return jsonify({'positions':agentPositions})

@app.route('/getObstacles', methods=['GET'])
def getObstacles():
    global randomModel

    if request.method == 'GET':
        carPositions = [{"id": str(agent.unique_id), "x": x, "y":1, "z":z} for (a, x, z) in randomModel.grid.coord_iter() for agent in a if isinstance(agent, Pared) ]

        return jsonify({'positions':carPositions})

@app.route('/getCajas', methods=['GET'])
def getCajas():
    global randomModel

    if request.method == 'GET':
        BOXboolPosition = [{"id": str(agent.unique_id), "x": x, "y": 1, "z": z} for (a, x, z) in randomModel.grid.coord_iter() for agent in a if isinstance(agent, Caja)]

        return jsonify({'positions': BOXboolPosition})

@app.route('/getPilas', methods=['GET'])
def getPilas():
    global randomModel

    if request.method == 'GET':
        pilaPosition = [{"id": str(agent.unique_id), "x": x, "y": 1, "z": z} for (a, x, z) in randomModel.grid.coord_iter() for agent in a if isinstance(agent, Stack)]

        return jsonify({'positions': pilaPosition})

@app.route('/update', methods=['GET'])
def updateModel():
    global currentStep, randomModel
    if request.method == 'GET':
        randomModel.step()
        currentStep += 1
        return jsonify({'message':f'Model updated to step {currentStep}.', 'currentStep':currentStep})

if __name__=='__main__':
    app.run(host="localhost", port=8585, debug=True)