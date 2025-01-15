import dramlib as dl
import json
from pathlib import Path
from os.path import join
from os import makedirs
import os

import pkg_process_input as ppi
import pkg_process_data as ppd

trace_analyzer_file = "DRAMSys_ddr4-example_example_ch0.tdb"
path_file = 'paths.json'
control_file = 'control.json'
platform = 'cnn'
dsys_cfg = "ddr4-example.json"

with open(control_file, 'r') as file:
    control_data = json.load(file)['control']
    path = control_data['path']
    prefix = control_data['prefix']
    exp_folder = join(path, f"exp_{prefix}")
    ctrl_path = join(exp_folder, control_data['ctrl_path'])
    input_path = join(exp_folder, control_data['input_path'])
    apps = control_data['apps']
    data = control_data['addr_map']
    addr_maps = [
        # addr_map, dsys_cfg
        (key, data[key]) for key in data
    ]
    data = control_data['var_n_val']
    var_n_val = [
        # variable, values
        (key, data[key]) for key in data
    ]
    file.close()

makedirs(ctrl_path, exist_ok=True)
makedirs(input_path, exist_ok=True)

ctrl_inputs = ppd.get_ctrl_inputs(ctrl_path, dsys_cfg, apps, var_n_val, platform, prefix)

address_map_inputs = ppd.get_addr_map_inputs(addr_maps, input_path, apps, var_n_val, platform, prefix)

ctrl_cfgs = ppi.start_ctrl(ctrl_inputs, path_file)

for app in ctrl_cfgs:
    for config in ctrl_cfgs[app]:
        main_file, file_list = ctrl_cfgs[app][config] 
        for file in file_list:
            print(f'running {file}...')
            dl.run_cnn(file)
            print(f'converting trace {file}...')
            dl.conv_trace(file)
            print(f'done {file}')

dsys_cfgs = ppi.start_dsys(ctrl_cfgs, address_map_inputs, path_file)

for addr_map in dsys_cfgs:
    for app in dsys_cfgs[addr_map]:
        for config in dsys_cfgs[addr_map][app]:
            main_file, file_list = dsys_cfgs[addr_map][app][config]
            for file in file_list:
                ppi.update_trace_file(file)
                dl.run_dramsys(file)
                new_trace_analyzer_file = ppi.create_trace_analyzer_file(file)
                os.system(f'mv {trace_analyzer_file} {new_trace_analyzer_file}')

for addr_map in dsys_cfgs:
    for app in dsys_cfgs[addr_map]:
        for config in dsys_cfgs[addr_map][app]:
            main_file, file_list = dsys_cfgs[addr_map][app][config]
            for file in file_list:
                dcf = dl.ConfigFile()
                dcf.update_config(file)
                data = dcf.get_parser_data()

                output_dramsys  = data['path_to_output_dramsys']
                output_parsed   = data['path_to_output_parsed']

                parser = dl.DsysParser(power=False)
                parser.parse_file(output_dramsys, output_file=output_parsed)
            dl.group(main_file)
            ppi.plot(main_file)