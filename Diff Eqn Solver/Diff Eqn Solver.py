import matplotlib.pyplot as plt

# Define plotting functions for models

#Exponential Growth
def EG(x0, a, t_max, dt):
    Xs = [x0]
    t = 0
    Ts= [t]
    while t<t_max:
        t += dt
        x = Xs[-1]
        Ts.append(t)
        Xs.append(x + dt*(a*x))
    plt.plot(Ts, Xs)
    plt.show()

#Logistic Growth
def LG(x0, a, k, t_max, dt):
    Xs = [x0]
    t = 0
    Ts= [t]
    while t<t_max:
        t += dt
        x = Xs[-1]
        Ts.append(t)
        Xs.append(x+ dt*(a*x*(1-x/k)))
    plt.plot(Ts, Xs)
    plt.show()

#Lotka-Voltera
def LV(x0, y0, gamma, t_max, dt):
    Xs = [x0]
    Ys = [y0]
    t = 0
    Ts= [t]
    while t < t_max:
        t += dt
        x,y = [Xs[-1], Ys[-1]]
        Ts.append(t)
        Xs.append(x+ dt*(x-x*y))
        Ys.append(y + dt*gamma*(-y+x*y))
    plt.plot(Ts, Xs)
    plt.plot(Ts, Ys)
    plt.show()

#Competative Lotka-Voltera
def CLV(x0, y0, gamma1, beta, gamma2, t_max, dt):
    Xs = [x0]
    Ys = [y0]
    t = 0
    Ts= [t]
    while t < t_max:
        t += dt
        x,y = [Xs[-1],Ys[-1]]
        Ts.append(t)
        Xs.append(x+ dt*x*(1-x-gamma1*y))
        Ys.append(y + dt*beta*y*(1-y-gamma2*x))
    plt.plot(Ts, Xs)
    plt.plot(Ts, Ys)
    plt.show()

#Spruce Budworm
def SBW(x0, R, k, t_max, dt):
    Xs = [x0]
    t = 0
    Ts= [t]
    while t < t_max:
        t += dt
        x = Xs[-1]
        Ts.append(t)
        Xs.append(x + dt*( R*x*(1-x/k) - x*x/(1+x*x) ))
    plt.plot(Ts, Xs)
    plt.show()

#Enzyme-Reaction

def ERS(x0, y0, a, b, t_max, dt):
    Xs = [x0]
    Ys = [y0]
    t = 0
    Ts= [t]
    while t < t_max:
        t+=dt
        x,y = [Xs[-1],Ys[-1]]
        Ts.append(t)
        Xs.append(x+ dt*(a-x+x*x*y))
        Ys.append(y + dt*(b-x*x*y))
    plt.plot(Ts,Xs)
    plt.plot(Ts,Ys)
    plt.show()




if __name__ == '__main__':

    dt = 0.0001
    t_max = 75
    x0 = 1
    y0 = 0.9
    
    #EG(x0, 1, t_max, dt)
    #LG(x0, 1, 5, t_max, dt)
    #LV(x0, y0, 0.9, t_max, dt)
    #CLV(x0, y0, 0.5, 0.2, 0.3, t_max, dt)
    #SBW(x0, 0.8, 5, t_max, dt)
    #ERS(x0, y0, 0.19, 0.5, t_max, dt)