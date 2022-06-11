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
SV_IP_TYPE = socket.AF_INET6
IP = "127.0.0.1"
IPv6 = "2400:1a00:b111:61a1:4e38:c8f3:6c35:a68e"
PORT = 6969

# Buffers
BUFF_CAP = 2048 
FORMAT   = "utf-8"
