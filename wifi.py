import os
import requests
import sys

class Wifi:

    def __init__(self, cfg):
        self.cfg = cfg
        self.events = []
        self.session_ids = []
    
    def getAll (self):
        self.events = []
        offset = 0
        step = int(self.cfg.filters.stepsize)
        isData = True
        while isData:
            # print("offset", offset, "step", step)
            r = requests.get(self.cfg.api.wifi, 
                params = {
                    "limit": f"{step}",
                    "offset": f"{offset}",
                    "filter[fcfs_seq_id][_eq]": self.cfg.fcfs_seq_id,
                    "filter[device_tag][_eq]": self.cfg.device_tag,
                },
                headers = {"X-Api-Key": os.getenv("APIDATAGOV")})
            try:
                theData = r.json()["data"]
                # print(theData)
                # time.sleep(10)
                if theData != []:
                    # print("appending ", len(theData), " elements")
                    self.events += theData
                    offset += step
                else:
                    isData = False
            except:
                # print("done gathering data")
                print("error in data fetch/JSON conversion")
                sys.exit(-1)
            # Find the unique session ids.
        # print("done")
        self.extractSessionIds()

    def extractSessionIds(self):
        session_ids = {}
        for o in self.events:
            session_ids[o["session_id"]] = 1
        self.session_ids = session_ids.keys()

    def extractUniquePatrons(self):
        patronsInSessions = {}
        for s in self.session_ids:
            patrons = set()
            for e in self.events:
                patrons.add(e["patron_index"])
            patronsInSessions[s] = patrons
        return patronsInSessions
        
    def getSessionIds(self):
        return self.session_ids
    
    def getSessionLength(self, sid):
        count = 0
        for e in self.events:
            if e["session_id"] == sid:
                count += 1
        return count

    def patronsInSession(self, sid):
        p = set()
        for e in self.events:
            if e["session_id"] == sid:
                p.add(e["patron_index"])
        return p

    def getEventIds(self, sid):
        es = set()
        for e in self.events:
            if e["session_id"] == sid:
                es.add(e["event_id"])
        return es

    def getEvents(self):
        return self.events
    
    def len(self):
        return len(self.events)