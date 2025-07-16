import numpy
from fractions import Fraction

a = numpy.array([[2,3],[3,2]])
b = numpy.array([6,12])

res=numpy.linalg.solve(a, b)
print(res)