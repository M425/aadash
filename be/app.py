# flask_web/app.py
from flask import Flask, jsonify, send_from_directory, current_app
import ansible_utils as ansible_utils
import api_utils

app = Flask(
    __name__,
    static_url_path='', 
    static_folder='web/static',
    template_folder='web/templates'
)

@app.errorhandler(500)
def internal_error(error):
    # note that we set the 404 status explicitly
    return jsonify(api_utils.response(msg=f'500 Error')), 500

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return jsonify(api_utils.response(msg='Not found')), 404

@app.after_request
def apply_caching(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

@app.route('/', methods=['GET'])
def redirect_to_index():
    return current_app.send_static_file('index.html')

@app.route('/api/v2/jobs/<job_id>/stdout/')
def sample_api_job_stdout(job_id):
    fileout = open('ansible_job_sample.txt', 'r')
    contents = fileout.read()
    fileout.close()
    return contents


@app.route('/api/job/<job_id>')
def api_job_get(job_id):
    job_stdout = api_utils.ans_api_job_stdout(job_id)
    job_parsed = ansible_utils.parse(job_stdout)
    return jsonify(api_utils.response(msg="Job parsed", body=job_parsed))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
