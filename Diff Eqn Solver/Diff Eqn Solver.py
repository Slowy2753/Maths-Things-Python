import matplotlib.pyplot as plt

#Initial values N,P
V=[0.1,0.1]

#Modeling accurace dt value
dt=0.001

#Initial time
t=0

#K value
k=1

#For plotting
Ns=[]
Ps=[]
Ts=[]

while t<1yea 00:
    N=V[0]
    
    P=V[1]
    
    
    g1=N*(1-P)
    g2=k*P*(N-1)
    
    V=[N + dt*g1,
       P + dt*g2]
    t=t+dt
    
    Ns.append(N)
    Ps.append(P)
    Ts.append(t)
    

plt.plot(Ts,Ns)
plt.plot(Ts,Ps)
plt.show()