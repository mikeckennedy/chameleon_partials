def test_root(testapp):
    res = testapp.get('/', status=200)
    # The home page renders video_square.pt partials, which nest video_image.pt; the
    # thumbnail markup proves render_partial reached the template via the BeforeRender
    # subscriber and that nested partials rendered.
    assert b'img.youtube.com/vi/' in res.body
    assert b'views</div>' in res.body


def test_listing(testapp):
    res = testapp.get('/listing', status=200)
    assert res.body.count(b'img.youtube.com/vi/') > 3


def test_notfound(testapp):
    res = testapp.get('/badurl', status=404)
    assert res.status_code == 404
