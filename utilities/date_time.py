import maya
import datetime


def create_utc_timestamp():
    dt = datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S-%f')
    mt = maya.now().iso8601()
    prit(dt)
    print(mt)
