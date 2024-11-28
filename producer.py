from confluent_kafka import Producer
import random
import datetime
import json 

p = Producer({'bootstrap.servers': 'localhost:9092,localhost:9093,localhost:9094'})

#deliver kafaka function
def delivery_report(err, msg):
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

def send_notification(topic, payload):
    p.produce(topic, payload.encode('utf-8'), callback=delivery_report)
    p.poll(0)

    print(f'Message sent to {topic}: {payload}')

# deliver payload function
def random_topic():
    topic_list=['Sensor_1','Sensor_2','Sensor_3']
    return random.choice(topic_list)

    
def iso_time():
    now = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=8)))
    return now.isoformat()

def random_value():
    value=random.randint(0,100)
    return value



# 生成傳感器的 payload
def generate_sensor_payload():
    payload = {
        "Battery": f"{random_value()}",
        "Temperature": f"{random_value()}",
        "Humidity": f"{random_value()}",
        "Timestamp": iso_time()
    }
    return json.dumps(payload)  

#生成隨機數據
if __name__ == "__main__":
    topic = random_topic()
    payload = generate_sensor_payload()
    send_notification(topic, payload)

    # 確保消息發送
    p.flush()