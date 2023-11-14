# MultiModel uncertainty analysis tool
This GitHub contains a tool built for handeling uncertainty analysis of [multimodel](https://multi-model.nl/en_gb/) model runs.
It was made to easily run multiple instances of a Multi-Model, and analyse the outcomes of the different runs. 
It heavily relies on the Energy System Description Language (ESDL), a file format/programming language that stores information about energy systems. ESDL is used extensively in the Multi-Model project.
More information about ESDL can be found [here](https://www.esdl.nl).
Moreover, this tool uses [Airflow](https://airflow.apache.org), a pipe-line software that lets the user execute wildly different programming tasks in the correct sequence. More information about airflow can be found [here](https://airflow.apache.org).  
Lastly, the [Exploratory Modeling and Analysis (EMA) workbench](https://emaworkbench.readthedocs.io/en/latest/) was used in this project, as a way of handling the uncertainty sampling, and analysis.
The EMA workbench is a python package that contains tools for running models under deep uncertainty.

## Contents
The core Python code of this project contains a quick and user programmable way to write ESDL scenario's, and to analyse subsequent outcomes.
This package also contains [Directed Acyclic Graphs (DAG's)](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html). DAGs are the way that airflow stores pipe-lines. 
The dags in this project are used to run multiple Multimodel runs in airflow, just by activating one DAG.

Lastly, this folder contains a basic, working version of airflow, using a docker installation. 
Docker is a widely used way of creating a "virtual environment" for software that has specific needs, like airflow. Learn more about Docker [here](https://docker-curriculum.com). Using docker is  recommended for this project.
This repository contains all the files of the docker-airflow set up for this project. Airflow has a standard docker build, the one in this project one is a little more barebones. The airflow build is described in the docker-compose.yaml file.

## Standalone installation (tested for windows only)

First download or clone this repository to a local folder.
Then, [install docker desktop](https://www.docker.com/products/docker-desktop/), and open docker so that the docker engine is running.

Next, navigate to the project folder in windows explorer.
Now open a windows command prompt in that folder location, by doing the following.
For windows 10, type cmd in the file adress bar, and hit enter.
For windows 11 the same trick works, or you can right click and select "open in windows terminal".

In this terminal, we want to run a couple of commands to set up the docker airflow environment.
First, run the following command.
```
docker compose airflow-init
```
This should initialize the airflow installation in this folder. This command automatically looks for the docker-compose.yaml file, and uses it to set up the installation.

Next, we want to build our python environment (by installing some packages described in the requirements.txt file). Do this by entering the following line:
```
docker compose build
```

Now that we have everything setup, we should be able to launch a local airflow webserver using the following command.

```
docker compose up -d
```

Now, you can navicate to the airflow server by going to localhost:8080 in a web-browser. It might take a minute to set up.

The default username and password are both airflow.
After loging in, you should see a dashboard with all the dags of this project.

## Use
For direct use, the inputs.xlsx file in the dags folder contains the inputs for the DAG runs.
Enter your inputs in the inputs.xlsx to fit your needs, then trigger the Multiple_Model_Runs DAG from the airflow webserver.
The format explainer tab in the inputs.xlsx file gives more information about what can be changed, and how it should be entered.
A brief overview of the different settings is also provided below.

The user can choose which values in the ESDL file to use as uncertainties (and the upper and lower boundaries for these uncertainties), and which to use as levers. The user can insert policies with these levers. The user can also select where to fetch the base esdl file from, how many samples to create, how many times to duplicate the total runs, and other file specifications.

Moreover, the user can change a couple of important airflow settings, like the maximum amount of parallel tasks (to not overload the system).
Some tasks in the DAGs are [deferred](https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/deferring.html), the interval when they check if they can continue can be altered by the user.
Which outcomes to look at and save can also be changed by the user, as well as which model to run.
A more detailed description about the user inputs is given below. For a comprehensive overview, please use the inputs.xlsx file.

### User inputs
This module has a couple of key user features. The most important ones are listed below. 
For the most detailed information, please refer to the inputs.xlsx file.
+ Uncerainties in an ESDL file that should be altered between runs
  + Including a user defined lower and upper bound for these uncertainties
+ Policies build up out levers, for which the values are set by the user
+ The levers locations in the ESDL input file
+ The outcomes of interest from the ESDL output file
+ General settings
  + The file locations of each of the files required for the system to function
  + The amount of uncertainty scenario's to sample
  + Which sampler to use fo the uncertainty sampling
  + The amount or re-runs per scenario (to account for madel stochastisity)
  + Settings about the use of airflow, regarding the amount of parrallel task, and wait time between tasks

## Pipeline description
The tool contains three dags, two of which build up the pipeline itself. The last dag is a dummy model, which can be replaced by a Multi-model.
The workflow of the core dags is shown below.
![alt text](https://github.com/arthurronner/MultiModel_uncertainty_analysis_tool/blob/main/model_figure.png)

The multiple_model_runs DAG activates first, and initializes variables and scenarios that are required for the model runs.
The second task makes sure that the bridging dag fetches these settings correctly, airflow needs some time to ensure that the updated version is loaded.
The third task then calls be bridging dag.
The write_results task both fetches and analyses the results.
The delete_variable task resets a variable (so that the bridging dag does not crash when deleting/altering folders inbetween runs).

The bridging_dag itself has a linear structure of subsequent model runs. It makes sure that each of these runs are performed sequentially (per row), to make sure that the system is not overloaded.

The bridging_dag is set to do nothing if the Multiple_Model_Runs DAG is not currently running. 

## Limitations

This repository is by no means comprehensive, but should in principle be easy to extend depending on the users needs.
All of the functionality of this module is written in esdl_to_ema.py. Further documentation is provided in the python file itself.

List of limitations:
+ Regarding reading/writing from/to esdl files:
  + The program does not look at the entirety of an ESDL file. For now, it only considers area objects and asset objects.
  In these objects, it only considers costInformation and KPIs attributes.
  + The program cannot write a value that previously did not exist in the ESDL file.
  + If a location cannot be found, the program will simply not write the new value.
  + The handler only checks the FIRST instance of an esdl energy system.
    + In principle ESDL files can have multiple instances of the same energy system, for different points in time for example.
  
+ For now, the program only handles real, integer, and boolean parameters.
+ For now, the program only incorporates the montecarlo and sobol samplers. Other samplers can be easily implemented however.
+ Outcomes are all assumed to be scalar outcomes, there is currently no support for vector and/or time series outcomes in this handler.
+ Proper error handling has not been implemented in this module.
  + Most importantly, nearly no saveguards are implemented for when the input file is structured in a way that is not expected
   by the program.
+ This project has has not been tested with any of the multimodels.
+ The airflow settings used in this project are system dependent, and might not work perfectly on another machine.
  + The user is advised to change these settings when the airflow runs are not going smoothly.

If the user wants to extend the tool, all limitations (except for those that relate to airflow) are coded in the esdl_to_ema.py file.
If any of these features needs to be extended, please contact arthur.ronner@live.nl for help on how the code was written and how this extension could be added.

## Known issue(s)
Bug encountered once: "duplicate key value violates unique constraint "dag_run_dag_id_execution_date_key" when triggering a DAG.
Due to two models starting exactly at the same time, down to the millisecond. A delay could be added to the first of each parallel task in the bridging DAG to prevent this from happening. Unknown how often this bug occurs.

## Integration with the orchestrator

In the future, to use this module in combination with the model orchestrator, the following steps should be taken.
Here we assume that the user has a working orchestrator installation running with docker and airflow.
+ The python packages specified in the requirements.txt file in this repository should be added to the requirements.txt file in the orchestrator directory.
  + And to finalise this installation, the user should run the docker compose build command in the directory just like in the setup.
+ The ema_dag.py, run_models_dag.py, esdl_to_ema.py and inputs.xlsx files should be copied to the dags directory.
+ The correct settings in the inputs.xlsx file should be specified.
  + Special care should be taken in setting up the correct file locations.
+ Now, the Multiple_Model_Runs DAG can be run from the airflow webserver.
  
