import requests
from fastapi import HTTPException

import logging
import base64

OPENWHISK_APIHOST = 'http://localhost:3233'

OPENWHISK_USER = 'user'
OPENWHISK_PASS = 'pass'




def call_openwhisk_action(action_name, params):
    url = f"{OPENWHISK_APIHOST}/api/v1/namespaces/guest/actions/{action_name}?blocking=true&result=true"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic ' + base64.b64encode(f"{OPENWHISK_USER}:{OPENWHISK_PASS}".encode()).decode()
    }
    try:
        response = requests.post(url, headers=headers, json=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Failed to call OpenWhisk action: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to call OpenWhisk action")
    
    
    

