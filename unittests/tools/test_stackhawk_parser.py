import datetime

from dojo.tools.stackhawk.parser import StackHawkParser
from dojo.models import Test, Finding
from unittests.dojo_test_case import DojoTestCase


class TestStackHawkParser(DojoTestCase):
    __test_datetime = datetime.datetime(2022, 2, 16, 23, 7, 19, 575000, datetime.timezone.utc)

    def test_invalid_json_format(self):
        testfile = open("unittests/scans/stackhawk/invalid.json")
        parser = StackHawkParser()
        with self.assertRaises(Exception):
            parser.get_findings(testfile, Test())

    def test_parser_ensures_data_is_for_stackhawk_before_parsing(self):
        testfile = open("unittests/scans/stackhawk/oddly_familiar_json_that_isnt_us.json")
        parser = StackHawkParser()
        with self.assertRaises(Exception):
            parser.get_findings(testfile, Test())

    def test_stackhawk_parser_with_no_vuln_has_no_findings(self):
        testfile = open("unittests/scans/stackhawk/stackhawk_zero_vul.json")
        parser = StackHawkParser()
        findings = parser.get_findings(testfile, Test())
        testfile.close()
        self.assertEqual(0, len(findings))

    def test_stackhawk_parser_with_one_high_vuln_has_one_findings(self):
        testfile = open("unittests/scans/stackhawk/stackhawk_one_vul.json")
        parser = StackHawkParser()
        findings = parser.get_findings(testfile, Test())
        testfile.close()
        self.__assertAllEndpointsAreClean(findings)
        self.assertEqual(1, len(findings))

        finding = findings[0]

        self.__assertFindingEquals(
            finding,
            "Anti CSRF Tokens Scanner",
            self.__test_datetime,
            "Secured Application",
            "Development",
            "High",
            1,
            "https://app.stackhawk.com/scans/e2ff5651-7eef-47e9-b743-0c2f7d861e27/finding/20012",
            "20012",
            "10"
        )

    def test_stackhawk_parser_with_many_vuln_has_many_findings_and_removes_duplicates(self):
        testfile = open("unittests/scans/stackhawk/stackhawk_many_vul.json")
        parser = StackHawkParser()
        findings = parser.get_findings(testfile, Test())
        testfile.close()
        self.__assertAllEndpointsAreClean(findings)
        self.assertEqual(6, len(findings))

        self.__assertFindingEquals(
            findings[0],
            "Cookie Slack Detector",
            self.__test_datetime,
            "Secured Application",
            "Development",
            "Low",
            3,
            "https://app.stackhawk.com/scans/e2ff5651-7eef-47e9-b743-0c2f7d861e27/finding/90027",
            "90027",
            "10"
        )

        self.__assertFindingEquals(
            findings[1],
            "Proxy Disclosure",
            self.__test_datetime,
            "Secured Application",
            "Development",
            "Medium",
            2,
            "https://app.stackhawk.com/scans/e2ff5651-7eef-47e9-b743-0c2f7d861e27/finding/40025",
            "40025",
            "10"
        )

        self.__assertFindingEquals(
            findings[2],
            "Anti CSRF Tokens Scanner",
            self.__test_datetime,
            "Secured Application",
            "Development",
            "High",
            1,
            "https://app.stackhawk.com/scans/e2ff5651-7eef-47e9-b743-0c2f7d861e27/finding/20012",
            "20012",
            "10"
        )

        self.__assertFindingEquals(
            findings[3],
            "Cross Site Scripting Weakness (Reflected in JSON Response)",
            self.__test_datetime,
            "Secured Application",
            "Development",
            "High",
            1,
            "https://app.stackhawk.com/scans/e2ff5651-7eef-47e9-b743-0c2f7d861e27/finding/40012",
            "40012",
            "1"
        )

        self.__assertFindingEquals(
            findings[4],
            "Content Security Policy (CSP) Header Not Set",
            self.__test_datetime,
            "Secured Application",
            "Development",
            "Medium",
            2,
            "https://app.stackhawk.com/scans/e2ff5651-7eef-47e9-b743-0c2f7d861e27/finding/10038",
            "10038",
            "12"
        )

        self.__assertFindingEquals(
            findings[5],
            "Permissions Policy Header Not Set",
            self.__test_datetime,
            "Secured Application",
            "Development",
            "Low",
            3,
            "https://app.stackhawk.com/scans/e2ff5651-7eef-47e9-b743-0c2f7d861e27/finding/10063",
            "10063",
            "12"
        )

    def test_that_a_scan_import_updates_the_test_description(self):
        testfile = open("unittests/scans/stackhawk/stackhawk_zero_vul.json")
        parser = StackHawkParser()
        test = Test()
        parser.get_findings(testfile, test)
        testfile.close()
        self.assertEqual(
            test.description,
            'View scan details here: ' +
            '[https://app.stackhawk.com/scans/e2ff5651-7eef-47e9-b743-0c2f7d861e27]' +
            '(https://app.stackhawk.com/scans/e2ff5651-7eef-47e9-b743-0c2f7d861e27)'
        )

    def __assertFindingEquals(
            self,
            actual_finding: Finding,
            title,
            date: datetime.datetime,
            application_name,
            environment,
            severity,
            severity_num,
            finding_url,
            finding_id,
            count
    ):
        self.assertEqual(title, actual_finding.title)
        self.assertEqual(date, actual_finding.date)
        self.assertEqual(application_name, actual_finding.component_name)
        self.assertEqual(environment, actual_finding.component_version)
        self.assertEqual(severity, actual_finding.severity)
        self.assertEqual("View this finding in the StackHawk platform at:\n[" + finding_url + '](' + finding_url + ')',
                         actual_finding.description)
        self.assertRegexpMatches(
            actual_finding.steps_to_reproduce,
            "Use a specific message link and click 'Validate' to see the cURL!.*"
        )
        self.assertTrue(actual_finding.active)
        self.assertTrue(actual_finding.verified)
        self.assertEqual(severity_num, actual_finding.numerical_severity)
        self.assertFalse(actual_finding.static_finding)
        self.assertTrue(actual_finding.dynamic_finding)
        self.assertEqual(finding_id, actual_finding.unique_id_from_tool)
        self.assertEqual(finding_id, actual_finding.vuln_id_from_tool)
        self.assertEqual(count, actual_finding.nb_occurences)
        self.assertEqual(application_name, actual_finding.service)

    def __assertAllEndpointsAreClean(self, findings):
        for finding in findings:
            for endpoint in finding.unsaved_endpoints:
                endpoint.clean()
