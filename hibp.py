import re

try:
    import requests
except ImportError:
    raise RuntimeError('Requests is required for hibp.')

try:
    import gevent
    from gevent import monkey
    from gevent.pool import Pool
except ImportError:
    raise RuntimeError('Gevent is required for hibp.')

monkey.patch_all(thread=False, select=False)


BASE_URL = "https://haveibeenpwned.com/api/v2/"
HEADERS = {"User-Agent": "hibp-python",}

class HIBP(object):
    def __init__(self):
        self.url = None
        self.res = None

    @classmethod
    def get_account_breaches(cls,account):
        req = cls()
        email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
        if not re.match(email_regex, account):
            raise ValueError("{} is an invalid email.".format(account))
        req.url = BASE_URL + "breachedaccount/{}".format(account)
        return req

    @classmethod
    def get_domain_breaches(cls,domain=None):
        req = cls()
        if domain is not None:
            req.url = BASE_URL +  "breaches?domain={}".format(domain)
        else:
            req.url = BASE_URL + "breaches"
        return req

    @classmethod
    def get_breach(cls,name):
        req = cls()
        req.url = BASE_URL + "breach/{}".format(name)
        return req

    @classmethod
    def get_dataclasses(cls):
        req = cls()
        req.url = BASE_URL + "dataclasses"
        return req

    def execute(self):
        try:
            res = requests.get(self.url, headers = HEADERS)
            self.res = res.json()
        except requests.exceptions.HTTPError:
            print("there was an error")
            return
        if res.status_code == 404:
            self.res = "object has not been pwned."
            return self
        return self
        
class AsyncHIBP(object):
    def __init__(self):
        self.pool_size = None
        self.pool = Pool(self.pool_size)
        self.session = requests.Session()
        self.timeout = 10
        self.url = None
        self.res = None

    def send(self,r):
        if self.pool is not None:
            return self.pool.spawn(r.execute)
        return gevent.spawn(r.execute)

    def map(self,reqs):
        jobs = [self.send(r) for r in reqs]
        gevent.joinall(jobs, timeout=self.timeout)
        return reqs
