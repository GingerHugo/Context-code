import re
import numpy as np

# print re.sub(r'def\s+([a-zA-Z_][a-zA-Z_0-9]*)\s*\(\s*\):', r'static PyObject*\npy_\1(void)\n{', 'def myfunc():')

# string = '##$da####d da!!!da d>>a*****sda dd???a\n'
# print (string + 'e').title() 
# # string = re.sub(r"[^A-Za-z0-9(),!?\'\`]", r"%", string)
# string = re.sub(r"\s{2,}", " ", string)  
# print string + 'e'

# p = re.compile(r'(\w+) (\w+)')
# s = "     . . . if you're just in the mood for a fun -- but bad -- movie , you might want to catch freaks as a matinee . "
 
# print s.strip()

a , b, c = [], [], []
a.append(0)
a.append(0)
a.append(0)
b.append(0)
b.append(0)
b.append(0)
b.append(1)
c.append(0)
c.append(0)
c.append(0)
c.append(1)
c.append(0)
c.append(0)
c.append(0)
c.append(1)
train = []
train.append(a)
train.append(b)
train.append(c)
trainA = np.array(train,dtype="int")
print trainA