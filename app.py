from flask import Flask, render_template
from flask_socketio import SocketIO
import threading
import queue
from confluent_kafka import Consumer, KafkaError
import json

# 解耦合消息隊列
message_queue = queue.Queue()

# 狀態存儲
sensor_states = {
    "Sensor_1": None,
    "Sensor_2": None,
    "Sensor_3": None
}

# Kafka 消费者
def kafka_consumer():
    global sensor_states

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

            # 處理 Kafka 消息
            topic = msg.topic()
            message = json.loads(msg.value().decode('utf-8'))

            # 检查狀態是否有變化
            if sensor_states[topic] != message:
                sensor_states[topic] = message  # 更新狀態換存
                message_queue.put({"sensor": topic, "data": message})  # 推送更新到對列
    except KeyboardInterrupt:
        pass
    finally:
        c.close()

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

# 後台任務：推送 Kafka 更新到前端
def background_task():
    while True:
        if not message_queue.empty():
            update = message_queue.get()
            socketio.emit('sensor_update', update)  # 發送给前端
        socketio.sleep(1)

if __name__ == "__main__":
    kafka_thread = threading.Thread(target=kafka_consumer)
    kafka_thread.daemon = True
    kafka_thread.start()

    socketio.start_background_task(background_task)
    socketio.run(app,host='0.0.0.0')
