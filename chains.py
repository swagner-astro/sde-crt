from node.special import *
from node.node import *

def generate_timerange_set(param, times):
    l = {}
    for t in times:
        l['T=' + str(t)] = {'param': param | {'Tmax' : t}}

    return l

def param_from_numerical(dx_adv, delta, sigma, beta_s, r, n_timesteps):
    """
    For simulations Kruells9 and the like.
    first return dict are the parameters for the batch, missing x0, y0 and t_inj
    since these are indepenent.
    second return dict are all other parameters (numerical)
    """
    dx_diff = dx_adv / delta

    dt = (dx_adv - dx_diff / 4) / beta_s
    q = dt / (dx_adv / dx_diff - 0.25)**2
    assert q > 0
    assert dt > 0
    Xsh = dx_adv * (1 - sigma) + sigma * dx_diff
    Tmax = n_timesteps * dt
    
    param_sim = {'beta_s' : beta_s, 'q' : q, 'Xsh' : Xsh, 'dt' : dt, 'Tmax' : Tmax, 'r' : r}
    param_num = {'dx_adv' : dx_adv, 'dx_diff' : dx_diff, 'delta' : delta, 'sigma' : sigma}
    return param_sim, param_num

def get_chain_parameter_series(batch_cls, cache, param_sets, confine_x, bin_count=30, histo_opts={}, plot_on=True):
    batch = BatchNode('batch', batch_cls = batch_cls, cache=cache, ignore_cache=False)
    points = PointNode('points', {'batch' : batch}, cache=cache, ignore_cache=False)

    points_range = {}
    for name, kw in param_sets.items():
        points_range[name] = {'points' : points.copy(name, last_kwargs=kw)}

    valuesx = ValuesNode('valuesx', index=0, cache=cache, ignore_cache=False)
    valuesp = ValuesNode('valuesp', index=1, cache=cache, ignore_cache=False,
            confinements=[(0, lambda x : np.abs(x) < confine_x)],
        )

    histo_opts = {'bin_count' : bin_count, 'plot' : plot_on, 'cache' : cache, 'ignore_cache' : False} | histo_opts
    histogramx = HistogramNode('histox', {'values' : valuesx}, log_bins=False, normalize='width', **histo_opts)
    histogramp = HistogramNode('histop', {'values' : valuesp}, log_bins=True, normalize='density', **histo_opts)

    histosetx = copy_to_group('groupx', histogramx, last_parents=points_range)
    histosetp = copy_to_group('groupp', histogramp, last_parents=points_range)

    return histosetx, histosetp

def get_chain_times_maxpl(batch_cls, cache, param, times, confine_x=np.inf, bin_count=30, histo_opts={}, plot_on=True):
    param_sets = generate_timerange_set(param, times)
    histosetx, histosetp = get_chain_parameter_series(batch_cls, cache, param_sets, confine_x, bin_count=bin_count, histo_opts=histo_opts, plot_on=plot_on)

    max_histop = histosetp['T=' + str(max(times))]
    powerlaw = PowerlawNode('pl', {'dataset' : max_histop}, plot=plot_on)#, color_cycle=cycle)

    return histosetx, histosetp, powerlaw

def get_chain_single(batch_cls, cache, confine_x, bin_count=30, histo_opts={}, param=None):
    batch = BatchNode('batch', batch_cls = batch_cls, cache=cache, param=param, ignore_cache=False)
    points = PointNode('points', {'batch' : batch}, cache=cache, ignore_cache=False)

    valuesx = ValuesNode('valuesx', {'points' : points}, index=0, cache=cache, ignore_cache=False)
    valuesp = ValuesNode('valuesp', {'points' : points}, index=1, cache=cache, ignore_cache=False,
            confinements=[(0, lambda x : np.abs(x) < confine_x)],
        )

    histo_opts = {'bin_count' : bin_count, 'plot' : True, 'cache' : cache, 'ignore_cache' : False} | histo_opts
    histogramx = HistogramNode('histox', {'values' : valuesx}, log_bins=False, normalize='width', **histo_opts)
    histogramp = HistogramNode('histop', {'values' : valuesp}, log_bins=True, normalize='density', **histo_opts)

    return histogramx, histogramp

def get_chain_powerlaw_datapoint(batch_cls, cache, confine_x, xparam_callback, histo_opts={}):
    """
    """
    cycle = ColorCycle(['red', 'green', 'blue', 'yellow', 'black', 'violet'])

    histogramx, histogramp = get_chain_single(batch_cls, cache, confine_x, histo_opts={'color_cycle': cycle} | histo_opts)
    histogramp.plot_on = 'spectra'

    powerlaw = PowerlawNode('pl', {'dataset' : histogramp }, plot='spectra', color_cycle=cycle)

    xparam_get = CommonCallbackNode('xparam_get', parents=histogramp, callback=xparam_callback)

    datapoint_chain = NodeGroup('datapoint_group', {'x' : xparam_get, 'y': powerlaw[1], 'dy' : powerlaw[3]})
    
    return NodeGroup('group', {'datapoint': datapoint_chain, 'histogram_x' : histogramx})

def get_chain_powerlaw_datapoint_tseries(batch_cls, cache, confine_x, times, xparam_callback, histo_opts={}):
    cycle = ColorCycle(['red', 'green', 'blue', 'yellow', 'black', 'violet'])

    param_sets = {'T=' + str(t) : {'param' : {'Tmax' : t}} for t in times}
    histosetx, histosetp = get_chain_parameter_series(batch_cls, cache, param_sets, confine_x, histo_opts={'color_cycle': cycle} | histo_opts, plot_on='spectra')

    max_histop = histosetp['T=' + str(max(times))]
    powerlaw = PowerlawNode('pl', {'dataset' : max_histop}, plot='spectra', color_cycle=cycle)

    xparam_get = CommonCallbackNode('xparam_get', parents=max_histop, callback=xparam_callback)

    datapoint_chain = NodeGroup('datapoint_group', {'x' : xparam_get, 'y': powerlaw[1], 'dy' : powerlaw[3]})
    
    return NodeGroup('group', {'datapoint': datapoint_chain, 'histosetx' : histosetx, 'histosetp': histosetp, 'powerlaw': powerlaw})
