import os
import base64
import router.main as router
import vg_web
from dotenv import load_dotenv

load_dotenv(verbose=True)
HOST_IP = os.getenv('HOST_IP')
HOST_PORT = os.getenv('HOST_PORT')

web = vg_web.App(router)
web.run(HOST_IP, HOST_PORT)