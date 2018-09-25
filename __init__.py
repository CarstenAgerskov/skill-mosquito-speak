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

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from mycroft import intent_file_handler
from mycroft.skills.core import MycroftSkill
import paho.mqtt.client as mqtt
import re
from mycroft.messagebus.message import Message
from mycroft.util.log import LOG

__author__ = 'cagerskov'

try:
    client
    LOG.info('Client exist')
    client.loop_stop()
    client.disconnect()
    LOG.info('Stopped old client loop')
except NameError:
    client = mqtt.Client()
    LOG.info('Client created')


class MosquitoSpeak(MycroftSkill):
    def __init__(self):
        super(MosquitoSpeak, self).__init__(name='MosquitoSpeak')
        self.host = None
        self.port = None
        self.topic = None
        self.uuid = None
        self.last_message = None
        self.splitRegex = None
        self.retainFirst = None
        self.retainLast = None
        self.loop_succeeded = False

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe(self.topic)
        if rc == 0:
            LOG.info('Connected to ' + self.topic)
        else:
            LOG.error('Connection to ' + self.topic +
                      ' failed, error code ' + rc)

    def on_message(self, client, userdata, msg):
        try:
            m = msg.payload.decode('utf-8')

            if m.startswith('_utterance') and len(m.split(' ', 1)) > 1:
                self.emitter.emit(
                    Message('recognizer_loop:utterance',
                            {'lang': 'en-us',
                             'utterances': [m.split(' ', 1)[1]]}))

                return

            if self.splitRegex:
                m = re.sub(self.splitRegex, lambda x:
                    x.group(0)[0:int(self.retainFirst)] +
                    ' ' + x.group(0)[int(self.retainLast):], m)
            self.speak(m)
            self.last_message = m

        except Exception as e:
            LOG.error('Error: {0}'.format(e))

    def initialize(self):
        self.host = self.settings.get('host')
        self.port = int(self.settings.get('port'))
        self.topic = self.settings.get('topic')
        self.splitRegex = self.settings.get('splitRegex')
        self.retainFirst = self.settings.get('retainFirst')
        self.retainLast = self.settings.get('retainLast')
        self.last_message = 'There is no last message'
        self.loop_succeeded = False

        client.on_connect = self.on_connect
        client.on_message = self.on_message
        try:
            LOG.info("Connecting to host " + self.host + " on port " + str(self.port))
            client.connect_async(self.host, self.port, 60)
            client.loop_start()
            self.loop_succeeded = True
        except Exception as e:
            LOG.error('Error: {0}'.format(e))

    @intent_file_handler('RepeatLastMessage.intent')
    def repeat_last_message_intent(self):
        self.speak(self.last_message)

        if not self.loop_succeeded:
            self.speak_dialog('not_configured')

    def stop(self):
        pass


def create_skill():
    return MosquitoSpeak()
