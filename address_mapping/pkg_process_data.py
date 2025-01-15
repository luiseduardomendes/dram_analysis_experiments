import pkg_process_input as ppi
from os.path import join
from os import makedirs

def get_ctrl_inputs(ctrl_path, dsys_cfg, apps, var_n_val, platform, prefix):
    ctrl_inputs = {}
    for app in apps:
        ctrl_inputs[app] = {}
        for variable, values in var_n_val:
            ctrl_inputs[app][variable] = ppi.create_input(ctrl_path, app, variable, values, dsys_cfg, prefix, platform)
    return ctrl_inputs

def get_addr_map_inputs(addr_maps, input_path, apps, var_n_val, platform, prefix):
    address_map_inputs = {}
    for addr_map, new_dsys_cfg in addr_maps:
        address_map_inputs[addr_map] = {}
        new_path = join(input_path, addr_map)
        makedirs(new_path, exist_ok=True)
        for app in apps:
            address_map_inputs[addr_map][app] = {}
            for variable, values in var_n_val:
                address_map_inputs[addr_map][app][variable] = ppi.create_input(new_path, app, variable, values, new_dsys_cfg, prefix, platform)

    return address_map_inputs





