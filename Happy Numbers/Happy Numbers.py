import os
import time
import numpy as np
from numba import njit

# step is converted into c machiene code to run more quickly
@njit
def step(n):
    result = 0
    while n > 0:
        result += (n % 10) ** 2
        n //= 10
    return result

@njit
def get_bit(arr, i):
    # byte that contains bit i is i//8
    # bit position (from right) is i % 8
    # we shift the binary right by bit position and check divisbility by 2
    return (int(arr[i // 8]) >> (7 - i % 8)) % 2

@njit
def set_bit(arr, i, new):
    current = get_bit(arr, i)

    if new == current:
        return
    elif current == 0 and new == 1:
        arr[i // 8] = int(arr[i // 8]) + (128 >> i % 8)
    elif current == 1 and new == 0:
        arr[i // 8] = int(arr[i // 8]) - (128 >> i % 8)

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
def populate_happy_array1(happy_array, happy_999):
    for i in range(1, 999):
        if i in happy_999:
            set_bit(happy_array, i, 1)    

# Define a function that will populate number 1000 through imax       
@njit
def populate_happy_array2(happy_array, imax):
    for i in range(1000, imax):
        # as step_2(n) < n for n > 999 we can do one step and check happiness
        if get_bit(happy_array,step(i)) == 1:   # reference precomputed results
            set_bit(happy_array, i, 1)

def create_happy_array(imax):
    n_bytes = (imax + 7) // 8 
    happy_array = np.zeros(n_bytes, dtype=np.uint8)
    populate_happy_array1(happy_array, happy_to_999())
    populate_happy_array2(happy_array, n_bytes*8)
    return happy_array

if __name__ == '__main__':
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(script_dir, "happy_array.bits")

    t_start = time.time()
        
    imax = 10**9
    happy_array = create_happy_array(imax)
            
    t_end = time.time()
    print(t_end - t_start)

    #happy_array.tofile(path)