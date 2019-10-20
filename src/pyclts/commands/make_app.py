"""
Create the CLTS javascript app.
"""
import collections
import json


def run(args, test=False):
    tts = args.repos.bipa

    def sound_to_dict(snd):
        res = collections.OrderedDict([('name', snd.name), ('bipa', snd.s), ('type', snd.type)])
        for f in snd._name_order:
            res[f] = getattr(snd, f)
        return res

    # retrieve all sounds in the datasets
    all_sounds = collections.OrderedDict()
    for td in args.repos.iter_transcriptiondata():
        for sound in td.data:
            if ' ' in sound:
                snd = tts[sound]
                glyph = snd.s
                assert '<?>' not in snd.s
                if snd.s not in all_sounds:
                    all_sounds[glyph] = sound_to_dict(snd)
                for item in td.data[sound]:
                    if item['grapheme'] not in all_sounds:
                        all_sounds[item['grapheme']] = all_sounds[glyph]

                all_sounds[glyph][td.id] = td.data[sound]
        if test:
            break

    # add sounds from transcription system
    for sound in tts:
        if sound not in all_sounds:
            snd = tts[sound]
            if snd.type != 'marker':
                if snd.s in all_sounds:
                    all_sounds[sound] = all_sounds[snd.s]
                else:
                    all_sounds[sound] = sound_to_dict(snd)

    args.log.info('{0} unique graphemes loaded'.format(len(all_sounds)))

    for i, sc in enumerate(args.repos.iter_soundclass()):
        for sound in all_sounds:
            try:
                all_sounds[sound][sc.id] = [dict(grapheme=sc[sound])]
            except KeyError:  # pragma: no cover
                pass
            if i == 0:
                if hasattr(sound, 's'):
                    all_sounds[sound]['bipa'] = tts[sound].s
        if test:
            break

    datafile = args.repos.repos / 'app' / 'data.js'
    with datafile.open('w', encoding='utf8') as handler:
        handler.write('var BIPA = ' + json.dumps(all_sounds, indent=2) + ';\n')
        handler.write('var normalize = ' + json.dumps(tts._normalize) + ';\n')
    args.log.info('{0} written'.format(datafile))
