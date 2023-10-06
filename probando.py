
from decimal import Decimal as D

a = D('0.6')
b = D('2')
c = D('0.05')

result = (D(5)/D('2'))
print(result)  # This will correctly print 6
print(result, float(result))