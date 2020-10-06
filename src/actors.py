from datetime import timedelta
from time import sleep

from thespian.actors import Actor, ActorSystem

# https://github.com/malefs/security-smell-detector-python-gist/blob/e90764deb06ae4d3c45e702db7ad00351520348f/gist-hash/b51a9cabd41edae990fd6e844f10ef8e/snippet.py


class BellBoy(Actor):
    def receiveMessage(self, message, sender):
        print(f"BellBoy got message {type(message)}")
        if type(message) is str and "start" in message:
            self.startBellboyServices()
        if type(message) is str and "heartbeat" in message:
            print("Got heartbeat message...")
        else:
            self.wakeupAfter(timedelta(seconds=1), "wakeup")

    def startBellboyServices(self):
        """Starts all other BellBoy system actors."""
        gui = self.createActor(StatusWebGUI)
        self.send(gui, "start")

        sensor = self.createActor(Sensor)
        self.send(sensor, "start")


class StatusWebGUI(Actor):
    def receiveMessage(self, message, sender):
        print(f"StatusWebGUI got message {type(message)}")


class Sensor(Actor):
    def receiveMessage(self, message, sender):
        print(f"Sensor got message {type(message)}")


if __name__ == "__main__":
    # Start each actor in its own process.
    system = ActorSystem("multiprocQueueBase")
    bellboy = system.createActor(BellBoy)
    system.tell(bellboy, "start")
    try:
        while True:
            sleep(2)
    finally:
        system.shutdown()
