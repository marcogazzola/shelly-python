from shellypython.shelly import (Shelly, Mqtt)
import logging
logging.basicConfig(level=logging.DEBUG)

print (Mqtt().to_dictionary())
# x = Attributes("test", "test2")
# print(x.to_dictionary())
#x = Shelly("http://localhost:8123/local")
# print (x.to_dictionary())
#print(x.shelly_status_api())
#print(x.get_shelly_status())
