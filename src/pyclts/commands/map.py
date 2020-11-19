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
    bipa = args.repos.transcriptionsystem("bipa")

    new_rows = []
    clusters = set()
    with open(args.graphemes) as grapheme_file:
        for row in csv.DictReader(grapheme_file, delimiter="\t"):
            bipa_grapheme = row["BIPA"]
            raw_grapheme = row["GRAPHEME"]

            if bipa_grapheme and bipa_grapheme != "<NA>":
                if bipa[bipa_grapheme].type != "unknownsound":
                    row["BIPA"] = str(bipa[bipa_grapheme])
                else:
                    row["BIPA"] = "<NA>"
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
                            row["BIPA"] = "<NA>"
                    else:
                        row["BIPA"] = "<NA>"
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
                            row["BIPA"] = "<NA>"
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
                    row["BIPA"] = str(sound)

            # Collect modified info
            new_rows.append(row)

    # Sort the new rows, write to disk, and show information
    new_rows = sorted(
        new_rows,
        key=lambda r: (
            not any([r["BIPA"].startswith(na) for na in ["<NA>", "(?)", "(!)", "*"]]),
            r["GRAPHEME"],
        ),
    )

    unknown = [
        row
        for row in new_rows
        if any([row["BIPA"].startswith(na) for na in ["<NA>", "(?)", "(!)", "*"]])
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
