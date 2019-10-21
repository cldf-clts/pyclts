"""

"""
import collections

import attr
from csvw.dsv import UnicodeWriter

from pyclts.models import is_valid_sound


@attr.s
class Grapheme(object):
    GRAPHEME = attr.ib()
    NAME = attr.ib()
    EXPLICIT = attr.ib()
    ALIAS = attr.ib()
    DATASET = attr.ib()
    FREQUENCY = attr.ib(default=0)
    URL = attr.ib(default='')
    FEATURES = attr.ib(default='')
    IMAGE = attr.ib(default='')
    SOUND = attr.ib(default='')
    NOTE = attr.ib(default='')


def run(args, test=False):
    def writer(*comps):
        return UnicodeWriter(args.repos.path('data', *comps), delimiter='\t')

    sounds = collections.defaultdict(dict)
    data = []
    bipa = args.repos.bipa
    # start from assembling bipa-sounds
    for grapheme, sound in sorted(
            bipa.sounds.items(), key=lambda p: p[1].alias if p[1].alias else False):
        if sound.type not in ['marker']:
            if sound.alias:
                assert sound.name in sounds
                sounds[sound.name]['aliases'].add(grapheme)
            else:
                assert sound.name not in sounds
                sounds[sound.name] = {
                    'grapheme': grapheme,
                    'unicode': sound.uname or '',
                    'generated': '',
                    'note': sound.note or '',
                    'type': sound.type,
                    'aliases': set(),
                    'normalized': '+' if sound.normalized else ''
                }
            data.append(Grapheme(
                grapheme,
                sound.name,
                '+',
                '',
                'bipa',
                '0',
                '',
                '',
                '',
                '',
                sound.note or ''))

    # add sounds systematically by their alias
    for td in args.repos.iter_transcriptiondata():
        for name in td.names:
            bipa_sound = bipa[name]
            # check for consistency of mapping here
            if not is_valid_sound(bipa_sound, bipa):
                continue

            sound = sounds.get(name)
            if not sound:
                sound = sounds[name] = {
                    'grapheme': bipa_sound.s,
                    'aliases': {bipa_sound.s},
                    'generated': '+',
                    'unicode': bipa_sound.uname or '',
                    'note': '',
                    'type': bipa_sound.type,
                    'alias': '+' if bipa_sound.alias else '',
                    'normalized': '+' if bipa_sound.normalized else ''
                }

            for item in td.data[name]:
                sound['aliases'].add(item['grapheme'])
                # add the values here
                data.append(Grapheme(
                    item['grapheme'],
                    name,
                    item['explicit'],
                    '',  # sounds[name]['alias'],
                    td.id,
                    item.get('frequency', ''),
                    item.get('url', ''),
                    item.get('features', ''),
                    item.get('image', ''),
                    item.get('sound', ''),
                ))
        if test:
            break

    # sound classes have a generative component, so we need to treat them
    # separately
    for sc in args.repos.iter_soundclass():
        for name in sounds:
            try:
                grapheme = sc[name]
                data.append(Grapheme(
                    grapheme,
                    name,
                    '+' if name in sc.data else '',
                    '',
                    sc.id,
                ))
            except KeyError:  # pragma: no cover
                args.log.debug(name, sounds[name]['grapheme'])
        if test:
            break

    # last run, check again for each of the remaining transcription systems,
    # whether we can translate the sound
    for ts in args.repos.iter_transcriptionsystem(exclude=['bipa']):
        for name in sounds:
            try:
                ts_sound = ts[name]
                if is_valid_sound(ts_sound, ts):
                    sounds[name]['aliases'].add(ts_sound.s)
                    data.append(Grapheme(
                        ts_sound.s,
                        name,
                        '' if sounds[name]['generated'] else '+',
                        '',  # sounds[name]['alias'],
                        ts.id,
                    ))
            except ValueError:
                pass
            except TypeError:
                args.log.debug('{0}: {1}'.format(ts.id, name))
        if test:
            break

    with writer('sounds.tsv') as w:
        w.writerow(['NAME', 'TYPE', 'GRAPHEME', 'UNICODE', 'GENERATED', 'NOTE'])
        for k, v in sorted(sounds.items(), reverse=True):
            w.writerow([k, v['type'], v['grapheme'], v['unicode'], v['generated'], v['note']])

    with writer('graphemes.tsv') as w:
        w.writerow([f.name for f in attr.fields(Grapheme)])
        for row in data:
            w.writerow(attr.astuple(row))
