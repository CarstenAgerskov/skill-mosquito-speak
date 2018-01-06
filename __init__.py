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

from mycroft.skills.core import intent_handler
from os.path import dirname
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
import paho.mqtt.client as mqtt
from multiprocessing import Manager
from ctypes import c_char_p
import uuid
import time

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

    def initialize(self):
        self.load_data_files(dirname(__file__))
        self.initialize_mqtt()

    def initialize_mqtt(self):
        self.host = self.settings.get("host")
        self.port = self.settings.get("port")
        self.topic = self.settings.get("topic")
        manager = Manager()
        self.uuid = manager.Value(c_char_p, str(uuid.uuid1()))
        self.last_message = manager.Value(c_char_p, "There is no last message")

        client = mqtt.Client()

        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.connect(self.host, str(self.port), 120)
        client.loop_start()

        time.sleep(1)
        client.publish(self.topic, "_starting " + self.uuid.value)

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe(self.topic)

    def on_message(self, client, userdata, msg):
        m = str(msg.payload)
        if m.startswith("_starting") and not m.endswith(self.uuid.value):
            client.loop_stop()
            client.disconnect()
#            self.speak("Mosquito speak disconnected")
            return
        if m.startswith("_starting"):
#            self.speak("Mosquito speak connected")
            return
        self.speak(m)
        self.last_message.value = m

    @intent_handler(IntentBuilder("RepeatLastMessageIntent").require("RepeatMessageKeyword").build())
    def repeat_last_message_intent(self):
        self.speak(self.last_message.value)

    def stop(self):
        pass


def create_skill():
    return MosquitoSpeak()
