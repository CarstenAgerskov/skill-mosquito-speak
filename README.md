## Mosquito Speak
Allow Mycroft to notify you on events, by speaking text received on a mqtt bus.
Send utterances to activate other mycroft skills, over mqtt.

## Description
This skill has two purposes:
1) Instead of triggering a skill by asking Mycroft a question, this skill triggers when a text message is received on mqtt.
It can be used for notifications. For instance, a smart home server could publish the text "Somebody is at the door", if the doorbell is pressed.
It is possible to make Mycroft repeat the last text it received on mqtt.

2) Send an utterance in text from mqtt, to activate other skills. For instance, if your
home automation detect that a window is opened, send the text "_utterance remind me to close the window in 10 minutes" on mqtt to
trigger the "reminder" skill.


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

## Installation
The best way to install mosquito speak is to use Mycroft. Say:

* "Hey Mycroft, install mosquito speak"

Or use [msm](https://mycroft.ai/documentation/msm/) from the command line.

When a new version of the Mycroft core is released, it may take some time
for the Mycroft team to accept the skill. It is verified that the Skill
still passes all tests and standards. During that time, the skill cannot
be installed using the methods above. Likewise, it may take some time
for emergency patches to pass the acceptance.

It is possible to install the skill directly from my repository instead,
risking the consequences of the skill not passing the acceptance by the
Mycroft team. And the skill will not auto update in case of new features
or bugfixes.

I maintain a numnber of branches, corresponding to the Mycroft version.

The following commands installs the skill manually, replace branch "origin/18.2.6b" below
with the branch that best corresponds to the mycroft core version you are running:
```
cd /opt/mycroft/skills/
git clone https://github.com/CarstenAgerskov/skill-mosquito-speak.git carstena-mosquito-speak
cd carstena-mosquito-speak/
git checkout origin/18.2.6b
```


Either install requirements on a Python 3 based Mycroft core
```
cd <your mycroft-core directory>
# When using bash/zsh use source as shown below, otherwise consult the venv documentation
source .venv/bin/activate
cd /opt/mycroft/skills/carstena-mosquito-speak/
pip install -r requirements.txt

```


Or install requirements on a Python 2 based Mycroft core
```
workon mycroft
pip install -r requirements.txt
```

Branch 18.2.6b, is for python 3 based Mycroft cores.

Branch master is for python 2 based Mycroft cores.

## Credits
Carsten Agerskov (https://github.com/CarstenAgerskov)
