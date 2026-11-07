"""Rendering tests for chameleon_partials: bare partials, partials with model data,
layouts, nested (recursive) partials, and error conditions (missing template, and
rendering before register_extensions)."""

from pathlib import Path

# noinspection PyPackageRequirements
import pytest as pytest

import chameleon_partials


@pytest.fixture
def registered_extension():
    folder = (Path(__file__).parent / 'test_templates').as_posix()
    chameleon_partials.register_extensions(folder, auto_reload=True, cache_init=True)

    # Allow test to work with extensions as registered
    print('********************************************')
    print(folder)
    print('********************************************')
    yield

    # Roll back the fact that we registered the extensions for future tests.
    chameleon_partials.has_registered_extensions = False


def test_render_empty(registered_extension):
    html: chameleon_partials.HTML = chameleon_partials.render_partial('render/bare.pt')
    assert '<h1>This is bare HTML fragment</h1>' in html.html_text


def test_render_with_data(registered_extension):
    name = 'Sarah'
    age = 32
    html: chameleon_partials.HTML = chameleon_partials.render_partial('render/with_data.pt', name=name, age=age)
    assert f'<span>Your name is {name} and age is {age}</span>' in html.html_text


def test_render_with_layout(registered_extension):
    value_text = 'The message is clear'
    html: chameleon_partials.HTML = chameleon_partials.render_partial('render/with_layout.pt', message=value_text)
    assert '<title>Chameleon Partials Test Template</title>' in html.html_text
    assert value_text in html.html_text


def test_render_recursive(registered_extension):
    value_text = 'The message is clear'
    inner_text = 'The message is recursive'

    html: chameleon_partials.HTML = chameleon_partials.render_partial(
        'render/recursive.pt', message=value_text, inner=inner_text
    )
    assert value_text in html.html_text
    assert inner_text in html.html_text


def test_missing_template(registered_extension):
    with pytest.raises(ValueError):
        chameleon_partials.render_partial('no-way.pt', message=7)


@pytest.mark.parametrize(
    'name',
    [
        '../test_rendering.py',
        'render/../../test_rendering.py',
        # Chameleon's loader strips the name before joining it, so leading whitespace used to pass the lexical
        # check (as the folder ' ..') and then load ../test_rendering.py. Whitespace inside a segment is not
        # stripped and was always refused; it is pinned here with the others.
        ' ../test_rendering.py',
        '\t../test_rendering.py',
        '\n../test_rendering.py',
        'render/ ../../test_rendering.py',
        (Path(__file__).parent / 'test_templates' / 'render' / 'bare.pt').as_posix(),
        'chameleon_partials:py.typed',
    ],
)
def test_names_outside_the_folder_are_not_found(registered_extension, name):
    # Each of these names a real file, outside the registered folder or through a path or package
    # spec that could reach anywhere: refused as a missing template.
    with pytest.raises(ValueError, match='Template not found'):
        chameleon_partials.render_partial(name)


def test_a_dot_dot_that_stays_inside_the_folder_is_fine(registered_extension):
    html: chameleon_partials.HTML = chameleon_partials.render_partial('render/../render/bare.pt')
    assert '<h1>This is bare HTML fragment</h1>' in html.html_text


@pytest.mark.parametrize('name', [' render/bare.pt', 'render/bare.pt ', '\trender/bare.pt\n'])
def test_surrounding_whitespace_still_renders(registered_extension, name):
    # Chameleon strips it, so stripping it first changes nothing for a harmless name.
    html: chameleon_partials.HTML = chameleon_partials.render_partial(name)
    assert '<h1>This is bare HTML fragment</h1>' in html.html_text


def test_every_spelling_of_a_partial_is_one_template(registered_extension):
    # Chameleon caches a compiled template per name it is given; without normalizing the name, a request-chosen
    # spelling could add a compiled template per request for the life of the process.
    spellings = [
        'render/bare.pt',
        './render/bare.pt',
        'render//bare.pt',
        'render/./bare.pt',
        'render/../render/bare.pt',
        ' render/bare.pt',
        'render/bare.pt ',
    ]
    for name in spellings:
        html: chameleon_partials.HTML = chameleon_partials.render_partial(name)
        assert '<h1>This is bare HTML fragment</h1>' in html.html_text

    loader = chameleon_partials.__templates
    assert [name for name, *_ in loader.registry] == ['render/bare.pt']  # keyed by (name, template class)


@pytest.mark.parametrize('name', ['render', 'render/', '.', './', ''])
def test_a_folder_name_is_not_a_template(registered_extension, name):
    # Used to surface as an IsADirectoryError from inside Chameleon, which "not found" handlers miss.
    with pytest.raises(ValueError, match='Template not found'):
        chameleon_partials.render_partial(name)


def test_a_partial_that_includes_itself_raises_recursion_error(registered_extension):
    with pytest.raises(RecursionError):
        chameleon_partials.render_partial('render/self_including.pt', n=0)


def test_template_name_hook(registered_extension):
    # chameleon-rs resolves names for this package through _template_name; pin its contract.
    folder = chameleon_partials.template_path
    assert chameleon_partials._template_name(' ./render/../render//bare.pt ', folder) == 'render/bare.pt'
    for refused in ['../test_rendering.py', ' ../test_rendering.py', 'render', 'no-way.pt', '', '/etc/hosts']:
        assert chameleon_partials._template_name(refused, folder) is None


def test_not_registered():
    with pytest.raises(chameleon_partials.PartialsException):
        chameleon_partials.render_partial('doesnt-matter.pt', message=7)
