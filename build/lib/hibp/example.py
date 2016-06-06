from hibp import HIBP, AsyncHIBP
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logging.getLogger("requests").setLevel(logging.WARNING)

if __name__ == '__main__':
    # random set of query paramaters
    names = ['adobe','ashleymadison', 'naughtyamerica', 'myspace']
    accounts = ["ssgrn", "pegasos1","barackobama"]
    domains = ['twitter.com', 'facebook.com','github.com','adobe.com']

    # setup HIBP objects for request executions
    reqs = [HIBP.get_breach(x) for x in names] \
           + [HIBP.get_account_breaches(x) for x in accounts] \
           + [HIBP.get_domain_breaches(x) for x in domains]

    ### SERIAL
    start_time = time.time()
    for req in reqs:
        req.execute()
    elapsed_time = time.time() - start_time
    logging.info("serial impl took %.2f seconds" % elapsed_time)

    ### CONCURRENT
    start_time = time.time()
    async_reqs = AsyncHIBP().map(reqs)
    elapsed_time = time.time() - start_time
    logging.info("concurrent impl took %.2f seconds" % elapsed_time)

    ### LAZILY CONCURRENT
    start_time = time.time()
    async_reqs = AsyncHIBP().imap(reqs)
    elapsed_time = time.time() - start_time
    logging.info("lazily concurrent impl took %.2f seconds" % elapsed_time)
