from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.conf import settings



class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    groups = models.ManyToManyField(Group, related_name="customuser_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="customuser_permissions", blank=True)

#User = get_user_model()

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='courses_taught')
    students = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='courses_enrolled', blank=True)
    duration = models.PositiveIntegerField(default=4)

    image = models.ImageField(upload_to='course_images/', blank=True, null=True, default='course_images/default.jpg')

    def is_completed_by(self, user):
        quizzes = self.quizzes.all()
        for quiz in quizzes:
            result = quiz.quizresult_set.filter(user=user).order_by('-timestamp').first()
            if not result or result.score < 50:
                return False
        return True

    def __str__(self):
        return self.title

class Teacher(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)



class Lesson(models.Model):
    course = models.ForeignKey("Course", on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    pdf = models.FileField(upload_to='lesson_pdfs/', blank=True, null=True)
    video = models.FileField(upload_to='lesson_videos/', blank=True, null=True)

    def __str__(self):
        return self.title

class Quiz(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="quizzes"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.course.title})"

    @property
    def total_questions(self):
        return self.questions.count()

class QuizAttempt(models.Model):
    quiz       = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    completed  = models.BooleanField(default=False)
    score      = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} – {self.quiz.title} ({'done' if self.completed else 'open'})"


class QuizQuestion(models.Model):
    quiz = models.ForeignKey("Quiz", on_delete=models.CASCADE, related_name="questions")
    #lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    question_text = models.TextField()
    choice_a = models.CharField(max_length=200)
    choice_b = models.CharField(max_length=200)
    choice_c = models.CharField(max_length=200)
    choice_d = models.CharField(max_length=200)
    correct_choice = models.CharField(max_length=1, choices=[('A','A'), ('B','B'), ('C','C'), ('D','D')])



class QuizResult(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField()
    total = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} - {self.score}/{self.total}"
