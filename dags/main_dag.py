import os
import logging

from airflow import DAG
from datetime import datetime, timedelta, timezone
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.sensors.time_sensor import TimeSensor
from airflow.models import Variable


default_args = {
"owner": "Arthur",
"retries": 0,
"retry_delay": timedelta(minutes = 1)
}


log = logging.getLogger(__name__)


def initialize_scenarios(**kwargs):
    """This task initialises an esdl_ema_handler object, and stores important
    information from the handler in airflow variables. This is necessary as 
    these tasks have to be read by the bridging dag."""

    from esdl_to_ema import esdl_ema_handler
    
    ti = kwargs["ti"]
    dag_run = ti.dag_run
    if not dag_run.conf:
        n_runs = None
        input_file = "/opt/airflow/dags/inputs.xlsx"
        save = True
    else:
        n_runs = int(dag_run.conf["number_of_runs"])
        input_file = str(dag_run.conf["input_file"])
        save = dag_run.conf["save"]
    logging.info(input_file)
    handler = esdl_ema_handler(input_file = input_file, save_self = save, n_runs = n_runs, alter_json = True)
    handler.create_experiment_inputs()
    
    Variable.set(key = "num_runs", value = handler.experiments.num_samples*handler.experiments.num_runs_per_scen)
    Variable.set(key = "work_dir", value = handler.work_dir)
    Variable.set(key = "max_parallel", value = handler.airflow.parallel_processes)
    Variable.set(key = "short_wait", value = handler.airflow.short_wait)
    Variable.set(key = "long_wait", value = handler.airflow.long_wait)
    Variable.set(key = "model_id", value = handler.airflow.model_id)
    lst = [handler.sub_dirs[i] + "config.json" for i in range(handler.experiments.num_samples*handler.experiments.num_runs_per_scen)]
    Variable.set(key = "config_files", value = lst, serialize_json=True)
    logging.info(Variable.get("config_files", deserialize_json=True) )
    logging.info(type(Variable.get("config_files", deserialize_json = True)))
    return

def finalize_runs(**kwargs):
    import dill
    from esdl_to_ema import dummy_output_pairplot
    work_dir = Variable.get("work_dir")
    logging.info(str(work_dir))
    #Variable.set(key = "config_files", value = ["/opt/airflow/dags/meso_config.json"], serialize_json = True)
    with open(str(work_dir) + "handler", "rb") as file:
        handler = dill.load(file)
        logging.info(handler.sub_dirs)
        handler.load_experiment_output(save = True)
    
    dummy_output_pairplot(handler, group_by = handler.group_by_run_and_pol)

    return


with DAG(
    dag_id="Multiple_Model_Runs",
    default_args = default_args,
    description = "This is a test to check if the basic setup of this DAG works.",
    start_date = datetime(2023,1,15),
    schedule_interval = "@daily",
    catchup=False,
    is_paused_upon_creation=True

) as dag:
    initialize = PythonOperator(
        task_id = "initialize",
        python_callable = initialize_scenarios,
        )
    wait = TimeSensor(
    task_id="timeout_for_some_time",
    timeout=80,
    soft_fail=True,
    target_time=(datetime.now(tz=timezone.utc) + timedelta(seconds=65)).time(),
)
    write_results = PythonOperator(
        task_id = "write_results",
        python_callable = finalize_runs,
        )
    
    remove_variable = BashOperator(
         task_id="delete_variable",
         bash_command="airflow variables delete config_files",
         trigger_rule= "all_done"
)
    run_model_call_dag = TriggerDagRunOperator(
        task_id = "call_model_generator_dag",
        trigger_dag_id = "bridging_dag",
        wait_for_completion = True,
        deferrable= True,
        poke_interval = 20
        )
    
    initialize >> wait >> run_model_call_dag >> write_results >> remove_variable