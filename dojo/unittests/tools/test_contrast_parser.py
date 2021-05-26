import datetime

from django.test import TestCase

from dojo.models import Test, Engagement, Product
from dojo.tools.contrast.parser import ContrastParser


class TestContrastParser(TestCase):

    def test_example_report(self):
        test = Test()
        test.engagement = Engagement()
        test.engagement.product = Product()
        testfile = open("dojo/unittests/scans/contrast/contrast-node-goat.csv")
        parser = ContrastParser()
        findings = parser.get_findings(testfile, test)
        self.assertEqual(18, len(findings))
        with self.subTest(i=0):
            finding = findings[0]
            self.assertEqual("Info", finding.severity)
            self.assertEqual("Forms Without Autocomplete Prevention on 2 pages", finding.title)
            self.assertEqual("OMEC-Y0TI-FRLE-FJQQ", finding.unique_id_from_tool)
            self.assertEqual(522, finding.cwe)
            self.assertEqual(datetime.date(2018, 4, 23), finding.date.date())
            # endpoints
            self.assertIsNotNone(finding.unsaved_endpoints)
            self.assertEqual(1, len(finding.unsaved_endpoints))
            endpoint = finding.unsaved_endpoints[0]
            endpoint.clean()
            self.assertFalse(endpoint.is_broken)
            self.assertEqual('http', endpoint.protocol)
            self.assertEqual('0.0.0.0', endpoint.host)
            self.assertEqual('WebGoat/login.mvc', endpoint.path)
        with self.subTest(i=11):
            finding = findings[11]
            self.assertEqual(datetime.date(2018, 4, 23), finding.date.date())
            self.assertEqual("High", finding.severity)
            self.assertEqual("path-traversal", finding.vuln_id_from_tool)
            self.assertIsNone(finding.unique_id_from_tool)  # aggregated finding
            self.assertEqual(4, finding.nb_occurences)
            self.assertEqual(22, finding.cwe)
            # endpoints
            self.assertIsNotNone(finding.unsaved_endpoints)
            self.assertEqual(4, len(finding.unsaved_endpoints))
            endpoint = finding.unsaved_endpoints[0]
            endpoint.clean()
            self.assertFalse(endpoint.is_broken)
            self.assertEqual('http', endpoint.protocol)
            self.assertEqual('0.0.0.0', endpoint.host)
            self.assertEqual('WebGoat/services/SoapRequest', endpoint.path)
            endpoint = finding.unsaved_endpoints[1]
            endpoint.clean()
            self.assertFalse(endpoint.is_broken)
            self.assertEqual('http', endpoint.protocol)
            self.assertEqual('0.0.0.0', endpoint.host)
            self.assertEqual('WebGoat/attack', endpoint.path)

    def test_example2_report(self):
        test = Test()
        test.engagement = Engagement()
        test.engagement.product = Product()
        testfile = open("dojo/unittests/scans/contrast/vulnerabilities2020-09-21.csv")
        parser = ContrastParser()
        findings = parser.get_findings(testfile, test)
        self.assertEqual(1, len(findings))
        with self.subTest(i=0):
            finding = findings[0]
            self.assertEqual(datetime.date(2020, 5, 22), finding.date.date())
            self.assertEqual("Medium", finding.severity)
            self.assertEqual("crypto-bad-mac", finding.vuln_id_from_tool)
            self.assertEqual("072U-8EYA-BNSH-PGN6", finding.unique_id_from_tool)
            self.assertEqual(327, finding.cwe)
            self.assertEqual(0, len(finding.unsaved_endpoints))
