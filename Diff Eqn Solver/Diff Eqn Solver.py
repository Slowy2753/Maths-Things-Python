import matplotlib.pyplot as plt

#Initial values X,Y
Xs=[1]
Ys=[1]
Ts=[0]

#Initial time
t=0

#Modeling accurace dt value
dt=0.0001

# Define some models

#Exponential Growth
def EG(x,a, dt):
    x_new = x + dt*(a*x)
    return(x_new, 0)

#Logistic Growth
def LG(x, a, k, dt):
    x_new = x + dt*(a*x*(1-x/k))
    return(x_new, 0)

#Lotka-Voltera
def LV(x, y, gamma, dt):
    x_new = x + dt*(x-x*y)
    y_new = y + dt*gamma*(-y+x*y)
    return(x_new, y_new)

#Competative Lotka-Voltera
def CLV(x, y, gamma1, beta, gamma2, dt):
    x_new = x + dt*x*(1-x-gamma1*y)
    y_new = y + dt*beta*y*(1-y-gamma2*x)
    return(x_new, y_new)

#Spruce Budworm
def SBW(x,R,k,dt):
    x_new = x + dt*( R*x*(1-x/k) - x*x/(1+x*x) )
    return(x_new, 0)

#Enzyme-Reaction
def ERS(x,y,a,b,dt):
    x_new = x + dt*(a-x+x*x*y)
    y_new = y + dt*(b-x*x*y)
    return(x_new, y_new)




while t<75:
    t=t+dt
    #X,Y = EG(Xs[-1], a=1, dt=dt)
    #X,Y = LG(Xs[-1], a=1, k=5, dt=dt)
    #X,Y = LV(Xs[-1], Ys[-1], gamma=1 ,dt=dt)
    #X,Y = CLV(Xs[-1], Ys[-1], gamma1=0.9, beta=0.5, gamma2=0.1, dt=dt)
    #X,Y = SBW(Xs[-1], R=1, k=5, dt=dt)
    #X,Y = ERS(Xs[-1], Ys[-1], a=0.1603746, b=0.6 ,dt=dt)
    
    Xs.append(X)
    Ys.append(Y)
    Ts.append(t)
    

plt.plot(Ts,Xs)
# Comment out below if looking at 1D
#plt.plot(Ts,Ys)
plt.show()