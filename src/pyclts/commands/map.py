"""
Map a given sound inventory list to CLTS
"""

from pyclts.cli_util import add_format, Table
from pyclts.models import is_valid_sound
from csvw.dsv import UnicodeDictReader


def register(parser):
    add_format(parser, default="simple")
    parser.add_argument("graphemes", help="the file with the graphemes")


def run(args, test=False):
    # Instantiate BIPA
    bipa = args.repos.transcriptionsystem("bipa")

    # Iterave over graphemes and collect them
    new_rows = []
    unmapped, premapped, skipped, modified, mapped = 0, 0, 0, 0, 0
    with UnicodeDictReader(args.graphemes, delimiter='\t') as reader:
        for row in reader:
            if "SYMBOLS" not in row:
                row["SYMBOLS"] = ''
            bipa_grapheme = row["BIPA"].strip()
            raw_grapheme = row["GRAPHEME"].strip()

            # basic condition: do not touch <NA>
            if bipa_grapheme == "<NA>":
                skipped += 1
            # second condition: we receive a value and interpret it
            elif bipa_grapheme:
                sound = bipa[bipa_grapheme]
                if sound.type != "unknownsound":
                    if sound.type == 'marker':
                        premapped += 1
                    elif not is_valid_sound(sound, bipa):
                        row["BIPA"] = '(!)'
                        unmapped += 1
                    elif sound.s != bipa_grapheme:
                        row["BIPA"] = '(?)' + sound.s
                        modified += 1
                    else:
                        premapped += 1
                else:
                    row["BIPA"] = '(?)'
                    unmapped += 1
            else:
                sound = bipa[raw_grapheme]
                if sound.type == "unknownsound":
                    match = list(bipa._regex.finditer(raw_grapheme))
                    if len(match) == 2:
                        sound1 = bipa[raw_grapheme[:match[1].start()]]
                        sound2 = bipa[raw_grapheme[match[1].start():]]
                        if sound1.type == "consonant" and sound2.type == "consonant":
                            # check for prenasalized stuff
                            if sound1.manner == "nasal" and (
                                sound2.place == sound2.place
                                or sound2.manner
                                in ["stop", "affricate", "fricative", "implosive"]
                            ):
                                row["BIPA"] = "(*)ⁿ" + str(sound2)
                                mapped += 1
                            else:
                                row["BIPA"] = "(?)"
                                unmapped += 1
                        else:
                            row["BIPA"] = "(?)"
                            unmapped += 1
                    else:
                        row["BIPA"] = "(?)"
                        unmapped += 1
                elif sound.type == "marker":
                    row["BIPA"] = str(sound)
                    mapped += 1
                elif sound.type == "cluster":
                    # check for prenasalized stuff
                    if sound.from_sound.manner == "nasal" and (
                        sound.from_sound.place == sound.to_sound.place
                        or sound.to_sound.manner
                        in ["stop", "affricate", "fricative", "implosive"]
                    ):
                        row["BIPA"] = "(*)ⁿ" + str(sound.to_sound)
                        mapped += 1
                    elif (
                        sound.to_sound.manner == "fricative"
                        and sound.from_sound.manner == "stop"
                    ):
                        new_sound = bipa[
                            sound.to_sound.name.replace("fricative", "affricate")
                        ]
                        if new_sound.type == "consonant":
                            row["BIPA"] = "(*)" + str(new_sound.to_sound)
                            mapped += 1
                        else:
                            row["BIPA"] = "(?)"
                            unmapped += 1
                    elif (
                        sound.from_sound.manner == sound.to_sound.manner
                        and sound.from_sound.place == sound.to_sound.place
                        and sound.from_sound.phonation == sound.to_sound.phonation
                    ):
                        features = {
                            k: v or sound.to_sound.featuredict[k]
                            for k, v in sound.from_sound.featuredict.items()
                        }
                        features["duration"] = "long"
                        row["BIPA"] = '(*)' + str(
                            bipa[
                                " ".join([f for f in features.values() if f])
                                + " "
                                + sound.from_sound.type])
                        mapped += 1
                    else:
                        row["BIPA"] = "(!)" + str(sound)
                        mapped += 1
                else:
                    if is_valid_sound(sound, bipa):
                        row["BIPA"] = sound.s
                        mapped += 1
                    else:
                        row["BIPA"] = '(!)'
                        unmapped += 1
            if row['BIPA']:
                if row['BIPA'].startswith('*'):
                    sound = bipa[row['BIPA'][1:]]
                elif row['BIPA'].startswith('('):
                    sound = bipa[row['BIPA'][3:]]
                else:
                    sound = bipa[row['BIPA']]

                if sound.type not in ['unknownsound', 'marker']:
                    row['SYMBOLS'] = sound.symbols

            # Collect modified info
            new_rows.append([row[h] for h in row])

    # Sort the new rows, write to disk, and show information
    header = [h for h in row]

    with open(args.graphemes[:-4] + ".mapped.tsv", "w") as f:
        f.write('\t'.join([h for h in row]) + '\n')
        for row in sorted(
                new_rows, key=lambda x: (x[header.index('BIPA')], x[header.index('GRAPHEME')])):
            f.write('\t'.join(row) + '\n')
    table = [
        ['mapped', mapped, mapped / len(new_rows), len(new_rows)],
        ['premapped', premapped, premapped / len(new_rows), len(new_rows)],
        ['skipped', skipped, skipped / len(new_rows), len(new_rows)],
        ['unmapped', unmapped, unmapped / len(new_rows), len(new_rows)]
    ]
    with Table(args, 'type', 'items', 'proportion', 'total') as text:
        text += table
