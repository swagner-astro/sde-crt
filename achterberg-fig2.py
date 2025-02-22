import sys
sys.path.insert(0, 'lib')
sys.path.insert(0, 'src/evaluation')
from pybatch.special.kruells import *
import proplot as pplt
import logging
import chains
import formats
from node.cache import PickleNodeCache

from powerlawseries import *

pplt.rc.update({
        'text.usetex' : True,
        })

logging.basicConfig(level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def cb(this_param, param, other_param):
    dt = other_param['alpha'] / param['V']
    q = 1 / this_param['epsilon']
    batch_param = param | {'q' : q, 'dt' : dt}
    label_fmt_fields = this_param | other_param
    return {'param': batch_param, 'label_fmt_fields': label_fmt_fields}

param = {
          'r' : 4,
          'x0' : 0,
          'y0' : 1,
          't_inj' : 0.5,
          'Tmax' : 10000,
          'V' : 1,
          'Ls' : 1,
        }
other_param = {
            'alpha' : 0.05,
        }

name = 'achterberg_fig2'
cache = PickleNodeCache('pickle', name)
chain = chains.get_chain_powerlaw_datapoint(PyBatchAchterberg1, cache, np.inf, lambda c: c['label_fmt_fields']['epsilon'], histo_opts={'bin_count' : 50}, negate_index=True)
chain.map_tree(lambda n: setattr(n, 'ignore_cache', True), "values")

var = PowerlawSeriesVariable('\\epsilon', 'epsilon', [0.01, 0.02, 0.04, 0.05, 0.08, 0.1, 0.2, 0.3, 0.4, 0.5, 0.8, 1])
pls = PowerlawSeries(chain, var, cb, 
            callback_kwargs={'param': param, 'other_param': other_param}
        )

axs_format = SliceDict()
axs_format[4] = dict(xlabel='$\\epsilon$', ylabel='Powerlaw index $s$', xscale='log')
axs_format[slice(None, None, None)] = dict(toplabels=('Spatial distribution', 'Momentum distribution', 'Powerlaw indizes'), leftlabels=('CES', 'KPPC'))
nfmt = NodeFigureFormat(base=formats.histsandpowerlaw2, fig_legend_kw={'loc': 'b', 'ncols': 6, 'order': 'F'}, axs_format=axs_format, legends_kw={0: None, 1: None, 2: None})
nfig = NodeFigure(nfmt)
nfig.format(suptitle='Fig. 2 of Achterberg/Schure')
chain_x, chain_p = pls.histogram_chains

memo = {}
kppc_cls = PyBatchAchterberg1KPPC
chain_x_kppc = chain_x.copy("kppc", last_kwargs={'batch_cls': kppc_cls}, memo=memo)
chain_p_kppc = chain_p.copy("kppc", last_kwargs={'batch_cls': kppc_cls}, memo=memo)
datarow_kppc = pls.datarow_chain.copy("kppc", last_parents={'batch_cls': kppc_cls}, memo=memo)

nfig.add(chain_x, 0, plot_on='spectra')
nfig.add(chain_p, 2, plot_on='spectra')
nfig.add(chain_x_kppc, 1, plot_on='spectra')
nfig.add(chain_p_kppc, 3, plot_on='spectra')
nfig.add(pls.datarow_chain, 4)
nfig.add(datarow_kppc, 4)
nfig.pad(0.2, 4)
#nfig.show_nodes("achterberg_tree.pdf")
nfig.savefig("figures/{}.pdf".format(name), fig_legend_kw={'handles' : chain_p.handles_complete_tree})

