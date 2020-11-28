from flask import Flask, request
from rq import Queue, get_current_job
from fractions import Fraction
from rq.job import Job
import pandas as pd
import redis
import time

app = Flask(__name__)

r = redis.Redis()
queue = Queue(connection=r)
job_ids = []
data = pd.read_csv('test.csv')
total_rows = data.shape[0]

def upload() :
	job = get_current_job()

	current = job.meta['job_progess'].numerator * (total_rows // job.meta['job_progess'].denominator)

	for i in range(current, total_rows) :
		job = queue.fetch_job(job.id)

		if job.meta['status'] == 'stopped' or job.meta['status'] == "terminated": 
			return 
		
		print(i)
		
		job.refresh()
		job.meta['job_progess']+= Fraction(1, total_rows)
		job.save_meta()

		time.sleep(1)

	job.meta['job_progess'] = 'completed'


@app.route('/task',  methods=['GET', 'POST'])
def home() :
	job_id = str(len(job_ids) + 1)
	job_metadata = {
		'job_id' : job_id,
		'job_progess' : Fraction(0, total_rows),
		'status' :  'running'
	}
	job_object = queue.enqueue(upload, job_id = job_metadata['job_id'], meta = job_metadata, result_ttl=999999, ttl=999999, job_timeout=999999)
	job_ids.append(job_id)
	
	return app.make_response(('Uploaded!!', 200))

@app.route('/stop', methods=['GET', 'POST'])
def stop() :
	job_id = str(request.get_json().get('id'))
	job = queue.fetch_job(job_id)
	job.refresh()

	if job.meta['status'] == 'terminated' :
		return app.make_response(('Job has already been terminated', 400))

	if job.meta['status'] == 'stopped' :
		return app.make_response(('Job has already been stopped', 400))

	if job.meta['status'] == 'completed' :
		return app.make_response(('Job has already been stopped', 400))

	job.meta['status'] = 'stopped'
	job.save()
	job.cancel()

	return app.make_response(('Job was successfully stopped.', 200))


@app.route('/resume', methods=['GET', 'POST'])
def resume() :
	job_id = str(request.get_json().get('id'))
	job = queue.fetch_job(job_id)
	job.refresh()

	if job.meta['status'] == 'terminated' :
		return app.make_response(('Job has already been terminated', 400))

	if job.meta['status'] == 'resume' :
		return app.make_response(('Job is already in running.', 400))

	if job.meta['status'] == 'completed' :
		return app.make_response(('Job has already been stopped', 400))
	
	job.meta['status'] = 'resume'
	job_object = queue.enqueue(upload, job_id = job.meta['job_id'], 
					meta = job.meta, 
					result_ttl=999999, ttl=999999, job_timeout=999999)

	return app.make_response(('Job was successfully resumed.', 200))


@app.route('/terminate', methods=['GET', 'POST'])
def terminate() :
	job_id = str(request.get_json().get('id'))
	job = queue.fetch_job(job_id)
	job.refresh()

	if job.meta['status'] == 'terminated' :
		return app.make_response(('Job has already been terminated.', 400))

	if job.meta['status'] == 'resume' :
		return app.make_response(('Cant terminate the running app.', 400))

	if job.meta['status'] == 'completed' :
		return app.make_response(('Job has already been stopped', 400))

	job.meta['status'] = 'terminated'
	job.save()
	job.cancel()

	return app.make_response(('Job was successfully terminated.', 200))



@app.route('/list_tasks')
def list_task() :
	list_of_tasks = {}

	for i in job_ids :
		data = {}
		job = queue.fetch_job(i)

		data['job_id'] = job.id
		data['progress'] = str(round(float(job.meta['job_progess']) * 100, 2)) + '%'
		data['status'] = job.meta['status']

		list_of_tasks[i] = data

	return list_of_tasks


if __name__ == '__main__':
    app.run(debug=True)