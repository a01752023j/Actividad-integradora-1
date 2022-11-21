// TC2008B. Sistemas Multiagentes y Gráficas Computacionales
// C# client to interact with Python. Based on the code provided by Sergio Ruiz.
// Octavio Navarro. October 2021

using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;

[Serializable]
public class AgentData
{
    public string id;
    public float x, y, z;
    public bool tieneCaja;

    public AgentData(string id, float x, float y, float z, bool tieneCaja)
    {
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z;
        this.tieneCaja = tieneCaja;
    }
}

[Serializable]
public class CajaData
{
    public string id;
    public float x, y, z;
    public string tipo;

    public CajaData(string id, float x, float y, float z, string tipo)
    {
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z;
        this.tipo = tipo;
    }
}

[Serializable]
public class PilaData
{
    public string id;
    public float x, y, z;
    public int numCajas;

    public PilaData(string id, float x, float y, float z, int numCajas)
    {
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z;
        this.numCajas = numCajas;
    }
}
[Serializable]


public class AgentsData
{
    public List<AgentData> positions;

    public AgentsData() => this.positions = new List<AgentData>();
}

[Serializable]

public class CajasData
{
    public List<CajaData> positions;

    public CajasData() => this.positions = new List<CajaData>();
}

[Serializable]

public class PilasData
{
    public List<PilaData> positions;

    public PilasData() => this.positions = new List<PilaData>();
}


public class AgentController : MonoBehaviour
{
    // private string url = "https://agents.us-south.cf.appdomain.cloud/";
    string serverUrl = "http://localhost:8585";
    string getAgentsEndpoint = "/getAgents";
    string getObstaclesEndpoint = "/getObstacles";
    string getCajasEndpoint = "/getCajas";
    string getPilasEndpoint = "/getPilas";
    string sendConfigEndpoint = "/init";
    string updateEndpoint = "/update";
    AgentsData agentsData, obstacleData;
    CajasData cajasData;
    PilasData pilasData;
    Dictionary<string, GameObject> agents, robotCaja, cajasInst, idPilas;
    Dictionary<string, Vector3> prevPositions, currPositions;
    Dictionary<string, int> cajasPila;

    bool updated = false, started = false;

    public GameObject agentPrefab, obstaclePrefab, floor, box, pile, prefabCarry;
    public int NAgents, width, height, cajas, pasos;
    public float timeToUpdate = 5.0f;
    private float timer, dt;

    void Start()
    {
        agentsData = new AgentsData();
        obstacleData = new AgentsData();
        cajasData = new CajasData();
        pilasData = new PilasData();
        prevPositions = new Dictionary<string, Vector3>();
        currPositions = new Dictionary<string, Vector3>();

        agents = new Dictionary<string, GameObject>();
        robotCaja = new Dictionary<string, GameObject>();
        cajasInst = new Dictionary<string, GameObject>();
        idPilas = new Dictionary<string, GameObject>();
        cajasPila = new Dictionary<string, int>();

        floor.transform.localScale = new Vector3((float)width / 10, 1, (float)height / 10);
        floor.transform.localPosition = new Vector3((float)width / 2 - 0.5f, 0, (float)height / 2 - 0.5f);

        timer = timeToUpdate;

        StartCoroutine(SendConfiguration());
    }

    private void Update()
    {
        if (timer < 0)
        {
            timer = timeToUpdate;
            updated = false;
            StartCoroutine(UpdateSimulation());
        }

        if (updated)
        {
            timer -= Time.deltaTime;
            dt = 1.0f - (timer / timeToUpdate);

            foreach (var agent in currPositions)
            {
                Vector3 currentPosition = agent.Value;
                Vector3 previousPosition = prevPositions[agent.Key];

                Vector3 interpolated = Vector3.Lerp(previousPosition, currentPosition, dt);
                Vector3 direction = currentPosition - interpolated;

                agents[agent.Key].transform.localPosition = interpolated;
                if (direction != Vector3.zero) agents[agent.Key].transform.rotation = Quaternion.LookRotation(direction);
                robotCaja[agent.Key].transform.localPosition = interpolated;
                if (direction != Vector3.zero) robotCaja[agent.Key].transform.rotation = Quaternion.LookRotation(direction);

            }

            // float t = (timer / timeToUpdate);
            // dt = t * t * ( 3f - 2f*t);
        }
    }

    IEnumerator UpdateSimulation()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + updateEndpoint);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            StartCoroutine(GetAgentsData());
            StartCoroutine(GetPilasData());
            StartCoroutine(GetCajasData());
        }
    }

    IEnumerator SendConfiguration()
    {
        WWWForm form = new WWWForm();

        form.AddField("NAgents", NAgents.ToString());
        form.AddField("width", width.ToString());
        form.AddField("height", height.ToString());
        form.AddField("cajas", cajas.ToString());
        form.AddField("pasos", pasos.ToString());

        UnityWebRequest www = UnityWebRequest.Post(serverUrl + sendConfigEndpoint, form);
        www.SetRequestHeader("Content-Type", "application/x-www-form-urlencoded");

        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        else
        {
            Debug.Log("Configuration upload complete!");
            Debug.Log("Getting Agents positions");
            StartCoroutine(GetAgentsData());
            StartCoroutine(GetPilasData());
            StartCoroutine(GetObstacleData());
            StartCoroutine(GetCajasData());
        }
    }

    IEnumerator GetAgentsData()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getAgentsEndpoint);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            agentsData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            Debug.Log(www.downloadHandler.text);

            foreach (AgentData agent in agentsData.positions)
            {
                Vector3 newAgentPosition = new Vector3(agent.x, (float)1, agent.z);

                if (!started)
                {
                    prevPositions[agent.id] = newAgentPosition;
                    agents[agent.id] = Instantiate(agentPrefab, newAgentPosition, Quaternion.identity);
                    robotCaja[agent.id] = Instantiate(prefabCarry, newAgentPosition, Quaternion.identity);
                    robotCaja[agent.id].SetActive(false);
                }
                else
                {
                    Vector3 currentPosition = new Vector3();
                    if (currPositions.TryGetValue(agent.id, out currentPosition))
                        prevPositions[agent.id] = currentPosition;
                    currPositions[agent.id] = newAgentPosition;
                    if (agent.tieneCaja == true)
                    {
                        agents[agent.id].SetActive(false);
                        robotCaja[agent.id].SetActive(true);
                    }
                    else
                    {
                        agents[agent.id].SetActive(true);
                        robotCaja[agent.id].SetActive(false);
                    }


                }
            }
        }
    }

    IEnumerator GetObstacleData()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getObstaclesEndpoint);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            obstacleData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            Debug.Log(obstacleData.positions);

            foreach (AgentData obstacle in obstacleData.positions)
            {
                Instantiate(obstaclePrefab, new Vector3(obstacle.x, (float)0.5, obstacle.z), Quaternion.identity);
            }
        }
    }

    IEnumerator GetCajasData()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getCajasEndpoint);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            cajasData = JsonUtility.FromJson<CajasData>(www.downloadHandler.text);

            Debug.Log(cajasData.positions);

            foreach (CajaData caja in cajasData.positions)
            {
                if (!started)
                {
                    cajasInst[caja.id] = Instantiate(box, new Vector3(caja.x, (float)0.4, caja.z), Quaternion.identity);
                    Debug.Log(cajasInst[caja.id]);
                }
                else
                {
                    if (caja.tipo == "vacio")
                    {
                        cajasInst[caja.id].SetActive(false);
                    }
                }
            }
            updated = true;
            if (!started) started = true;
        }
    }

    IEnumerator GetPilasData()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getPilasEndpoint);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            pilasData = JsonUtility.FromJson<PilasData>(www.downloadHandler.text);

            Debug.Log(pilasData.positions);

            foreach (PilaData pila in pilasData.positions)
            {
                if (!started)
                {
                    idPilas[pila.id] = Instantiate(pile, new Vector3(pila.x, (float)0.0, pila.z), Quaternion.identity);
                    cajasPila[pila.id] = pila.numCajas;
                }
                else
                {
                    if (pila.numCajas != cajasPila[pila.id])
                    {
                        cajasPila[pila.id] = cajasPila[pila.id] + 1;
                        Instantiate(box, new Vector3(pila.x, ((cajasPila[pila.id] * (float)0.94)), pila.z), Quaternion.identity);
                    }
                }
            }
        }
    }

}