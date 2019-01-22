import random

while True:
    try:
        name = input()
    except:
        break
    pas = ''.join(random.choice('oO0l1ij') for _ in range(16) )
    print( name, pas, 'False', sep='\t')

print ('admin1', 'aaaaaaaa', 'True', sep='\t')
