import numpy as np
#import decimal
from decimal import Decimal, ROUND_HALF_UP

a=0.165
print(round(a,2))
print(np.round(a,2))
#print(decimal.Decimal(str(a)).quantize(decimal.Decimal('.01'), rounding='ROUND_HALF_UP'))
print(Decimal(str(a)).quantize(Decimal('.01'), ROUND_HALF_UP))