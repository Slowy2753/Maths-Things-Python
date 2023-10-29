import numpy as np
import matplotlib.pyplot as plt
import random

r = [1, 0, 0]
g = [0, 1, 1]
point = [1, 1]
dist = [0, 0]
plt.axes().set_aspect('equal')

def draw_square():
    plt.plot ([-1, 1], [1, 1], marker = 'o', markersize = 2, color = r)
    plt.plot ([1, 1], [1, -1], marker = 'o', markersize = 2, color = r)
    plt.plot ([1, -1], [-1, -1], marker = 'o', markersize = 2,color = r)
    plt.plot ([-1, -1], [-1, 1], marker = 'o', markersize = 2,color = r)

#Have the user decide what fractal

def Vicsek():
    corners = [[1, 1], [1, -1], [-1, -1], [-1, 1], [0, 0]]
    list = [0, 1, 2, 3, 4]
    draw_fractal(corners = corners, list = list)
    
def Sierpinski():
    corners = [[1, 1], [1, -1], [-1, -1], [-1, 1], [0, 1], [-1, 0], [0, -1], [1, 0]]
    list = [0, 1, 2, 3, 4, 5, 6, 7]
    draw_fractal(corners = corners, list = list)

def draw_fractal(corners, list):
    draw_square()
    plt.plot(point[0], point[1], marker = 'o', markersize = 1, color = g)
    for i in range (1,50000):
        rand = random.choice(list)
    
        point[0] = (1/3)*point[0] + (2/3)*corners[rand][0]
        point[1] = (1/3)*point[1] + (2/3)*corners[rand][1]
    
        plt.plot(point[0], point[1], marker = 'o', markersize = 1, color = g)
    
    plt.show()


#Note by changing the draw_fractal function you can change the number of points generated
#and weather draw_square, which plots the square outline, is run
    
#print(Vicsek())
#print(Sierpinski())
