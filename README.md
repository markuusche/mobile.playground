![](https://cdn-icons-png.freepik.com/128/9414/9414933.png)

Red-X-Cross
======
QA Automation Test

Project Dependencies
---------------------

- `python`
- `selenium`
- `pytest`
- `pyyaml`
- `requests`
- `faker`
- `gspread`
- `oauth2client`
- `google-api-python-client`
- `opencv-python`
- `pytesseract`
- `pyperclip`

Coverage
---------

   * [Mobile]

Pre-Requisites
--------------

1. Python 3 (Make sure python is added to your system PATH)
2. Python Extension (VSCode)
3. pip
4. virtualenv
5. [tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
------------------------------------------------
Setting Up First Run on Your Local Machine
------------------------------------------

1. Clone this project on your local machine

   ``https://github.com/gloofo/Red-X-Cross``

2. Open a terminal inside your local clone of the repository.

3. Using python's virtualenv, create a virtual environment inside the project.
   Run:
   ``virtualenv venv``

   where venv is the name of the virtual environment you are creating.
   It is also recommended to use __venv__ as the name of your virtual environment
   cause this is the recognized file exception on our ``.gitignore``

4. Activate the virtualenv you just created.
   
   * Windows CMD
      ``venv\Scripts\activate``
    
   * Windows Git Bash
      ``source venv\Scripts\activate``

   * Windows Powershell
      ``venv\Scripts\activate.ps1``

   * MacOS/Linux
      ``source venv/bin/activate``

5. Install the project dependencies.
   ``pip install -r requirements.txt``

Thats it! You have setup your local environment to run test for this project.

Run the script by simply running this command

   ``pytest -vs``

Run the script in headless mode

  ``pytest -vs --headless``

Run the script with gsreport in headless mode

   ``pytest -vs --gsreport --headless``
   
</br>

> **Note:** It is expected that you cannot run this project without the api base url and its endpoints.</br>
> The purpose of this project is to demonstrate that I've developed something for personal use and future reference.</br>
> If you have any questions, feel free to contact me through one of my socials on my github profile.

