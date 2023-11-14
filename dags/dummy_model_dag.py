# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 13:49:45 2023

@author: Arthur
"""
from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
import logging
from airflow.models import Variable

default_args = {
"owner": "Arthur",
"retries": 0,
"retry_delay": timedelta(minutes = 1),
}

def random_noise(**kwargs):
    from esdl_to_ema import dummy_model
    import dill
    ti = kwargs['ti']
    dag_run = ti.dag_run
    logging.info(dag_run.conf['tasks']["CTM_ETM_Iteration_1"]["model_config"])
    
    
    #Extract the working directory for this specific run
    first_task = next(iter(dag_run.conf['tasks']))
    sub_dir = dag_run.conf['tasks'][first_task]["model_config"].get("base_path")
    
    work_dir = Variable.get("work_dir")
    logging.info(str(sub_dir))
    
    with open(str(work_dir) + "handler", "rb") as file:
        handler = dill.load(file)
    
    
    dummy_model(handler, sub_dir)
    return 

with DAG(
    dag_id="dummy_dag",
    default_args = default_args,
    description = "This is a blank dag that is here to test if the setup of the code works",
    start_date = datetime(2023,1,15),
    schedule_interval = "@daily",
    catchup=False,
    is_paused_upon_creation=True

) as dag:
    initialize = PythonOperator(
        task_id = "initialize",
        python_callable= random_noise
    )
    finalize = EmptyOperator(
        task_id= "finalize"
        )
    initialize >> finalize
