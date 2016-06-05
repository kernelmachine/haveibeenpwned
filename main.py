from hibp import HIBP, AsyncHIBP
import time
accounts = ['adobe','ashleymadison', 'naughtyamerica'] * 1
reqs = [HIBP.get_breach(x) for x in accounts]
### SERIAL
start_time = time.time()
for req in reqs:
    req.execute()
    print(req.res)
elapsed_time = time.time() - start_time
print("serial impl took %.2f seconds" % elapsed_time)
### CONCURRENT
start_time = time.time()
async_reqs = AsyncHIBP().map(reqs)
elapsed_time = time.time() - start_time
print("concurrent impl took %.2f seconds" % elapsed_time)
