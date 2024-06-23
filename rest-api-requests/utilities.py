
import os
from dotenv import load_dotenv
import pika
import json
import io

from minio import Minio
from minio.error import S3Error



def initialize_rabbitmq_connection():
    """Initialize and return a RabbitMQ connection."""
    credentials = pika.PlainCredentials(os.getenv('RABBITMQ_DEFAULT_USER'), os.getenv('RABBITMQ_DEFAULT_PASS'))
    rabbitmq_host = os.getenv('RABBITMQ_HOST')
    rabbitmq_port = os.getenv('RABBITMQ_PORT')
    parameters = pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    return connection


def publish_to_rabbitmq(event_payload, connection, queue_name):
    """Send event payload message to RabbitMQ."""
    try:
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)
        message = json.dumps(event_payload)
        channel.basic_publish(exchange='', routing_key=queue_name, body=message)
        print(f"Message sent to RabbitMQ: {message}")
        connection.close()
    except Exception as e:
        print(f"Failed to send message to RabbitMQ: {e}")
        
        
        
def save_to_minio(data):
    minio_client = Minio(
        os.getenv("MINIO_HOST"), 
        access_key=os.getenv("MINIO_BUCKET_ACCESS_KEY"), 
        secret_key=os.getenv("MINIO_BUCKET_SECRET_KEY"), 
        secure=False
        )
    object_name = f"{data['device_id']}/{data['timestamp']}.json"
    data_bytes = json.dumps(data).encode('utf-8')
    data_stream = io.BytesIO(data_bytes)

    try:
        minio_client.put_object(
            bucket_name=os.getenv("BUCKET_NAME"),
            object_name=object_name, 
            data=data_stream, 
            length=len(data_bytes),
            content_type='application/json')
        print(f"Data saved to MinIO: {object_name}")
    except S3Error as err:
        print(f"Failed to save data to MinIO: {err}")
        


def consume_and_save():
    connection = initialize_rabbitmq_connection()

    channel = connection.channel()

    channel.queue_declare(queue=os.getenv("RABBITMQ_QUEUE"), durable=True)
    
    method_frame, header_frame, body = channel.basic_get(os.getenv("RABBITMQ_QUEUE"))

    if method_frame:
        data = json.loads(body.decode('utf-8'))
        print(data)
        save_to_minio(data)
        channel.basic_ack(method_frame.delivery_tag)
        return {"message": "Data consumed and saved to MinIO.", "data": data}
    else:
        return {"message": "No messages in the queue."}