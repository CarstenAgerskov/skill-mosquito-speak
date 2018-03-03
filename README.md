## Mosquito Speak
Allow Mycroft to notify you on events, by speaking text received on a mqtt bus.
Send utterances to activate other mycroft skills, over mqtt.

## Description
This skill has two purposes:
1) Instead of triggering a skill by asking Mycroft a question, this skill triggers when a text message is received on mqtt.
It can be used for notifications. For instance, a smart home server could publish the text "Somebody is at the door", if the doorbell is pressed.
It is possible to make Mycroft repeat the last text it received on mqtt.

2) Send an utterance in text from mqtt, to activate other skills. For instance, if your
home automation detect that a window is opened, send the text "remind me to close the window in 10 minutes" to
trigger the "reminder" skill.

And a warning: Due to the way this skill is implemented, it may stop working in case of a live update, under certain circumstances. A workaround is restarting the skill (or restarting Mycroft).
The problem only affects this skill. I am still looking for a solution to this.


### Configuration
The skill is configured on your "Mycroft Home" page. Configure the mqtt server, port and topic that the skill will listen for text messages on.
Currently, password or certificates are not supported. (Maybe I will implement it if you promise to test it :)

A restart of the skill is needed when changing the configuration.

Optionally, it is possible to split the text, using a regular expression.

Example CamelCase: If you send the string "KitchenWindow is open",
you want to split KitchenWindow. After the split Mycroft will say "Kitchen Window is open". To do that set the parameters on "Mycroft Home" like this:
* Split text at pattern (optional): [a-z][A-Z]
* Retain characters in matched string until index: 1
* Retain characters in matched string from index: 1

What happens: The regex match "nK" in "KitchenWindow is open". We retain the characters until index 1 of "nK", which is n.
We retain the characters after index 1 of "nK", which is K. And we put a space in the middle.

Example hypen: Convert "Outside-temperature is -5 degrees" to "Outside temperature is -5 degrees"
* Split text at pattern (optional): [a-z|A-Z]-[a-z|A-Z]
* Retain characters in matched string until index: 1
* Retain characters in matched string from index: 2

What happens: The regex match "e-t" in "Outside-temperature is -5 degrees".  We retain the characters until index 1 of "e-t", which is e.
We retain the characters after index 2 of "e-t", which is t. And we put a space in the middle.

Example underscore: Convert "Kitchen_window is open" to "Kitchen Window is open"
* Split text at pattern (optional): _
* Retain characters in matched string until index: 0
* Retain characters in matched string from index: 1

What happens: The regex match "_" in "Kitchen_window is open".  We retain the characters until index 0 of "_", which is no characters.
We retain the characters after index 1 of "_", which is no characters. And we put a space in the middle.


## Examples
For this example you must have a mqtt server named "mqttserver". And a configuration on mycroft home setting the server to "mqttserver", port to 1883, and topic to "my-out/text"
Example of notification:
* You, at a linux command prompt: mosquitto_pub -h mqttserver -t my-out/text -m "the washing machine is done"
* Mycroft: "the washing machine is done"
* You: "Hey Mycroft, what was the last mosquito message"
* Mycroft: "the washing machine is done"

To send text as if it was spoken, prepend the sentense with "_utterance"
Example of
* You, at a linux command prompt: mosquitto_pub -h mqttserver -t my-out/text -m "_utterance remind me to close the window in 10 minutes"
* Mycroft: "reminder set for 9 minute and 59 seconds from now"
After 10 minutes
* Mycroft: "you have a reminder to close the window"


## Credits
Carsten Agerskov (https://github.com/CarstenAgerskov)
