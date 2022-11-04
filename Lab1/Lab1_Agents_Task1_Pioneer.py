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

    print(int(runTime))
    # Spin randomly to give it a random direction every 3 seconds
    if int(runTime) % 3 == 0:
        speed = random.random() * 10 - 5  # This is a random number between -5 and 5
        World.execute(dict(speedLeft=speed, speedRight=-speed), -1, random.random())

    # If the robot is too close to the wall, turn away from it
    threshold = 0.2
    if frontSensor < threshold:
        speed = random.getrandbits(1)*2-1  # This is either 1 or -1
        World.execute(dict(speedLeft=-speed, speedRight=speed), 2450 * 2/3, -1)
    # March in that direction
    speed = random.random() * 3 + 2  # Random number between 3 and 5 or -3 and -5
    motorSpeed = dict(speedLeft=speed, speedRight=speed)


def fixed_agent(simulationTime):
    global motorSpeed
    if simulationTime < 28000:
        motorSpeed = dict(speedLeft=2, speedRight=2)
    elif simulationTime < 55000:
        motorSpeed = dict(speedLeft=-0.1, speedRight=0.1)
    elif simulationTime < 80000:
        motorSpeed = dict(speedLeft=2, speedRight=2)
    else:
        # Crash into the corner
        motorSpeed = dict(speedLeft=0.7, speedRight=0.6)


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

    # This is the field of view of the robot
    # If the energy block is too far away, don't chase it
    if abs(energySensor.direction) > math.pi / 1.9 or energySensor.distance > 2.3:
        motorSpeed = dict(speedLeft=random.uniform(2-0.5, 2+0.5), speedRight=random.uniform(2-0.5, 2+0.5))
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
timeStart = time.time()


while robot:  # main Control loop
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

    # default_agent(simulationTime)
    # random_agent(runtime)
    # fixed_agent(simulationTime)
    # reflex_agent(simulationTime)
    memory_agent(simulationTime, runtime)

    ########################################
    # Action Phase: Assign speed to wheels #
    ########################################
    # assign speed to the wheels
    World.setMotorSpeeds(motorSpeed)
    # try to collect energy block (will fail if not within range)
    if World.getSensorReading("energySensor").distance <= 0.5:
        if World.collectNearestBlock() == 'Energy collected :)':
            print('Energy collected :)')
            counterStart = runtime
        else:
            print("Energy not collected :(")
