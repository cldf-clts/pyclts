"""
Metadata about the sources of transcription system data in CLTS are stored in sources/index.tsv.
"""
import dataclasses

from pyclts import datatypes


@dataclasses.dataclass
class Source:
    """CLTS is compiled from information about transcriptions and how these relate to
    sounds from many sources, such as phoneme inventory databases like PHOIBLE or
    relevant typological surveys."""
    NAME: str = dataclasses.field(
        metadata={"propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#id"})
    DESCRIPTION: str = dataclasses.field(
        metadata={"propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#description"})
    REFS: list[str] = dataclasses.field(
        metadata={"propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#source", "separator": ", "})
    TYPE: datatypes.DatatypeNameType = dataclasses.field(
        metadata={"dc:description": datatypes.__doc__.strip()}
    )
    #{
    #    "name": "URITEMPLATE",
    #    "dc:description":
    #        "Several CLTS sources provide an online catalog of the graphemes they "
    #        "describe. If this is the case, the URI template specified in this "
    #        "column was used to derive the URL column in graphemes.csv.",
    #    "datatype": {"base": "string"}
    #}

    @property
    def rel_path(self):
        return 'sources/index.tsv'

    def path_in_repos(self, api):
        return api.repos / self.rel_path


t = {
    "url": "sources/index.tsv",
            "dc:description":
                "CLTS is compiled from information about transcriptions and how these relate to "
                "sounds from many sources, such as phoneme inventory databases like PHOIBLE or "
                "relevant typological surveys.",
    "tableSchema": {
        "columns": [
            {
                "name": "NAME",
                "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#id",
                "datatype": {"base": "string"}
            },
            {
                "name": "DESCRIPTION",
                "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#description",
                "datatype": {"base": "string"}
            },
            {
                "name": "REFS",
                "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#source",
                "datatype": {"base": "string"},
                "separator": ", "
            },
            {
                "name": "TYPE",
                "dc:description":
                    "CLTS groups transcription information into three categories: "
                    "Transcription systems (`ts`), transcription data (`td`) and "
                    "soundclass systems (`sc`).",
                "datatype": {"base": "string", "format": "td|ts|sc"}
            },
            {
                "name": "URITEMPLATE",
                "dc:description":
                    "Several CLTS sources provide an online catalog of the graphemes they "
                    "describe. If this is the case, the URI template specified in this "
                    "column was used to derive the URL column in graphemes.csv.",
                "datatype": {"base": "string"}
            }
        ],
        "primaryKey": ["NAME"]
    }
}
