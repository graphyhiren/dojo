from django.test import TestCase
from dojo.tools.testssl.parser import TestsslParser
from dojo.models import Test


class TestTestsslParser(TestCase):

    def test_parse_file_with_no_vuln_has_no_finding(self):
        testfile = open("dojo/unittests/scans/testssl/defectdojo_no_vuln.csv")
        parser = TestsslParser()
        findings = parser.get_findings(testfile, Test())
        self.assertEqual(0, len(findings))

    def test_parse_file_with_one_vuln_has_one_finding(self):
        testfile = open("dojo/unittests/scans/testssl/defectdojo_one_vuln.csv")
        parser = TestsslParser()
        findings = parser.get_findings(testfile, Test())
        self.assertEqual(1, len(findings))

    def test_parse_file_with_many_vuln_has_many_findings(self):
        testfile = open("dojo/unittests/scans/testssl/defectdojo_many_vuln.csv")
        parser = TestsslParser()
        findings = parser.get_findings(testfile, Test())
        self.assertEqual(100, len(findings))
        # finding 8
        # "cipherlist_AVERAGE","www.defectdojo.org/185.199.110.153","443","LOW","offered","","CWE-310"
        finding = findings[8]
        self.assertEqual("Low", finding.severity)
        self.assertEqual(310, finding.cwe)
        # "LUCKY13","www.defectdojo.org/185.199.110.153","443","LOW","potentially vulnerable, uses TLS CBC ciphers","CVE-2013-0169","CWE-310"
        finding = findings[50]
        self.assertEqual("Low", finding.severity)
        self.assertEqual(310, finding.cwe)
        self.assertEqual("CVE-2013-0169", finding.cve)
        self.assertEqual(310, finding.cwe)

    def test_parse_file_with_many_cves(self):
        testfile = open("dojo/unittests/scans/testssl/many_cves.csv")
        parser = TestsslParser()
        findings = parser.get_findings(testfile, Test())
        self.assertEqual(2, len(findings))
        finding = findings[0]
        self.assertEqual("DROWN", finding.title)
        self.assertEqual("High", finding.severity)
        self.assertEqual("CVE-2016-0800", finding.cve)
        self.assertEqual(310, finding.cwe)
        finding = findings[1]
        self.assertEqual("DROWN", finding.title)
        self.assertEqual("High", finding.severity)
        self.assertEqual("CVE-2016-0703", finding.cve)
        self.assertEqual(310, finding.cwe)

    def test_parse_file_with_31_version(self):
        testfile = open("dojo/unittests/scans/testssl/demo.csv")
        parser = TestsslParser()
        findings = parser.get_findings(testfile, Test())
        self.assertEqual(12, len(findings))

    def test_parse_file_with_31_version2(self):
        testfile = open("dojo/unittests/scans/testssl/demo2.csv")
        parser = TestsslParser()
        findings = parser.get_findings(testfile, Test())
        self.assertEqual(3, len(findings))
