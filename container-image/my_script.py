import sys
import os
print ("Variables de entrada:",sys.argv[1:])
print ("Variables de entorno:", os.environ)

import boto3

region_name = os.environ.get('REGION')
hostname = os.environ.get('HOSTNAME')
queue_name = os.environ.get('QUEUE_NAME')
account_id = os.environ.get('AWS_ACCOUNT_ID')


sqs = boto3.client('sqs', region_name=region_name)

queue_url = "https://sqs.{}.amazonaws.com/{}/{}".format(region_name, account_id, queue_name)

msgs = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10)

if not("Messages" in msgs):
    print('No hay mensajes en la cola!')


print ("mensajes:", msgs['Messages'])

for message in msgs['Messages']:
    print ("mensaje:", message['Body'], end=' ')
    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=message['ReceiptHandle']
    )
    print ('borrado')

