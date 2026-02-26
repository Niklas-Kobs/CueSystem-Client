import time
from datetime import datetime

realTime = float(time.time())

addtime = 20 * 60

Est_Time_code = realTime + addtime

Est_Time = datetime.fromtimestamp(Est_Time_code)

Est_Time_format = Est_Time.strftime('%H:%M')

print(Est_Time_format)