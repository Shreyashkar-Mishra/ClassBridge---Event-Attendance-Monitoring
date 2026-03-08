from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Event, EventParticipation, ClassLog, Student, Coordinator
from .forms import EventForm, ClassLogForm, StudentRegistrationForm, FacultyRegistrationForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth import login
import openpyxl
from django.core.mail import EmailMessage
import io


def home_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')

def register_student(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto-login after registration
            messages.success(request, f"Welcome to ClassBridge, {user.first_name}! Your student account has been created.")
            return redirect('dashboard')
    else:
        form = StudentRegistrationForm()
        
    return render(request, 'registration/register.html', {'form': form})

def register_faculty(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = FacultyRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to the Faculty Portal, Professor {user.last_name}!")
            return redirect('dashboard')
    else:
        form = FacultyRegistrationForm()
        
    return render(request, 'registration/register_faculty.html', {'form': form})

def event_list(request):
    all_events = Event.objects.all().order_by('date')
    
    # We need to know which events the current student has already joined
    participated_event_ids = []
    if request.user.is_authenticated and request.user.user_type == 'student':
        participated_event_ids = EventParticipation.objects.filter(
            student=request.user.student_profile
        ).values_list('event_id', flat=True)
        
    context = {
        'events': all_events,
        'participated_event_ids': participated_event_ids
    }
    return render(request, 'event_list.html', context)



@login_required
def create_event(request):

    if request.user.user_type != 'coordinator':
        raise PermissionDenied("Only Coordinators can create events.")
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            new_event = form.save(commit=False)
            new_event.created_by = request.user.coordinator_profile
            new_event.save()
            return redirect('event_list')
    else:
        form=EventForm()
    return render(request,'create_event.html',{'form':form})


@login_required
def dashboard(request):
    user = request.user
    if user.user_type == 'student':
        # Get the 10 most recent class logs for the student dashboard!
        recent_logs = ClassLog.objects.all().order_by('-date')[:10]
        context = {
            'student_profile': user.student_profile,
            'class_logs': recent_logs
        }
        return render(request, 'dashboard_student.html', context)
        
    elif user.user_type == 'faculty':
        # Get only the logs created by THIS faculty member
        my_logs = ClassLog.objects.filter(logged_by=user.faculty_profile).order_by('-date')
        # Get all registered students for administration
        all_students = Student.objects.all().order_by('batch', 'roll_number')
        
        context = {
            'faculty_profile': user.faculty_profile,
            'my_logs': my_logs,
            'all_students': all_students
        }
        return render(request, 'dashboard_faculty.html', context)
        
    elif user.user_type == 'coordinator':
        # Get all registered students for administration
        all_students = Student.objects.all().order_by('batch', 'roll_number')
        context = {
            'coordinator_profile': user.coordinator_profile,
            'all_students': all_students
        }
        return render(request, 'dashboard_coordinator.html', context)
    else:
        raise PermissionDenied("You do not have a valid role assigned")

@login_required
def log_class(request):
    if request.user.user_type != 'faculty':
        raise PermissionDenied("Only Faculty members can log classes.")
        
    if request.method == 'POST':
        form = ClassLogForm(request.POST)
        if form.is_valid():
            new_log = form.save(commit=False)
            new_log.logged_by = request.user.faculty_profile
            new_log.save()
            messages.success(request, "Class log and AI video suggestions successfully created!")
            return redirect('dashboard')
    else:
        # Auto-fill today's date so they don't have to type it!
        from datetime import date
        form = ClassLogForm(initial={'date': date.today()})
        
    return render(request, 'create_class_log.html', {'form': form})

@login_required
def promote_to_coordinator(request, student_id):
    if request.user.user_type != 'faculty':
        raise PermissionDenied("Only Faculty can appoint coordinators.")
        
    student = get_object_or_404(Student, id=student_id)
    user = student.user
    
    # Transition the role
    user.user_type = 'coordinator'
    user.save()
    
    # Create or update Coordinator profile (batch defaults to student's batch)
    Coordinator.objects.get_or_create(
        user=user,
        defaults={'assigned_batch': student.batch}
    )
    
    # Keep student profile for visibility in roster
    
    messages.success(request, f"{user.first_name} {user.last_name} has been promoted to Student Coordinator!")
    return redirect('dashboard')


@login_required
def join_event(request, event_id):
    # Only allow students to join an event
    if request.user.user_type != 'student':
        messages.error(request, "Only students can join events.")
        return redirect('event_list')
    
    # Get the event they clicked on
    event = get_object_or_404(Event, id=event_id)
    student = request.user.student_profile
    
    # Check if they already joined (just in case they refresh the page)
    if EventParticipation.objects.filter(student=student, event=event).exists():
        messages.info(request, "You have already joined this event!")
    else:
        # Create the participation record
        EventParticipation.objects.create(student=student, event=event)
        messages.success(request, f"Successfully joined {event.title}!")
        
    return redirect('event_list')

@login_required
def event_participants(request, event_id):
    # Ensure they are a coordinator
    if request.user.user_type != 'coordinator':
        raise PermissionDenied("Only coordinators can view participants.")
        
    event = get_object_or_404(Event, id=event_id)
    
    # Disabled Security: Allow any coordinator to view participants
        
    # Get all students who joined this event
    participants = EventParticipation.objects.filter(event=event).select_related('student__user')
    
    context = {
        'event': event,
        'participants': participants,
    }
    return render(request, 'event_participants.html', context)


@login_required
def verify_participation(request, participation_id):
    if request.user.user_type != 'coordinator':
        raise PermissionDenied("Only coordinators can verify participation.")
        
    participation = get_object_or_404(EventParticipation, id=participation_id)
    
    # Disabled Security: Allow any coordinator to verify participants
        
    # Toggle the verification status!
    participation.is_verified = not participation.is_verified
    participation.save()
    
    messages.success(request, f"Updated verification for {participation.student.user.first_name}.")
    
    # Send them right back to the list
    return redirect('event_participants', event_id=participation.event.id)


@login_required
def email_preview(request, event_id):
    if request.user.user_type != 'coordinator':
        raise PermissionDenied("Only coordinators can prepare email reports.")
        
    event = get_object_or_404(Event, id=event_id)
    verified_participants = EventParticipation.objects.filter(event=event, is_verified=True)
    count = verified_participants.count()
    
    # Generate our highly professional "smart" email template!
    subject = f"Attendance Report: {event.title} - Official Verification"
    
    body = f"Respected Faculty,\n\n"
    body += f"I am writing this email to officially submit the verified attendance report for the '{event.title}' event, which concluded successfully on {event.date}.\n\n"
    body += f"A total of {count} students participated and have been thoroughly verified by the coordinating team. "
    body += "An Excel spreadsheet detailing their full names and officially registered roll numbers is attached to this email for your administrative records and grade processing.\n\n"
    body += "Please let me know if you require any further documentation regarding this event.\n\n"
    body += f"Best Regards,\n"
    body += f"{request.user.first_name} {request.user.last_name}\n"
    body += "Event Coordinator, ClassBridge"
    
    if request.method == 'POST':
        recipient = request.POST.get('recipient_email')
        if recipient:
            from django.core.mail import EmailMessage
            import openpyxl
            import io
            
            # Generate the Excel Attachment
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Verified Participants"
            ws.append(['First Name', 'Last Name', 'Roll Number'])
            for p in verified_participants:
                ws.append([p.student.user.first_name, p.student.user.last_name, p.student.roll_number])
                
            excel_file = io.BytesIO()
            wb.save(excel_file)
            excel_file.seek(0)
            
            # Send the email with the attachment
            email = EmailMessage(
                subject=subject,
                body=body,
                from_email='noreply@classbridge.edu',
                to=[recipient],
            )
            email.attach(f'{event.title.replace(" ", "_")}_Attendance.xlsx', excel_file.read(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            email.send()
            
            messages.success(request, f"Official report successfully dispatched to {recipient}.")
            return redirect('event_participants', event_id=event.id)
        else:
            messages.error(request, "Please provide a valid email address.")
    
    context = {
        'event': event,
        'email_subject': subject,
        'email_body': body,
    }
    return render(request, 'email_preview.html', context)
@login_required
def download_excel_report(request, event_id):
    if request.user.user_type != 'coordinator':
        raise PermissionDenied("Only coordinators can export reports.")
        
    event = get_object_or_404(Event, id=event_id)
    verified_participants = EventParticipation.objects.filter(event=event, is_verified=True)
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Verified Participants"
    ws.append(['First Name', 'Last Name', 'Roll Number'])
    for p in verified_participants:
        ws.append([p.student.user.first_name, p.student.user.last_name, p.student.roll_number])
        
    excel_file = io.BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)
    
    # MAGIC: This lines tells the browser to DOWNLOAD the file instead of displaying it!
    response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{event.title.replace(" ", "_")}_Attendance.xlsx"'
    return response

@login_required
def delete_event(request, event_id):
    if request.user.user_type != 'coordinator':
        raise PermissionDenied("Only Coordinators can delete events.")
    
    event = get_object_or_404(Event, id=event_id)
    title = event.title
    event.delete()
    messages.success(request, f"Event '{title}' has been permanently deleted.")
    return redirect('event_list')

@login_required
def delete_class_log(request, log_id):
    if request.user.user_type != 'faculty':
        raise PermissionDenied("Only Faculty can delete class logs.")
    
    log = get_object_or_404(ClassLog, id=log_id)
    
    # Ownership Check
    if log.logged_by.user != request.user:
        raise PermissionDenied("You can only delete your own class logs.")
    
    subject = log.subject
    log.delete()
    messages.success(request, f"Class log for '{subject}' has been deleted.")
    return redirect('dashboard')

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, "Your account has been permanently deleted.")
        return redirect('home')
    
    return render(request, 'registration/confirm_delete_account.html')

@login_required
def edit_student_roll(request, student_id):
    if request.user.user_type not in ['faculty', 'coordinator']:
        raise PermissionDenied("Only Faculty or Coordinators can edit student records.")
    
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        new_roll = request.POST.get('roll_number')
        if new_roll:
            # Check for uniqueness if changed
            if new_roll != student.roll_number and Student.objects.filter(roll_number=new_roll).exists():
                messages.error(request, f"Roll number '{new_roll}' is already assigned to another student.")
            else:
                student.roll_number = new_roll
                student.save()
                messages.success(request, f"Successfully updated roll number for {student.user.get_full_name()}.")
        return redirect('dashboard')
    
    return render(request, 'registration/edit_student_roll.html', {'student': student})

@login_required
def delete_student(request, student_id):
    if request.user.user_type not in ['faculty', 'coordinator']:
        raise PermissionDenied("Only Faculty or Coordinators can delete student records.")
    
    student = get_object_or_404(Student, id=student_id)
    user = student.user
    full_name = user.get_full_name()
    
    if request.method == 'POST':
        user.delete() # Also deletes student profile due to CASCADE
        messages.success(request, f"Student account for {full_name} has been permanently removed.")
        return redirect('dashboard')
    
    return render(request, 'registration/confirm_delete_student.html', {'student': student})