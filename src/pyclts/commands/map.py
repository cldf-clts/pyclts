"""
Map a given sound inventory list to CLTS
"""

from pyclts.cli_util import add_format, Table
from pyclts import CLTS
import csv


def register(parser):
    add_format(parser, default="simple")
    parser.add_argument("graphemes", help="the file with the graphemes")


def run(args, test=False):
    # Instantiate BIPA
    bipa = args.repos.transcriptionsystem("bipa")

    # Define list of unknown start strings
    unknown_start = ["<NA>", "(?)", "(!)", "*"]

    # Auxiliary funciton for bipa normalizing, adds a "(!)" prefix if it is changed
    def _normalize_grapheme(bipa_grapheme):
        normalized = str(bipa[bipa_grapheme])
        if normalized != bipa_grapheme:
            normalized = "(!)" + normalized

        return normalized

    # Iterave over graphemes and collect them
    new_rows = []
    clusters = set()
    with open(args.graphemes) as grapheme_file:
        for row in csv.DictReader(grapheme_file, delimiter="\t"):
            bipa_grapheme = row["BIPA"]
            raw_grapheme = row["GRAPHEME"]

            unknown_bipa = any([bipa_grapheme.startswith(unk) for unk in unknown_start])

            if bipa_grapheme == "<NA>":
                pass
            elif bipa_grapheme and not unknown_bipa:
                if bipa[bipa_grapheme].type != "unknownsound":
                    row["BIPA"] = _normalize_grapheme(bipa_grapheme)
                else:
                    row["BIPA"] = "(?)"
            else:
                sound = bipa[raw_grapheme]
                if sound.type == "unknownsound":
                    match = list(bipa._regex.finditer(raw_grapheme))
                    if len(match) == 2:
                        sound1 = bipa[raw_grapheme[: match[1].start()]]
                        sound2 = bipa[raw_grapheme[match[1].start() :]]
                        if sound1.type == "consonant" and sound2.type == "consonant":
                            # check for prenasalized stuff
                            if sound1.manner == "nasal" and (
                                sound2.place == sound2.place
                                or sound2.manner
                                in ["stop", "affricate", "fricative", "implosive"]
                            ):
                                row["BIPA"] = "*ⁿ" + str(sound2)
                            else:
                                row["BIPA"] = "(?)"
                        else:
                            row["BIPA"] = "(?)"
                    else:
                        row["BIPA"] = "(?)"
                elif sound.type == "marker":
                    row["BIPA"] = raw_grapheme
                elif sound.type == "cluster":
                    # check for prenasalized stuff
                    if sound.from_sound.manner == "nasal" and (
                        sound.from_sound.place == sound.to_sound.place
                        or sound.to_sound.manner
                        in ["stop", "affricate", "fricative", "implosive"]
                    ):
                        row["BIPA"] = "*ⁿ" + str(sound.to_sound)
                    elif (
                        sound.to_sound.manner == "fricative"
                        and sound.from_sound.manner == "stop"
                    ):
                        new_sound = bipa[
                            s.to_sound.name.replace("fricative", "affricate")
                        ]
                        if new_sound.type == "consonant":
                            row["BIPA"] = "*" + str(new_sound.to_sound)
                        else:
                            row["BIPA"] = "(?)"
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
                        row["BIPA"] = str(
                            bipa[
                                " ".join([f for f in features.values() if f])
                                + " "
                                + sound.from_sound.type
                            ]
                        )
                    else:
                        row["BIPA"] = "(!)" + str(sound)
                        clusters.add(raw_grapheme)
                else:
                    row["BIPA"] = _normalize_grapheme(bipa_grapheme)

            # Collect modified info
            new_rows.append(row)

    # Sort the new rows, write to disk, and show information
    new_rows = sorted(
        new_rows,
        key=lambda r: (
            not any([r["BIPA"].startswith(na) for na in unknown_start]),
            r["GRAPHEME"],
        ),
    )

    unknown = [
        row
        for row in new_rows
        if any([row["BIPA"].startswith(na) for na in unknown_start])
    ]
    print(
        "Unknown Sounds: {0} of {1} ({2:.2f}) ({3} of which clusters)".format(
            len(unknown), len(new_rows), len(unknown) / len(new_rows), len(clusters)
        )
    )

    with open(args.graphemes[:-4] + ".mapped.tsv", "w") as output:
        writer = csv.DictWriter(output, delimiter="\t", fieldnames=new_rows[0].keys())
        writer.writeheader()
        writer.writerows(new_rows)
