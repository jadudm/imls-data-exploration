# Getting started

```
python3 -m venv venv
source ./bin/venv/activate
pip install -r requirements.txt
export APIDATAGOV="<valid api key>"
python3 main.py
```

## Using main.py

The config.yaml must be configured with appropriate URLs for the api.data.gov passthrough.

```
python main.py +fcfs_seq_id=ME0064-003 +device_tag=basement
```

all operations are on a given FCFS Sequence Id and a tag.