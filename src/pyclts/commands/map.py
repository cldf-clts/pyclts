"""
Map a given sound inventory list to CLTS
"""
from pyclts.cli_util import add_format, Table
from pyclts import CLTS
from csvw.dsv import UnicodeReader

def register(parser):
    add_format(parser, default='simple')
    parser.add_argument(
        'graphemes',
        help='the file with the graphemes',
        )

def run(args, test=False):
    bipa = args.repos.transcriptionsystem('bipa')
    with UnicodeReader(args.graphemes, delimiter='\t') as reader:
        data = []
        for line in reader:
            data.append(line)
        header = data[0]
        data = data[1:]
    bidx, gidx = header.index('BIPA'), header.index('GRAPHEME')
    count = 0
    cluster = set()
    for i, line in enumerate(data):
        rg, bg = line[gidx], line[bidx]
        if bg and bg != '<NA>':
            if bipa[bg].type != 'unknownsound':
                pass
            else:
                data[i][bidx] = '<NA>'
                count += 1
        else:            
            s = bipa[rg]
            if s.type == 'unknownsound':
                match = list(bipa._regex.finditer(rg))
                if len(match) == 2:
                    s1 = bipa[rg[:match[1].start()]]
                    s2 = bipa[rg[match[1].start():]]
                    if s1.type == 'consonant' and s2.type == \
                            'consonant':
                        # check for prenasalized stuff
                        if s1.manner == 'nasal' and (
                                s2.place == s2.place or \
                                        s2.manner in ['stop', 'affricate',
                                            'fricative', 'implosive']):
                            data[i][bidx] = '*ⁿ'+s2.s
                        else:
                            data[i][bidx] = '?'
                            count += 1
                    else:
                        data[i][bidx] = '<NA>'
                        count += 1
                else:
                    data[i][bidx] = '<NA>'
                    count += 1
            elif s.type == 'marker':
                data[i][bidx] = rg
            elif s.type == 'cluster':
                # check for prenasalized stuff
                if s.from_sound.manner == 'nasal' and (
                        s.from_sound.place == s.to_sound.place or \
                                s.to_sound.manner in ['stop', 'affricate',
                                    'fricative', 'implosive']):
                    data[i][bidx] = '*ⁿ'+s.to_sound.s
                elif s.to_sound.manner == 'fricative' and s.from_sound.manner == 'stop':
                    ns = bipa[s.to_sound.name.replace('fricative',
                        'affricate')]
                    if ns.type == 'consonant':
                        data[i][bidx] = '*'+ns.to_sound.s
                    else:
                        data[i][bidx] = '<NA>'
                elif s.from_sound.manner == s.to_sound.manner and \
                        s.from_sound.place == s.to_sound.place and \
                        s.from_sound.phonation == s.to_sound.phonation:
                    features = {k: v or s.to_sound.featuredict[k] for k, v in
                            s.from_sound.featuredict.items()}
                    features['duration'] = 'long'
                    data[i][bidx] = bipa[' '.join([f for f in features.values() if f])+' '+s.from_sound.type].s
                else:
                    data[i][bidx] = '(!)'+s.s
                    cluster.add(rg)
            else:
                data[i][bidx] = s.s

    with open(args.graphemes[:-4]+'.mapped.tsv', 'w') as f:
        f.write('\t'.join(header)+'\n')
        for line in data:
            f.write('\t'.join(line)+'\n')

    print('Unknown Sounds: {0} of {1} ({2:.2f})'.format(
        count,
        len(data),
        count/len(data)))

