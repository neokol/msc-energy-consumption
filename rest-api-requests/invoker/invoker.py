import os
from dotenv import load_dotenv
import base64
from fastapi import HTTPException
import requests

load_dotenv()

def invoke_openwhisk_action(device_id):
    url = f"{os.getenv('OPENWHISK_APIHOST')}/api/v1/namespaces/{os.getenv('OPENWHISK_NAMESPACE')}/actions/deviceConsumption"
    params = {
        "blocking": "true",
        "result": "true"
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic ' + base64.b64encode(f"{os.getenv('OPENWHISK_USER')}:{os.getenv('OPENWHISK_PASS')}".encode()).decode()
    }
    payload = {
        "device_id": device_id
    }
    response = requests.post(url, json=payload, params=params, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    
def invoke_cost_copenwhisk_action(date):
    url = f"{os.getenv('OPENWHISK_APIHOST')}/api/v1/namespaces/{os.getenv('OPENWHISK_NAMESPACE')}/actions/costCalculation"
    params = {
        "blocking": "true",
        "result": "true"
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic ' + base64.b64encode(f"{os.getenv('OPENWHISK_USER')}:{os.getenv('OPENWHISK_PASS')}".encode()).decode()
    }
    payload = {
        "date": date
    }
    response = requests.post(url, json=payload, params=params, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    
    
def invoke_anormaly_copenwhisk_action():
    url = f"{os.getenv('OPENWHISK_APIHOST')}/api/v1/namespaces/{os.getenv('OPENWHISK_NAMESPACE')}/actions/detectAnormalities"
    params = {
        "blocking": "true",
        "result": "true"
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic ' + base64.b64encode(f"{os.getenv('OPENWHISK_USER')}:{os.getenv('OPENWHISK_PASS')}".encode()).decode()
    }
    response = requests.post(url,  params=params, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)