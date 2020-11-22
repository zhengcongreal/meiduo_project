from django.test import TestCase

# Create your tests here.
dict={}
list=[1,2,3,4,5]
dict[tuple(list)]=1
print(dict)