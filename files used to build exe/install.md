# How to install app

You can just use `chatbot.exe`, but if you do not trust exe files from the internet. (Which you shouldn't), here's how to build it.

Firstly, download any freeze library and the requirements. I used `pyinstaller`
```shell
pip install pyinstaller, -r ../requirements.txt
```

Then, convert it into exe
```shell
pyinstaller --onefile --icon=GPT.ico -w main.py
```
I recommend the python version, as it launches faster.

