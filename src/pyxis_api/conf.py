import json
import pickle
import socket
import time
import threading
import sys
import uuid
import random
import os
import tarfile
import io

DELAY = 0.2
DATA_DUPLICATION_AMT = 2

# Server constants
SV_IP_TYPE = socket.AF_INET

__ipv4 = socket.gethostbyname(socket.gethostname())
__ipv6 = "2400:1a00:b111:61a1:4e38:c8f3:6c35:a68e"
if SV_IP_TYPE == socket.AF_INET:
	IP = __ipv4 
else:
	IP = __ipv6

PORT = 6969

# Buffers
BUFF_CAP = 2048 
FORMAT   = "utf-8"
