import pika 
import json 

class RabbitMQProducer:
    def __init__(self):
        self.__host="localhost"
        self.__port=5672
        self.__username="guest"
        self.__password="guest"
        self.__routingKey="minha_routing_key"
        self.__exchange="datas_exchanges"
        self.__channel=self.__create_channel()

    def __create_channel(self):
        connection_parameters = pika.ConnectionParameters(
        host=self.__host,
        port=self.__port,
        credentials=pika.PlainCredentials(
            username=self.__username,
            password=self.__password
        )
        )

        channel = pika.BlockingConnection(connection_parameters).channel()

        channel.exchange_declare(
            exchange=self.__exchange,
            exchange_type="direct",
            durable=True
        )

        return channel
    
    def send_menssage(self, body):
        self.__channel.basic_publish(
            exchange=self.__exchange,
            routing_key=self.__routingKey,
            body=json.dumps(body), 
            properties=pika.BasicProperties(
                delivery_mode=2
            )
        )

    def close_connection(self):
        if self.__channel:
            self.__channel.close()
        if self.__channel.connection:
            self.__channel.connection.close()
