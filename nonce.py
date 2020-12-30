import time
import random

for i in range (1000):
    if random.randint(0, 20) == 0: 
        print(" nathan joined the game", flush = True)
    else:
        print('nonce:', str(random.randint(0, 1000000)).ljust(7, '0'), flush = True)

    time.sleep(0.3)