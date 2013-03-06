#Jack Dwyer 16/01/13
#Test script for drawing the rectangle grid over lay from the first craystal jpeg
import time, datetime, math, sys
from collections import namedtuple
from PIL import Image, ImageDraw

#magic zoom based on which image you are using and if it has been cropped
#Need for pixel to 'step' conversion
zoom = 0.5
Point = namedtuple('Point', ['x', 'y'])

def convert_step_to_pixels(steps):
    #1 step = 1.43 pixels
    return (steps/0.64) * zoom


def draw_grid(imageName, xcenter, ycenter):
    img = Image.open(imageName)
    centre = Point(xcenter, ycenter)
    draw = ImageDraw.Draw(img)
    topLeft = Point(centrePoint.x - (convert_step_to_pixels(totalHorSteps) * 0.5),
                    centrePoint.y - (convert_step_to_pixels(totalVerSteps) * 0.5))
    bottomRight = Point(centrePoint.x + (convert_step_to_pixels(totalHorSteps) * 0.5),
                        centrePoint.y + (convert_step_to_pixels(totalVerSteps) * 0.5))    
    
    
    #draw.rectangle((topLeft.x, topLeft.y, bottomRight.x, bottomRight.y), outline="red")
    
    
    cStep = convert_step_to_pixels(step)

    #Draw Vertcal Lines
    x = topLeft.x
    while x <= topLeft.x + convert_step_to_pixels(totalVerSteps) + 1:
        draw.line([(x, topLeft.y), (x, bottomRight.y)], fill="red")
        x += cStep

    #Draw Horizontal Lines
    y = topLeft.y
    while y <= bottomRight.y + 1:
        draw.line([(topLeft.x, y), (bottomRight.x, y)], fill="red")
        y += cStep

    del draw

    img.save("t.jpg")


def draw_gridi_(img, centrePoint, totalHorSteps=50, totalVerSteps=50, step=10):
    draw = ImageDraw.Draw(img)
    topLeft = Point(centrePoint.x - (convert_step_to_pixels(totalHorSteps) * 0.5),
                    centrePoint.y - (convert_step_to_pixels(totalVerSteps) * 0.5))
    bottomRight = Point(centrePoint.x + (convert_step_to_pixels(totalHorSteps) * 0.5),
                        centrePoint.y + (convert_step_to_pixels(totalVerSteps) * 0.5))    
    
    
    #draw.rectangle((topLeft.x, topLeft.y, bottomRight.x, bottomRight.y), outline="red")
    
    
    cStep = convert_step_to_pixels(step)

    #Draw Vertcal Lines
    x = topLeft.x
    while x <= topLeft.x + convert_step_to_pixels(totalVerSteps) + 1:
        draw.line([(x, topLeft.y), (x, bottomRight.y)], fill="red")
        x += cStep

    #Draw Horizontal Lines
    y = topLeft.y
    while y <= bottomRight.y + 1:
        draw.line([(topLeft.x, y), (bottomRight.x, y)], fill="red")
        y += cStep

    del draw
"""
img = Image.open("test1.jpg")
width, height = img.size
centre = Point(width * 0.5, height * 0.5)

 # Create a draw object
draw_grid(img, centre)

#draw.rectangle((100, 100, 100, 50), outline="red")

#draw.line([(10,10), (10,100)])

img.save("test.jpg")

#img.show()
"""
