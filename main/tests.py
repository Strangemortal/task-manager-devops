from django.test import TestCase, Client
from django.urls import reverse
from .models import User, Task, PersonalTodo

class TaskWorkflowTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create users specifically for the test
        self.admin = User.objects.create_superuser(username='testadmin', password='password', role='admin')
        self.user1 = User.objects.create_user(username='testuser1', password='password', role='frontend')
        self.user2 = User.objects.create_user(username='testuser2', password='password', role='backend')
        self.task = Task.objects.create(title='Test Task', description='Desc', assignee=self.user1, status='To Do')

    def test_privacy_restriction(self):
        self.client.login(username='testuser2', password='password')
        response = self.client.get(reverse('task_detail', args=[self.task.id]))
        self.assertEqual(response.status_code, 403)

    def test_submission_workflow(self):
        self.client.login(username='testuser1', password='password')
        self.client.get(reverse('update_task_status', args=[self.task.id, 'In Progress']))
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'In Progress')

        self.client.get(reverse('update_task_status', args=[self.task.id, 'Completed']))
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'Completed')

    def test_admin_rejection_with_feedback(self):
        self.task.status = 'Completed'
        self.task.save()
        login_success = self.client.login(username='testadmin', password='password')
        self.assertTrue(login_success)
        
        response = self.client.post(reverse('verify_task', args=[self.task.id]), {
            'verified': 'False',
            'comment': 'Please fix the layout'
        })
        self.assertEqual(response.status_code, 302) # Should redirect to superuser_dashboard
        
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'Rejected')
        
        from .models import Comment
        last_comment = Comment.objects.filter(task=self.task).last()
        self.assertIn('ADMIN REVIEW: Please fix the layout', last_comment.text)

    def test_personal_todo_creation(self):
        todo = PersonalTodo.objects.filter(user=self.user1, task=self.task).first()
        self.assertIsNotNone(todo)
        
        self.client.login(username='testuser1', password='password')
        self.client.get(reverse('toggle_todo', args=[todo.id]))
        todo.refresh_from_db()
        self.assertTrue(todo.is_completed)
