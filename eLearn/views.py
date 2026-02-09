
from django.shortcuts import render
from django.contrib.auth import login
from eLearn.forms import CustomUserCreationForm
from .models import *
from eLearn.forms import CourseForm, LessonForm
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib.auth import logout
from django.shortcuts import redirect

from eLearn.forms import CourseDurationForm

from django.http import HttpResponseForbidden
from .models import Quiz, QuizQuestion


@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    is_owner_teacher = (
        request.user.role == 'teacher' and lesson.course.teacher == request.user
    )

    if request.method == 'POST' and is_owner_teacher:
        lesson.content = request.POST.get('content', lesson.content)
        if 'pdf' in request.FILES:
            lesson.pdf = request.FILES['pdf']
        if 'video' in request.FILES:
            lesson.video = request.FILES['video']
        lesson.save()
        return redirect('lesson_detail', lesson_id=lesson.id)

    return render(request, 'lesson_detail.html', {
        'lesson': lesson,
        'can_edit': is_owner_teacher,  # useful for the template
    })


@login_required
def quiz_intro(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    # only students enrolled OR the teacher may enter
    if request.user not in quiz.course.students.all() and request.user != quiz.course.teacher:
        return HttpResponseForbidden("You are not enrolled in this course.")
    return render(request, "quiz_intro.html", {"quiz": quiz})

@login_required
def quiz_take(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()

    if request.method == "POST":
        score = 0
        wrong_qs = []                 # collect the questions answered incorrectly

        for q in questions:
            user_ans = request.POST.get(str(q.id))  # 'A', 'B', 'C', or 'D'
            if user_ans and user_ans.upper() == q.correct_choice.upper():
                score += 1
            else:
                wrong_qs.append({
                    "question": q.question_text,
                    "correct_choice": q.correct_choice,
                    "correct_text": getattr(q, f"choice_{q.correct_choice.lower()}"),
                    "user_answer": user_ans
                })

        # Save attempt
        QuizResult.objects.create(
            user     = request.user,
            quiz     = quiz,
            score    = score,
            total    = questions.count()
        )

        percent = round((score / questions.count()) * 100)

        # Decide message bucket
        if percent >= 80:
            headline = "🎉  Great job!"
            sub      = "You nailed it!"
            style    = "bg-green-100 text-green-800"
        elif 50 <= percent < 80:
            headline = "😊  Good effort"
            sub      = "Review the questions below to strengthen your skills."
            style    = "bg-yellow-100 text-yellow-800"
        else:
            headline = "⚠️  Needs improvement"
            sub      = "Keep practicing. Focus on the questions listed below."
            style    = "bg-red-100 text-red-800"

        context = {
            "quiz"         : quiz,
            "score"        : score,
            "total"        : questions.count(),
            "percent"      : percent,
            "wrong_qs"     : wrong_qs,
            "headline"     : headline,
            "sub"          : sub,
            "style"        : style,
        }
        return render(request, "quiz_result.html", context)

    # -------------- GET --------------
    minutes = questions.count()            # 1 min per Q
    return render(request, "quiz_take.html", {
        "quiz": quiz,
        "questions": questions,
        "minutes": minutes,
    })


@login_required
def edit_duration_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.user != course.teacher:
        return HttpResponseForbidden("Only the teacher can edit duration.")

    if request.method == 'POST':
        form = CourseDurationForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course duration updated successfully.')
            return redirect('course_detail', course_id=course.id)
    else:
        form = CourseDurationForm(instance=course)

    return render(request, 'edit_duration.html', {
        'form': form,
        'course': course
    })


@login_required
def add_quiz(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.user != course.teacher:
        return HttpResponseForbidden("Only the teacher can add quizzes.")

    if request.method == 'POST':
        # Create the Quiz
        quiz = Quiz.objects.create(
            course=course,
            title=request.POST['title'],
            description=request.POST.get('description', '')
        )

        # Add Questions
        i = 0
        while f'question-{i}-text' in request.POST:
            text = request.POST[f'question-{i}-text']
            choice_a = request.POST.get(f'question-{i}-A')
            choice_b = request.POST.get(f'question-{i}-B')
            choice_c = request.POST.get(f'question-{i}-C')
            choice_d = request.POST.get(f'question-{i}-D')
            correct = request.POST.get(f'question-{i}-correct')

            QuizQuestion.objects.create(
                quiz=quiz,
                question_text=text,
                choice_a=choice_a,
                choice_b=choice_b,
                choice_c=choice_c,
                choice_d=choice_d,
                correct_choice=correct
            )
            i += 1

        messages.success(request, f"Quiz created with {i} question(s).")
        return redirect('course_detail', course_id=course.id)

    # GET request: Show form
    return render(request, "add_quiz.html", {"course": course})

@login_required
def edit_profile(request):
    user = request.user

    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        """profile.bio = request.POST.get('bio')
        profile.email_notifications = bool(request.POST.get('email_notifications'))
        profile.public_profile = bool(request.POST.get('public_profile'))"""


        if request.FILES.get('avatar'):

            avatar = request.FILES['avatar']
            user.avatar = avatar

        user.save()
        #profile.save()
        return redirect('dashboard')

    return render(request, 'edit_profile.html')
def logout_view(request):
    logout(request)
    return redirect('home')
@login_required
def enroll_course_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Add user to course students if not already enrolled
    if request.user not in course.students.all():
        course.students.add(request.user)

    return redirect('course_detail', course_id=course.id)
def quiz_start_view(request, quiz_id):
    quiz = get_object_or_404(Lesson, id=quiz_id)
    return render(request, "quiz/start.html", {"quiz": quiz})


def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.role = form.cleaned_data['role']
            user.save()
            login(request, user)  # Auto-login after registration
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

from django.db.models import Count
def home_view(request):
    """
    Home page
    • Shows the 3 most–enrolled courses (“popular courses”)
    • Works for both signed-in and anonymous visitors
    """
    popular_courses = (
        Course.objects.annotate(num_students=Count("students"))
        .order_by("-num_students")[:3]
    )
    courses = Course.objects.all()
    context = {
        "popular_courses": popular_courses,
        "courses": courses,
    }
    return render(request, "home.html", context)

from django.db.models import Q
@login_required
def course_list_view(request):
    courses = Course.objects.all()
    popular_courses = (
        Course.objects.annotate(num_students=Count("students"))
        .order_by("-num_students")[:3]
    )
    query = request.GET.get("q", "")
    if query:
        courses = courses.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    context = {
        "popular_courses": popular_courses,
        "courses": courses,
    }
    return render(request, "course_list.html", context)

@login_required
def create_course_view(request):
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.duration = "4"
            course.image = request.FILES.get('image')
            course.save()
            return redirect("course_list")
    else:
        form = CourseForm()
    return render(request, "create_course.html", {"form": form})


@login_required
def course_detail_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    is_enrolled = request.user in course.students.all()
    is_teacher = request.user == course.teacher
    quizzes = Quiz.objects.filter(course=course)
    # Get best attempt per quiz for the logged-in user
    best_scores = {}
    for quiz in quizzes:
        best_result = QuizResult.objects.filter(user=request.user, quiz=quiz).order_by('-score').first()
        if best_result:
            best_scores[quiz.id] = best_result.score

    if request.method == "POST" and not is_enrolled:
        course.students.add(request.user)
        return redirect("course_detail", course_id=course.id)

    return render(request, "course_detail.html", {"course": course, "is_enrolled": is_enrolled, "is_teacher": is_teacher,'best_scores': best_scores,})


@login_required
def lesson_list_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    lessons = course.lessons.all()

    return render(request, "lesson_list.html", {"course": course, "lessons": lessons})

@login_required
def create_lesson_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.user != course.teacher:
        return redirect("course_detail", course_id=course.id)  # Prevent non-teachers from creating lessons

    if request.method == "POST":
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            return redirect("course_detail", course_id=course.id)
    else:
        form = LessonForm()

    return render(request, "create_lesson.html", {"form": form, "course": course})


"""@login_required
def quiz_view(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    questions = QuizQuestion.objects.filter(quiz=quiz)

    if request.method == 'POST':
        score = 0
        for question in questions:
            user_answer = request.POST.get(str(question.id))
            if user_answer and user_answer.lower().strip() == question.correct_answer.lower().strip():
                score += 1

        QuizResult.objects.create(user=request.user, lesson=lesson, score=score)

        return render(request, 'quiz_result.html', {
            'lesson': lesson,
            'score': score,
            'total': questions.count()
        })

    return render(request, 'quiz.html', {
        'lesson': lesson,
        'questions': questions
    })"""

from .models import Course, QuizResult


@login_required
def dashboard_view(request):
    user = request.user

    # 1) all enrolled courses
    enrolled_qs = user.courses_enrolled.all()
    enrolled_count = enrolled_qs.count()

    # 2) count total quizzes and passed quizzes
    all_results = QuizResult.objects.filter(user=user)
    # A passed quiz requires at least 50% correct answers
    passed_results = all_results.filter(score__gte=models.F('total') * 0.5)

    # Get distinct quizzes the user has attempted
    attempted_quiz_ids = all_results.values_list('quiz_id', flat=True).distinct()
    passed_quiz_ids = passed_results.values_list('quiz_id', flat=True).distinct()

    # For total quizzes, count only distinct quizzes the user has attempted
    # This ensures the denominator is consistent with the numerator
    total_quizzes = len(attempted_quiz_ids)
    passed_quizzes_count = len(passed_quiz_ids)

    # 3) which courses are "completed"?
    #    A course is completed if the user has passed ≥50% of _that course's_ quizzes
    completed_courses_list = []
    for course in enrolled_qs:
        qs = course.quizzes.all()
        if not qs:
            continue
        # count how many of that course's quizzes this user has passed
        passed = passed_results.filter(quiz__in=qs).count()
        if passed / qs.count() >= 0.5:
            completed_courses_list.append(course)

    # 4) recent activity: quiz completions
    recent = []
    for r in all_results.order_by('-timestamp')[:5]:
        recent.append({
            'type': 'quiz',
            'description': f"You scored {r.score}/{r.total} on {r.quiz.title}",
            'timestamp': r.timestamp
        })

    # Sort by most recent first
    recent.sort(key=lambda x: x['timestamp'], reverse=True)
    recent = recent[:5]

    # Calculate progress percentages for the template
    course_progress = (len(completed_courses_list) / enrolled_count * 100) if enrolled_count > 0 else 0
    quiz_progress = (passed_quizzes_count / total_quizzes * 100) if total_quizzes > 0 else 0
    overall_progress = int((course_progress + quiz_progress) / 2)

    # Format data to match template expectations
    completed_courses = {
        'count': len(completed_courses_list)
    }

    completed_quizzes = {
        'count': passed_quizzes_count
    }

    return render(request, 'dashboard.html', {
        'enrolled_courses': enrolled_qs,
        'enrolled_count': enrolled_count,
        'completed_courses': completed_courses_list,
        'completed_courses_count': len(completed_courses_list),  # For the completed courses section
        'total_quizzes': total_quizzes,
        'completed_quizzes': completed_quizzes,
        'recent_activities': recent,
        'overall_progress': overall_progress,
        'course_progress': int(course_progress),
        'quiz_progress': int(quiz_progress),
    })
