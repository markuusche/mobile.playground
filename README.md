![](https://cdn-icons-png.freepik.com/128/9414/9414933.png)

Red-X-Cross
======
QA Automation Test

Project Dependencies
---------------------

- `Python`
- `Selenium`
- `Pytest`
- `Pyyaml`
- `Requests`
- `Faker`

Coverage
---------

   * OG [Mobile] [Vue]

Pre-Requisites
--------------

1. Python 3 (Make sure python is added to your system PATH)
2. Python Extension (VSCode)
3. pip
4. virtualenv

------------------------------------------------
Setting Up First Run on Your Local Machine
------------------------------------------

1. Clone this project on your local machine

   ``https://github.com/gloofo/Red-X-Cross.git``

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

   ``pytest -vs`` or ``pytest -vs --headless``


