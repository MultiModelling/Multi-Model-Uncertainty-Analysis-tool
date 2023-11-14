# Folder content
This folder contains most of the work of the project. Below is a list of files and what they contain.

+ test_runs is a folder in which the results of an example of the tool are stored.
  + Note that for the resultant pair plot, the category that is 0 was not written to the output file, as it does not exist in the ESDL file.
+ bridging_dag.py contains the intermediate DAG that calls all model runs.
+ dummy_model_dag.py contains the DAG of the dummy model. It uses the dummy_model function from the esdl_to_ema.py file.
+ esdl_to_ema.py contains most of the source code. It features the following.
  + A "handler" object that handles most of the actions of this toolbox (called esdl_to_ema_handler)
  + A dummy pairplot function, that creates a pairplot from model outputs
  + A dummy model function, that can be used to test this uncertainty analysis tool.
+ inputs.xlsx is the unput file that is read out by the model runs. Inputs used should be written in this file.
  + For now, the inputs.xlsx file contains a mock-up example based on the meso case model.
+ main_dag.py contains the DAG that the user should activate to start an uncertainty analysis run, called Multiple_Model_Runs.
+ meso_config.json contains the json input file for the meso case model. This is the base json file that is altered between runs for the example.
+ test.esdl contains the meso case esdl file, used as an input for the example run that is currently set up.
