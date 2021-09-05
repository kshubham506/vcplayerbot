from urlextract import URLExtract
from utils.Logger import *
from utils.Singleton import Singleton


class ExtractLinks(metaclass=Singleton):
    def __init__(self):
        self.extractor = URLExtract()

    def extractLinksOld(self, a):
        try:
            # print("\nextract Links ")
            start = 0
            pos = 0
            links = []
            # if not a:
            # return links
            while a.find("http", start) >= 0:
                pos = a.find("http", start)
                end = a.find(" ", pos)
                end1 = a.find("\n", pos)
                if end == -1:
                    end = 99999
                if end1 == -1:
                    end1 = 99999
                fend = min(end, end1)
                if fend == 99999:
                    fend = len(a)
                links.append(a[pos:fend])

                start = fend

            nt = a[:]
            for i in links:
                nt = nt.replace(i, "")

            start = 0
            pos = 0
            while nt.find("www.", start) >= 0:
                pos = nt.find("www.", start)
                end = nt.find(" ", pos)
                end1 = nt.find("\n", pos)
                if end == -1:
                    end = 99999
                if end1 == -1:
                    end1 = 99999
                fend = min(end, end1)
                if fend == 99999:
                    fend = len(nt)
                links.append(nt[pos:fend])
                start = fend
            return links
        except Exception as ex:
            logException("Error in extractLinksOld : {} ".format(ex))
            return []

    def extractLinks(self, a):
        try:
            self.extractor.update_when_older(7)
            urls = self.extractor.find_urls(a)
            oldLi = self.extractLinksOld(a)
            if len(oldLi) > len(urls):
                return oldLi
            return urls
        except Exception as ex:
            logException("Error in extractLinks : {}".format(ex))
            return []
