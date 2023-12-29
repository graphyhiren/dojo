from defusedxml import ElementTree as ET
from html2text import html2text

from dojo.models import Endpoint, Finding


class ZapParser(object):
    """Parser for XML file generated by the OWASP Zed Attacl Proxy (ZAP) tool https://www.zaproxy.org/."""

    MAPPING_SEVERITY = {"0": "Info", "1": "Low", "2": "Medium", "3": "High"}
    MAPPING_CONFIDENCE = {
        # "0": ??? CONFIDENCE_FALSE_POSITIVE => we don't do anything for now. it seems that the tool doesn't export them (filtered)
        "1": 7,  # CONFIDENCE_LOW => Tentative
        "2": 4,  # CONFIDENCE_MEDIUM => Firm
        "3": 1,  # CONFIDENCE_HIGH => Certain
        "4": 1,  # CONFIDENCE_USER_CONFIRMED => Certain
    }

    def get_scan_types(self):
        return ["ZAP Scan"]

    def get_label_for_scan_types(self, scan_type):
        return "ZAP Scan"

    def get_description_for_scan_types(self, scan_type):
        return "ZAP XML report format."

    def get_findings(self, file, test):
        tree = ET.parse(file)
        items = list()
        for node in tree.findall("site"):
            for item in node.findall("alerts/alertitem"):
                finding = Finding(
                    test=test,
                    title=item.findtext("alert"),
                    description=html2text(item.findtext("desc")),
                    severity=self.MAPPING_SEVERITY.get(
                        item.findtext("riskcode")
                    ),
                    scanner_confidence=self.MAPPING_CONFIDENCE.get(
                        item.findtext("riskcode")
                    ),
                    mitigation=html2text(item.findtext("solution")),
                    references=html2text(item.findtext("reference")),
                    dynamic_finding=True,
                    static_finding=False,
                    vuln_id_from_tool=item.findtext("pluginid"),
                )
                if (
                    item.findtext("cweid") is not None
                    and item.findtext("cweid").isdigit()
                ):
                    finding.cwe = int(item.findtext("cweid"))

                finding.unsaved_endpoints = []
                finding.unsaved_req_resp = []
                for instance in item.findall("instances/instance"):
                    endpoint = Endpoint.from_uri(instance.findtext("uri"))
                    # If the requestheader key is set, the report is in the "XML with requests and responses"
                    # format - load requests and responses and add them to the
                    # database
                    if instance.findtext("requestheader") is not None:
                        # Assemble the request from header and body
                        request = instance.findtext(
                            "requestheader"
                        ) + instance.findtext("requestbody")
                        response = instance.findtext(
                            "responseheader"
                        ) + instance.findtext("responsebody")
                    else:
                        # The report is in the regular XML format, without requests and responses.
                        # Use the default settings for constructing the request
                        # and response fields.
                        request = f"Method: {instance.findtext('method')} \nParam: {instance.findtext('param')} \nAttack: {instance.findtext('attack')} \nEndpointQuery: {endpoint.query} \nEndpointFragment: {endpoint.fragment}"
                        response = f"{instance.findtext('evidence')}"

                    # we remove query and fragment because with some configuration
                    # the tool generate them on-the-go and it produces a lot of
                    # fake endpoints
                    endpoint.query = None
                    endpoint.fragment = None
                    finding.unsaved_endpoints.append(endpoint)
                    finding.unsaved_req_resp.append(
                        {"req": request, "resp": response}
                    )
                items.append(finding)
        return items
