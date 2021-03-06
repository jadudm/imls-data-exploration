# Getting started

```
npm install
```

Live reload is also supported.

```
# (in a terminal)
make js
# (in another terminal)
make html
```

## Authorization

The `utils.js` file must be configured with the appropriate api.data.gov key.

## API Key

Create a (git ignored) `key.js`:

```
const api_key = "YOURKEYHERE"
module.exports = {
    api_key
  };
```

all operations are on a given FCFS Sequence Id and a tag.

## Examples for command line tool

**NOTE: It now produces pictures.**

If I want to explore Berea, KY, I would use:

```
python main.py +fcfs_seq_id="KY0069-003" +device_tag="berea1" 
```

At the time of this particular commit, that yielded:

```
2  sessions logged.
6  devices /  16150  minutes.
131  patrons /  8722  minutes.
```

This seems like too few sessions, so it is something we should investigate. The `config.yaml` specifies `filters.minimum` and `filters.maximum`, which determine if something is a patron or device. 

* If a given `patron_index` is present for less than `filters.minimum` minutes, it is not considered a valid patron.
* If a given `patron_index` is present for more than `filters.maximum` minutes, it is not considered a valid patron.
* If a given `patron_index` is present for more than `filters.maximum` minutes, it **is** considered a valid device.

Patrons are (we suspect) people. Devices are (we suspect) things like routers, TVs, printers, and any other wifi device that is everpresent. The example above uses a minimum of 10 minutes, and a maximum of 10 hours (600 minutes).

### Changing filter criteria on the command line

This is meant to be an exploratory tool, or the start of one. It was written before the JS explorations began, but it still might help double-check/inform our work.

The config file uses the Hydra framework to read it in/work with the YAML, meaning we can augment/override elements on the command line. This command adds two fields (the `fcfs_seq_id` and `device_tag`, both of which are required for the script to function) and overrides the minimum filter.

```
python main.py +fcfs_seq_id="KY0069-003" +device_tag="berea1" filters.minimum=60
```

With the override (requiring patrons to be present for 60 minutes) yields:

```
6  devices /  16150  minutes.
39  patrons /  6440  minutes.
```

