#!/usr/bin/env python2.7
#Jack Dwyer 07/01/13
#prepend 

# motor_ (ois motor units, depends on each motor also)
# unit_ (*real units*)
# pixel_ (unit to pixel)

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

from beamline import variables as mxvariables
sys.path.insert(0, '/xray/progs/dcss_test')
from dcss_runs import DCSSRuns 
 

#Calibration Factors:
CALgonibase_x = 1.4
CALsample_y = 0.54


Point = namedtuple('Point', ['x', 'y'])


def convertToMachine(x, y):
    return (x*1.4, y*0.54)

def xfrange(start, stop, step):
    print step
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

 

def check_file(count):
    if os.path.exists(os.path.join(path, 'raster_{0}'.format(count))):
        check_file(count + 1)
    else:
        return count
 

def move_x(point):
    #get current position
    current = gonibase_x.MON
    print "CURRENT: ",
    print current
    diff = point - current
    print "DIFF: ",
    print diff

    #convert to actual machine steps
    move = diff*1.4
    
    gonibase_x.move(current+move, disableHome=True, wait=True)

def move_y(point):
    #get current position
    current = sample_y.MON
    print "CURRENT: ", 
    print current 
    diff = point - current 
    print "DIFF: ", 
    print diff
    #convert to actual machine steps
    move = diff*0.54
    sample_y.move(current+move, disableHome=True, wait=True)

def gen_pos(initPoint, center=False):
    #real *units*
    unit_verTotalSteps = 50
    unit_horTotalSteps = 50
    step = 10
    print initPoint

    if center:
        x = initPoint.x + ((unit_horTotalSteps * 1.4) / 2)
        y = initPoint.y - ((unit_verTotalSteps * 0.54) / 2)
        initPoint = Point(x, y)

    
    #Set up start_run
    EPN = mxvariables.EPN
    path = os.path.join('/data/frames', EPN, 'rastering')
    rasteringCount = 1
    #TODO STORE IN REDIS
    rasterRunCount = 3
    #Check rastering folder exists
    #if not os.path.isdir(path):
    #    os.makedirs(path)
        
    dcssArgs = {'status': None,
    'exposure_time': 1,
    'attenuation': 90,
    'run': 0,
    'start_frame': rasteringCount,
    'start_angle': 0,
    'debug': False,
    'end_angle': None,
    'collect': False,
    'energy1': None,
    'next_frame': 0,
    'delta': 1,
    'directory': path,
    'file_root': 'raster_{0}'.format(rasterRunCount),
    'beam_stop': None,
    'distance': 500}

 
    #generate collector object
    runs = DCSSRuns()
 

    
    print initPoint

    xPositions = list((x) for x in xfrange(initPoint.x - ((unit_horTotalSteps * 1.4) / 2 ), initPoint.x + ((unit_horTotalSteps * 1.4) / 2), 14))
    yPositions = list((y) for y in xfrange(initPoint.y - ((unit_verTotalSteps * 0.53) / 2), initPoint.y + ((unit_verTotalSteps * 0.53) / 2), 5.3))
    
    for x in xPositions:
        logger.debug("Moving X to: %s" % x)
        gonibase_x.move(x, wait=True)
        for y in yPositions:
            logger.debug("Moving Y to: %s" % y)
            sample_y.move(y, wait=True)
           
            logger.info("Taking Shot!")
            
            count = check_file(rasteringCount, path)
            dcssArgs["start_frame"] = count
            
            runs.set_run('run%s' % dcssArgs['run'], **dcssArgs) 
            runs.start_run(dcssArgs['run'])
            
            rasteringCount += 1
 

    print xPositions
    print yPositions
    
    time.sleep(100)

    x = initPoint.x - ((unit_horTotalSteps * 1.4) / 2)
    y = initPoint.y + ((unit_verTotalSteps * 0.54) / 2)
    logger.debug("bottom right")
    gonibase_x.move(x, wait=True)
    sample_y.move(y, wait=True)
    time.sleep(5)

    x = initPoint.x + ((unit_horTotalSteps * 1.4) / 2)
    y = initPoint.y + ((unit_verTotalSteps * 0.54) / 2)
    logger.debug("bottom left")
    gonibase_x.move(x, wait=True)
    sample_y.move(y, wait=True)
    time.sleep(5)

    x = initPoint.x - ((unit_horTotalSteps * 1.4) / 2)
    y = initPoint.y - ((unit_verTotalSteps * 0.54) / 2)
    logger.debug('top right')
    gonibase_x.move(x, wait=True)
    sample_y.move(y, wait=True)
    time.sleep(5)
   
    x = initPoint.x + ((unit_horTotalSteps * 1.4) / 2)
    y = initPoint.y - ((unit_verTotalSteps * 0.54) / 2)
    logger.debug("top left")
    gonibase_x.move(x, wait=True)
    sample_y.move(y, wait=True)
    time.sleep(5)


    gonibase_x.move(initPoint.x, wait=True)
    sample_y.move(initPoint.y, wait=True)

def generate_positions(initPoint, centre=True, totalHorSteps=49, totalVerSteps=49, step=10):
    """Returns a list of Points for each shot location """
    positions = []
    #Sort out if top left, or centre
    if centre: #Make sure we move motor to begin at top left
        x = initPoint.x - ((totalHorSteps*0.53) / 2)
        y = initPoint.y + ((totalVerSteps*1.4) / 2)
        initPoint = Point(x, y)
    else:
        initPoint = initPoint
       
    xBoundary = [initPoint.x, (initPoint.x + (totalVerSteps * 1.4))]
    yBoundary = [(initPoint.y - (totalHorSteps*0.53)), initPoint.y]
   
    
    
    
    # log("%s %s,%s" % ("Starting X: ", min(initPoint), max(initPoint)))
   
   
    logger.debug("%s %s" % ("Starting X Position:", initPoint.x))
   
    logger.debug("%s %s" % ("Starting Y Position:", initPoint.y))
 
    logger.debug("%s %s,%s" % ("X Boundaries: ", min(xBoundary), max(xBoundary)))
    logger.debug("%s %s,%s" % ("Y Boundaries: ", min(yBoundary), max(yBoundary)))
 
    inc = 0 
    yPosition = initPoint.y 
    xPosition = initPoint.x
    
    positions = list(product(xfrange(min(xBoundary), max(xBoundary), 14), xfrange(min(yBoundary), max(yBoundary), 5.3)))



    logger.debug("===Positions===")
    logger.debug(positions)
    logger.debug("===============")
    return positions
 

def check_file(count, path):
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
    initPoint = Point(round(gonibase_x.MON,1), round(sample_y.MON,1))
    


    gen_pos(initPoint) 
    
    
    
    
    
    
    
    
    
    
    
    sys.exit(0)
    time.sleep(100) 
    positions = generate_positions(initPoint)
    
    logger.debug("First Pos: %r, %r" % (positions[0]))
    logger.debug("Final Pos: %r, %r" % (positions[-1]))
    
    logger.info("Downloading initial image")
    download_image("test_init")

    imageXCenter = caget("03ID:XTAL:cursor1:CursorX")
    imageYCenter = caget("03ID:XTAL:cursor1:CursorY")
    draw_grid('test_init.jpg', imageXCenter, imageYCenter)
    logger.debug("imageXCenter: %s" % imageXCenter)
    logger.debug("imageYCenter: %s" % imageYCenter)
   
    #draw_grid("test_init.jpg", imageXCenter, imageYCenter)
    print "positions: first"
    print positions[0]
    print "Last"
    print positions[-1]
    #This should be inital positions
    #move_x(positions[0][0])
    #move_y(positions[-1][1])
    gonibase_x.move(positions[-1][0], wait=True, disableHome=True)
    sample_y.move(positions[0][1], wait=True)


    #this should be final positions
    #move_x(positions[-1][0])
    #move_y(positions[0][1])
    print "fiished"
    time.sleep(10)
    print 'starting'

    #this should be final positions
    gonibase_x.move(initPoint.x, wait=True)
    sample_y.move(initPoint.y, wait=True)


    
    """
    #move to final position
    if args.debug:
        #omega.move(args.angle, disableHome=True, wait=True)
        logger.debug("omega") 
        p = convertToMachine(positions[-1][0], positions[0][1])
        print p
        #gonibase_x.move(p[0], disableHome=True)
        logger.debug("goni")
        #sample_y.move(p[1], wait=True, disableHome=True)
        print "moved y to far"
        
        #time.sleep(10)

        p = convertToMachine(positions[0][0], positions[-1][1])
        print p
        #gonibase_x.move(p[0], disableHome=True)
        logger.debug("goni")
        #sample_y.move(p[1], wait=True, disableHome=True)
        print "moved to initial"

        
        print "Y Position: ", 
        print positions[0][1]
        sample_y.move(positions[0][1], disableHome=True, wait=True)
        logger.debug("sample_y") 
        logger.debug("moved to far corner")
        
        time.sleep(15)
        #move back to init
        logger.debug("Moving back to inital position")

        gonibase_x.move(positions[0][0], disableHome=True)
        print positions[0][0]
        sample_y.move(positions[-1][1], disableHome=True, wait=True)
        print positions[-1][1]
        """ 

    

    """
    for position in positions:
        

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
