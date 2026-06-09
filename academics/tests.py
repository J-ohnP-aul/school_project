from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import StudentProfile, TeacherProfile
from academics.models import Assessment, Competency, Subject, Term


class AssessmentRecordingTests(TestCase):
    def setUp(self):
        self.teacher_user = User.objects.create_user(
            username='teacher_assessment',
            password='password123',
        )
        self.teacher = TeacherProfile.objects.create(
            user=self.teacher_user,
            subject='Mathematics',
        )

        self.student_user = User.objects.create_user(
            username='student_assessment',
            password='password123',
        )
        self.student = StudentProfile.objects.create(
            user=self.student_user,
            admission_number='ADM-001',
            grade='Grade 2',
            guardian_name='Guardian Name',
            guardian_phone='0712345678',
        )

        self.subject = Subject.objects.create(name='Mathematics')
        self.term = Term.objects.create(name='Term 1')
        self.competency = Competency.objects.create(name='Number Sense')

        self.client.force_login(self.teacher_user)

    def test_record_assessment_saves_with_performance_band(self):
        response = self.client.post(
            reverse('academics:record_assessment'),
            {
                'student': self.student.pk,
                'subject': self.subject.pk,
                'competency': self.competency.pk,
                'term': self.term.pk,
                'perfomance_band': 'ME',
                'remarks': 'Improving well.',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Assessment.objects.count(), 1)

        assessment = Assessment.objects.get()
        self.assertEqual(assessment.teacher, self.teacher)
        self.assertEqual(assessment.perfomance_band, 'ME')


class CBCAssessmentTests(TestCase):
    def setUp(self):
        # Teacher and related objects
        self.teacher_user = User.objects.create_user(username='t1', password='pw')
        self.teacher = TeacherProfile.objects.create(user=self.teacher_user, subject='Science')

        self.client.force_login(self.teacher_user)

        # Subject/term/competency
        self.subject = Subject.objects.create(name='Science')
        self.term = Term.objects.create(name='Term 1')
        self.competency = Competency.objects.create(name='General')

    def _create_student(self, idx, grade='Grade X', stream=''):
        u = User.objects.create_user(username=f'student{idx}', password='pw')
        s = StudentProfile.objects.create(
            user=u,
            admission_number=f'ADM-{idx:03d}',
            grade=grade,
            stream=stream,
            guardian_name='G',
            guardian_phone='0712345678'
        )
        return s

    def test_draftassessment_save_and_retrieve(self):
        from academics.models import DraftAssessment

        student = self._create_student(1, grade='Grade 1', stream='A')

        draft_data = {str(student.id): {'percentage': 78, 'remarks': 'Good', 'absent': False}}

        draft = DraftAssessment.objects.create(
            teacher=self.teacher,
            grade='Grade 1',
            stream='A',
            subject=self.subject,
            competency=self.competency,
            term=self.term,
            draft_data=draft_data
        )

        fetched = DraftAssessment.objects.get(id=draft.id)
        self.assertEqual(fetched.draft_data, draft_data)
        filled, total = fetched.get_completion_count()
        self.assertEqual(filled, 1)
        self.assertEqual(total, 1)

    def test_get_streams_endpoint_returns_existing_streams(self):
        # create students with streams
        self._create_student(2, grade='G3', stream='A')
        self._create_student(3, grade='G3', stream='B')
        self._create_student(4, grade='G3', stream='')

        url = reverse('academics:get_streams') + '?grade=G3'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        streams = [s['value'] for s in data.get('streams', [])]
        # first option is '' for All Streams
        self.assertIn('', streams)
        self.assertIn('A', streams)
        self.assertIn('B', streams)

    def test_get_students_paginates_20_per_page(self):
        # create 25 students in same grade
        students = [self._create_student(i, grade='G4') for i in range(1, 26)]

        url = reverse('academics:get_students')
        params = {
            'grade': 'G4',
            'stream': '',
            'subject': str(self.subject.id),
            'competency': str(self.competency.id),
            'term': str(self.term.id),
        }
        resp1 = self.client.get(url, params)
        self.assertEqual(resp1.status_code, 200)
        d1 = resp1.json()
        self.assertEqual(len(d1['students']), 20)
        self.assertTrue(d1['has_next'])

        # second page
        params['page'] = 2
        resp2 = self.client.get(url, params)
        d2 = resp2.json()
        self.assertEqual(len(d2['students']), 5)
        self.assertFalse(d2['has_next'])

    def test_get_band_from_percentage_boundaries(self):
        from academics.views import get_band_from_percentage

        self.assertEqual(get_band_from_percentage(95), 'EE1')
        self.assertEqual(get_band_from_percentage(90), 'EE1')
        self.assertEqual(get_band_from_percentage(89.9), 'EE2')
        self.assertEqual(get_band_from_percentage(75), 'EE2')
        self.assertEqual(get_band_from_percentage(74.9), 'ME1')
        self.assertEqual(get_band_from_percentage(58), 'ME1')
        self.assertEqual(get_band_from_percentage(41), 'ME2')
        self.assertEqual(get_band_from_percentage(31), 'AE1')
        self.assertEqual(get_band_from_percentage(21), 'AE2')
        self.assertEqual(get_band_from_percentage(11), 'BE1')
        self.assertEqual(get_band_from_percentage(1), 'BE2')
        self.assertEqual(get_band_from_percentage(0), 'BE2')

    def test_save_draft_stores_partial_data_and_resume(self):
        # create two students and save a draft via API
        s1 = self._create_student(30, grade='G5')
        s2 = self._create_student(31, grade='G5')

        url = reverse('academics:save_draft')
        payload = {
            'grade': 'G5',
            'stream': '',
            'subject_id': self.subject.id,
            'competency_id': self.competency.id,
            'term_id': self.term.id,
            'draft_data': {
                str(s1.id): {'percentage': 88, 'remarks': 'Nice'},
                str(s2.id): {'percentage': '', 'remarks': ''}
            }
        }
        import json
        resp = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get('success'))
        draft_id = data.get('draft_id')
        from academics.models import DraftAssessment
        draft = DraftAssessment.objects.get(id=draft_id)
        self.assertIn(str(s1.id), draft.draft_data)

        # Now fetch students and ensure draft values are returned
        students_url = reverse('academics:get_students')
        params = {
            'grade': 'G5',
            'stream': '',
            'subject': str(self.subject.id),
            'competency': str(self.competency.id),
            'term': str(self.term.id),
        }
        gresp = self.client.get(students_url, params)
        self.assertEqual(gresp.status_code, 200)
        gdata = gresp.json()
        self.assertEqual(gdata.get('draft_id'), draft_id)
        # find student entry
        entries = {e['id']: e for e in gdata['students']}
        self.assertEqual(entries[s1.id]['percentage'], 88)

    def test_submit_final_saves_assessments_and_deletes_draft(self):
        # create 2 students and a draft
        s1 = self._create_student(40, grade='G6')
        s2 = self._create_student(41, grade='G6')

        from academics.models import DraftAssessment, Assessment
        draft = DraftAssessment.objects.create(
            teacher=self.teacher,
            grade='G6',
            stream='',
            subject=self.subject,
            competency=self.competency,
            term=self.term,
            draft_data={
                str(s1.id): {'percentage': 92, 'remarks': ''},
                str(s2.id): {'percentage': '', 'remarks': ''}
            }
        )

        url = reverse('academics:submit_assessments')
        payload = {
            'grade': 'G6',
            'stream': '',
            'subject_id': self.subject.id,
            'competency_id': self.competency.id,
            'term_id': self.term.id,
            'assessments': {
                str(s1.id): {'percentage': 92, 'remarks': ''},
                str(s2.id): {'percentage': '', 'remarks': ''}
            }
        }
        import json
        resp = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get('success'))
        # One saved, one skipped
        self.assertEqual(data.get('saved'), 1)
        self.assertEqual(data.get('skipped'), 1)
        # draft should be deleted
        self.assertFalse(DraftAssessment.objects.filter(id=draft.id).exists())
        # assessment should be created for s1
        self.assertTrue(Assessment.objects.filter(student_id=s1.id, subject=self.subject).exists())

    def test_absent_checkbox_behavior_and_missing_scores(self):
        # create student marked absent
        s_absent = self._create_student(50, grade='G7')

        from academics.models import DraftAssessment, Assessment
        DraftAssessment.objects.create(
            teacher=self.teacher,
            grade='G7',
            stream='',
            subject=self.subject,
            competency=self.competency,
            term=self.term,
            draft_data={
                str(s_absent.id): {'percentage': '', 'remarks': '', 'absent': True}
            }
        )

        # fetch students should show absent True
        students_url = reverse('academics:get_students')
        params = {
            'grade': 'G7',
            'stream': '',
            'subject': str(self.subject.id),
            'competency': str(self.competency.id),
            'term': str(self.term.id),
        }
        resp = self.client.get(students_url, params)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        found = False
        for e in data['students']:
            if e['id'] == s_absent.id:
                found = True
                self.assertTrue(e['absent'])
        self.assertTrue(found)

        # submitting should skip absent student
        url = reverse('academics:submit_assessments')
        payload = {
            'grade': 'G7',
            'stream': '',
            'subject_id': self.subject.id,
            'competency_id': self.competency.id,
            'term_id': self.term.id,
            'assessments': {
                str(s_absent.id): {'percentage': '', 'remarks': '', 'absent': True}
            }
        }
        import json
        sresp = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(sresp.status_code, 200)
        sdata = sresp.json()
        self.assertEqual(sdata.get('saved'), 0)
        self.assertEqual(sdata.get('skipped'), 1)
        self.assertFalse(Assessment.objects.filter(student_id=s_absent.id).exists())

    def test_pending_drafts_appear_on_dashboard(self):
        from academics.models import DraftAssessment
        s1 = self._create_student(60, grade='G8')
        DraftAssessment.objects.create(
            teacher=self.teacher,
            grade='G8',
            stream='',
            subject=self.subject,
            competency=self.competency,
            term=self.term,
            draft_data={str(s1.id): {'percentage': 55}}
        )

        url = reverse('academics:pending_drafts')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        drafts = resp.context['drafts']
        self.assertTrue(any(d.grade == 'G8' for d in drafts))
