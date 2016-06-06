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

# global variables
BASE_URL = "https://haveibeenpwned.com/api/v2/"
HEADERS = {"User-Agent": "hibp-python",}

# enumerate the types of services that are callable
class Services(Enum):
    AccountBreach = "accountbreach"
    DomainBreach = "domainbreach"
    Breach = "breach"
    AllBreaches = "allbreaches"
    DataClasses = "dataclasses"

# generic HIBP class
class HIBP(object):
    '''
    Generic HIBP object.

    Attributes:
        - url -> url to query
        - service -> service to query
        - param -> parameter to service
        - response -> response object to URL request
    '''
    def __init__(self):
        self.url = None
        self.service = None
        self.param = None
        self.response = None

    @classmethod
    def get_account_breaches(cls,account):
        '''
        Setup request to retrieve all breaches on a particular account

        Args:
            - account -> account you want to query. can be email or username to
                         anything
        Returns:
            - HIBP object with updated url, service, and param attributes
        '''
        req = cls()
        req.url = BASE_URL + "breachedaccount/{}".format(account)
        req.service = Services.AccountBreach
        req.param = account
        return req

    @classmethod
    def get_domain_breaches(cls,domain):
        '''
        Setup request to retrieve all breaches on a particular domain

        Args:
            - domain -> domain you want to query. must be valid domain,
                         according to RFC 1035
        Returns:
            - HIBP object with updated url, service, and param attributes
        '''
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
        '''
        Setup request to retrieve a specific breach.

        Args:
            - name -> name of breach you want to query. To get a list of
                      all breach names, run HIBP.get_all_breaches()
        Returns:
            - HIBP object with updated url, service, and param attributes
        '''
        req = cls()
        req.url = BASE_URL + "breach/{}".format(name)
        req.service = Services.Breach
        req.param = name
        return req

    @classmethod
    def get_all_breaches(cls):
        '''
        Setup request to retrieve all breaches recorded on HIBP.com so far.

        Returns:
            - HIBP object with updated url, service, and param attributes
        '''
        req = cls()
        req.url = BASE_URL + "breaches"
        req.service = Services.AllBreaches
        return req

    @classmethod
    def get_dataclasses(cls):
        '''
        Setup request to retrieve all dataclasses on HIBP.

        Returns:
            - HIBP object with updated url, service, and param attributes
        '''
        req = cls()
        req.url = BASE_URL + "dataclasses"
        req.service = Services.DataClasses
        return req

    def execute(self):
        '''
        Execute a GET request on HIBP REST API service based on request
        object setup with one of the query services above.

        Returns:
            - If query parameter is pwned:
                HIBP object with updated response attribute that contains
                parsed JSON object with pwnage data.
            - Else:
               HIBP object with updated response attribute that contains
               string saying that the object has not been pwned.
        '''
        if self.url is None:
            raise ValueError("setup HIBP object with a query service before executing \
                              request.")
        try:
            response = requests.get(self.url, headers = HEADERS)
        except requests.exceptions.HTTPError:
            print("there was an error")
            return
        if response.status_code == 404 and self.service == Services.AccountBreach:
            self.response = "object has not been pwned."
            return self
        elif response.text == "[]" and self.service == Services.DomainBreach:
            self.response = "object has not been pwned."
            return self
        elif response.status_code == 404 and self.service == Services.Breach:
            raise ValueError("invalid breach name {}.".format(self.param))
        else:
            self.response = response.json()
        return self
        
class AsyncHIBP(object):
    '''
    Generic AsyncHIBP object. Use this object to do concurrent HIBP requests
    on multiple queries via gevent.

    Attributes:
        - pool_size -> size of gevent pool
        - pool -> Gevent pool
        - session -> requests session object
        - timeout -> timeout, how long we wait for the URL to respond
        - url -> url to respond on
        - response -> response object to URL request
    '''
    def __init__(self):
        self.pool_size = None
        self.pool = Pool(self.pool_size)
        self.session = requests.Session()
        self.timeout = 10
        self.url = None
        self.response = None

    def send(self,hibp_obj):
        '''
        Spawns gevent/pool threads that will run the execute method on each
        HIBP object.

        Attributes:
            - hibp_obj -> HIBP object
        '''
        if self.pool is not None:
            return self.pool.spawn(hibp_obj.execute)
        return gevent.spawn(hibp_obj.execute)

    def map(self,hibp_objs):
        '''
        Asynchronously map the HIBP execution job to multiple queries.

        Attributes:
            - hibp_objs - list of HIBP objects
        '''
        jobs = [self.send(hibp_obj) for hibp_obj in hibp_objs]
        gevent.joinall(jobs, timeout=self.timeout)
        return hibp_objs

    def imap(self,hibp_objs):
        '''
        Lazily + Asynchronously map the HIBP execution job to multiple queries.

        Attributes:
            - hibp_objs - list of HIBP objects
        '''
        for hibp_obj in self.pool.imap_unordered(HIBP.execute, hibp_objs):
                yield hibp_obj.response
        self.pool.join()
