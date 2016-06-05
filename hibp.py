from enum import Enum
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

class Services(Enum):
    AccountBreach = "accountbreach"
    DomainBreach = "domainbreach"
    Breach = "breach"
    AllBreaches = "allbreaches"
    DataClasses = "dataclasses"

class HIBP(object):
    def __init__(self):
        self.url = None
        self.res = None
        self.service = None
        self.param = None
    @classmethod
    def get_account_breaches(cls,account):
        req = cls()
        email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
        if not re.match(email_regex, account):
            raise ValueError("{} is an invalid email.".format(account))
        req.url = BASE_URL + "breachedaccount/{}".format(account)
        req.service = Services.AccountBreach
        req.param = account
        return req

    @classmethod
    def get_domain_breaches(cls,domain):
        req = cls()
        domain_regex = re.compile(r"[a-zA-Z\d-]{,63}(\.[a-zA-Z\d-]{,63})+")
        if not re.match(domain_regex, domain):
            raise ValueError("{} is an invalid domain.".format(domain))
        req.url = BASE_URL +  "breaches?domain={}".format(domain)
        req.service = Services.DomainBreach
        req.param = domain
        return req

    @classmethod
    def get_breach(cls,name):
        req = cls()
        req.url = BASE_URL + "breach/{}".format(name)
        req.service = Services.Breach
        req.param = name
        return req

    @classmethod
    def get_all_breaches(cls):
        req = cls()
        req.url = BASE_URL + "breaches"
        req.service = Services.AllBreaches
        return req

    @classmethod
    def get_dataclasses(cls):
        req = cls()
        req.url = BASE_URL + "dataclasses"
        req.service = Services.DataClasses
        return req

    def execute(self):
        try:
            res = requests.get(self.url, headers = HEADERS)
        except requests.exceptions.HTTPError:
            print("there was an error")
            return
        if res.status_code == 404 and self.service == Services.AccountBreach:
            self.res = "object has not been pwned."
            return self
        elif res.text == "[]" and self.service == Services.DomainBreach:
            self.res = "object has not been pwned."
            return self
        elif res.status_code == 404 and self.service == Services.Breach:
            raise ValueError("invalid breach name {}.".format(self.param))
        else:
            self.res = res.json()
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
