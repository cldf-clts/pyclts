"""
Metadata about the sources of transcription system data in CLTS are stored in sources/index.tsv.
"""
import dataclasses
from typing import Optional

from uritemplate import URITemplate
from pycldf.sources import Source as CldfSource
from clldutils.misc import nfilter

from pyclts import datatypes
from pyclts.util import dict_reader, CLDFTable, normalize_whitespace


@dataclasses.dataclass(frozen=True)
class Source(CLDFTable):
    """
    CLTS is compiled from information about transcriptions and how these relate to
    sounds from many sources, such as phoneme inventory databases like PHOIBLE or
    relevant typological surveys.
    """
    NAME: str = dataclasses.field(  # pylint: disable=C0103
        metadata={"propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#id"})
    DESCRIPTION: str = dataclasses.field(  # pylint: disable=C0103
        metadata={"propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#description"})
    REFS: list[str] = dataclasses.field(  # pylint: disable=C0103
        metadata={"propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#source", "separator": ", "})
    TYPE: datatypes.DatatypeNameType = dataclasses.field(  # pylint: disable=C0103
        metadata={"dc:description": normalize_whitespace(datatypes.__doc__)}
    )
    URITEMPLATE: Optional[URITemplate] = dataclasses.field(  # pylint: disable=C0103
        metadata={
            "dc:description":
                "Several CLTS sources provide an online catalog of the graphemes they "
                "describe. If this is the case, the URI template specified in this "
                "column was used to derive the URL column in graphemes.csv."}
    )

    @classmethod
    def rel_path(cls) -> str:  # pylint: disable=C0116
        return 'sources/index.tsv'

    @classmethod
    def from_row(cls, row):
        """Instantiate a Source from a row in the index table."""
        row['REFS'] = nfilter([s.strip() for s in row['REFS'].split(',')])
        row['URITEMPLATE'] = URITemplate(row['URITEMPLATE']) if row['URITEMPLATE'] else None
        return cls(**row)

    @classmethod
    def sources_from_repos(cls, api):
        """Instantiate Source objects with the data from the index in the repos."""
        return [cls.from_row(r) for r in dict_reader(cls.path_in_repos(api))]

    def get_references(self, api) -> dict[str, CldfSource]:
        """Retrieve the bib entries for the reference keys."""
        return {key: CldfSource.from_entry(key, api.references[key]) for key in self.REFS}
