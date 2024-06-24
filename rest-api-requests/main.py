from invoker.invoker import invoke_anormaly_copenwhisk_action, invoke_openwhisk_action, invoke_cost_copenwhisk_action

import os
from fastapi import FastAPI, HTTPException, Request
from typing import List

from schemas import EnergyReading, Device
from datetime import datetime
from minio import Minio
from minio.error import S3Error
import json
from dotenv import load_dotenv
import io

from actions_old import call_openwhisk_action
from utilities import (
    publish_to_rabbitmq,
    initialize_rabbitmq_connection,
    consume_and_save)
load_dotenv() 



app = FastAPI(
    title= "Energy Consumption",
    description="Cloud energy consumption system for Smart Devices",
    version="0.0.1",
    contact={"name":"Developer","email":"itp23107@hua.gr"}
)


#Initialize MinIO client
minio_client = Minio(
    os.getenv('MINIO_HOST'),  # MinIO server URL
    access_key=os.getenv('MINIO_BUCKET_ACCESS_KEY'),
    secret_key=os.getenv('MINIO_BUCKET_SECRET_KEY'),
    secure=False
)
bucket_name = os.getenv('BUCKET_NAME')

# # Ensure bucket exists
found = minio_client.bucket_exists(bucket_name)
if not found:
    minio_client.make_bucket(bucket_name)
else:
    print(f"Bucket {bucket_name} already exists")


# Mock database
energy_data = []
devices = []

@app.get("/")
def read_root():
    return {"message": "Welcome to the Home Energy Monitoring System"}

@app.get("/api/energy", response_model=List[EnergyReading])
def get_energy_readings():
    return energy_data

@app.post("/api/energy")
def add_energy_reading(reading: EnergyReading):
    energy_data.append(reading)
    # Save to MinIO
    try:
        s3_key = f"energy/{reading.device_id}/{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        data = json.dumps(reading.dict()).encode('utf-8')
        data_stream = io.BytesIO(data)
        minio_client.put_object(
            bucket_name,
            s3_key,
            data=data_stream,
            length=len(data),
            content_type="application/json"
        )
    except S3Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # Convert list of EnergyReading objects to list of dictionaries
    energy_data_dicts = [e.dict() for e in energy_data]
    
    # Analyze consumption
    analysis_result = call_openwhisk_action('analyze_consumption_api', {'readings': energy_data_dicts})
    
    return {
        "message": "Energy reading added successfully",
        "analysis": analysis_result
    }

@app.post("/api/provide_energy")
def receive_energy_data(data: EnergyReading):
    try:
        connection = initialize_rabbitmq_connection()
        publish_to_rabbitmq(data.dict(), connection, 'energy_data')
        return {"message": "Data received and queued for processing."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/api/consume_and_save")
def consume_and_save_data():
    try:
        result = consume_and_save()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@app.post("/api/device_consumption")
def get_device_consumption(device_id: str):
    try:
        result = invoke_openwhisk_action(device_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@app.post("/api/cost_per_day")
def get_daily_cost(date: str):
    try:
        result = invoke_cost_copenwhisk_action(date)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/anomaly_detection")
def get_anomaly_device(date: str):
    try:
        result = invoke_anormaly_copenwhisk_action(date)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
@app.post('/webhook/minio')
async def minio_webhook(request: Request):
    """Endpoint to receive MinIO event notifications."""
    try:
        data = await request.json()
        print(f"Received data: {data}")  # Log received data

        if data.get('EventName') == 's3:ObjectCreated:Put':
            connection = initialize_rabbitmq_connection()
            try:
                # Assuming data is already a dict, if not, convert appropriately
                publish_to_rabbitmq(data, connection, 'energy_data')
                return {"status": "success", "message": "Upload event sent to RabbitMQ"}
            finally:
                connection.close()  # Ensure the connection is closed after publishing
        else:
            return {"status": "ignored", "message": "Event not relevant"}

    except Exception as e:
        print(f"Error processing webhook: {e}")  # Log the error
        raise HTTPException(status_code=500, detail=str(e))