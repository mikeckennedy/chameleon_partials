# noinspection PyPackageRequirements
from pyramid.events import BeforeRender, subscriber

import chameleon_partials


@subscriber(BeforeRender)
def add_global(event):
    event['render_partial'] = chameleon_partials.render_partial
