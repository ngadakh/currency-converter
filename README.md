# Currency Converter

This project is about transfering amount to user present in the system. This also support the top currencies present.

We have included the third party service to get the all currenies and it's corresponding exchange rates.

# Setup and Configuration

Before running application on locally we need to configure config parameters in `config.py`. 

(Some parameters with test values)

`SQLALCHEMY_DATABASE_URI : sqlite:/// + join(BASE_DIR, 'app.db')`

`BASE_CURRENCY = "USD"`

`FILE_UPLOAD_PATH = join(BASE_DIR, 'app', 'static')`

### Steps to run currency converter project locally
1. Install Python interpreter (preferably Python3)
1. Set appropriate parameters in `config.py` as said above.
2. Create a virtual environment `env` using following command 

       python3 -m venv env 
3. Activate virtual env using  

        source env/bin/activate
4. Run flask application

        python run.py



# Unit Test Cases
Unit test cases are integral part of this project. We need to do some configuration in `config.py` before running test cases.

Currently, the class `TestConfiguration` is already added in `config.py` but we can update that class anytime if we want to extend unit tests framework.

### How to run unit test cases?

    python -m unittest discover

# Coverage
1. Run unit test cases with `coverage` module

        coverage run -m unittest
2. Get the coverage report on terminal

        coverage report -m
3. Get the coverage report in HTML format

        coverage html



# Docker Containerization

### Steps to create image and run the application

1. Create `Dockerfile` on project path and add required image build steps in it. 
        
2. Create a docker image

        docker image build -t currency_converter .

3. Check docker images

        docker images

4. Run the application

        docker run -p 8080:8080 -d currency_converter

5. Open your favourite browser and open 

        http://localhost:8080


