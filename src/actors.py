from thespian.actors import Actor, ActorSystem


class BellBoy(Actor):
    def receiveMessage(self, message, sender):
        print(f"BellBoy got message {message}")
        if "start" in message:
            self.startBellboyServices()

    def startBellboyServices(self):
        """Starts all other BellBoy system actors."""
        gui = self.createActor(StatusWebGUI)
        self.send(gui, "start")

        sensor = self.createActor(Sensor)
        self.send(sensor, "start")


class StatusWebGUI(Actor):
    def receiveMessage(self, message, sender):
        print(f"StatusWebGUI got message {message}")


class Sensor(Actor):
    def receiveMessage(self, message, sender):
        print(f"Sensor got message {message}")


system = ActorSystem().createActor(BellBoy)
ActorSystem().tell(system, "start")
