import hashlib
import json

from dojo.models import Endpoint, Finding

SEVERITY_MAP = {
    "BLOCKER": "Critical",
    "CRITICAL": "High",
    "MAJOR": "Medium",
    "MINOR": "Low",
    "INFO": "Info",
}


def _mask(text, n_plain=4):
    length = len(text)
    if length <= n_plain:
        n_plain = 0

    return text[:n_plain] + ("*" * (length - n_plain))


class WhispersParser(object):
    """
    Identify hardcoded secrets in static structured text
    """

    def get_scan_types(self):
        return ["Whispers Scan"]

    def get_label_for_scan_types(self, scan_type):
        return "Whispers Scan"

    def get_description_for_scan_types(self, scan_type):
        return "Whispers report file can be imported in JSON format (option --json)."

    def get_findings(self, file, test):
        tree = json.load(file)
        dupes = dict()

        for vuln in tree:
            summary = (
                f'Hardcoded {vuln.get("message")} "{vuln.get("key")}" '
                f'in {vuln.get("file")}:{vuln.get("line")}'
            )
            description = f'{summary} `{_mask(vuln.get("value"))}`'

            finding = Finding(
                title=summary,
                description=description,
                mitigation=(
                    "Replace hardcoded secret with a placeholder (ie: ENV-VAR). "
                    "Invalidate the leaked secret and generate a new one. "
                    "Supply the new secret through a placeholder to avoid disclosing "
                    "sensitive information in code."
                ),
                references=Endpoint.from_uri(
                    "https://cwe.mitre.org/data/definitions/798.html"
                ),
                cwe=798,
                severity=SEVERITY_MAP.get(vuln.get("severity"), "Info"),
                file_path=vuln.get("file"),
                line=int(vuln.get("line")),
                uniq_id_from_tool=hashlib.sha256(str(description).encode("utf-8")).hexdigest(),
                static_finding=True,
                dynamic_finding=False,
                test=test,
            )

            # internal de-duplication
            dupe_key = finding.hash_code
            if dupe_key in dupes:
                find = dupes[dupe_key]
                if finding.description:
                    find.description += "\n" + finding.description
                find.unsaved_endpoints.extend(finding.unsaved_endpoints)
                dupes[dupe_key] = find
            else:
                dupes[dupe_key] = finding

        return list(dupes.values())
