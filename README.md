# Prolem statement
We want to offer an implementation through which the user can now stop the long-running task at any given point in time, and can choose to resume or terminate it. This will ensure that the resources like compute/memory/storage/time are used efficiently at our end, and do not go into processing tasks that have already been stopped (and then to roll back the work done post the stop-action)


### Solution
1. I have created /task, /resume, /stop, /terminate, /list_tasks endpoints.
2. /task will help to upload the necessary files in to the pipeline.
3. for the pipeline purpose I have used Queue DataStructure(FIFO).
4. /stop helps to stop the current running task and with this next task in the queue will start running.
5. /resume will resume the task based on the id provided for this the current task should stop running.
6. /terminate helps to completely stop the task fro further execution and now you wont be able to resume the task.
7. /list_tasks will list all the task in the queue with its metadata.


### Techology used 
1. Flask framework for creating API's.
2. Redis for scheduling tasks


### Files 
1. test.py : help to prepare the test data csv.
2. app.py : the main program responsible to perform task.


### Future Work
1. SQL Database can be used to persist task and its metadata.


### Steps to run
1. Create a python3 virtual enviornment.
2. Install the requirements via `pip install -r requirements.txt`.
3. Open two terminals in one run  `flask run` and in second run `rq worker`(make sure redis-server is installed).
4. Now that the server is running, you can make POST and GET request now.