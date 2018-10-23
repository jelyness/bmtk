import numpy as np
import pandas as pd
import bmtk.analyzer.cell_vars as cell_vars

def epsp_analysis(report_file=None, config_file='config.json', t_min=100, t_duration=1000, t_spike=None):
#     t_start = 300
#     t_duration=1000
    amp_min = 0.1
    amp_max = 50
    v_spike = -15
    report_file = report_file or cell_vars.get_cell_report(config_file)
    var_report = cell_vars.CellVarsFile(report_file)
    gids = np.array(var_report.gids)

    t_min = t_spike or t_min
    v_all = var_report.data(gids, 'v', time_window=[t_min, t_min+t_duration])

    i_bl = 0
    tt = var_report.time_trace
    if t_spike is None:
        nz = np.nonzero(v_all > v_spike)
        cells_spike = np.unique(nz[1])
        assert(len(cells_spike)==1)
        i_bl = nz[0][0]
        t_spike = tt[i_bl]
        v_all = v_all[i_bl:,:]
    

    v_peak = np.max(v_all, axis=0)
    v_bl = v_all[0,:]
    amp = v_peak - v_bl
    cells_epsp = np.flatnonzero((amp_min < amp) & (amp < amp_max))

    v_mid = (v_bl + v_peak)/2
    n_conn = len(cells_epsp)
    i_start = np.zeros(n_conn, dtype=int)
    i_end = np.zeros(n_conn, dtype=int)
    for i, cell in enumerate(cells_epsp):
        i_up = np.flatnonzero(v_all[:,cell] > v_mid[cell])
        i_start[i] = i_up[0]
        i_end[i] = i_up[-1]

    t_start = tt[i_start+i_bl]
    t_end = tt[i_end+i_bl]
    width = t_end - t_start
    return {'gid':gids[cells_epsp], 'amp': amp[cells_epsp], 'width': width, 'delay': t_start-t_spike}
        