# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 14:35:26 2023

@author: Arthur
"""

import os
import logging
import json

from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.operators.empty import EmptyOperator
from airflow.models import Variable


default_args = {
"owner": "Arthur",
"retries": 0,
"retry_delay": timedelta(minutes = 1)
}



with DAG(
    dag_id="bridging_dag",
    default_args = default_args,
    description = "This is a test to check if the basic setup of this DAG works.",
    start_date = datetime(2023,1,15),
    schedule_interval = "@daily",
    catchup=False,
    is_paused_upon_creation=True

) as dag:
    start = EmptyOperator(
        task_id= "start")
    
    finalize = EmptyOperator(
        task_id = "finalize")
    
    #This is not recommended behaviour, variables should not be accessed here in the ideal case.
    #Didn't yet find an alternative however.

    max_par = int(Variable.get("max_parallel", default_var=4)) 
    config_files = Variable.get("config_files", deserialize_json=True, default_var= [])
    model_id = Variable.get("model_id")
    num_runs = int(Variable.get("num_runs", default_var=4))
    short_wait = int(Variable.get("wait_time", default_var = 5))
    ind = 0
    prev = start
    num_large_blocks = num_runs % max_par
    
    #Check if the config files make sense. 
    if len(config_files) == num_runs:    
        for i in range(num_runs):
            with open(config_files[i],"r") as file:
                config = json.load(file)

                task = TriggerDagRunOperator(
                    task_id = f"trigger_model_{i}",
                    trigger_dag_id= model_id,
                    wait_for_completion=True,
                    poke_interval = short_wait,
                    deferrable=True,
                    conf= config
                    )
            
            if num_large_blocks > 0:
                block_size = int((num_runs/max_par) + 1)
            else:
                block_size = int(num_runs/max_par)
    
            if i - ind < block_size - 1:
                prev >> task
                prev = task
            
            elif i - ind == block_size - 1:
                prev >> task >> finalize
                prev = start
                
                num_large_blocks -= 1
                ind = i + 1   
    else:
        start >> finalize