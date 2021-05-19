import hydra
from omegaconf import DictConfig, OmegaConf
import os, sys
from PIL import Image, ImageColor, ImageDraw
import wifi

def isValidPatron(w, pndx):
    # They're valid if they've been around for more than 10 minutes,
    # but less than 8 hours. 
    minutes = countMinutes(w, pndx)
    if minutes < w.cfg["filters"]["minimum"]:
        return False
    elif minutes > w.cfg["filters"]["maximum"]:
        return False
    else:
        return True


def countMinutes(w, pndx):
    minutes = 0
    for e in w.getEvents():
        if e["patron_index"] == pndx:
            minutes += 1
    return minutes

def getDevices(w):
    # Anything lingering too long?
    devices = set()
    uniqP = w.extractUniquePatrons()
    # Now, given a { session : set(patron_index)} structure
    for s in uniqP:
        for pndx in uniqP[s]:
            m = countMinutes(w, pndx)
            if m > w.cfg["filters"]["maximum"]:
                devices.add(pndx)
    return devices

def getPatrons(w):
    patrons = set()
    uniqP = w.extractUniquePatrons()
    # Now, given a { session : set(patron_index)} structure
    for s in uniqP:
        for pndx in uniqP[s]:
            # Given a patron index, lets see if they are "valid"
            if isValidPatron(w, pndx):
                patrons.add(pndx)
    return patrons

def summaryStats(cfg):
    for min in [15, 30, 60, 90]:
        for max in [360, 480, 600, 720]:
            cfg["filters"]["minimum"] = min
            cfg["filters"]["maximum"] = max
            devices = getDevices(w)
            deviceMinutes = sum([countMinutes(w, d) for d in devices])
            patrons = getPatrons(w)
            patronMinutes = sum([countMinutes(w, p) for p in patrons])
            print("{},{},{},{},{},{},{},{},{}".format(
                cfg["fcfs_seq_id"],
                cfg["device_tag"],
                cfg["filters"]["minimum"],
                cfg["filters"]["maximum"],
                len(w.session_ids),
                len(devices),
                deviceMinutes,
                len(patrons),
                patronMinutes
            ))

def getColorNameByIndex(ndx):
    colors = list(ImageColor.colormap.keys())
    return colors[ndx % len(colors)]


def drawPrettyPictures(w):
    sessions = w.getSessionIds()
    # Draw a picture of each session
    for s in sessions:
        eventMap = {}
        print(f"Processing session {s}")
        # width is number of patrons, height is number of unique event ids.
        width = max(w.patronsInSession(s)) + 1
        # There's... gaps in the event IDs. We don't want gaps.
        event_ids = sorted(w.getEventIds(s))
        remapped = 0
        for e in event_ids:
            eventMap[e] = remapped
            remapped += 1
        height = len(eventMap) + 1
        print(f"[w, h]: {width}, {height}")
        img = Image.new( mode = "RGB", size = (width, height) )
        draw = ImageDraw.Draw(img)
        filename = f"{s}-{w.cfg.fcfs_seq_id}-{w.cfg.device_tag}.png"
        # Now, pixels need to be drawn.
        for e in w.getEvents():
            if e["session_id"] == s:
                x = e["patron_index"]
                y = eventMap[e["event_id"]]
                print(f"[x, y]: [{x}, {y}]")
                # img.putpixel((x, y), (155,155,55)) 
                draw.ellipse((x, y, x+2, y+2), fill=getColorNameByIndex(x))
        img.save(filename)

@hydra.main(config_name="config")
def main(cfg : DictConfig) -> None:
    w = wifi.Wifi(cfg)
    w.getAll()
    # summaryStats(cfg)
    drawPrettyPictures(w)

    #print(len(w.session_ids), " sessions logged.")
    #print(len(devices), " devices / ", deviceMinutes, " minutes.")
    #print(len(patrons), " patrons / ", patronMinutes, " minutes.")

if __name__ == "__main__":
    if os.getenv("APIDATAGOV") == None:
        print("Please set APIDATAGOV in the env with a valid API key.")
        sys.exit(-1)
    main()
