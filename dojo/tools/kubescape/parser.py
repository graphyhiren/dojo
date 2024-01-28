import json
from dojo.models import Endpoint, Finding


class KubescapeParser(object):
    def get_scan_types(self):
        return ["Kubescape JSON Importer"]

    def get_label_for_scan_types(self, scan_type):
        return scan_type  # no custom label for now

    def get_description_for_scan_types(self, scan_type):
        return "Import result of Kubescape JSON output."

    def severity_mapper(self, input):
        if input == 1:
            return "Low"
        elif input == 2:
            return "Medium"
        elif input == 3:
            return "High"

    def get_findings(self, filename, test):
        findings = []
        try:
            data = json.load(filename)
        except ValueError:
            data = {}
        for resource in data["resources"]:
            resourceid = resource["resourceID"]
            results = ([each for each in data["results"] if each.get('resourceID') == resourceid])
            controls = results[0].get("controls", [])
            try:
                prioritizedResource = results[0]["prioritizedResource"]["severity"]
            except KeyError:
                prioritizedResource = "Info"
            for control in controls:
                controlID = control['controlID']#.get('name')
                description = control["name"] + "\n\n"
                description += "**Rules:** " + str(control["rules"])
                """TODO, PARSE THE RIGHT VALUES INTO THE FINDING"""
                if self.severity_mapper(prioritizedResource) == None:
                    severity = "Info"
                else:
                    severity = self.severity_mapper(prioritizedResource)
                find = Finding(title=resourceid+"_"+str(controlID),
                test=test,
                description=description,
                severity=severity,
                static_finding=True)
                findings.append(find)
        return findings
