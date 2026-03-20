"""
Map a given sound inventory list to CLTS
"""

from pyclts.models import is_valid_sound, UnknownSound, Marker, Consonant, Cluster


def register(parser):  # pylint: disable=C0116
    parser.add_argument("dataset", help="the file with the graphemes")


def run(args, test=False):  # pylint: disable=C0116
    # Instantiate BIPA
    bipa = args.repos.transcriptionsystem("bipa")

    # Iterave over graphemes and collect them
    new_rows, header = [], []
    unmapped, premapped, skipped, modified, mapped = 0, 0, 0, 0, 0
    rows = args.repos.get_source(args.dataset)
    for row in rows:
        row.setdefault("SYMBOLS", '')
        bipa_grapheme = row["BIPA"].strip()
        raw_grapheme = row["GRAPHEME"].strip()

        # basic condition: do not touch <NA>
        if bipa_grapheme == "<NA>":
            skipped += 1
        # second condition: we receive a value and interpret it
        elif bipa_grapheme:
            sound = bipa[bipa_grapheme]
            if not isinstance(sound, UnknownSound):
                if isinstance(sound, Marker):
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
            if isinstance(sound, UnknownSound):
                match = list(bipa._regex.finditer(raw_grapheme))
                if len(match) == 2:
                    sound1 = bipa[raw_grapheme[:match[1].start()]]
                    sound2 = bipa[raw_grapheme[match[1].start():]]
                    if isinstance(sound1, Consonant) and isinstance(sound2, Consonant):
                        # check for prenasalized stuff
                        if sound1.features.manner == "nasal" and (
                            sound2.features.place == sound2.features.place
                            or sound2.features.manner
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
            elif isinstance(sound, Marker):
                row["BIPA"] = str(sound)
                mapped += 1
            elif isinstance(sound, Cluster):
                # check for prenasalized stuff
                if sound.from_sound.features.manner == "nasal" and (
                    sound.from_sound.features.place == sound.to_sound.features.place
                    or sound.to_sound.features.manner
                    in ["stop", "affricate", "fricative", "implosive"]
                ):
                    row["BIPA"] = "(*)ⁿ" + str(sound.to_sound)
                    mapped += 1
                elif (
                    sound.to_sound.features.manner == "fricative"
                    and sound.from_sound.features.manner == "stop"
                ):
                    new_sound = bipa[
                        sound.to_sound.name.replace("fricative", "affricate")
                    ]
                    if isinstance(new_sound, Consonant):
                        row["BIPA"] = "(*)" + str(new_sound.to_sound)
                        mapped += 1
                    else:
                        row["BIPA"] = "(?)"
                        unmapped += 1
                elif (
                    sound.from_sound.features.manner == sound.to_sound.features.manner
                    and sound.from_sound.features.place == sound.to_sound.features.place
                    and sound.from_sound.features.phonation == sound.to_sound.features.phonation
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
                            + sound.from_sound.type()])
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

            if not isinstance(sound, (Marker, UnknownSound)):
                row['SYMBOLS'] = sound.symbols

        # Collect modified info
        new_rows.append([row[h] for h in row])

    header = [h for h in row]

    print('\t'.join(header))
    for row in sorted(
            new_rows, key=lambda x: (x[header.index('BIPA')], x[header.index('GRAPHEME')])):
        print('\t'.join(row))
    table = [
        ['mapped', mapped, mapped / len(new_rows), len(new_rows)],
        ['premapped', premapped, premapped / len(new_rows), len(new_rows)],
        ['skipped', skipped, skipped / len(new_rows), len(new_rows)],
        ['unmapped', unmapped, unmapped / len(new_rows), len(new_rows)]
    ]
    for row in table:
        args.log.info('{0[0]} {0[1]} items ({0[2]:.2f}) in {0[3]} rows'.format(
            row))
