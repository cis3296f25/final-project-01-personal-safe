# Personal Password Safe
“Personal Safe” password manager will be developed as a lightweight application to securely store and manage passwords. It will allow users to create a master account, then add, retrieve, and organize all their login credentials, which will all be encrypted and decrypted locally on their own personal device. There are plenty of password managers like LastPass and 1Password, but unlike “Personal Safe”, many of them rely on cloud storage which introduces risks if their servers are compromised. This project is different because all encryption happens on the client side, meaning data never leaves the user’s device in a plain form. The intended users are everyday people who want better security or people who are just serious about their privacy. Ultimately, this project will provide a security tool for users wanting to protect their passwords. 

# How to run
Ensure Python 3.13.5 is installed. You can check by running: python3 --version

## To build the project:
1. Change directory to project root  
`cd final-project-04-personal-safe`
2. Create a virtual environment  
`python -m venv .venv`
3. Point to the new virtual environment as the source  
    * Windows  
    `.venv\Scripts\activate`
    * Mac/Linux  
    `source venv/bin/activate`
4. Install PyInstaller  
`pip install pyinstaller`
5. Build the application  
`pyinstaller --onefile --windowed main.py`
6. Run Personal Safe
    * Windows 
    Navigate to dist directory: 
    `cd dist`
    Run the executable file:
    `.\main.exe`
    * Mac/Linux  
    Allow the executable to run:  
    `chmod +x ./dist/main`  
    Run the executable:  
    `./dist/main` 
7. To deactivate virtual environment:
    `deactivate`

# How to contribute
Follow this project board to know the latest status of the project: [[http://...](https://github.com/orgs/cis3296f25/projects/47)] 

### How to build
- Use this github repository: [...](https://github.com/cis3296f25/final-project-04-personal-safe) 
- Use main branch for a more stable release.  
