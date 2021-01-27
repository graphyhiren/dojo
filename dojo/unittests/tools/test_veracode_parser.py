from django.test import SimpleTestCase
from dojo.tools.veracode.parser import VeracodeXMLParser
from dojo.models import Test


class TestVeracodeScannerParser(SimpleTestCase):
    def test_parse_without_file(self):
        parser = VeracodeXMLParser()
        findings = parser.get_findings(None, Test())
        self.assertEqual(0, len(findings))

    def test_parse_file_with_one_finding(self):
        testfile = open("dojo/unittests/scans/veracode/one_finding.xml")
        parser = VeracodeXMLParser()
        findings = parser.get_findings(testfile, Test())
        self.assertEqual(1, len(findings))

    def test_parse_file_with_multiple_finding(self):
        testfile = open("dojo/unittests/scans/veracode/many_findings.xml")
        parser = VeracodeXMLParser()
        findings = parser.get_findings(testfile, Test())
        self.assertEqual(3, len(findings))
