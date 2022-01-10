import os
import subprocess # For executing a shell command
import time
import pathlib
import logging
import platform    # For getting the operating system name

# example paths in K-Master stations
kmaster_paths = [
    '',
    r'C:\_drop',
    r'C:\K-Master']


def ping_station(host):
    """
    Returns True if host (str) responds to a ping request.
    """
    # if parameter is a list, we will extract firs element
    if isinstance(host, list):
        host = host[0]

    if subprocess.run(["ping", "-n", "1", host], shell=True).returncode == 0:
        return True
    else:
        return False


# Create list of items (keys) based on the checkboxes layout
# needed for GUI update
# example output: ['TCP-OS51', 'TCP-OS52', 'TCP-OS53', 'TCP-OS54']
def extract_keys_from_checkboxes(layout_list):
    items_list = []
    for i in range(0, len(layout_list)):
        items_list.append(layout_list[i][0].Key)
    return [i for i in items_list if i]  # remove None values in the list


# # create list of stations that are selected by the user
# # f.e station_list = fs.create_item_list(list_tcp + list_mds + list_other)
# def selected_stations(station_list):
#     active_stations = []
#     for i in station_list:
#         if main_app.main().values[i]:
#             active_stations.append(i)
#     return active_stations


# extract OS numbers from given station list and create list with address IP for every station
# station list is generated from extract_keys_from_checkboxes() function
def create_list_of_IP_servers(station_list):
    servers = []
    ip_address_range = '172.30.201.'

    # if parameter is a string, we will change it into one-element list
    if isinstance(station_list, str) :
        station_list = [station_list]

    for i in station_list:
        servers.append(ip_address_range + (i.partition('-')[2].replace('OS', '')))
    return servers


def process_exists(host, process_name='KM.exe', user='user', password='pass'):

    # if parameter is a list, we will extract firs element
    if isinstance(host, list):
        host = host[0]

    call = 'TASKLIST', '/s', host, '/u', user, '/p', password, '/FI', 'imagename eq %s' % process_name

    output = subprocess.check_output(call, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, shell=True).decode('cp866', 'ignore')

    if process_name in output:
        return True
    else:
        return False


def start_stop_restart_station(station_list, action, tcp_version='', timeout=''):
    # TODO excepction when tcpversion is wrong or not installed on remote
    # TODO check if stopper -restart will restart station when tcp is not running

    arg = ''
    tcp_app_path = fr'"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\TCPSystemv{tcp_version}\Start TCP System v{tcp_version}.lnk"'

    # validation: set default value when timeout will not be given by the user
    if timeout == '':
        timeout = 3

    if action == 'start':
        arg = tcp_app_path
    elif action == 'stop':
        arg = "Stopper.exe"
    else:
        arg = "Stopper.exe -Restart"

    for server_ip in create_list_of_IP_servers(station_list):
        print(f'Station {server_ip}: ', arg)
        subprocess.Popen('psexec -s -i -accepteula \\\\' + server_ip + ' cmd /c ' + arg, stdin=subprocess.DEVNULL,
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        time.sleep(int(timeout))

    print('END')


def copy_file(source, destination, parameters):
    # validation: check if file exists on OS station
    if pathlib.Path(str(source)).exists():
        print(f'Copying from {source} to {destination}')
        subprocess.call(['xcopy', str(pathlib.Path(source)), str(pathlib.Path(destination)), parameters], shell=True)
    else:
        print('File {} does not exist'.format(source))
    # try:
    #     subprocess.call(['xcopy', str(pathlib.Path(source)), str(pathlib.Path(destination)), parameters], shell=True)
    # except:
    #     pass

def remove_file(file_path):
    # TODO add verification when file exis
    # The process cannot access the file because it is being used by another process

    if pathlib.Path(str(file_path)).exists():
        print(f'Removing {file_path}')
        subprocess.call(['del', '/Q/F', file_path], shell=True)
    else:
        print('File {} does not exist'.format(file_path))


def copy_files_from_to_OS(source, destination, stations_ip, action=''):

    if action == 'copy_folder_to_OS':  # copy folder TO OS station
        directory_name = os.path.basename(source)  # get directory name from destination path
        destination_path = r'\c$\\' + destination.replace(r'C:', '') + '\\' + directory_name + '\\'
        source_path = source
        parameters = '/E/C/Y/I'
    elif action == 'copy_file_to_OS':  # copy file TO OS station
        destination_path = r'\c$\\' + destination.replace(r'C:', '')
        source_path = source
        parameters = '/C/Y'
    else:  # action = 'download_file' or 'download_logs' # copy file FROM OS station
        file_name = os.path.basename(source)  # get name of the file we want to download
        destination_path = destination
        source_path = r'\c$\\' + source.replace(r'C:', '')
        parameters = '/C/Y'

    # copy (and replace) file/folder
    for station in stations_ip:
        station_path = r'\\' + station
        #print(True if os.system("ping -c 1 " + station) == 0 else False)
        if action in ('copy_folder_to_OS', 'copy_file_to_OS'):
            copy_file(source_path, station_path + destination_path, parameters)
        else:
            # copy file FROM OS station to local computer
            copy_file(station_path + source_path, destination, parameters)

            # rename file so the name contains OS number, f.e. TCP.sdf -> TCP51.sdf
            # TODO FileNotFoundError: [WinError 2] The system cannot find the file specified: 'C:/Users/renatc/Downloads\\TCP-log.txt' -> 'C:/Users/renatc/Downloads\\TCP-log55.txt'
            # TODO FileExistsError: [WinError 183] Cannot create a file when that file already exists: 'C:/Users/renatc/Downloads/test\\TCP-log.txt' -> 'C:/Users/renatc/Downloads/test\\TCP-log51.txt'
            os_number = station.split('.')[-1]
            try:
                os.rename(os.path.join(destination, file_name),
                          os.path.join(destination,
                                       file_name.split('.')[0] + os_number + '.' + file_name.split('.')[1]))
            except (FileNotFoundError, FileExistsError, IndexError):
                print('Error while renaming file')
    print('END')


def remove_file_from_OS(stations_ip, file_path):
    source_path = r'\c$' + file_path.replace(r'C:', '')
    for station in stations_ip:
        remove_file(file_path=r'\\' + station + source_path)
    print('END')


def download_clear_logs(tcp_sw, logs_name, stations_ip, destination_path='', action=''):
    log_path = rf'C:\K-Master\TCP\TCPv{tcp_sw}\Logs'

    for log in logs_name:
        if action == 'download_logs':
            copy_files_from_to_OS(source=os.path.join(log_path, log), destination=destination_path, stations_ip=stations_ip)
        elif action == 'clear_logs':
            remove_file_from_OS(stations_ip, os.path.join(log_path, log))
