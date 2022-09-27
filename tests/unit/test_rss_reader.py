import unittest
from io import StringIO
from unittest.mock import patch
from rss_reader import arg_parser

class TestArgParser(unittest.TestCase):
    @patch('sys.stderr', new_callable=StringIO)
    def test_should_exit_on_missing_url_arg(self, mock_stderr):
        """ Try to run without mandatory url arg """
        args = []
        with self.assertRaises(SystemExit):
            arg_parser.parse_args(args)
        self.assertRegexpMatches(
            mock_stderr.getvalue(),
            r"the following arguments are required")

    @patch('sys.stderr', new_callable=StringIO)
    def test_should_accept_only_one_positional_arg(self, mock_stderr):
        """ Try to pass more than one positional arg. """
        args = ["http://www.example.com", "other_string"]
        with self.assertRaises(SystemExit):
            arg_parser.parse_args(args)
        self.assertRegexpMatches(
            mock_stderr.getvalue(),
            r"unrecognized arguments")

    @patch('sys.stderr', new_callable=StringIO)
    def test_limit_should_accept_only_integer(self, mock_stderr):
        """ Try to pass string as limit value and then int. """
        args = ["http://www.example.com", "--limit", "dasdas"]
        with self.assertRaises(SystemExit):
            arg_parser.parse_args(args)
        self.assertRegexpMatches(
            mock_stderr.getvalue(),
            r"argument --limit: invalid int value")
        args = ["http://www.example.com", "--limit", "10"]
        self.assertEqual(arg_parser.parse_args(args).limit, 10)

    def test_json_arg(self):
        """ Try to pass --json arg. """
        args = ["http://www.example.com", "--json"]
        self.assertTrue(arg_parser.parse_args(args).to_json)

    def test_verbose_arg(self):
        """ Try to pass --verbose arg. """
        args = ["http://www.example.com", "--verbose"]
        self.assertTrue(arg_parser.parse_args(args).verbose)

    @patch('sys.stdout', new_callable=StringIO)
    def test_version_arg(self, mock_stdout):
        """
        Try to pass --version arg only.
        This should not raise an error of missing url arg
        and show version.
        """
        args = ["--version"]
        version_regex = r"^rss_reader (\d+\\.)?(\d+\\.)?(\\*|\d+).*$"
        with self.assertRaises(SystemExit):
            arg_parser.parse_args(args)
        self.assertRegexpMatches(
            mock_stdout.getvalue(),
            version_regex)

if __name__ == '__main__':
    unittest.main()

