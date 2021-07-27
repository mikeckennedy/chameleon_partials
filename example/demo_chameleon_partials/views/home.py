# noinspection PyPackageRequirements
from pyramid.view import view_config

import chameleon_partials
from demo_chameleon_partials.services import video_service


@view_config(route_name='index', renderer='demo_chameleon_partials:templates/home/index.pt')
def index(_):
    row1 = video_service.top_videos()
    model = dict(rows=[row1])
    return chameleon_partials.extend_model(model)


@view_config(route_name='listing', renderer='demo_chameleon_partials:templates/home/listing.pt')
def listing(_):
    videos = video_service.all_videos()
    model = dict(videos=videos)
    return chameleon_partials.extend_model(model)
