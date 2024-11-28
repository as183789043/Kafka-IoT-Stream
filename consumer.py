from confluent_kafka import Consumer, KafkaError

c = Consumer({
    'bootstrap.servers': 'localhost:9092,localhost:9093,localhost:9094',
    'group.id': 'notification-group',
    'auto.offset.reset': 'earliest'
})

c.subscribe(['Sensor_1','Sensor_2','Sensor_3'])

try:
    while True:
        msg = c.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(msg.error())
                break
        print(f'Received message from topic {msg.topic()}: {msg.value().decode("utf-8")}')

except KeyboardInterrupt:
    pass

finally:
    c.close()
