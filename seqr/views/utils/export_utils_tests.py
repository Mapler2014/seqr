# -*- coding: utf-8 -*-

from django.test import TestCase

from openpyxl import load_workbook
from StringIO import StringIO
import mock

from seqr.views.utils.export_utils import export_table, export_multiple_files


class ExportTableUtilsTest(TestCase):
    fixtures = ['users', '1kg_project']

    def test_export_table(self):
        header = ['column1', 'column2']
        rows = [['row1_v1', 'row1_v2'], ['row2_v1', 'row2_v2']]

        # test tsv format
        response = export_table('test_file', header, rows, file_format='tsv')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('content-disposition'), 'attachment; filename="test_file.tsv"')
        self.assertEqual(response.content, '\n'.join(['\t'.join(row) for row in [header]+rows]) + '\n')

        # test Excel format
        response = export_table('test_file', header, rows, file_format='xls')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('content-disposition'), 'attachment; filename="test_file.xlsx"')
        wb = load_workbook(StringIO(response.content))
        worksheet = wb.active

        self.assertListEqual([cell.value for cell in worksheet['A']], ['Column1', 'row1_v1', 'row2_v1'])
        self.assertListEqual([cell.value for cell in worksheet['B']], ['Column2', 'row1_v2', 'row2_v2'])
        self.assertEqual([cell.value for cell in worksheet['C']], [None, None, None])

        # test unknown format
        self.assertRaisesRegexp(ValueError, '.*format.*',
            lambda: export_table('test_file', header, rows, file_format='unknown_format')
        )

    @mock.patch('seqr.views.utils.export_utils.zipfile.ZipFile')
    def test_export_multiple_files(self, mock_zip):
        mock_zip_content = {}
        def mock_write_zip(file, content):
            mock_zip_content[file] = content.decode('utf-8')
        mock_zip.return_value.__enter__.return_value.writestr.side_effect = mock_write_zip

        header1 = ['col1', 'col2']
        header2 = ['col1']
        header3 = ['col2', 'col3', 'col1']
        rows = [{'col2': 'row1_v2', 'col1': u'row1_v1\xe2'}, {'col1': 'row2_v1'}]

        # test csv format
        response = export_multiple_files([[u'file1\xe3', header1, rows], ['file2', header2, rows]], 'zipfile')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('content-disposition'), 'attachment; filename="zipfile.zip"')
        self.assertDictEqual(mock_zip_content, {
            u'file1\xe3.csv': u'col1,col2\nrow1_v1\xe2,row1_v2\nrow2_v1,',
            'file2.csv': u'col1\nrow1_v1\xe2\nrow2_v1',
        })
        mock_zip_content = {}

        response = export_multiple_files(
            [['file1', header1, rows], ['file2', header2, rows]], 'zipfile', file_format='tsv')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('content-disposition'), 'attachment; filename="zipfile.zip"')
        self.assertDictEqual(mock_zip_content, {
            'file1.tsv': u'col1\tcol2\nrow1_v1\xe2\trow1_v2\nrow2_v1\t',
            'file2.tsv': u'col1\nrow1_v1\xe2\nrow2_v1',
        })
        mock_zip_content = {}

        response = export_multiple_files(
            [['file1', header1, rows], ['file2', header3, rows]], 'zipfile', add_header_prefix=True, blank_value='X')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('content-disposition'), 'attachment; filename="zipfile.zip"')
        self.assertDictEqual(mock_zip_content, {
            'file1.csv': u'col1,01-col2\nrow1_v1\xe2,row1_v2\nrow2_v1,X',
            'file2.csv': u'col2,01-col3,02-col1\nrow1_v2,X,row1_v1\xe2\nX,X,row2_v1',
        })
        mock_zip_content = {}

        # test unknown format
        with self.assertRaises(ValueError) as cm:
            export_multiple_files([['file1', header1, rows], ['file2', header2, rows]], 'zipfile', file_format='foo')
        self.assertEqual(cm.exception.message, 'Invalid file_format: foo')
