# Make sure to have the server side running in V-REP:
# in a child script of a V-REP scene, add following command
# to be executed just once, at simulation start:
#
# simExtRemoteApiStart(19999)
# then start simulation, and run this program.
#
# IMPORTANT: for each successful call to simxStart, there
# should be a corresponding call to simxFinish at the end!
import math
import random
import time

import Lab1_Agents_Task1_World as World

# connect to the server
robot = World.init()
# print important parts of the robot
print(sorted(robot.keys()))
motorSpeed = dict(speedLeft=0, speedRight=0)


def default_agent(simulationTime):
    global motorSpeed
    motorSpeed = dict(speedLeft=0, speedRight=0)

    if simulationTime < 5000:
        motorSpeed = dict(speedLeft=1, speedRight=1.5)
    elif simulationTime < 10000:
        motorSpeed = dict(speedLeft=-1.5, speedRight=-1.0)
    elif simulationTime < 15000:
        print("Turning for a bit...", )
        World.execute(dict(speedLeft=2, speedRight=-2), 15000, -1)
        print("... got dizzy, stopping!")
        print("BTW, nearest energy block is at:", World.getSensorReading("energySensor"))

    return motorSpeed


def random_agent(runTime):
    global motorSpeed
    frontSensor = World.getSensorReading("ultraSonicSensorFront")

    # Spin randomly to give it a random direction every 3 seconds
    if int(runTime) % 3 == 0:
        speed = random.random() * 10 - 5  # This is a random number between -5 and 5
        World.execute(dict(speedLeft=speed, speedRight=-speed), -1, random.random())

    # If the robot is too close to the wall, turn away from it
    threshold = 0.2
    if frontSensor < threshold:
        speed = random.getrandbits(1) * 2 - 1  # This is either 1 or -1
        World.execute(dict(speedLeft=-speed, speedRight=speed), 2450 * 2 / 3, -1)
    # March in that direction
    speed = random.random() * 3 + 2  # Random number between 3 and 5 or -3 and -5
    motorSpeed = dict(speedLeft=speed, speedRight=speed)


ctrStart = 0


# Giving it a global variable could be seen as "memory"
# But I'm too lazy to do modules on simulationTime.
# It's just a lazy way of making it re-do everything
def fixed_agent(simulationTime):
    global motorSpeed, ctrStart
    ctr = simulationTime - ctrStart

    # The following sequence of moves guarantees at least 2 energy blocks
    # It doesn't care after that, it just re-runs everything
    if ctr < 28000:
        motorSpeed = dict(speedLeft=2, speedRight=2)
    elif ctr < 55000:
        motorSpeed = dict(speedLeft=-0.1, speedRight=0.1)
    elif ctr < 80000:
        motorSpeed = dict(speedLeft=2, speedRight=2)
    elif ctr < 100000:
        # Crash into the corner
        motorSpeed = dict(speedLeft=0.7, speedRight=0.6)
    else:
        ctrStart = simulationTime  # Reset the counter


def reflex_agent(simulationTime):
    global motorSpeed

    # Get the sensor readings
    rightSensor = World.getSensorReading("ultraSonicSensorRight")
    leftSensor = World.getSensorReading("ultraSonicSensorLeft")

    # If the robot is too close to the wall, turn away from it
    threshold = 0.2
    if rightSensor < threshold or leftSensor < threshold:
        World.execute(dict(speedLeft=-1, speedRight=-1), 500, -1)
        if rightSensor < leftSensor:
            World.execute(dict(speedLeft=-1, speedRight=1), 2450 / 1, -1)
        else:
            World.execute(dict(speedLeft=1, speedRight=-1), 2450 / 1, -1)

    energySensor = World.getSensorReading("energySensor")
    # is the energy block on the wrong side of the wall?
    energyOnWrongSide = False
    if leftSensor < energySensor.distance and energySensor.direction < 0:
        energyOnWrongSide = True
    elif rightSensor < energySensor.distance and energySensor.direction > 0:
        energyOnWrongSide = True

    # This is the field of view of the robot
    # If the energy block is too far away, don't chase it
    if abs(energySensor.direction) > math.pi / 1.9 or energySensor.distance > 2.3 or energyOnWrongSide:
        wiggle_room = 0.5
        motorSpeed = dict(speedLeft=random.uniform(2 - wiggle_room, 2 + wiggle_room), speedRight=random.uniform(2 - wiggle_room, 2 + wiggle_room))
        return

    threshold = 0.25
    # If all these check, go in the direction of the energy block
    if energySensor.direction > threshold:
        motorSpeed = dict(speedLeft=2, speedRight=1.5)
    elif energySensor.direction < -threshold:
        motorSpeed = dict(speedLeft=1.5, speedRight=2)
    else:
        motorSpeed = dict(speedLeft=2, speedRight=2)


counter = 0
counterStart = 0
stuck = False
def memory_agent(simulationTime, runTime):
    global motorSpeed, counter, stuck, counterStart

    counter = runTime - counterStart

    if not stuck:
        reflex_agent(simulationTime)

    timeUntilStuck = 45
    # The robot took too long to get to the energy block
    if counter > timeUntilStuck and not stuck:
        print('I\'m stuck')
        stuck = True

    stuckTime = 15
    if stuck and counter < timeUntilStuck + stuckTime:
        random_agent(runTime)
    elif stuck:
        print('I\'m not stuck')
        counterStart = runTime
        stuck = False


energyTaken = 0
wallHits = 0
resultCounterStart = 0
timeStart = time.time()


ENDGAME = False
while robot and not ENDGAME:  # main Control loop
    #######################################################
    # Perception Phase: Get information about environment #
    #######################################################
    runtime = time.time() - timeStart
    simulationTime = World.getSimulationTime()
    # if simulationTime % 1000 == 0:
    # print some useful info, but not too often
    # print('Time:', simulationTime, 'ultraSonicSensorLeft:', World.getSensorReading("ultraSonicSensorLeft"),
    #       "ultraSonicSensorRight:", World.getSensorReading("ultraSonicSensorRight"))

    ##############################################
    # Reasoning: figure out which action to take #
    ##############################################

    # ******CHOOSE AN AGENT HERE****** #
    # default_agent(simulationTime)
    # random_agent(runtime)
    # fixed_agent(simulationTime)
    # reflex_agent(simulationTime)
    memory_agent(simulationTime, runtime)

    # The following code calculates how many times the robot hits the wall
    # If the sensors are too close to the wall for too long, it counts as a wall hit
    resultCounter = runtime - resultCounterStart
    rightSensor = World.getSensorReading("ultraSonicSensorRight")
    leftSensor = World.getSensorReading("ultraSonicSensorLeft")
    frontSensor = World.getSensorReading("ultraSonicSensorFront")
    threshold = 0.2
    if rightSensor < threshold or leftSensor < threshold or frontSensor < threshold:
        if resultCounter > 2:   # If it's been too long, it's a wall hit
            wallHits += 1
            resultCounterStart = runtime
    else:
        resultCounterStart = runtime    # Reset the counter

    ########################################
    # Action Phase: Assign speed to wheels #
    ########################################
    # assign speed to the wheels
    World.setMotorSpeeds(motorSpeed)
    # try to collect energy block (will fail if not within range)
    energy_dist = World.getSensorReading("energySensor").distance
    if energy_dist <= 0.5:
        if World.collectNearestBlock() == 'Energy collected :)':
            print('Energy collected :)')
            energyTaken += 1
            counterStart = runtime
            stuck = False
        else:
            print("Energy not collected :(")
    # end if all energy blocks are collected or simulation time is over (ten minutes)
    elif energy_dist > 100 or runtime >= 600:
        # stop the simulation
        World.stopSimulation()
        print("Simulation stopped")
        ENDGAME = True

    if int(runtime) % 60 == 0 and not ENDGAME and runtime != 0:
        print('Time:', int(runtime), ', Energy:', energyTaken, ', Wall Hits:', wallHits)

print("")
print("Results:")
print("Total energy collected: ", energyTaken)
print("Total time: ", runtime)
print("Average energy per minute: ", energyTaken / (runtime / 60))
print("Total wall hits: ", wallHits)
