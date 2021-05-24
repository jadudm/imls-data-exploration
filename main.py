import datetime
import hydra
from omegaconf import DictConfig, OmegaConf
import math, os, sys
from PIL import Image, ImageColor, ImageDraw, ImageFont
import wifi

cached = {}
def isValidPatron(w, sessionid, pndx):
    # They're valid if they've been around for more than 10 minutes,
    # but less than 8 hours. 
    minutes = 0
    if sessionid not in cached:
        cached[sessionid] = dict()

    if pndx in cached[sessionid]:
        minutes = cached[sessionid][pndx]
    else:
        minutes = countMinutes(w, sessionid, pndx)
        print(sessionid, pndx, minutes)
        cached[sessionid][pndx] = minutes
    result = False
    if minutes < int(w.cfg["filters"]["minimum"]):
        result = False
    elif minutes > int(w.cfg["filters"]["maximum"]):
        result = False
    else:
        result = True
    return result

# FIXME: This has to be a measure between the min and max
# timestamps that we saw a device. This cannot be a count
# of how many minutes a device was around.
def countMinutes(w, sessionid, pndx):
    mintime = None
    maxtime = None
    for e in w.getEvents():
        if e["session_id"] == sessionid and e["patron_index"] == pndx:
            ts = e["localtime"]
            time = datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
            if mintime == None:
                mintime = time
            if maxtime == None:
                maxtime = time
            if time < mintime:
                mintime = time
            if time > maxtime:
                maxtime = time

    diff = maxtime - mintime
    mins = math.ceil(diff.total_seconds() / 60)
    return mins

def getMinMaxTime(w, sessionid, pndx):
    mintime = None
    maxtime = None
    for e in w.getEvents():
        if e["session_id"] == sessionid and e["patron_index"] == pndx:
            ts = e["localtime"]
            time = datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
            if mintime == None:
                mintime = time
            if maxtime == None:
                maxtime = time
            if time < mintime:
                mintime = time
            if time > maxtime:
                maxtime = time
    return (mintime, maxtime)

def getMinMaxEventIds(w, sessionid, pndx):
    mintime = None
    maxtime = None
    for e in w.getEvents():
        if e["session_id"] == sessionid and e["patron_index"] == pndx:
            eid = e["event_id"]
            if mintime == None:
                mintime = eid
            if maxtime == None:
                maxtime = eid
            if  eid < mintime:
                mintime = eid
            if eid > maxtime:
                maxtime = eid
    return (mintime, maxtime)

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

def summaryStats(w):
    for min in [15, 30, 60, 90]:
        for max in [360, 480, 600, 720]:
            w.cfg["filters"]["minimum"] = min
            w.cfg["filters"]["maximum"] = max
            devices = getDevices(w)
            deviceMinutes = sum([countMinutes(w, d) for d in devices])
            patrons = getPatrons(w)
            patronMinutes = sum([countMinutes(w, p) for p in patrons])
            print("{},{},{},{},{},{},{},{},{}".format(
                w.cfg["fcfs_seq_id"],
                w.cfg["device_tag"],
                w.cfg["filters"]["minimum"],
                w.cfg["filters"]["maximum"],
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
    HOURLINEINTERVAL = 2
    sessions = w.getSessionIds()
    print("sessions: ", sessions)
    # Draw a picture of each session
    count = 0
    for s in sessions:
        eventMap = {}
        hoursDrawn = set()
        twelves = set()
        print(f"Processing session {count} - {s}")
        # width is number of patrons, height is number of unique event ids.
        width = max(w.patronsInSession(s)) + 1
        event_ids = sorted(w.getEventIds(s))
        minid = min(event_ids)

        # There's... gaps in the event IDs. We don't want gaps?
        # remapped = 0
        # for e in event_ids:
        #     eventMap[e] = remapped
        #     remapped += 1
        # height = len(eventMap) + 1
        for e in event_ids:
            eventMap[e] = e - minid

        height = max(event_ids) - minid
        print(f"[w, h]: {width}, {height}")

        if width != 0 and height != 0:
            img = Image.new( mode = "RGB", size = (width, height) )
            draw = ImageDraw.Draw(img)
            
            # Lets make the date/times 5% of the width, and the label 20% 
            fontsize = int(width / 3)
            fnt = ImageFont.truetype(hydra.utils.to_absolute_path("OpenSans-Bold.ttf"), fontsize)
            label = f"{w.cfg.fcfs_seq_id} {w.cfg.device_tag}"
            labelsize = draw.textsize(label, font=fnt)[0]
            while (labelsize > int(width * .10)) and fontsize > 8:
                #print(labelsize, int(width * .05))
                # print("labelsize", labelsize)
                fontsize = fontsize - 5
                fnt = ImageFont.truetype(hydra.utils.to_absolute_path("OpenSans-Bold.ttf"), fontsize)
                labelsize = draw.textsize(label, font=fnt)[0]

            filename = f"{count}-{s}-{w.cfg['filters']['minimum']}-{w.cfg['filters']['maximum']}-{w.cfg.fcfs_seq_id}-{w.cfg.device_tag}.png"
            draw.text((width - labelsize - int(labelsize * .1), 4), label, font=fnt, fill=(255,255,255,128))
            count += 1

            # Now, pixels need to be drawn.
            for e in w.getEvents():
                if e["session_id"] == s:
                    x = e["patron_index"]
                    y = eventMap[e["event_id"]]
                    # Draw lines every 2 hours?
                    time = datetime.datetime.strptime(e["localtime"], "%Y-%m-%dT%H:%M:%SZ")
                    dayhour = f"{time.day}-{time.hour}"

                    # Shrink the font if needed
                    fontsize = int(width / 4)
                    labelsize = draw.textsize(dayhour, font=fnt)[0]
                    while (labelsize > int(width * .05)) and fontsize > 8:
                        #print(labelsize, int(width * .0025))
                        #print("labelsize 2", labelsize, "fontsize", fontsize)
                        fontsize = fontsize - 2
                        fnt = ImageFont.truetype(hydra.utils.to_absolute_path("OpenSans-Bold.ttf"), fontsize)
                        labelsize = draw.textsize(label, font=fnt)[0]
            
            
                    if ((time.hour % HOURLINEINTERVAL == 0) and dayhour not in hoursDrawn):
                        hoursDrawn.add(dayhour)
                        draw.line([(0, y), (width, y)], fill="white")
                    if ((time.hour % 12 == 0) and dayhour not in twelves):
                        twelves.add(dayhour)
                        color = ""
                        if time.hour == 0:
                            color = "steelblue"
                        if time.hour == 12:
                            color = "palegoldenrod"
                        draw.text((0,y), dayhour, font=fnt, fill=(255,255,255,128))
                        draw.line([(0, y), (width, y)], fill=color, width=4)
                    
                    if isValidPatron(w, e["session_id"], e["patron_index"]):
                        draw.ellipse((x, y, x+2, y+2), fill=getColorNameByIndex(x))
                        (mineid, maxeid) = getMinMaxEventIds(w, e["session_id"], e["patron_index"])
                        draw.line([(x, eventMap[mineid]), (x, eventMap[maxeid])], fill=getColorNameByIndex(x))
                    else:
                        draw.ellipse((x, y, x+2, y+2), fill="lightgray")
            img.save(filename)

@hydra.main(config_name="config")
def main(cfg : DictConfig) -> None:
    w = wifi.makeWifi(cfg)
    w.getAll()
    # summaryStats(w)
    drawPrettyPictures(w)

    #print(len(w.session_ids), " sessions logged.")
    #print(len(devices), " devices / ", deviceMinutes, " minutes.")
    #print(len(patrons), " patrons / ", patronMinutes, " minutes.")

if __name__ == "__main__":
    if os.getenv("APIDATAGOV") == None:
        print("Please set APIDATAGOV in the env with a valid API key.")
        sys.exit(-1)
    main()
