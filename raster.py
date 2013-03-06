#!/usr/bin/env python2.7
#Jack Dwyer 07/01/13
import time, datetime, math, sys, os
from collections import namedtuple
from itertools import product
import requests, argparse, logging
from epics import caput, caget
import beamline
from draw_grid import draw_grid

logging.basicConfig(format='[%(asctime)s -- %(levelname)s] -- %(message)s',
                    datefmt='%Y-%m-%d %H:%M', level=logging.INFO)

logger = logging.getLogger(__file__)


#Calibration Factors:
CALgonibase_x = 1.4
CALsample_y = 0.54




Point = namedtuple('Point', ['inc', 'x', 'y'])




def xfrange(start, stop, step):
    while start < stop: 
        yield start
        start += step
    yield stop

def download_image(name):
    #Full size XTAL.MJPG
    r = requests.get("http://10.108.2.53:8080/XTAL.OVER.jpg")
    with open(".".join((name, "jpg")), "wb") as f:
        for chunk in r.iter_content():
            f.write(chunk)
       
def generate_positions(initPoint, centre=True, totalHorSteps=49, totalVerSteps=49, step=10):
    """Returns a list of Points for each shot location """
    positions = []
    #Sort out if top left, or centre
    if centre: #Make sure we move motor to begin at top left
        x = initPoint.x - (totalHorSteps / 2)
        y = initPoint.y + (totalVerSteps / 2)
        initPoint = Point(100, x, y)
    else:
        initPoint = initPoint
       
    xBoundary = [initPoint.x, (initPoint.x + totalVerSteps)]
    yBoundary = [(initPoint.y - totalHorSteps), initPoint.y]
   
    # log("%s %s,%s" % ("Starting X: ", min(initPoint), max(initPoint)))
   
   
    logger.debug("%s %s" % ("Starting X Position:", initPoint.x))
   
    logger.debug("%s %s" % ("Starting Y Position:", initPoint.y))
 
    logger.debug("%s %s,%s" % ("X Boundaries: ", min(xBoundary), max(xBoundary)))
    logger.debug("%s %s,%s" % ("Y Boundaries: ", min(yBoundary), max(yBoundary)))
 
    inc = 0 
    yPosition = initPoint.y 
    xPosition = initPoint.x

    positions = list(product(xfrange(min(xBoundary), max(xBoundary), 10), xfrange(min(yBoundary), max(yBoundary), 10)))

     
    #logger.debug("===Positions===")
    #logger.debug(positions)
    #logger.debug("===============")
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

    logger.debug("ANGLE %s" % args.angle)

    start = time.time()

    #Motor Objects
    sample_x = beamline.motors.sample_x
    sample_y = beamline.motors.sample_y
    omega = beamline.motors.omega
    gonibase_x = beamline.motors.gonibase_x
 
    #Generate Motor Objects
       
    #Move omega
    #omega.move(args.angle)

    #Get initial starting point
    initPoint = Point(00,round(gonibase_x.MON,1), round(sample_y.MON,1))

    positions = generate_positions(initPoint)
    
    logger.debug("First Pos: %r, %r" % (positions[0]))
    logger.debug("Final Pos: %r, %r" % (positions[-1]))
    
    logger.info("Downloading initial image")
    download_image("test_init")

    imageXCenter = caget("03ID:XTAL:cursor1:CursorX")
    imageYCenter = caget("03ID:XTAL:cursor1:CursorY")
    
    logger.debug("imageXCenter: %s" % imageXCenter)
    logger.debug("imageYCenter: %s" % imageYCenter)
   
    #draw_grid("test_init.jpg", imageXCenter, imageYCenter)

    
    #move to final position
    if args.debug:
        gonibase_x.move(positions[-1][0]/CALgonibase_x)
        sample_y.move(positions[-1][1]/CALsample_y)
        time.sleep(5)
        #move back to init
       
        gonibase_x.move(positions[-1][0]/CALgonibase_x)
        sample_y.move(positions[-1][1]/CALsample_y)

    
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

    logger.debug("Time Taken (seconds): %s" % (time.time() - start))
