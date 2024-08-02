> [!NOTE] 
> _It is expected that you cannot run this project without the api base url and its endpoints._ </br>
> _The purpose of this project is to demonstrate that I've developed something for personal use and future reference._ </br>
> _If you have any questions, feel free to contact me through one of my socials on my github profile._


![](https://cdn-icons-png.freepik.com/128/9414/9414933.png)

mobile.playground (casino)
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

Pre-requisites
--------------

1. Python 3 (Make sure python is added to your system PATH)
2. Python Extension (VSCode)
3. pip
4. virtualenv
5. [tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
------------------------------------------------
Setting up first run on your local machine
------------------------------------------

1. Clone this project on your local machine

   ```
   https://github.com/markuusche/mobile.playground
   ```

3. Open a terminal inside your local clone of the repository.

4. Using python's virtualenv, create a virtual environment inside the project. <br>
   Install:
   ```
   pip install virtualenv
   ```
   Create a virtual environment:
   ```
   virtualenv venv
   ```

   where venv is the name of the virtual environment you are creating.
   It is also recommended to use __venv__ as the name of your virtual environment
   cause this is the recognized file exception on our ``.gitignore``

6. Activate the virtualenv you just created.
   
   * Windows CMD
      ```bash
      venv\Scripts\activate
      ```
   * Windows Git Bash
      ```bash
      source venv/scripts/activate
      ```
   * Windows Powershell
      ```bash
      venv\Scripts\activate.ps1
      ```
   * MacOS/Linux
      ```bash
     source venv/bin/activate
      ```

7. Install the project dependencies.
    ```bash
     pip install -r requirements.txt
    ```

Thats it! You have setup your local environment to run test for this project.

Run the script in headless mode
```
pytest --headless
```

Run the script with a gsreport in headless mode
```
pytest --gsreport --headless
```
</br>

> [!CAUTION]
> Be aware that the test script might be flaky sometimes.

> [!IMPORTANT]
> If the test case failed on the first run. Re-run the test case base on what the test case that failed. <br>
> For ex. the baccarat game failed, you can run this specific test case with:
> `` pytest -k test_baccarat``.<br>
> If one or several test case failed, verify or replicate if the test case really failed.


