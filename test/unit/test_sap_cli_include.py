#!/usr/bin/env python3

import unittest
from unittest.mock import patch, mock_open
from io import StringIO
from argparse import ArgumentParser

import sap.cli.include

from mock import Connection
from fixtures_adt import LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK


FIXTURE_STDIN_REPORT_SRC='* from stdin'
FIXTURE_FILE_REPORT_SRC='* from file'


def parse_args(*argv):
    parser = ArgumentParser()
    sap.cli.include.CommandGroup().install_parser(parser)
    return parser.parse_args(argv)


class TestIncludeCommandGroup(unittest.TestCase):

    def test_constructor(self):
        sap.cli.include.CommandGroup()


class TestIncludeCreate(unittest.TestCase):

    def test_create_include_with_corrnr(self):
        connection = Connection([EMPTY_RESPONSE_OK])

        args = parse_args('create', 'zinclude', 'description', 'package', '--corrnr', '420')
        args.execute(connection, args)

        self.assertEqual(connection.execs[0].params['corrNr'], '420')


class TestIncludeWrite(unittest.TestCase):

    def test_read_from_stdin(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, EMPTY_RESPONSE_OK])

        args = parse_args('write', 'zinclude', '-')
        with patch('sys.stdin', StringIO(FIXTURE_STDIN_REPORT_SRC)):
            sap.cli.include.write(conn, args)

        self.assertEqual(len(conn.execs), 3)

        self.maxDiff = None
        self.assertEqual(conn.execs[1][3], FIXTURE_STDIN_REPORT_SRC)

    def test_read_from_file(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, EMPTY_RESPONSE_OK])

        args = parse_args('write', 'zinclude', 'zinclude.abap')
        with patch('sap.cli.include.open', mock_open(read_data=FIXTURE_FILE_REPORT_SRC)) as m:
            sap.cli.include.write(conn, args)

        m.assert_called_once_with('zinclude.abap')

        self.assertEqual(len(conn.execs), 3)

        self.maxDiff = None
        self.assertEqual(conn.execs[1][3], FIXTURE_FILE_REPORT_SRC)

    def test_write_with_corrnr(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, EMPTY_RESPONSE_OK])

        args = parse_args('write', 'zinclude', 'zinclude.abap', '--corrnr', '420')
        with patch('sap.cli.include.open', mock_open(read_data=FIXTURE_FILE_REPORT_SRC)) as m:
            sap.cli.include.write(conn, args)

        self.assertEqual(conn.execs[1].params['corrNr'], '420')


class TestIncludeActivate(unittest.TestCase):

    def test_activate(self):
        conn = Connection([EMPTY_RESPONSE_OK])

        args = parse_args('activate', 'test_activation')
        sap.cli.include.activate(conn, args)

        self.assertEqual(len(conn.execs), 1)
        self.assertIn('test_activation', conn.execs[0].body)


if __name__ == '__main__':
    unittest.main()
