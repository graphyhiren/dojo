from collections import namedtuple

BlackduckBinaryAnalysisFinding = namedtuple(
    "BlackduckBinaryAnalysisFinding",
    [
        "report_path",
        "component",
        "version",
        "latest_version",
        "cve",
        "matching_type",
        "cvss_v2",
        "cve_publication_date",
        "object_compilation_date",
        "object_name",
        "object_full_path",
        "object_sha1",
        "cvss_v3",
        "cvss_vector_v2",
        "cvss_vector_v3",
        "summary",
        "distribution_package",
        "cvss_distribution_v2",
        "cvss_distribution_v3",
        "triage_vectors",
        "unresolving_triage_vectors",
        "note_type",
        "note_reason",
        "vulnerability_url",
        "missing_exploit_mitigations",
        "bdsa",
        "version_override_type",
    ],
)

