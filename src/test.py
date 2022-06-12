import pyzipper 
import zipfile
import os

text = b"Hello world" * 1000
pwd = b"password"
file = "test.txt"

with pyzipper.AESZipFile('new_test.zip',
                         'w',
                         compression=pyzipper.ZIP_LZMA,
                         encryption=pyzipper.WZ_AES) as zf:
    zf.setpassword(pwd)
    zf.writestr('test.txt', "What ever you do, don't tell anyone!")

with pyzipper.AESZipFile("new_test.zip") as zf:
    zf.setpassword(pwd)
    my_secrets = zf.read('test.txt')
