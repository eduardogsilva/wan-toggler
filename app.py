from flask import Flask, render_template, redirect, url_for, request, Response
from dotenv import load_dotenv
import os
import paramiko

load_dotenv()

app = Flask(__name__)

WAN1_NAME = os.getenv('WAN1_NAME')
WAN2_NAME = os.getenv('WAN2_NAME')
WAN1_INTERFACE = os.getenv('WAN1_INTERFACE')
WAN2_INTERFACE = os.getenv('WAN2_INTERFACE')
SCRIPT_WAN1 = os.getenv('SCRIPT_WAN1')
SCRIPT_WAN2 = os.getenv('SCRIPT_WAN2')
SCRIPT_TOGGLE = os.getenv('SCRIPT_TOGGLE')
SCRIPT_CHECK = os.getenv('SCRIPT_CHECK')
HTML_REFRESH = int(os.getenv('HTML_REFRESH', 0))
WEB_USER = os.getenv('WEB_USER')
WEB_PASSWORD = os.getenv('WEB_PASSWORD', '')

ROUTER_IP = os.getenv('ROUTER_IP')
ROUTER_USER = os.getenv('ROUTER_USER')
ROUTER_PASSWORD = os.getenv('ROUTER_PASSWORD')

def execute_script(script_name):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ROUTER_IP, username=ROUTER_USER, password=ROUTER_PASSWORD,
                    look_for_keys=False, timeout=10, allow_agent=False)
        stdin, stdout, stderr = ssh.exec_command(f'/system script run {script_name}')
        output = stdout.read().decode()
        error = stderr.read().decode()
        ssh.close()
        if error:
            return error
        if output:
            return output
        return None
    except Exception as e:
        return str(e)


def check_current_isp():
    output = execute_script(SCRIPT_CHECK)
    if '%' in output:
        interface = output.split('%')[1].strip()
        if interface == WAN1_INTERFACE:
            return WAN1_NAME
        elif interface == WAN2_INTERFACE:
            return WAN2_NAME
    return output


def check_auth(username, password):
    return username == WEB_USER and password == WEB_PASSWORD


def authenticate():
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


@app.before_request
def require_auth():
    if WEB_USER and WEB_PASSWORD is not None:  # Verifica se WEB_USER está definido e WEB_PASSWORD pode ser vazio
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()


@app.route('/')
def index():
    current_isp = check_current_isp()
    error = request.args.get('error')
    return render_template('index.html', isp=current_isp, wan1_name=WAN1_NAME, wan2_name=WAN2_NAME, error=error, refresh=HTML_REFRESH)


@app.route('/toggle')
def toggle_isp():
    error = execute_script(SCRIPT_TOGGLE)
    if error:
        return redirect(url_for('index', error=error))
    return redirect(url_for('index'))


@app.route('/set/<wan>')
def set_isp(wan):
    if wan == 'WAN1':
        error = execute_script(SCRIPT_WAN1)
        if error:
            return redirect(url_for('index', error=error))
    elif wan == 'WAN2':
        error = execute_script(SCRIPT_WAN2)
        if error:
            return redirect(url_for('index', error=error))
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
