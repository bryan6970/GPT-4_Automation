# How to install app

Firstly, download any freeze library and the requirements. I used `pyinstaller`
```shell
pip install pyinstaller, -r ../requirements.txt
```

Then, convert it into exe
```shell
pyinstaller --onefile --icon=GPT.ico -w main.py
```
I recommend the python version, as it launches faster.

