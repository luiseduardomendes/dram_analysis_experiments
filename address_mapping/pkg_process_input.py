import dramlib as dl
import json
from os.path import join
from os import makedirs
import os

def create_input(path, app, variable, values, dsys_cfg, prefix, platform):
    folder = join(path, app)
    makedirs(folder, exist_ok=True)
    file = join(folder, variable + ".json")
    data = {    
        "params":{
            "prefix": prefix,
            "platform": platform,
            "app": app,
            "dsys_cfg": dsys_cfg,
            "variable": variable,
            "values": values
        }
    }
    with open(file, 'w') as f:
        json.dump(data, f)
        f.close()
    return file

def start(input_file, path_file):
    dcf = dl.ConfigFile()
    dcf.start(input_file, path_file)
    default_file = dcf.save_defaults()
    main_file, file_list = dcf.save()
    return default_file, main_file, file_list
    
def start_ctrl(ctrl_inputs, path_file):
    ctrl_cfgs = {}
    for app in ctrl_inputs:
        ctrl_cfgs[app] = {}
        for config in ctrl_inputs[app]:
            default_file, main_file, file_list = start(ctrl_inputs[app][config], path_file)
            ctrl_cfgs[app][config] = (main_file, file_list)
    return ctrl_cfgs

def __update__(ctrl, exp):
    dcf_exp = dl.ConfigFile()
    dcf_exp.update_config(exp)
    
    dcf_ctrl = dl.ConfigFile()
    dcf_ctrl.update_config(ctrl)

    if dcf_ctrl.data['params']['value'] == dcf_exp.data['params']['value']:
        dcf_exp.data['paths']['path_to_created_trace_file']  = dcf_ctrl.data['paths']['path_to_created_trace_file'] 

        df = dcf_exp.create_experiment(exp, dcf_exp.data)
        
    else:
        raise Exception("Mismatch")

def update_trace(control_cfg, exp_cfg):
    main_file_control,  file_list_control = control_cfg
    main_file_exp,      file_list_exp     = exp_cfg


    for ctrl, exp in zip(file_list_control, file_list_exp):  
        __update__(ctrl, exp)
    __update__(main_file_control, main_file_exp)

def start_dsys(ctrl_cfgs, dsys_data, path_file):
    dsys_cfgs = {}
    for addr_map in dsys_data:
        dsys_cfgs[addr_map] = {}
        for app in dsys_data[addr_map]:
            dsys_cfgs[addr_map][app] = {}
            for config in dsys_data[addr_map][app]:
                files = dsys_data[addr_map][app][config]
                exp_input = files
                control_cfg = ctrl_cfgs[app][config]
                default_file, main_file, file_list = start(exp_input, path_file)
                exp_cfg = (main_file, file_list)

                dsys_cfgs[addr_map][app][config] = exp_cfg

                update_trace(control_cfg, exp_cfg)
    return dsys_cfgs

def update_trace_file(spc_cfg_file):
    dcf = dl.ConfigFile()
    dcf.update_config(spc_cfg_file)
    data = dcf.get_conv_data()

    dramsys_path    = data['path_to_dramsys']
    new_trace_file  = data['path_to_new_trace_file']
    old_trace_file  = data['path_to_old_trace_file']
    new_cfg_file    = data['path_to_new_cfg_file']
    old_cfg_file    = data['path_to_old_cfg_file']
    clkmhz          = data['clkMhz']

    conv = dl.ISSConverter(dramsys_path)
    conv.create_new_config_file(
        old_cfg_file, 
        new_cfg_file, 
        new_trace_file, 
        8, clkmhz
    )

def create_trace_analyzer_file(file):
    dcf = dl.ConfigFile()
    dcf.update_config(file)

    folder = join(
        dcf.data['paths']['output_data'],
        'trace_analyzer_data',
        dcf.data['addpath']['relative_folder'],
    )
    makedirs(folder, exist_ok=True)
    output_file = join(
        folder,
        dcf.data['addpath']['filename_no_ext'] + '.tdb'
    )
    return output_file   

def plot(gnc_cfg_file):
    dcf = dl.ConfigFile()
    dcf.update_config(gnc_cfg_file)
    data = dcf.get_analyser_data()

    csv_file = data['path_to_group_csv']
    variable = data['variable']
    output   = data['path_to_output_graphs']
    print(output)

    plotter = dl.Plotter(csv_file, variable, output)
    plotter.average_bandwidth()
    plotter.average_bandwidth_idle()
    plotter.total_time()
