import hashlib
import json
from urllib.parse import urlparse
from dojo.models import Endpoint, Finding


class SecureCodeBoxParser(object):
    """
    importing Findings generated by https://github.com/secureCodeBox/secureCodeBox
    """

    def get_scan_types(self):
        return ["SecureCodeBox Findings Import"]

    def get_label_for_scan_types(self, scan_type):
        return "SecureCodeBox Findings Import"

    def get_description_for_scan_types(self, scan_type):
        return "SecureCodeBox Findings file in JSON format can be imported."

    def get_findings(self, file, test):
        if file is None:
            return []
        try:
            tree = json.load(file)
        except json.JSONDecodeError:
            raise ValueError("file is not valid json")
        else:
            dupes = dict()
            for idx, content in enumerate(tree):
                finding = Finding(
                    static_finding=True, dynamic_finding=False, active=False, verified=False)
                node = tree[idx]
                self.set_finding_base_info(finding, node, test)
                finding_unique_string = str(node['location'] +
                                            finding.description + finding.title)
                dupe_key = hashlib.md5(
                    finding_unique_string.encode('utf-8')).hexdigest()
                if dupe_key not in dupes:
                    self.set_finding_endpoint(finding, node)
                    dupes[dupe_key] = finding
            return list(dupes.values())

    def set_finding_endpoint(self, finding, node):
        finding.unsaved_endpoints = list()
        endpoint = Endpoint()
        url = node['location']
        parsedUrl = urlparse(url)
        endpoint.protocol = parsedUrl.scheme
        endpoint.query = parsedUrl.query
        endpoint.fragment = parsedUrl.fragment
        endpoint.path = parsedUrl.path
        try:
            (endpoint.host, port) = parsedUrl.netloc.split(':')
            endpoint.port = int(port)
        except:
            endpoint.host = parsedUrl.netloc
            endpoint.port = None
        if 'attributes' in node:
            attributes = node['attributes']
            # override if present in attributes
            endpoint.host = attributes.get('hostname', endpoint.host)
            # override if present in attributes
            endpoint.port = attributes.get('port', endpoint.port)
            # override if present in attributes
            endpoint.protocol = attributes.get('protocol', endpoint.protocol)
        finding.unsaved_endpoints = [endpoint]

    def set_finding_base_info(self, finding, node, test):
        na = 'N/A'
        # using node.get('name',na) does not work because the value can still be None
        finding.title = node.get('name') or na
        finding.description = node.get('description') or na
        finding.severity = self.get_severity(node.get('severity'))
        finding.test = test

    def get_severity(self, severity):
        if severity == "LOW":
            return "Low"
        elif severity == "MEDIUM":
            return "Medium"
        elif severity == "HIGH":
            return "High"
        else:
            return "Info"
