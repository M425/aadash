import urllib.request, json, os

def response(msg='', body=''):
    return {
        'msg': msg,
        'body': body
    }

def ans_api(method='GET', path='', body={}):
    url = os.environ.get('ADASH_AAP_URL', 'http://localhost:5000')
    url = f'{url}/{path}'
    response = urllib.request.urlopen(f'{url}')
    data = response.read().decode(response.headers.get_content_charset())
    return data

def ans_api_job_stdout(job_id):
    data = ans_api(method='GET', path=f'api/v2/jobs/{job_id}/stdout/') 
    return data