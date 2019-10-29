import json
import os
import uuid
import logging
import boto3

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

def main(event, context):
    LOG.info("EVENT: " + json.dumps(event))
    
    query_string_params = event["queryStringParameters"]
    if query_string_params is not None:
        target_url = query_string_params['targetUrl']
        if target_url is not None:
            return create_short_url(event)
    
    path_parameters = event['pathParameters']
    if path_parameters is not None:
        if path_parameters['proxy'] is not None:
            return read_short_url(event)
            
    return {
        'statusCode': 200,
        'body': 'usage: ?targetUrl=URL'
    }
    
def create_short_url(event):
    table_name = os.environ.get('TABLE_NAME')
    
    target_url = event["queryStringParameters"]['targetUrl']
    id = str(uuid.uuid4())[0:8]
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    table.put_item(
        Item = {
            'id': id,
            'target_url': target_url
        }
    )
    
    url = ''.join(["http://",event["requestContext"]["domainName"],event["requestContext"]["path"],'/',str(id)]) \
        if event["requestContext"]["path"][-1] != '/' else \
        ''.join(["http://",event["requestContext"]["domainName"],event["requestContext"]["path"],str(id)])
    
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/plain'},
        'body': "Created URL: %s" % url
    }
    
def read_short_url(event):
    id = event['pathParameters']['proxy']
    
    table_name = os.environ.get('TABLE_NAME')
    
    ddb = boto3.resource('dynamodb')
    table = ddb.Table(table_name)
    response = table.get_item(Key={'id': id})
    LOG.debug("RESPONSE: " + json.dumps(response))
    
    item = response.get('Item', None)
    if item is None:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'text/plain'},
            'body': 'No redirect found for ' + id
        }
    
    return {
        'statusCode': 301,
        'headers': {
            'Location': item.get('target_url')
        }
    }
    
    
    
    