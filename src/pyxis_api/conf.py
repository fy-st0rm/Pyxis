import json
import pickle
import socket
import time
import threading

DELAY = 0.1

# Server constants
IP = "127.0.0.1"
IPv6 = "2400:1a00:b111:61a1:4e38:c8f3:6c35:a68e"
PORT = 6969

# Buffers
BUFF_CAP = 1024
FORMAT   = "utf-8"
