import PySimpleGUI as sg
import operations as fs
import logging

# log_file = 'run_log.txt'
#
# # Logging setup to send one format of logs to a log file and one to stdout:
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(name)s, %(asctime)s, [%(levelname)s], %(message)s',
#     filename=log_file,
#     filemode='w')

# update default font
sg.SetOptions(font=('Helvetica', 11), element_padding=(5,5))
sg.theme('LightGrey6') # https://www.geeksforgeeks.org/themes-in-pysimplegui/

# --------------------------------- LAYOUT ---------------------------------

# list of stations
list_tcp = [[sg.Checkbox('TCP-OS'+str(i), key='TCP-OS'+str(i), auto_size_text=True, metadata='Enabled')] for i in range(51,57)]
list_mds = [[sg.Checkbox('MDS-OS' + str(i), key='MDS-OS' + str(i), auto_size_text=True, metadata='Enabled')] for i in range(61, 66)]
list_other = [[sg.Checkbox('IJS-OS23', key='IJS-OS23', auto_size_text=True, metadata='Enabled')],
              [sg.Checkbox('IJS-OS24', key='IJS-OS24', auto_size_text=True, metadata='Enabled')],
              [sg.Checkbox('TC-OS91', key='TC-OS91', auto_size_text=True, metadata='Enabled')]]

layout_select_stations = [[sg.T('', font=('Helvetica', 3))],
                        [sg.Radio("All stations", group_id='RADIO1', enable_events=True, key="all_stations"),
                        sg.Radio('Only TCP', group_id='RADIO1', enable_events=True, key='only_tcp'),
                        sg.Radio('Only MDS', group_id='RADIO1', enable_events=True, key='only_mds'),
                        sg.Radio('None', group_id='RADIO1', enable_events=True, key='none')],
                        [sg.HorizontalSeparator()],
                          [sg.Button('Check station up'), sg.Button('Check TCP is up')],
                        [sg.Frame(title='TCP', layout=list_tcp),
                        sg.Frame(title='MDS', layout=list_mds),
                        sg.Frame(title='IJS and TC', layout=list_other)],
                        [sg.T('')],
                        [sg.Text('TCP version'),
                        sg.Input('', size=(20,20), key='tcp_version')],
                        [sg.Text('TCP SW', ), sg.Input('', size=(20,20), key='tcp_sw')],
                        [sg.T('')]]

# layout for TAB_1: START/STOP
layout_tab1 = [[sg.T('')],
               [sg.Text('Set timeout (in seconds):')],
                [sg.Text('time interval between starting another station', font=('Helvetica', 9, 'italic'))],
                [sg.Input(size=(10,10), default_text='2', key='timeout')],
               [sg.T('')],
                [sg.Button('START TCP'),
                sg.Button('STOP TCP'),
                 sg.Button('RESTART station')],
               [sg.T('')],
               [sg.Text(key='-OUTPUT1-')]]

# layout for TAB_2: COPY FILES
layout_tab2 = [#[sg.T("")],
               [sg.Text('Select file or folder you want to copy to OS station')],
               [sg.Text("File: "), sg.Input(key='input_copy_file', enable_events=True, size=(35,10)), sg.FileBrowse()],
               [sg.Text("Folder: "), sg.Input(key='input_copy_folder', enable_events=True, size=(35,10)), sg.FolderBrowse()],
               [sg.HorizontalSeparator()],
               #[sg.T("")],
               [sg.Text("Set destination path on OS station")],
               [sg.InputCombo([i for i in fs.kmaster_paths], key='destination_path')],
               #[sg.T("")],
               [sg.Button('Copy')],
               [sg.T('')],
               [sg.Text(size=(40,10), key='-OUTPUT2-', auto_size_text=True)]]

# layout for TAB_3: DOWNLOAD FILES
layout_tab3 = [
               [sg.T("")],
               [sg.Text("Enter path to the file on the OS station that you want download")],
                [sg.Text('example:', font=('Helvetica', 9, 'italic'))],
                [sg.Input(key='input_download_file', enable_events=True, size=(35,10))],
               [sg.T("")],
               [sg.Button('Download')],
               [sg.T('')],
               [sg.Text(size=(40,10), key='-OUTPUT3-', auto_size_text=True)]]

# layout for TAB_4: LOGS
layout_tab4 = [[sg.T('')],
            [sg.Checkbox('TCP-log.txt', key='TCP-log.txt', auto_size_text=True, default=True)],
              [sg.Checkbox('TCP-Diagnostic.txt', key='TCP-Diagnostic.txt', auto_size_text=True)],
              [sg.Checkbox('TCP-Button-log.txt', key='TCP-Button-log.txt', auto_size_text=True)],
               [sg.Checkbox('KRemoteDesktopClient-log.txt', key='KRemoteDesktopClient-log.txt', auto_size_text=True)],
                [sg.Button('Download logs'),
                sg.Button('Clear logs')],
               [sg.T('')],
               [sg.Text(key='-OUTPUT4-')]]


# main layout
tab_menu =[[sg.Frame('SELECT STATIONS', layout=layout_select_stations, expand_x=True, expand_y=True)],
    [sg.TabGroup([[
    sg.Tab('START / STOP stations', layout_tab1, element_justification='center', key='TAB_1'),
    sg.Tab('Copy file to OS', layout_tab2, key='TAB_2'),
    sg.Tab('Download file from OS', layout_tab3, key='TAB_3'),
    sg.Tab('Logs', layout_tab4, key='TAB_4')]],
        tab_location='center', expand_x=True, expand_y=True, key='TAB_GROUP', enable_events=True, title_color='yellow', selected_title_color='green')
    ]]


# create list of stations that are selected by the user
# example output: ['TCP-OS51', 'TCP-OS52', 'TCP-OS53', 'TCP-OS54', 'TCP-OS55', 'TCP-OS56']
def selected_stations():
    active_stations = []
    for i in fs.extract_keys_from_checkboxes(list_tcp + list_mds + list_other):
        if values[i]:
            active_stations.append(i)
    #logging.DEBUG('Stations selected by the user: ', active_stations)
    return active_stations


if __name__ == '__main__':
    window = sg.Window('K-Master application', tab_menu, size=(600, 800), grab_anywhere=True, resizable=False,
                       margins=(10, 10))

    while True:
        event, values = window.read()
        print('e=', event, 'v=', values)

        if event == sg.WIN_CLOSED:  # always,  always give a way out!
            break

        # UPDATE CHECKBOXES [ALL, ONLY TCP, ONLY MDS]
        # create list with selected stations
        if event in ('all_stations', 'only_tcp', 'only_mds', 'none'):
            # when checkbox is NOT disabled, check or uncheck it
            if event == 'all_stations':
                [window[i].update(True) for i in fs.extract_keys_from_checkboxes(list_tcp + list_mds + list_other) if
                 window[i].metadata == 'Enabled']
            if event == 'only_tcp':
                [window[i].update(True) for i in fs.extract_keys_from_checkboxes(list_tcp) if
                 window[i].metadata == 'Enabled']
                [window[i].update(False) for i in fs.extract_keys_from_checkboxes(list_mds + list_other) if
                 window[i].metadata == 'Enabled']
            if event == 'only_mds':
                [window[i].update(True) for i in fs.extract_keys_from_checkboxes(list_mds) if
                 window[i].metadata == 'Enabled']
                [window[i].update(False) for i in fs.extract_keys_from_checkboxes(list_tcp + list_other) if
                 window[i].metadata == 'Enabled']
            if event == 'none':
                [window[i].update(False) for i in fs.extract_keys_from_checkboxes(list_tcp + list_mds + list_other) if
                 window[i].metadata == 'Enabled']


        # Check if station is reachable
        if event == 'Check station up':
            for i in fs.extract_keys_from_checkboxes(list_tcp + list_mds + list_other):
                if not fs.ping_station(fs.create_list_of_IP_servers(i)):
                        window[i].update(False)
                        window[i].update(disabled=True)
                        window[i].metadata = 'Disabled'
                else:
                    window[i].update(disabled=False)
                    window[i].metadata = 'Enabled'

        # Check if TCP is running
        if event == 'Check TCP is up':
            # first check if station is up, then check if TCP is launched
            for i in selected_stations():
                if fs.ping_station(fs.create_list_of_IP_servers(i)):
                    if fs.process_exists(host=fs.create_list_of_IP_servers(i)):
                        print(f"Station {i} is running")
                        window[i].update(text_color='#A03E9A')
                    else:
                        print(f"Station {i} is NOT running")
                        window[i].update(text_color="#233142")


        # validation: popup when no station is selected
        if event in ("START TCP", "STOP TCP", "RESTART station", "Copy", "Download", "Download logs", "Clear logs"):
            if len(selected_stations()) == 0:
                sg.popup_ok('No station selected')
                continue

        # OPERATIONS FOR TAB 1
        # RUN or CLOSE TCP application
        if values['TAB_GROUP'] == 'TAB_1':

            window['tcp_version'].update(disabled=False)
            window['tcp_sw'].update(disabled=True)

            # validation: popup when TCP version is empty or contains a letter
            if event == "START TCP" \
                    and (values['tcp_version'] == ''
                         or any(c.isalpha() for c in values['tcp_version'])):
                sg.popup_ok('Please enter valid TCP version')
                continue

            # action when pressing START or STOP button
            if event in ("START TCP", "STOP TCP", "RESTART station"):
                action = ''
                if event == "START TCP":
                    action = 'starting'
                    fs.start_stop_restart_station(selected_stations(), 'start', values['tcp_version'],
                                                  values['timeout'])
                elif event == 'STOP TCP':
                    action = 'stopped'
                    fs.start_stop_restart_station(selected_stations(), 'stop')
                else:
                    action = 'restarting'
                    fs.start_stop_restart_station(selected_stations(), 'restart', values['tcp_version'])
                window['-OUTPUT1-'].update((f'Following stations are {action}:\n\n' + ', '.join(selected_stations())))

        # OPERATIONS FOR TAB 2
        # copy file/folder to OS station
        if values['TAB_GROUP'] == 'TAB_2':

            window['tcp_sw'].update(disabled=True)
            window['tcp_version'].update(disabled=True)

            # only one field can be used at the same time: choose file or choose folder
            if event == 'input_copy_file':
                window['input_copy_folder'].update('')
            elif event == 'input_copy_folder':
                window['input_copy_file'].update('')

            # copy selected folder/path to OS
            # TODO add try/except - exception when some paths are not given or are wrong
            # TODO add exception when some file already exist - replace(rename) or save both
            if event == 'Copy':

                # validation: when file or folder or destination path are not given
                if values['input_copy_file'] == '' and values['input_copy_folder'] == '' or values[
                    'destination_path'] == '':
                    sg.popup_ok('Please select file, folder and destination path')
                    continue

                source_path = ''
                action = ''
                if values['input_copy_file'] != '':
                    source_path = values['input_copy_file']
                    action = 'copy_file_to_OS'
                elif values['input_copy_folder'] != '':
                    source_path = values['input_copy_folder']
                    action = 'copy_folder_to_OS'
                fs.copy_files_from_to_OS(source_path,
                                         values['destination_path'],
                                         fs.create_list_of_IP_servers(selected_stations()),
                                         action)
                window['-OUTPUT2-'].update('Files are copied now')

        # OPERATIONS FOR TAB 3
        # download file from OS station to the local computer
        if values['TAB_GROUP'] == 'TAB_3':

            window['tcp_sw'].update(disabled=True)
            window['tcp_version'].update(disabled=True)

            if event == 'Download':

                # validation: when file is not given
                if values['input_download_file'] == '':
                    sg.popup_ok('Please select file')
                    continue

                folder_path = sg.popup_get_folder('Select folder for saving files')
                if folder_path is not None and folder_path != '':
                    fs.copy_files_from_to_OS(source=values['input_download_file'],
                                             destination=folder_path,
                                             stations_ip=fs.create_list_of_IP_servers(selected_stations()),
                                             action='download_file')

        # OPERATIONS FOR TAB 4
        # clear or download logs
        if values['TAB_GROUP'] == 'TAB_4':

            window['tcp_version'].update(disabled=True)
            window['tcp_sw'].update(disabled=False)

            action = ''
            folder_path = ''
            selected_logs = []

            # create list with name of log files that are selected by the user
            for i in fs.extract_keys_from_checkboxes(layout_tab4):
                if '.txt' in i and values[i]:
                    selected_logs.append(i)

            # validation: popup when TCP SW is empty or contains a letter
            if event in ("Download logs", "Clear logs") \
                    and (values['tcp_sw'] == ''
                         or any(c.isalpha() for c in values['tcp_sw'])):
                sg.popup_ok('Please enter valid TCP SW')
                continue

            if event == 'Clear logs':
                action = 'clear_logs'
            elif event == 'Download logs':
                folder_path = sg.popup_get_folder('Select folder for saving files')
                if folder_path is not None:
                    action = 'download_logs'

            if action != '':
                fs.download_clear_logs(tcp_sw=values['tcp_sw'],
                                       logs_name=selected_logs,
                                       destination_path=folder_path,
                                       stations_ip=fs.create_list_of_IP_servers(selected_stations()),
                                       action=action)

    window.close()