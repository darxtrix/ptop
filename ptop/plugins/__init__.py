'''
    List of sensors containing all the plugin objects
'''

from .cpu_sensor import cpu_sensor
from .disk_sensor import disk_sensor
from .memory_sensor import memory_sensor
from .process_sensor import process_sensor
from .system_sensor import system_sensor

# Sensors List
SENSORS_LIST = [
    cpu_sensor,
    disk_sensor,
    memory_sensor,
    process_sensor,
    system_sensor
]
