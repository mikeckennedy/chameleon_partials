# Writing partials

Once the thumbnail renders, the temptation is to turn every repeated block in the app into a partial on the same afternoon. Go ahead, but read this page first. It is the rulebook, and most of the rules exist because someone, usually the author, got them wrong once.


# Rule one: paths are relative to the registered folder

This is the rule everyone trips on, so it goes first. The first argument to [render_partial](../reference/render_partial.md#chameleon_partials.render_partial) is a path relative to the folder you gave [register_extensions](../reference/register_extensions.md#chameleon_partials.register_extensions). It is never relative to the template making the call, even when that template is itself a partial sitting in a subfolder.

Here is the full video card from the demo app. It lives in `shared/partials/` and it wants the thumbnail that lives right next to it. It still spells out the whole path:

``` html
<!-- templates/shared/partials/video_square.pt -->

    [${ render_partial('shared/partials/video_image.pt', video=video, classes=[]) }](https://www.youtube.com/watch?v=${ video.id })
    [${ video.author }](https://www.youtube.com/watch?v=${ video.id })
    <div class="views">${ "{:,}".format(video.views) } views</div>

```

The reason it trips people is that Chameleon itself uses the other convention. A layout is pulled in with `metal:use-macro="load: ../shared/_layout.pt"`, and that `load:` path is relative to the current template file. So in one `.pt` file you may have both kinds of path side by side. The rule of thumb: `load:` thinks like a file, [render_partial](../reference/render_partial.md#chameleon_partials.render_partial) thinks like the folder.

There is a second half to this rule. The name has to point at a regular file inside the registered folder. An absolute path, a `..` that climbs out of the folder, a `package:path` spec, or a bare folder name is reported as a missing template, with Chameleon's own `ValueError` reading `Template not found: ...`. A `..` that stays inside the folder is fine. Surrounding whitespace and redundant `./` or `//` segments are normalised away, so every spelling of a file compiles and caches as one template. On macOS and Windows a differently cased spelling will still load, but it caches as a second template, so pick one spelling and stick to it.


# Rule two: the model is exactly what you pass

Everything after the path becomes the fragment's model. Any Python object is welcome, and the template reaches into it with ordinary Chameleon expressions:

``` html
${ render_partial('shared/partials/user_card.pt', user=user, show_email=False) }
```

What you do not pass, the partial does not have. A name the template references but the call left out raises Chameleon's `NameError` at render time, with the expression and line number in the message. There are no defaults on the call side, so either pass every name the partial uses or give the partial its own fallback with `tal:define`.

Four names in the model are already spoken for. `encoding` belongs to the package, which passes `encoding='utf-8'` into Chameleon on every render; supply your own and Python raises `TypeError` for the duplicate keyword. `translate` and `target_language` are Chameleon's i18n hooks, and `repeat` is the name of Chameleon's loop-state object. A value under any of those names will not reach your template the way you expect, so call it something else.


# Fragments all the way down

Every partial automatically receives [render_partial](../reference/render_partial.md#chameleon_partials.render_partial) in its model, so a partial can render other partials with no extra wiring. The video card above does exactly that with the thumbnail, and the thumbnail could do it again if it had anything smaller to delegate to. The package puts no limit on the depth.

The one thing it cannot save you from is a partial that renders itself without a way to stop. That ends, as recursion in Python always does, with `RecursionError`. If a fragment genuinely needs to recurse, say for a comment thread, wrap the inner call in a `tal:condition` that checks a depth or a children list.


# Loops

Put the call inside a `tal:repeat` and you get one fragment per item. The loop variable in the outer template can be named whatever reads well there, and renamed to whatever the partial expects on the way in:

``` html
<span class="video" tal:repeat="v videos">
    ${ render_partial('shared/partials/video_square.pt', video=v) }
</span>
```

This is the listing page of the demo app in its entirety, give or take a heading. Each `v` becomes `video` inside the card, the card renders the thumbnail, and the page is done.


# Layouts

Partials and METAL layouts are made for different jobs and they get along well. A layout is the stage: the `<html>` skeleton, the navigation, the footer, with a slot where the page goes. Partials are the props. A page fills the slot and renders partials inside it:

``` html
<!-- templates/shared/_layout.pt -->
<!DOCTYPE html metal:define-macro="layout">
<html lang="en">
<body>
    <div metal:define-slot="content">No content</div>
</body>
</html>
```

``` html
<!-- templates/home/index.pt -->

    <div metal:fill-slot="content">
        <div tal:repeat="v videos">
            ${ render_partial('shared/partials/video_square.pt', video=v) }
        </div>
    </div>

```

The underscore on `_layout.pt` is a convention, not a requirement. It makes the one file that is never rendered directly stand out in a folder listing. Note the two path styles in `index.pt`, right next to each other: `load:` climbing up a directory, [render_partial](../reference/render_partial.md#chameleon_partials.render_partial) starting from the root.

A partial can use a layout too, because it is just a template. A fragment meant to be dropped into the middle of a page normally should not, since the page already has one.


# Rendering a fragment from Python

[render_partial](../reference/render_partial.md#chameleon_partials.render_partial) is an ordinary Python function, and that opens a door. A view can call it directly to return just a card for an HTMX request, to build the body of an email, or to check markup in a test. The return value is the `HTML` wrapper; its `html_text` attribute is the string:

``` python
import chameleon_partials

fragment = chameleon_partials.render_partial('shared/partials/video_square.pt', video=video)
return Response(fragment.html_text)
```

The direction matters. Going out to the wire, you want the string, so read `html_text`. Going back into another template, pass the `HTML` object itself. Chameleon escapes a plain string and inserts an `HTML` object verbatim, and the [Troubleshooting](troubleshooting.md) page has an entry for what it looks like when you mix those up.


# Never let the request choose the file

It is tempting, once fragments are cheap, to let a query parameter pick which one to render: `?style=card` or `?style=row`. Do it, but do it with a lookup table, never by building the path from the parameter:

``` python
PARTIALS = {'card': 'shared/partials/video_square.pt', 'row': 'shared/partials/video_row.pt'}
html = render_partial(PARTIALS[request.params['style']], video=video)
```

The containment check from rule one will refuse a name that climbs out of the templates folder, and that check is a safety net, not a design. A table of names you wrote means the request can choose between two fragments and nothing else.

The same caution applies to the model. Spreading a request's parameters straight into the call, as in `render_partial(name, **request.params)`, lets anyone who can type a URL set any name the template relies on. [render_partial](../reference/render_partial.md#chameleon_partials.render_partial) is only injected into the model when the key is absent, so a parameter literally called [render_partial](../reference/render_partial.md#chameleon_partials.render_partial) would take its place. Pass named keyword arguments and the request stays on the outside.


# A layout for the templates folder

The package has no opinion about folder structure, but the demo app's structure has held up well. Pages grouped by area, one layout, and all the fragments in one place where you can find them:

``` text
templates/
├── errors/
│   └── 404.pt
├── home/
│   ├── index.pt
│   └── listing.pt
└── shared/
    ├── _layout.pt
    └── partials/
        ├── video_image.pt
        └── video_square.pt
```
