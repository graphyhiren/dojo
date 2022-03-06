import csv
import hashlib
import io
import json

from dateutil.parser import parse
from dojo.models import Endpoint, Finding
from dojo.tools.parser_test import ParserTest


class GenericParser(object):
    ID = "Generic Findings Import"

    def get_scan_types(self):
        return [self.ID]

    def get_label_for_scan_types(self, scan_type):
        return scan_type  # no custom label for now

    def get_description_for_scan_types(self, scan_type):
        return "Import Generic findings in CSV format."

    def get_findings(self, filename, test):
        if filename.name.lower().endswith(".csv"):
            return self._get_findings_csv(filename)
        elif filename.name.lower().endswith(".json"):
            data = json.load(filename)
            test_internal = self._get_test_json(data)
            return test_internal.findings
        else:  # default to CSV like before
            return self._get_findings_csv(filename)

    def get_tests(self, scan_type, filename):
        # if the file is a CSV just use the old function
        if filename.name.lower().endswith(".csv"):
            test = ParserTest(name=self.ID, type=self.ID, version=None)
            test.findings = self._get_findings_csv(filename)
            return [test]
        # we manage it like a JSON file (default)
        data = json.load(filename)
        return [self._get_test_json(data)]

    def requires_file(self, scan_type):
        return True

    def _get_test_json(self, data):
        test_internal = ParserTest(
            name=data.get("name", self.ID),
            type=data.get("type", self.ID),
            version=data.get("version"),
        )
        test_internal.findings = list()
        for item in data.get("findings", []):
            # remove endpoints of the dictionnary
            unsaved_endpoints = None
            if "endpoints" in item:
                unsaved_endpoints = item["endpoints"]
                del item["endpoints"]
            # remove files of the dictionnary
            unsaved_files = None
            if "files" in item:
                unsaved_files = item["files"]
                del item["files"]

            finding = Finding(**item)

            # manage endpoints
            if unsaved_endpoints:
                finding.unsaved_endpoints = []
                for endpoint_item in unsaved_endpoints:
                    if type(endpoint_item) is str:
                        if "://" in endpoint_item:  # is the host full uri?
                            endpoint = Endpoint.from_uri(endpoint_item)
                            # can raise exception if the host is not valid URL
                        else:
                            endpoint = Endpoint.from_uri("//" + endpoint_item)
                            # can raise exception if there is no way to parse the host
                    else:
                        endpoint = Endpoint(**endpoint_item)
                    finding.unsaved_endpoints.append(endpoint)

            if unsaved_files:
                finding.unsaved_files = unsaved_files
            test_internal.findings.append(finding)
        return test_internal

    def _get_findings_csv(self, filename):
        content = filename.read()
        if type(content) is bytes:
            content = content.decode("utf-8")
        reader = csv.DictReader(io.StringIO(content), delimiter=",", quotechar='"')

        dupes = dict()
        for row in reader:
            finding = Finding(
                title=row["Title"],
                description=row["Description"],
                date=parse(row["Date"]).date(),
                severity=row["Severity"],
                duplicate=self._convert_bool(row.get("Duplicate", "FALSE")),  # bool False by default
                nb_occurences=1,
            )
            # manage active
            if "Active" in row:
                finding.active = self._convert_bool(row.get("Active"))
            # manage mitigation
            if "Mitigation" in row:
                finding.mitigation = row["Mitigation"]
            # manage impact
            if "Impact" in row:
                finding.impact = row["Impact"]
            # manage impact
            if "References" in row:
                finding.references = row["References"]
            # manage verified
            if "Verified" in row:
                finding.verified = self._convert_bool(row.get("Verified"))
            # manage false positives
            if "FalsePositive" in row:
                finding.false_p = self._convert_bool(row.get("FalsePositive"))
            # manage CVE
            if "CVE" in row:
                finding.cve = row["CVE"]
            # manage CWE
            if "CweId" in row:
                finding.cwe = int(row["CweId"])
            # FIXME remove this severity hack
            if finding.severity == "Unknown":
                finding.severity = "Info"

            if "CVSSV3" in row:
                finding.cvssv3 = row["CVSSV3"]

            # manage endpoints
            if "Url" in row:
                finding.unsaved_endpoints = [
                    Endpoint.from_uri(row["Url"]) if "://" in row["Url"] else Endpoint.from_uri("//" + row["Url"])
                ]

            # manage internal de-duplication
            key = hashlib.sha256(
                "|".join(
                    [
                        finding.severity,
                        finding.title,
                        finding.description,
                    ]
                ).encode("utf-8")
            ).hexdigest()
            if key in dupes:
                find = dupes[key]
                find.unsaved_endpoints.extend(finding.unsaved_endpoints)
                find.nb_occurences += 1
            else:
                dupes[key] = finding

        return list(dupes.values())

    def _convert_bool(self, val):
        return val.lower()[0:1] == "t"  # bool False by default
