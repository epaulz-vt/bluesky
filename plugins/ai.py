''' AI '''

from bluesky import core, stack, traf, scr #, settings, navdb, sim, tools
import numpy as np

def init_plugin():

    ai = AI()

    config = {
        'plugin_name': 'AI',
        'plugin_type': 'sim'
    }

    return config

# singleton class only needs to be created once (above)... all AI function go here (i think)
class AI(core.Entity):
    def __init__(self):
        super().__init__()

    @core.timed_function(name='ai_update', dt=2)
    def update(self):
        #scr.echo('Average position of traffic lat/long is: %.2f, %.2f' % (np.average(traf.lat), np.average(traf.lon)))
        with open('aada/test.txt', 'a') as f:
            f.write('Average position of traffic lat/long is: %.2f/%.2f\n' % (np.average(traf.lat), np.average(traf.lon)))
