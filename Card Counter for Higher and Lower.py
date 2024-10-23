import numpy as np
import matplotlib.pyplot as plt
 
#Ace is assumed to be low
x = [4]*13
values = [0,1,2,3,4,5,6,7,8,9,10,11,12]
names = ['Ace','2','3','4','5','6','7','8','9','10','J','Q','K']

Playing = True

card_dict = {'a': 0,
             '2': 1,
             '3': 2,
             '4': 3,
             '5': 4,
             '6': 5,
             '7': 6,
             '8': 7,
             '9':8,
             '10': 9,
             'j': 10,
             'q': 11,
             'k': 12}

while(Playing==True):
    card = input("What card has been revealed? ")
    card = card_dict[card]
    x[card] -= 1
    
    cards = np.repeat(values, x)
    median = np.median(cards)
    
    #print(x)
    plt.bar(names, height=x, color='c',edgecolor='k', alpha=0.5)
    plt.axvline(median, color='k', linestyle='dashed', linewidth=1)
    plt.show()
    
    if card>median:
        print("Higher")
    elif card<median:
        print("Lower")
    else:
        print("Guess either way")