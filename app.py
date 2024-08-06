from flask import Flask, render_template, redirect, url_for
from dotenv import load_dotenv
import os
import paramiko

load_dotenv()  # Carrega as variáveis do arquivo .env

app = Flask(__name__)

WAN1_NAME = os.getenv('WAN1_NAME')
WAN2_NAME = os.getenv('WAN2_NAME')
SCRIPT_WAN1 = os.getenv('SCRIPT_WAN1')
SCRIPT_WAN2 = os.getenv('SCRIPT_WAN2')
SCRIPT_TOGGLE = os.getenv('SCRIPT_TOGGLE')

ROUTER_IP = os.getenv('ROUTER_IP')
ROUTER_USER = os.getenv('ROUTER_USER')
ROUTER_PASSWORD = os.getenv('ROUTER_PASSWORD')

current_isp = WAN1_NAME  # Inicialmente configurado para WAN1_NAME

def execute_script(script_name):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ROUTER_IP, username=ROUTER_USER, password=ROUTER_PASSWORD)
        stdin, stdout, stderr = ssh.exec_command(f'/system script run {script_name}')
        output = stdout.read().decode()
        error = stderr.read().decode()
        ssh.close()
        return output, error
    except Exception as e:
        return str(e), ""

@app.route('/')
def index():
    return render_template('index.html', isp=current_isp, wan1_name=WAN1_NAME, wan2_name=WAN2_NAME)

@app.route('/toggle')
def toggle_isp():
    global current_isp
    output, error = execute_script(SCRIPT_TOGGLE)
    if current_isp == WAN1_NAME:
        current_isp = WAN2_NAME
    else:
        current_isp = WAN1_NAME
    return redirect(url_for('index'))

@app.route('/set/<wan>')
def set_isp(wan):
    global current_isp
    if wan == 'WAN1':
        output, error = execute_script(SCRIPT_WAN1)
        current_isp = WAN1_NAME
    elif wan == 'WAN2':
        output, error = execute_script(SCRIPT_WAN2)
        current_isp = WAN2_NAME
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)