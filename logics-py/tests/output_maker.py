#from logics import Logics
import os

text_str = "hello world"
numeric_int = 2
numeric_float = 2.5
numeric_int_neg = -3
numeric_float_neg = -1.5
dict_base = {numeric_int , text_str, numeric_int, numeric_float, numeric_float_neg,numeric_int_neg }
line = ""
f = open("tests/tests.lgx", "w")
for x in dict_base:
    for y in dict_base:
        try:
            line += str(x) + "+" + str(y) + "\n"
            line += f"#EXPECT: {str(x + y)} \n" # str(repr(Logics.run(x + y))))
        except:
            line = line + "#EXPECT:error" + "\n"
        
        
f.write(line)