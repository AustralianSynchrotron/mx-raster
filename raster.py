#!/usr/bin/env python2.7
#Jack Dwyer 07/01/13
import time, datetime, math, sys, os
from collections import namedtuple
import requests, argparse, logging
#from epics import caput, caget
#import beamline


logging.basicConfig(format='[%(asctime)s -- %(levelname)s] -- %(message)s',
                    datefmt='%Y-%m-%d %H:%M', level=logging.INFO)

logger = logging.getLogger(__file__)

Point = namedtuple('Point', ['x', 'y'])
 
def log(message):
    print ("%s -- %s" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message))


def download_image(name):
    #Full size XTAL.MJPG
    r = requests.get("http://10.108.2.53:8080/XTAL.MJPG.jpg")
    with open(name+".jpg", "wb") as f:
        for chunk in r.iter_content():
            f.write(chunk)
            
    #XTAL.ROI1
    r = requests.get("http://10.108.2.53:8080/XTAL.ROI1.jpg")
    with open("ROI1_"+name+".jpg", "wb") as f:
        for chunk in r.iter_content():
            f.write(chunk)




def move_motor(motor, pos):
    print motor.MON
    log("Checking position is at required position %s" % pos)
    #make sure omega drive is at 0 degrees
    if math.fabs(motor.SP - pos) < 0.2:
        log("Motor in Position %s" % pos)
        return
    else:
        log("Motor moving")
        motor.move(pos)
       
        start = time.time()
        while motor.inPosition():
            time.sleep(0.05)
            if (time.time() - start > 2):
                break
           
        while not motor.inPosition():
            time.sleep(0.05)
           
        move_motor(motor, pos)
 
 
def generate_positions(initPoint, centre=True, totalHorSteps=49, totalVerSteps=49, step=10):
    """Returns a list of Points for each shot location """
    positions = []
    #Sort out if top left, or centre
    if centre: #Make sure we move motor to begin at top left
        x = initPoint.x - (totalHorSteps / 2)
        y = initPoint.y + (totalVerSteps / 2)
        initPoint = Point(x, y)
    else:
        initPoint = initPoint
       
    xBoundary = [initPoint.x, (initPoint.x + totalVerSteps)]
    yBoundary = [(initPoint.y - totalHorSteps), initPoint.y]
   
   # log("%s %s,%s" % ("Starting X: ", min(initPoint), max(initPoint)))
   
   
    logger("%s %s" % ("Starting X Position:", initPoint.x))
   
    logger("%s %s" % ("Starting Y Position:", initPoint.y))
 
    logger("%s %s,%s" % ("X Boundaries: ", min(xBoundary), max(xBoundary)))
    logger("%s %s,%s" % ("Y Boundaries: ", min(yBoundary), max(yBoundary)))
 
 
    yPosition = initPoint.y
    xPosition = initPoint.x
 
    #Generate position
    while yPosition >= min(yBoundary):
        if xPosition <= max(xBoundary): #Need to move from left to right
            while xPosition <= max(xBoundary):
                if xPosition < min(xBoundary):
                    xPosition = xPosition + step
                else:
                    positions.append(Point(xPosition, yPosition))
                    xPosition = xPosition + step
        else:   #Need to reverse back, so move right to left
            while xPosition >= min(xBoundary):
                if xPosition > max(xBoundary):
                    xPosition = xPosition - step
                else:
                    positions.append(Point(xPosition, yPosition))
                    xPosition = xPosition - step
        yPosition = yPosition - step
        print ""
 
    return positions
 

def check_file(count):
    if os.path.exists(os.path.join(path, 'raster_{0}'.format(count))):
        check_file(count + 1)
    else:
        return count
 
 
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description="Auto Rastering")
    parser.add_argument("--debug", action='store_true', default=False)
    parser.add_argument("-a", "--angle", type=int, default=0)

    try:
        args = parser.parse_args()
    except argparse.ArgumentError, e:
        print e

    if args.debug:
        logger.setLevel(logging.DEBUG)

    logger.debug(args.angle)

    start = time.time()

    #Motor Objects
    sample_x = beamline.motors.sample_x
    sample_y = beamline.motors.sample_y
    omega = beamline.motors.omega
    gonibase_x = beamline.motors.gonibase_x
 
    #Generate Motor Objects
    hor = mx.Motor("SR03ID01GON01:X", deadband=0.1)
    ver = mx.Motor("SR03ID01GON01:SAMPLE_Y", deadband=0.1)
    omega = mx.Motor('SR03ID01GON01:OMEGA')
       
    #Move omega
    omega.move(args.angle)

    #Get initial starting point
    initPoint = Point(round(gonibase_x.MON,1), round(sample_y.MON,1))

    positions = generate_positions(initPoint)
    print positions
    print len(positions)
    
    """ 
    for position in positions:
        log("moving hor %s" % position.x)
        #hor.move(position.x)
        log("moving ver %s" % position.y)
        #ver.move(position.y)
        move_motor(hor, position.x)
        move_motor(ver, position.y)
        log("Taking Shot!")
        
        count = check_file(rasteringCount)
        dcssArgs["start_frame"] = count
        
        runs.set_run('run%s' % dcssArgs['run'], **dcssArgs) 
        runs.start_run(dcssArgs['run'])
        
        rasteringCount += 1
    
    #move back to centre
    move_motor(hor, initPoint.x)
    move_motor(ver, initPoint.y)
    """
    print "TOTAL TIME TAKEN: ",
    print time.time() - start
    print "Mins: ",
    print (time.time() - start) / 60.0
