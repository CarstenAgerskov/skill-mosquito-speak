"""
skill mosquito-speak
Copyright (C) 2017  Carsten Agerskov

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from mycroft import intent_file_handler
from os.path import dirname
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
import paho.mqtt.client as mqtt
from multiprocessing import Manager
from ctypes import c_char_p
import uuid
import time
import re
import os
from websocket import create_connection, WebSocketTimeoutException
from mycroft.configuration import Configuration
from mycroft.messagebus.message import Message
from mycroft.util.log import LOG
from mycroft.api import DeviceApi

MOSQUITO_SPEAK_ID = "MOSQUITO_SPEAK_ID"

__author__ = 'cagerskov'

LOGGER = getLogger(__name__)


class MosquitoSpeak(MycroftSkill):
    def __init__(self):
        super(MosquitoSpeak, self).__init__(name="MosquitoSpeak")
        self.host = None
        self.port = None
        self.topic = None
        self.uuid = None
        self.last_message = None
        self.splitRegex = None
        self.retainFirst = None
        self.retainLast = None

    @property
    def device_name(self):
        # assume the "name" of the device is the "room name"
        device = DeviceApi().get()
        return device['name'].replace(' ', '_')

    def initialize(self):
        self.load_data_files(dirname(__file__))
        self.__init_client()
        self.__init_mqtt()

    def __init_mqtt(self):
        self.host = self.settings.get("host")
        self.port = self.settings.get("port")
        self.topic = self.settings.get("topic")
        self.splitRegex = self.settings.get("splitRegex")
        self.retainFirst = self.settings.get("retainFirst")
        self.retainLast = self.settings.get("retainLast")
        manager = Manager()
        self.uuid = manager.Value(c_char_p, str(uuid.uuid1()))
        self.last_message = manager.Value(c_char_p, "There is no last message")

        if not os.environ.get(MOSQUITO_SPEAK_ID):
            os.environ[MOSQUITO_SPEAK_ID] = str(uuid.uuid1())
            LOG.info("Getting new uuid")
        else:
            LOG.info("Reusing uuid")

        self.my_id = os.environ.get(MOSQUITO_SPEAK_ID)
        LOG.info(str("UUID is " + self.my_id))

        try:
            client = mqtt.Client(
                'mycroft_' + self.device_name)  # use self.device_name from home.mycroft.ai to provide a unique device name
            LOG.info("MQTT client named: mycroft_" + self.device_name)
        except Exception:
            client = mqtt.Client()
            LOG.info("MQTT client auto named")

        client.connect(self.host, str(self.port), 120)
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.loop_start()

        time.sleep(1)
        client.publish(self.topic, "_starting " + self.my_id + " " + self.uuid.value)

    def __init_client(self):
        config = Configuration.get().get("websocket")

        host = config.get('host')
        port = config.get('port')

        uri = 'ws://' + host + ':' + str(port) + '/core'
        self.ws = create_connection(uri)

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe(self.topic)

    def on_message(self, client, userdata, msg):
        try:
            m = str(msg.payload)
            if m.startswith("_starting"):
                p = m.split(" ")

                if len(p) == 3 and p[1] == self.my_id and p[2] != self.uuid.value:
                    client.loop_stop()
                    client.disconnect()
                    LOG.info("Stopping old callback")
                    return
                LOG.info("Starting new callback")
                return

            if m.startswith("_utterance") and len(m.split(" ", 1)) > 1:
                m = Message("recognizer_loop:utterance", {"lang": "en-us", "utterances": [m.split(" ", 1)[1]]})
                self.ws.send(m.serialize())
                return

            if self.splitRegex:
                m = re.sub(self.splitRegex, lambda x: x.group(0)[0:int(self.retainFirst)] +
                                                      ' ' + x.group(0)[int(self.retainLast):], m)
            self.speak(m)
            self.last_message.value = m

        except Exception as e:
            LOG.error("Error: {0}".format(e))

    @intent_file_handler('RepeatLastMessage.intent')
    def repeat_last_message_intent(self):
        self.speak(self.last_message.value)

    def stop(self):
        pass


def create_skill():
    return MosquitoSpeak()
