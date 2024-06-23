import requests
from fastapi import HTTPException

import logging
import base64

OPENWHISK_APIHOST = 'http://20.19.91.100:3233'
OPENWHISK_AUTH = ('23bc46b1-71f6-4ed5-8c54-816aa4f8c502:123zO3xZCLrMN6v2BKK1dXYFpXlPkccOFqm12CdAsMgRU4VrNZ9lyGVCGuMDGIwP', '')

OPENWHISK_USER = '23bc46b1-71f6-4ed5-8c54-816aa4f8c502'
OPENWHISK_PASS = '123zO3xZCLrMN6v2BKK1dXYFpXlPkccOFqm12CdAsMgRU4VrNZ9lyGVCGuMDGIwP'




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
    
    
    

