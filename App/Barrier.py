#!/usr/bin/python3

import logging, os, time, json, queue, datetime, threading, mariadb
import paho.mqtt.client as mqtt

# Set logging settings
logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S")

# Define Message Queue
message_queue = queue.Queue()

# Define Barrier Class
class Barrier:

    class Info: # Info sbuclass

        def __init__(self, barrier_id, name, latitude, longitude, firmware, software, modem, ip, fqdn):
            self.barrier_id = barrier_id
            self.name = name
            self.latitude = latitude
            self.longitude = longitude
            self.firmware = firmware
            self.software = software
            self.modem = modem
            self.ip = ip
            self.fqdn = fqdn
            self.last_update = str(datetime.datetime.now().isoformat(timespec='seconds'))

        def changed_info(self, sql_client): # Method that return list of changed value(s) between os env vs in app value
            changed_info = False
            sql_cursor = sql_client.cursor()
            sql_cursor.execute("select * from barrier where id = (%s)", (f"{self.barrier_id}",))
            barrier_values = sql_cursor.fetchone()
            cpt = 0
            for attr_name, attr_value in self.__dict__.items():
                if f"{attr_name}" != f"last_update":
                    if f"{attr_value}" != f"{barrier_values[cpt]}":
                        logging.info(f"{attr_value} is different than {barrier_values[cpt]}")
                        setattr(self, attr_name, f"{barrier_values[cpt]}")
                        changed_info = True
                    cpt +=1
            sql_cursor.close()
            return changed_info

    class Status: #Status subclass

        def __init__(self, position, temperature, signal):
            self.position = position
            self.temperature = temperature
            self.signal = signal
            self.last_update = str(datetime.datetime.now().isoformat(timespec='seconds'))

        def get_status(self): # Method that send status of class Barrier
            return json.dumps(self.__dict__)

    def __init__(self, barrier_id, name, latitude, longitude, firmware, software, modem, ip, fqdn, position, temperature, signal):
        self.info = self.Info(barrier_id, name, latitude, longitude, firmware, software, modem, ip, fqdn)
        self.status = self.Status(position, temperature, signal)

    def open(self): # Method that open barrier
        if self.status.position == "closed":
            self.status.position = "opened"
        else:
            logging.info(f"{self.name} is already opened")

    def close(self): # Method that close barrier
        if self.status.position == "opened":
            self.status.position = "closed"
        else:
            logging.info(f"{self.name} is already closed")

def on_connect(client, userdata, flags, rc, props=None): # Function that subscribe to a topic
    if rc == 0:
        logging.info(f"Connected to MQTT Broker")
        client.subscribe(f"barrier/commands/{barrier.info.name}")
        logging.info(f"Subscribed to topic barrier/commands/{barrier.info.name}")
    else:
        logging.info(f"Failed to connect, return code {rc}")
        quit()

def on_message(client, userdata, msg): # Function that return message received in subscribed topic
    try:
        json_payload = msg.payload.decode('utf-8')
        message_queue.put(json_payload)
    except json.JSONDecodeError:
        logging.info(f"Error: Received message is not valid JSON: {msg.payload.decode('utf-8', errors='ignore')}")
    except Exception as e:
        logging.info(f"An error occurred: {e}")

def publish_status(client): # Function that send status of barrier
    barrier.status.last_update = str(datetime.datetime.now().isoformat(timespec='seconds'))
    client.publish(f"barrier/{barrier.info.name}", barrier.status.get_status(), qos=1)

def thread_status(mqtt_client): # Thread for updating barrier status every 60 seconds
    while True:
        publish_status(mqtt_client)
        time.sleep(60)

def publish_info(mqtt_client, sql_client): # Function that send info of barrier
    barrier = init_barrier(sql_client)
    for attr_name, attr_value in barrier.info.__dict__.items():
        mqtt_client.publish(f"barrier/{barrier.info.name}/{attr_name}", f"{attr_value}", qos=1)

def thread_info(mqtt_client, sql_client): # Thread for updating barrier infos every 15 minutes
    while True:
        publish_info(mqtt_client, sql_client)
        time.sleep(900)

def main_loop(sql_client, mqtt_client): # Main program loop logic
    while True:
        if barrier.info.changed_info(sql_client):
            publish_info(mqtt_client, sql_client)
        if not message_queue.empty():
            command = message_queue.get()
            match f"{command}":
                case "open":
                    barrier.open()
                    publish_status(mqtt_client)
                case "close":
                    barrier.close()
                    publish_status(mqtt_client)
                case _:
                    logging.info(f"Command {command} is not defined, defined commands are open or close")
        time.sleep(1)

def mysql_connect():
    try:
        sql_client = mariadb.connect(
                user=f"{os.environ.get('db_user')}"",
                password=f"{os.environ.get('db_password')}",
                host=f"{os.environ.get('db_host')}",
                database=f"{os.environ.get('bd_name')}",
                autocommit=True)
        return sql_client
    except mariadb.Error as e:
        logging.info(f"Error connecting to MariaDB Platform: {e}")
        quit()

def init_barrier(sql_client): # Function that initialize barrier
    sql_cursor = sql_client.cursor()
    sql_cursor.execute ("select * from barrier where name = (%s)", (os.environ.get(f"name"),))
    barrier_values = sql_cursor.fetchone()
    barrier = Barrier(f"{barrier_values[0]}", f"{barrier_values[1]}", f"{barrier_values[2]}", f"{barrier_values[3]}",
                      f"{barrier_values[4]}", f"{barrier_values[5]}", f"{barrier_values[6]}", f"{barrier_values[7]}",
                      f"{barrier_values[8]}", f"{os.environ.get('position')}", f"{os.environ.get('temperature')}",
                      f"{os.environ.get('signal')}")
    sql_cursor.close()
    return barrier

# Main
if __name__ == "__main__":
    sql_client = mysql_connect()
    barrier = init_barrier(sql_client)
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(f"{os.environ.get('mqtt_host')}", 1883)
    thread_info = threading.Thread(target=thread_info, args=(mqtt_client, sql_client,), daemon=True)
    thread_status = threading.Thread(target=thread_status, args=(mqtt_client,), daemon=True)
    thread_info.start()
    thread_status.start()
    mqtt_client.loop_start()
    try:
        main_loop(sql_client, mqtt_client)
    except KeyboardInterrupt:
        thread_info.stop()
        thread_status.stop()
        mqtt_client.loop_stop() # Stop the loop gracefully
        mqtt_client.disconnect()
        sql_client.close()
