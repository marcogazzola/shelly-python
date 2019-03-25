from shellypython.shelly import Shelly
from memory_profiler import profile
from guppy import hpy 

h = hpy() 

print (h.heap())

@profile
def my_func():
    print("qui")
    x = Shelly("192.168.1.82", "admin", "admin").update_data()
    print(x.__dict__)
    # x = Shelly("192.168.1.81", "admin", "admin").update_data()
    # print(x.__dict__)

if __name__ == '__main__':
    my_func()
