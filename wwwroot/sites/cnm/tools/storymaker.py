"""Tiny helper so the story files stay readable.

S(section, day, "HH:MM", slug, headline, summary, dateline, byline, body,
  photo=("kind", "label") or None, caption="", tags="y2k dotcom")

section : WORLD US WEATHER BUSINESS SPORTS TECH SHOWBIZ POLITICS LAW HEALTH TRAVEL FOOD STYLE
day     : day of December 1999 (1-20)
body    : paragraphs separated by blank lines; the dateline is glued onto paragraph one.
"""


def S(section, day, hhmm, slug, headline, summary, dateline, byline, body,
      photo=None, caption="", tags=""):
    paras = [" ".join(p.split()) for p in body.strip().split("\n\n") if p.strip()]
    return dict(section=section, day=day, hhmm=hhmm, slug=slug, headline=headline,
                summary=" ".join(summary.split()), dateline=dateline, byline=byline,
                paras=paras, photo=photo, caption=" ".join(caption.split()),
                tags=tags.split())
