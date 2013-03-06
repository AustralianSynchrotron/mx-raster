import beamline

redisKey = "rastering:"

positions = json.loads(beamline.redis.get(redisKey)

for key, value in positions.iteritems():
    print key

print "Enter image file name to center"
image = raw_input(">> ")

if positions[image][0] == "sample_y":
    motor = beamline.motors.sample_y
elif positions[image][0] == "sample_x":
    motor = beamline.motors.sample_x
else:
    print "Failed to find image"
    sys.exit(1)

beamline.motors.gonibase_x.move(positions[image][1], wait=True)
motor.move(positions[image][2], wait=True)

print "finished"
