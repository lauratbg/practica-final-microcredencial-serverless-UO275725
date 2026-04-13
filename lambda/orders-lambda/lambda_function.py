import json
import boto3
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
eventbridge = boto3.client('events', region_name='eu-north-1')

TABLE_NAME = 'orders-practica-final-uo275725'

def lambda_handler(event, context):
    print("EVENT RECIBIDO:", json.dumps(event))
    method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method')

    if method == 'POST':
        body = json.loads(event.get('body') or '{}')

        # ID corto: primer kebab del pedido + 6 caracteres random
        items = body.get('items', [])
        if items:
            first_name = items[0].get('name', 'kebab').lower().replace(' ', '-')
        else:
            first_name = 'kebab'
        short_id = str(uuid.uuid4())[:6]
        order_id = f"{first_name}-{short_id}"

        table = dynamodb.Table(TABLE_NAME)
        table.put_item(Item={
            'orderId': order_id,
            'status': 'PENDING',
            'data': json.dumps(body),
            'createdAt': datetime.utcnow().isoformat()
        })

        eventbridge.put_events(Entries=[{
            'Source': 'tienda.orders',
            'DetailType': 'order.created',
            'Detail': json.dumps({'orderId': order_id, **body}),
            'EventBusName': 'default'
        }])

        return {
            'statusCode': 201,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'orderId': order_id, 'status': 'PENDING'})
        }

    if method == 'GET':
        path_params = event.get('pathParameters') or {}
        order_id = path_params.get('id')

        table = dynamodb.Table(TABLE_NAME)
        result = table.get_item(Key={'orderId': order_id})

        if 'Item' not in result:
            return {'statusCode': 404, 'body': json.dumps({'error': 'Order not found'})}

        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'orderId': result['Item']['orderId'],
                'status': result['Item']['status']
            })
        }

    return {'statusCode': 400, 'body': json.dumps({'error': 'Method not supported'})}