## Mosquito Speak
Allow Mycroft to notify you on events, by speaking text received on a mqtt bus. 

## Description
Instead of triggering a skill by asking Mycroft a question, this skill triggers when a text message is received on mqtt.
It can be used for notifications. For instance, a smart home server could publish the text "Somebody is at the door", if the doorbell is pressed.
It is possible to make Mycroft repeat the last text it received on mqtt.

### Configuration
The skill is configured on your "Mycroft Home" page. Configure the mqtt server, port and topic that the skill will listen for text messages on.
Currently, password or certificates are not supported. (Maybe I will implement it if you promise to test it :)

## Examples
For this example you must have a mqtt server named "mqttserver". And a configuration on mycroft home setting the server to "mqttserver", port to 1883, and topic to "my-out/text"
* You, at a linux command prompt: mosquitto_pub -h mqttserver -t my-out/text -m "the washing machine is done"
* Mycroft: "the washing machine is done"
* You: "Hey Mycroft, repeat the last mosquito message"
* Mycroft: "the washing machine is done"

## Credits
Carsten Agerskov (https://github.com/CarstenAgerskov)
