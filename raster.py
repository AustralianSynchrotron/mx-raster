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
import json


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

redisKey = "rastering:"
beamline.redis.delete(redisKey)


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

 
def raster(motor, motorName, attenuation, initPoint, unit_totalHor, unit_totalVer, unit_steps, runCount):
    #real *units*
    unit_verTotalSteps = unit_totalHor
    unit_horTotalSteps = unit_totalVer 
    step = unit_steps
    
    motor_vsteps = unit_steps * CALsample_y
    motor_hsteps = unit_steps * CALgonibase_x 

    #Set up start_run
    EPN = mxvariables.EPN
    path = os.path.join('/data/frames', EPN, 'rastering')
    
    #TODO STORE IN REDIS
    rasterRunCount = runCount
    #Check rastering folder exists
    #if not os.path.isdir(path):
    #    os.makedirs(path)
     
    dcssArgs = {'status': None,
    'exposure_time': 1,
    'attenuation': attenuation,
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
    files = {} 
 
    #generate collector object
    runs = DCSSRuns()
 
    xPositions = list((x) for x in xfrange(initPoint.x - ((unit_horTotalSteps * CALgonibase_x) / 2 ), initPoint.x + ((unit_horTotalSteps * CALgonibase_x) / 2), motor_hsteps))
    yPositions = list((y) for y in xfrange(initPoint.y - ((unit_verTotalSteps * CALsample_y) / 2), initPoint.y + ((unit_verTotalSteps * CALsample_y) / 2), motor_vsteps))
    
    for x in xPositions:
        logger.debug("Moving X to: %s" % x)
        gonibase_x.move(x, wait=True)
        for y in yPositions:
            logger.debug("Moving Y to: %s" % y)
            motor.move(y, wait=True)
           
            logger.info("Taking Shot!")
            
            count = check_file(rasteringCount, path)
            dcssArgs["start_frame"] = count
            
            runs.set_run('run%s' % dcssArgs['run'], **dcssArgs) 
            runs.start_run(dcssArgs['run'])
            fileName = "raster_{0}_{1}_{2}.img" % (count, dcss['run'], rasteringCount)
            files[fileName] = (motorName, x, y)
            beamline.redis.set(rediskey, json.dumps())        
            rasteringCount += 1
 
    beamline.redis.set(redisKey, json.dumps(files))
    #Back to starting points
    gonibase_x.move(initPoint.x, wait=True)
    motor.move(initPoint.y, wait=True)


def check_file(count, path):
    if os.path.exists(os.path.join(path, 'raster_{0}'.format(count))):
        check_file(count + 1, path)
    else:
        return count
 
if __name__ == '__main__':
    if caget("SR03ID01HU03LENS01:ZOOM.RBV") != 1700:
        logging.warning("Zoom level needs to be medium")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Auto Rastering")
    parser.add_argument("--debug", action='store_true', default=False)
    parser.add_argument("-a", "--angle", type=int, default=0)
    parser.add_argument("--steps", type=int, default=10)
    parser.add_argument("--grid-size-H", type=int, default=50)
    parser.add_argument("--grid-size-V", type=int, default=50)
    parser.add_argument("--run-count", type=int, default=1)
    parser.add_argument("--attenuation", type=int, default=95)

    try:
        args = parser.parse_args()
    except argparse.ArgumentError, e:
        print e

    if args.debug:
        logger.setLevel(logging.DEBUG)

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
 
    logger.info("Downloading initial image")
    download_image("test_init")

    imageXCenter = caget("03ID:XTAL:cursor1:CursorX")
    imageYCenter = caget("03ID:XTAL:cursor1:CursorY")
    #draw_grid('test_init.jpg', imageXCenter, imageYCenter)
    logger.debug("imageXCenter: %s" % imageXCenter)
    logger.debug("imageYCenter: %s" % imageYCenter)
    
    if (omega.MON == 0):
        raster(sample_y, "sample_y", args.attenuation, initPoint, args.grid-size-H, args.grid-size-V, args.steps, args.run-count) 
    elif (gonibase_x.MON == 90):
        raster(sample_x, "sample_x", args.attenuation, initPoint, args.grid-size-H, args.grid-size-V, args.steps, args.run-count) 
    else:
        logger.warning("Omega needs to be at 0 or 90 degrees")
        sys.exit(1)

    logger.debug("Time Taken (seconds): %s" % (time.time() - start))
