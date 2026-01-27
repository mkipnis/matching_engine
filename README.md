
To build:
```
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

To run from the docker
```
docker compose up -d --build
```
URL: http://localhost:8050
