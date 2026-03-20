"""
Map a given sound inventory list to CLTS
"""
import dataclasses
import logging
from typing import Optional

from pyclts.models import is_valid_sound, UnknownSound, Marker, Consonant, Cluster
from pyclts.transcriptionsystem import TranscriptionSystem


def register(parser):  # pylint: disable=C0116
    parser.add_argument("dataset", help="the file with the graphemes")


@dataclasses.dataclass
class Report:
    """Keep stats of the mapping process."""
    unmapped: int = 0
    premapped: int = 0
    skipped: int = 0
    modified: int = 0
    mapped: int = 0

    def printout(self, nrows: int, log: logging.Logger):
        """Print the results."""
        for attr in ['mapped', 'premapped', 'skipped', 'unmapped']:
            log.info(
                '%s %s items (%.2f) in %s rows',
                attr, getattr(self, attr), getattr(self, attr) / nrows, nrows)


def _map_bipa_grapheme(
        bipa_grapheme: str,
        bipa: TranscriptionSystem,
        report: Report
) -> Optional[str]:
    sound = bipa[bipa_grapheme]
    if not isinstance(sound, UnknownSound):
        if isinstance(sound, Marker):
            report.premapped += 1
        elif not is_valid_sound(sound, bipa):
            report.unmapped += 1
            return '(!)'
        elif sound.s != bipa_grapheme:
            report.modified += 1
            return '(?)' + sound.s
        else:
            report.premapped += 1
    else:
        report.unmapped += 1
        return '(?)'
    return None


def _map_unknown(raw_grapheme: str, bipa: TranscriptionSystem, report: Report) -> str:
    match = list(bipa._regex.finditer(raw_grapheme))  # pylint: disable=W0212
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
                report.mapped += 1
                return "(*)ⁿ" + str(sound2)
    report.unmapped += 1
    return "(?)"


def _map_cluster(sound: Cluster, bipa: TranscriptionSystem, report: Report) -> str:
    # check for prenasalized stuff
    if sound.from_sound.features.manner == "nasal" and (
            sound.from_sound.features.place == sound.to_sound.features.place
            or sound.to_sound.features.manner
            in ["stop", "affricate", "fricative", "implosive"]
    ):
        report.mapped += 1
        return "(*)ⁿ" + str(sound.to_sound)

    if sound.to_sound.features.manner == "fricative" and sound.from_sound.features.manner == "stop":
        new_sound = bipa[sound.to_sound.name.replace("fricative", "affricate")]
        if isinstance(new_sound, Consonant):
            report.mapped += 1
            return "(*)" + str(new_sound.to_sound)
        report.unmapped += 1
        return "(?)"

    if (
            sound.from_sound.features.manner == sound.to_sound.features.manner
            and sound.from_sound.features.place == sound.to_sound.features.place
            and sound.from_sound.features.phonation == sound.to_sound.features.phonation
    ):
        features = {
            k: v or sound.to_sound.featuredict[k] for k, v in sound.from_sound.featuredict.items()}
        features["duration"] = "long"
        report.mapped += 1
        return '(*)' + str(
            bipa[" ".join([f for f in features.values() if f]) + " " + sound.from_sound.type()])

    report.mapped += 1
    return "(!)" + str(sound)


def _map_sound(raw_grapheme, bipa, report) -> str:
    sound = bipa[raw_grapheme]
    if isinstance(sound, UnknownSound):
        return _map_unknown(raw_grapheme, bipa, report)
    if isinstance(sound, Marker):
        report.mapped += 1
        return str(sound)
    if isinstance(sound, Cluster):
        return _map_cluster(sound, bipa, report)
    if is_valid_sound(sound, bipa):
        report.mapped += 1
        return sound.s
    report.unmapped += 1
    return '(!)'


def run(args):  # pylint: disable=C0116
    # Instantiate BIPA
    bipa = args.repos.transcriptionsystem("bipa")

    # Iterave over graphemes and collect them
    new_rows, header, row = [], [], {}
    report = Report()
    for row in args.repos.get_source(args.dataset):
        row.setdefault("SYMBOLS", '')
        bipa_grapheme = row["BIPA"].strip()
        raw_grapheme = row["GRAPHEME"].strip()

        # basic condition: do not touch <NA>
        if bipa_grapheme == "<NA>":
            report.skipped += 1
        # second condition: we receive a value and interpret it
        elif bipa_grapheme:
            res = _map_bipa_grapheme(bipa_grapheme, bipa, report)
            if res:
                row['BIPA'] = res
        else:
            row['BIPA'] = _map_sound(raw_grapheme, bipa, report)

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

    header = list(row.keys())

    print('\t'.join(header))
    for row in sorted(
            new_rows, key=lambda x: (x[header.index('BIPA')], x[header.index('GRAPHEME')])):
        print('\t'.join(row))

    report.printout(len(new_rows), args.log)
