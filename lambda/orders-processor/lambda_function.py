import json
import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
sns = boto3.client('sns', region_name='eu-north-1')

TABLE_NAME = 'orders-practica-final-uo275725'
SNS_TOPIC_ARN = 'arnawssnseu-north-1430165813080orders-notifications-uo275725'

def lambda_handler(event, context)
    print(EVENT, json.dumps(event))

    for record in event['Records']
        body = json.loads(record['body'])
        detail = body.get('detail', {})
        order_id = detail.get('orderId')
        items = detail.get('items', [])
        extras = detail.get('extras', [])
        notes = detail.get('notes', '')

        print(ORDER ID, order_id)

        if not order_id
            print(No orderId encontrado)
            continue

        table = dynamodb.Table(TABLE_NAME)
        table.update_item(
            Key={'orderId' order_id},
            UpdateExpression='SET #s = val',
            ExpressionAttributeNames={'#s' 'status'},
            ExpressionAttributeValues={'val' 'PROCESSED'}
        )
        print(DynamoDB actualizado)

        productos = 'n'.join([f  - {i.get('qty')}x {i.get('name')} ({i.get('price')}€) for i in items])
        total = sum(i.get('qty', 0)  i.get('price', 0) for i in items)
        extras_str = ', '.join(extras) if extras else 'Ninguno'

        mensaje = f¡Pedido confirmado! 🥙

ID del pedido {order_id}

Productos
{productos}

Extras {extras_str}
{f'Notas {notes}' if notes else ''}
Total {total.2f}€

¡Gracias por tu pedido en Kebab Palace!

        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=f'🥙 Pedido {order_id} confirmado',
            Message=mensaje
        )
        print(SNS enviado)

    return {'statusCode' 200}