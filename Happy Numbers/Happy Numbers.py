import time
import pickle
from numba import njit

# step is converted into c machiene code to run more quickly
@njit
def step(n):
    result = 0
    while n > 0:
        result += (n % 10) ** 2
        n //= 10
    return result

# Defines a function that returns all the happy numbers between 1 and 999
# @njit (Works but is slower)
def happy_to_999():
    # Initialize happy and sad lists
    happy = [1]
    sad = []

    for i in range(2, 1000):
        seq = []
        
        if i in happy or i in sad:
            continue
        else:
            seq.append(i)
            t = True
            while t:
                new = step(seq[-1])
                
                if new in sad:
                    sad.extend(seq)
                    t = False
                elif new in happy:
                    happy.extend(seq)
                    t = False
                elif new in seq:
                    sad.extend(seq)
                    t = False
                else:
                    seq.append(new)
    return(happy)

# Define a function that will populate number 1000 through imax
def populate_happy_array1(happy):
    for i in range(1, 1000):
        if i in happy:
            happy_array[i] = True      

# Define a function that will populate number 1000 through imax       
@njit
def populate_happy_array2(happy_array, imax):
    for i in range(1000, imax):
        if happy_array[step(i)]:  # Reference precomputed happy numbers
            happy_array[i] = True


if __name__ == '__main__':
    
    t_start = time.time()
    
    imax = 10**10
    
    # Squares of digits from 0 to 9
    squares = [i**2 for i in range(10)]
    happy_array = bytearray(imax)  #Creates a byte array of length imax
    
    # Populate the happy array for numbers 1 through 999
    populate_happy_array1(happy_to_999())
    
    # Call the optimized function
    populate_happy_array2(happy_array, imax)
        
    t_end = time.time()
    print(t_end - t_start)

    #with open("happy_array.pkl", "wb") as file:
    #    pickle.dump(happy_array, file)