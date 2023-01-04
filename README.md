# Automating Facebook WebScraping service using Cloud Run
Automate the process of getting the latest post from webpage by using Cloud Run.
every day at 11pm Cloud Scheduler will send a HTTP POST request to Cloud Run, Cloud Run will start the automation by referencing the step in Dockerfile. The Dockerfile will create a docker container with:

* Python 3.10 image
* Manually install all the missing libraries
* Install Python dependencies
* Install Chrome
* Copy local code to container image
* Run the web server on container startup

Once the container has successfully been built, it will run the main.py file.
Main.py file will create a server using Python Flask

The process will:

* Create a chrome web driver
* Go to facebook and sign in 
* Go to target home page (cafestorythailand) 
* Auto-scrolling with Selenium
* Extract see more button
* Extract the selected data (text)
* Save it to Google Cloud Storage
