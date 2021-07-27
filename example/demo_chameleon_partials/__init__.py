from pathlib import Path

from pyramid.config import Configurator

import chameleon_partials


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    with Configurator(settings=settings) as config:
        config.include('pyramid_chameleon')
        config.include('.routes')
        config.scan()
        folder = (Path(__file__).parent / "templates").as_posix()
        chameleon_partials.register_extensions(folder, auto_reload=True, cache_init=True)

    return config.make_wsgi_app()
