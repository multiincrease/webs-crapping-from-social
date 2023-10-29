
--after unzip the file open the folder

- if venv is available in folder dont create a virtual environment 
                         
                         or

- create a a virtual environment if venv is not there

        

- after create virtual environment 

    python -m venv venv

- activate the venv using

    myvenv\Scripts\activate
    For windows 
    source venv/bin/activate
    For Linux


- if venv is already exists dont need to install requirements 

- if you created your virtual environment
    - install requirements

        pip install -r requirements.txt

- now run main file using
  
  python main.py

 - after running flow of code
    - after running the main file select the option "Enter your choice (1/2/3/4): "
       - if you select google map (1):
            - "Enter the search term for Google Maps:" 
       - if you select facebook(2):
            - enter email or phone number 
            - enter password
            - enter page name or query to scrape
       - if you select instagram(3) 
            - enter email or phone number
            - enter password 
            - enter page name or any query 
            - enter limit of pages to scrape
       - if select twitter(4)
            - enter twitter handel name only the name after @ in twitter
             