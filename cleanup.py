import datetime
import hydra
from omegaconf import DictConfig, OmegaConf
import os, pprint, re, sys
from PIL import Image, ImageColor, ImageDraw, ImageFont
import wifi


def first(ls):
    return ls[0]

def getDays(w, s, eids):
    days = set()
    for eid in eids:
        the_event = w.getEventById(eid)
        time = the_event["localtime"]
        date = re.search("(.*?)T.*", time, re.IGNORECASE)[1]
        days.add(date)
    return sorted(days)

def mapSessionEvents(w, sessions):
    session_maps = {}
    for s in sessions:
        remapped = {}
        # Get a set of the days in the dataset
        event_ids = sorted(w.getEventIds(s))
        days = getDays(w, s, event_ids)
        for day in days:
            print(day)
            if day not in remapped:
                remapped[day] = set()
            for eid in event_ids:
                the_event = w.getEventById(eid)
                # If this event is in this day, then add it to a list.
                if re.search(day, the_event["localtime"], re.IGNORECASE):
                    remapped[day].add(eid)
        session_maps[s] = remapped
    # pprint.pprint(session_maps)
    return session_maps

def remap(w, day, eids):
    mfgs = {}
    mfgndx = 0
    patrons = {}
    patronndx = 0
    for eid in sorted(eids):
        # print("inspecting", eid)
        evt = w.getEventById(eid)
        # print("evt", evt)
        evt["session_id"] = day
        if evt["manufacturer_index"] not in mfgs:
            mfgs[evt["manufacturer_index"]] = mfgndx
            evt["manufacturer_index"] = mfgndx
            w.setEvent(evt)
            mfgndx += 1
        else:
            evt["manufacturer_index"] = mfgs[evt["manufacturer_index"]]
            w.setEvent(evt)
        if evt["patron_index"] not in patrons:
            patrons[evt["patron_index"]] = patronndx
            evt["patron_index"] = patronndx
            w.setEvent(evt)
            patronndx += 1
        else:
            evt["patron_index"] = patrons[evt["patron_index"]]
            w.setEvent(evt)
    return eids
        

def cleanup(w):
    sessions = w.getSessionIds()
    maps = mapSessionEvents(w, sessions)
    # Now we have session maps, where a session is a set of eids keyed by day.
    # Now, each needs to be remapped, so that the mfg index starts at 0, and the patron index
    # starts at zero.
    newmaps = {}
    for session_id, daymap in maps.items():
        for day, event_ids in daymap.items():
            remapped = remap(w, day, event_ids)
            if session_id not in newmaps:
                newmaps[session_id] = {}
            newmaps[session_id][day] = remapped
    w.enpickle()

@hydra.main(config_name="config")
def main(cfg : DictConfig) -> None:
    w = wifi.makeWifi(cfg)
    w.getAll()
    cleanup(w)

if __name__ == "__main__":
    if os.getenv("APIDATAGOV") == None:
        print("Please set APIDATAGOV in the env with a valid API key.")
        sys.exit(-1)
    main()