

from gpiozero import DistanceSensor

sensor = DistanceSensor(echo=24, trigger=23, max_distance=200.0 / 100.0)

while True:
    print("trying to get distance")
    print(sensor.distance * 100.0)
