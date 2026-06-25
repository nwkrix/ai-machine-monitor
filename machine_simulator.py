#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 19:49:53 2026

@author: Christian Nwachioma
"""
import random
import time
import csv
from datetime import datetime


class MachineSimulator:
    def __init__(self):
        # Normal operating ranges
        self.temperature = 65.0       # Celsius
        self.vibration = 0.02         # mm/s
        self.pressure = 100.0         # PSI
        self.motor_current = 12.0     # Amps
        self.cycle_time = 5.0         # seconds

        self.machine_health = 100
        self.fault_state = "NORMAL"


    def generate_temperature(self):
        base = 65
        
        if self.machine_health < 70: 
            base += 20
        
        self.temperature = ( 
            base + random.uniform(-2,2)
        )
        return round(self.temperature,2)
    
    
    def generate_vibration(self):
        base = 0.02
        if self.machine_health < 70:
            base = 0.15

        self.vibration = (
            base +
            random.uniform(-0.01,0.01)
        )
        
        return round(max(self.vibration,0),4)


    def generate_pressure(self):
        noise = random.uniform(-1, 1)

        if self.machine_health < 60:
            noise += random.uniform(-5, 5)

        self.pressure += noise

        return round(self.pressure, 2)


    def generate_motor_current(self):
        noise = random.uniform(-0.2, 0.2)

        if self.machine_health < 70:
            noise += random.uniform(0.5, 2)

        self.motor_current += noise

        return round(self.motor_current, 2)


    
    def generate_cycle_time(self): 
        base = 5.0
        
        if self.machine_health < 70: 
            base += 1.5
            
        self.cycle_time = (
            base +
            random.uniform(-0.3,0.3)
        )

        return round(self.cycle_time,2)


    def inject_fault(self):
        
        if self.machine_health < 100:
            self.machine_health += 0.02

        # Random degradation event
        #if random.random() < 0.02:
        if random.random() < 0.005:
            self.machine_health -= random.randint(5, 15)

        if self.machine_health < 50:
            self.fault_state = "CRITICAL"

        elif self.machine_health < 75:
            self.fault_state = "WARNING"

        else:
            self.fault_state = "NORMAL"


    def generate_fault_code(self):

        if self.fault_state == "NORMAL":
            return "NONE"

        elif self.fault_state == "WARNING":
            return random.choice([
                "TEMP_HIGH",
                "VIBRATION_RISE",
                "CURRENT_SPIKE"
            ])

        else:
            return random.choice([
                "MOTOR_FAILURE",
                "OVERHEAT",
                "PRESSURE_LOSS",
                "BEARING_DAMAGE"
            ])


    def read_sensors(self):

        self.inject_fault()

        data = {
            "timestamp": datetime.now(),

            "temperature_C":
                self.generate_temperature(),

            "vibration_mm_s":
                self.generate_vibration(),

            "pressure_PSI":
                self.generate_pressure(),

            "motor_current_A":
                self.generate_motor_current(),

            "cycle_time_s":
                self.generate_cycle_time(),

            "machine_health":
                self.machine_health,

            "fault_code":
                self.generate_fault_code(),

            "status":
                self.fault_state
        }

        return data



# ------------------------------------------------
# Generate simulated machine telemetry
# ------------------------------------------------

if __name__ == "__main__":

    machine = MachineSimulator()

    filename = "machine_data.csv"


    with open(filename, "w", newline="") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "timestamp",
                "temperature_C",
                "vibration_mm_s",
                "pressure_PSI",
                "motor_current_A",
                "cycle_time_s",
                "machine_health",
                "fault_code",
                "status"
            ]
        )

        writer.writeheader()


        for i in range(1000):

            sensor_data = machine.read_sensors()

            writer.writerow(sensor_data)

            print(sensor_data)

            time.sleep(0.1)


    print("\nSimulation complete")
    print(f"Generated {filename}")
