from hibp import HIBP, AsyncHIBP


class hibp(object):

    def __init__(self):
        self._HIBP = hibp.HIBP
        self._AsyncHIBP = hibp.AsyncHIBP()


    @property
    def HIBP(self):
        return self._HIBP

    @property
    def AsyncHIBP(self):
        return self._AsyncHIBP
