import time, datetime, math, sys, os
from collections import namedtuple

from raster import *



try:
    execfile('/xray/progs/Python/setup.py')
except IOError:
    print "Failed to load /xray/progs/Python/setup.py"
    sys.exit(1)
    
   
import mx
from beamline import variables as mxvariables

sys.path.insert(0, '/xray/progs/dcss_test')

fz = open("positions.txt", "w+")

#Generate Motor Objects
hor = mx.Motor("SR03ID01GON01:X", deadband=0.1)
ver = mx.Motor("SR03ID01GON01:SAMPLE_Y", deadband=0.1)
omega = mx.Motor('SR03ID01GON01:OMEGA')

log("zero out omega")

#Uncomment, to zero out omega motor
move_motor(omega, 0)

#Get initial starting point
initPoint = Point(round(hor.MON,1), round(ver.MON,1))



positions = generate_positions(initPoint, centre=True)
print positions
print initPoint


pMax = max(positions)
pMin = min(positions)
print "MAX: ",
print(pMax)
print "MIN: ",
print(pMin)

download_image("pre_init_point")


#Moving motor to min
print "moving to min point:"
fz.write("\nMoving to min point: ")
fz.write("\nX = ")
fz.write(str(pMin.x))
fz.write("\nY = ")
fz.write(str(pMin.y))
print(pMin)
move_motor(hor, pMin.x)
move_motor(ver, pMin.y)
download_image("min_point")
fz.write("\nCOMPLETED MOVE ================\n\n")



time.sleep(1)

print "moving to max point"
print (pMax)

fz.write("\nMoving to max point:")
fz.write("\nX = ")
fz.write(str(pMax.x))
fz.write("\nY = ")
fz.write(str(pMax.y))

move_motor(hor, pMax.x)
move_motor(ver, pMax.y)
download_image("max_point")

fz.write("\nCOMPLETED MOVE ================ \n\n")



time.sleep(1)
print "moving to init point"

fz.write("Moving to init point: ")
fz.write("\nX = ")
fz.write(str(initPoint.x))
fz.write("\nY = ")
fz.write(str(initPoint.y))

move_motor(hor, initPoint.x)
move_motor(ver, initPoint.y)
download_image("post_init_point")

fz.write("\nCOMPLETED MOVE ================\n\n")

fz.close()


print "completed"
