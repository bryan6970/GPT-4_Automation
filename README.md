# GPT-4 Automation
Using GPT-4 to do automation!!

## How to use
Firstly, download any freeze library and the requirements. I used `pyinstaller`
```shell
pip install pyinstaller, -r requirements.txt
```

Then, convert it into exe
```shell
pyinstaller --onefile --icon="files used to build exe/GPT.ico" -w "files used to build exe/main.py"
```
I recommend the python version, as it launches faster.

Unnecessary (but good to have steps)
1. Put a path to a .pickle file for it to load faster 
2. To use gcalendar function, go to console.google.com and set up a project there. Use the calendar API, and download the OAuth credentials folder. Ensure to add yourself as the test user.


