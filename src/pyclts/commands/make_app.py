"""
Create the CLTS javascript app.
"""
import json
import collections

from pyclts.models import Marker


def _sound_to_dict(snd):
    res = collections.OrderedDict([('name', snd.name), ('bipa', snd.s), ('type', snd.type())])
    for f, val in snd.features:
        res[f] = val
    return res


def _add_td(args, tts, all_sounds):
    for td in args.repos.iter_transcriptiondata():
        for sound in td.data:
            if ' ' in sound:
                snd = tts[sound]
                glyph = snd.s
                assert '<?>' not in snd.s, f'{td.id}: {sound} {snd.s}'
                if snd.s not in all_sounds:
                    all_sounds[glyph] = _sound_to_dict(snd)
                for item in td.data[sound]:
                    if item['grapheme'] not in all_sounds:
                        all_sounds[item['grapheme']] = all_sounds[glyph]

                all_sounds[glyph][td.id] = td.data[sound]


def _add_ts(tts, all_sounds):
    # add sounds from transcription system
    for sound in tts:
        if sound not in all_sounds:
            snd = tts[sound]
            if not isinstance(snd, Marker):
                if snd.s in all_sounds:
                    all_sounds[sound] = all_sounds[snd.s]
                else:
                    all_sounds[sound] = _sound_to_dict(snd)


def _add_sc(args, tts, all_sounds):
    for i, sc in enumerate(args.repos.iter_soundclass()):
        for sound in all_sounds:
            try:
                all_sounds[sound][sc.id] = [dict(grapheme=sc[sound])]  # pylint: disable=R1735
            except KeyError:  # pragma: no cover
                pass
            if i == 0:
                if hasattr(sound, 's'):
                    all_sounds[sound]['bipa'] = tts[sound].s


def run(args):  # pylint: disable=C0116
    tts = args.repos.bipa
    # retrieve all sounds in the datasets
    all_sounds = collections.OrderedDict()
    _add_td(args, tts, all_sounds)
    _add_ts(tts, all_sounds)

    args.log.info('%s unique graphemes loaded', len(all_sounds))

    _add_sc(args, tts, all_sounds)

    datafile = args.repos.repos / 'app' / 'data.js'
    datafile.write_text('\n'.join([
        f'var BIPA = {json.dumps(all_sounds, indent=2)};\n',
        f'var normalize = {json.dumps(tts._normalize)};\n']))  # pylint: disable=W0212
    args.log.info('%s written', datafile)
