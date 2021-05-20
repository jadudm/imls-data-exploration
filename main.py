import datetime
import hydra
from omegaconf import DictConfig, OmegaConf
import os, sys
from PIL import Image, ImageColor, ImageDraw, ImageFont
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
    HOURLINEINTERVAL = 4
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
            fontsize = 120
            if width < 1500:
                fontsize = 60
            fnt = ImageFont.truetype(hydra.utils.to_absolute_path("OpenSans-Bold.ttf"), fontsize)
            draw = ImageDraw.Draw(img)
            filename = f"{count}-{s}-{w.cfg.fcfs_seq_id}-{w.cfg.device_tag}.png"
            label = f"{w.cfg.fcfs_seq_id} {w.cfg.device_tag}"
            labelsize = draw.textsize(label, font=fnt)[0]
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
                    draw.ellipse((x, y, x+2, y+2), fill=getColorNameByIndex(x))
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
