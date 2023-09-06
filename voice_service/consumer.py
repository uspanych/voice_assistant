import json
import base64
import pika
from worker import func

credentials = pika.PlainCredentials('user', '2302')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost', credentials=credentials)
)

channel = connection.channel()
channel.exchange_declare(exchange='topic_v1', exchange_type='topic')
channel.queue_bind(
    exchange='topic_v1', queue='events.files'
)


def callback(ch, method, properties, body):
    """Сделал функцию, с целью получения сообщения и тестирования celery с моделью, лучше
    тут навести красоту по твоему усмотрению.
    """

    decode_body = json.loads(body.decode())

    file = base64.b64decode(decode_body.get('file'))
    # the following code will delete the message from the queue
    ch.basic_ack(delivery_tag=method.delivery_tag)

    func(file)


channel.basic_consume(on_message_callback=callback, queue='events.files')
print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
