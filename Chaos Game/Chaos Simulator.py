import numpy as np
import matplotlib.pyplot as plt
import random


point = [0, 1]
plt.axes().set_aspect('equal')

def c(sides):
    corners = []
    for i in range (0,sides):
        theta=(i*2*np.pi)/sides
        corners.append([np.cos(theta),np.sin(theta)])
    return(corners)

def l(sides):
    list = []
    for i in range(0, sides):
        list.append(i)
    return list

def plot_poly(corners):
    length = len(corners)
    plt.plot([corners[length-1][1],corners[0][1]],[corners[length-1][0],corners[0][0]]
                 , marker = 'o', markersize = 2, color = 'red')
    for i in range(0,length-1):
        plt.plot([corners[i][1],corners[i+1][1]],[corners[i][0],corners[i+1][0]]
                 , marker = 'o', markersize = 2, color = 'red')

def draw_fractal(corners, list, r):
    #plot_poly(corners)
    for i in range (1,500000):
        rand = random.choice(list)
    
        point[0] = (1-r)*point[0] + (r)*corners[rand][0]
        point[1] = (1-r)*point[1] + (r)*corners[rand][1]
    
        if i>=10:
            plt.plot(point[1], point[0], marker = 'o', markersize = 1, color = 'black')
    
def chaos(sides, ratio):
    corners = c(sides)
    list = l(sides)
    draw_fractal(corners, list , ratio)
    plt.show()

#Note the r value is standard with Wikipedia
#if comparing results to the WolframAlpha article use 1-r
print(chaos(5,5/8))

#Note by changing the draw_fractal function you can change the number of points generated
#and weather plot_poly is run which plots the outline of the n-gon

plt.show()