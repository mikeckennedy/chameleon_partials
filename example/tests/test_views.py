from demo_chameleon_partials.views.home import index
from demo_chameleon_partials.views.notfound import notfound_view


def test_index_view(app_request):
    info = index(app_request)
    assert app_request.response.status_int == 200
    assert len(info['rows']) == 1


def test_notfound_view(app_request):
    info = notfound_view(app_request)
    assert app_request.response.status_int == 404
    assert info == {}
