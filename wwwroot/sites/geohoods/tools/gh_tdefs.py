"""gh_tdefs.py -- tiny helpers for declaring GeoHoods homepage themes (see gh_themes*.py)."""


def S(kind, heads, pool=None, n=(3, 5), prob=1.0, **kw):
    """a section: kind is one of para list top10 log table photos poems recipes story faq updates links
    about poll quote specs; heads are alternative headings; pool the raw material."""
    d = dict(kind=kind, heads=heads if isinstance(heads, list) else [heads], pool=pool or [], n=n, prob=prob)
    d.update(kw)
    return d


def SUB(fname, titles, sections, prob=1.0):
    return dict(fname=fname, titles=titles if isinstance(titles, list) else [titles], sections=sections, prob=prob)


def T(key, hood, suburb, count, **kw):
    d = dict(key=key, hood=hood, suburb=suburb, count=count, titles=['{first}\'s Home Page'], headlines=None,
             intro=[], sections=[], subpages=[], images=[], styles=['plain'], layouts=['single'], midi=[None],
             ring=None, keywords='', desc=['A homepage.'], vars={}, entities=[], gb=[], age=(18, 60),
             gender=None, handle=None, features={})
    d.update(kw)
    return d
