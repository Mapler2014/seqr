import json
import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls.base import reverse

from seqr.views.apis.phenotips_api import phenotips_edit_handler, phenotips_pdf_handler, receive_hpo_table_handler, update_individual_hpo_terms
from seqr.views.utils.test_utils import _check_login, create_proxy_request_stub

INDIVIDUAL_GUID = 'I000001_na19675'

NEW_INDIVIDUAL_GUID = 'I000001_nw19675'

class PhenotipsAPITest(TestCase):
    fixtures = ['users', '1kg_project', 'reference_data']
    multi_db = True

    @mock.patch('seqr.views.apis.phenotips_api.proxy_request', create_proxy_request_stub())
    def test_phenotips_edit(self):
        url = reverse(phenotips_edit_handler, args=['R0001_1kg', 'I000001_na19675'])
        _check_login(self, url)

        response = self.client.post(url, content_type='application/json', data=json.dumps({'some_json': 'test'}))
        self.assertEqual(response.status_code, 200)

    @mock.patch('seqr.views.apis.phenotips_api.proxy_request', create_proxy_request_stub())
    def test_phenotips_pdf(self):
        url = reverse(phenotips_pdf_handler, args=['R0001_1kg', 'I000001_na19675'])
        _check_login(self, url)

        response = self.client.post(url, content_type='application/json', data=json.dumps({'some_json': 'test'}))
        self.assertEqual(response.status_code, 200)

    def test_receive_hpo_table_handler(self):
        url = reverse(receive_hpo_table_handler, args=['R0001_1kg'])
        _check_login(self, url)

        # Send invalid requests
        header = 'family_id,indiv_id,hpo_term_yes,hpo_term_no'
        rows = [
            '1,NA19678,,',
            '1,NA19679,HP:0001631 (Defect in the atrial septum),',
            '1,HG00731,HP:0002017,HP:0012469 (Infantile spasms);HP:0011675 (Arrhythmia)',
        ]
        f = SimpleUploadedFile('updates.csv', b"{}\n{}".format(header, '\n'.join(rows)))
        response = self.client.post(url, data={'f': f})
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.json(), {'errors': ['Invalid header, missing individual id column'], 'warnings': []})

        header = 'family_id,individual_id,hpo_term_yes,hpo_term_no'
        f = SimpleUploadedFile('updates.csv', b"{}\n{}".format(header, '\n'.join(rows)))
        response = self.client.post(url, data={'f': f})
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.json(), {'errors': ['Invalid header, missing hpo terms columns'], 'warnings': []})

        header = 'family_id,individual_id,hpo_term_present,hpo_term_absent'
        f = SimpleUploadedFile('updates.csv', b"{}\n{}".format(header, '\n'.join(rows)))
        response = self.client.post(url, data={'f': f})
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.json(), {'errors': [
            'Unable to find individuals to update for any of the 3 parsed individuals. No matching ids found for 1 individuals. No changes detected for 2 individuals.'
        ], 'warnings': []})

        # send valid request
        rows.append('1,NA19675_1,HP:0002017,HP:0012469 (Infantile spasms);HP:0011675 (Arrhythmia)')
        f = SimpleUploadedFile('updates.csv', b"{}\n{}".format(header, '\n'.join(rows)))
        response = self.client.post(url, data={'f': f})
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), {
            'updatesByIndividualGuid': {'I000001_na19675': [
                {'id': 'HP:0002017', 'observed': 'yes', 'category': 'HP:0025031', 'label': 'Nausea and vomiting', 'type': 'phenotype'},
                {'id': 'HP:0012469', 'observed': 'no', 'category': 'HP:0025031', 'label': 'Infantile spasms', 'type': 'phenotype'},
            ]},
            'uploadedFileId': mock.ANY,
            'errors': [],
            'warnings': [
                "The following HPO terms were not found in seqr's HPO data and will not be added: HP:0001631 (NA19679); HP:0011675 (NA19675_1)",
                'Unable to find matching ids for 1 individuals. The following entries will not be updated: HG00731',
                'No changes detected for 2 individuals. The following entries will not be updated: NA19678, NA19679',
            ],
            'info': ['1 individuals will be updated'],
        })

    def test_update_individual_hpo_terms(self):
        url = reverse(update_individual_hpo_terms, args=[INDIVIDUAL_GUID])
        _check_login(self, url)

        # response = self.client.get(url)
        # self.assertEqual(response.status_code, 200)
        # response_json = response.json()
        # self.assertListEqual(response_json.keys(),
        #     ['phenotipsData', 'phenotipsEid'])