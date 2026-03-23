import json
import os
import numpy as np
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from django.db import IntegrityError
from django.utils import timezone

from .models import Person, Attendance
from .face_utils import get_embedding, find_best_match, decode_base64_image, save_face_image


# ─── Home ─────────────────────────────────────────────────────────────────────

def index(request):
    total_persons = Person.objects.count()
    today = timezone.now().date()
    today_count = Attendance.objects.filter(date=today).count()
    recent = Attendance.objects.select_related('person').order_by('-time_in')[:10]
    return render(request, 'recognition/index.html', {
        'total_persons': total_persons,
        'today_count': today_count,
        'recent': recent,
        'today': today,
    })


# ─── Register New Person ───────────────────────────────────────────────────────

def register_page(request):
    return render(request, 'recognition/register.html')


@csrf_exempt
def register_person(request):
    """
    POST endpoint to register a new person.
    Receives: name, employee_id, image (base64)
    Extracts ArcFace embedding and stores in DB.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'})

    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        employee_id = data.get('employee_id', '').strip()
        image_b64 = data.get('image')

        if not name or not employee_id or not image_b64:
            return JsonResponse({'success': False, 'error': 'Name, Employee ID and image are required.'})

        # Decode image
        img_np = decode_base64_image(image_b64)
        if img_np is None:
            return JsonResponse({'success': False, 'error': 'Could not decode image.'})

        # Get ArcFace embedding via MTCNN
        embedding = get_embedding(img_np)
        if embedding is None:
            return JsonResponse({'success': False, 'error': 'No face detected. Please try again with a clearer photo.'})

        # Save photo to media
        photo_filename = f"persons/{employee_id}.jpg"
        photo_path = os.path.join(settings.MEDIA_ROOT, photo_filename)
        os.makedirs(os.path.dirname(photo_path), exist_ok=True)
        save_face_image(img_np, photo_path)

        # Create Person record
        person = Person(name=name, employee_id=employee_id, photo=photo_filename)
        person.set_embedding(embedding)
        person.save()

        return JsonResponse({'success': True, 'message': f'✅ {name} registered successfully!'})

    except IntegrityError:
        return JsonResponse({'success': False, 'error': f'Employee ID already exists.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ─── Mark Attendance ───────────────────────────────────────────────────────────

def recognize_page(request):
    return render(request, 'recognition/recognize.html')


@csrf_exempt
def recognize_face(request):
    """
    POST endpoint to mark attendance.
    Receives: image (base64)
    Returns: matched person name or unknown.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'})

    try:
        data = json.loads(request.body)
        image_b64 = data.get('image')

        if not image_b64:
            return JsonResponse({'success': False, 'error': 'Image required.'})

        # Decode image
        img_np = decode_base64_image(image_b64)
        if img_np is None:
            return JsonResponse({'success': False, 'error': 'Could not decode image.'})

        # Get query embedding
        query_embedding = get_embedding(img_np)
        if query_embedding is None:
            return JsonResponse({'success': False, 'error': 'No face detected. Look directly at the camera.'})

        # Search all persons
        all_persons = Person.objects.all()
        if not all_persons.exists():
            return JsonResponse({'success': False, 'error': 'No registered persons found. Please register first.'})

        threshold = getattr(settings, 'FACE_MATCH_THRESHOLD', 0.68)
        matched_person, score = find_best_match(query_embedding, all_persons, threshold)

        if matched_person is None:
            return JsonResponse({
                'success': False,
                'error': f'Face not recognized (best score: {score:.2f}). Please register or try again.'
            })

        # Mark attendance (prevent duplicate for same day)
        today = timezone.now().date()
        attendance, created = Attendance.objects.get_or_create(
            person=matched_person,
            date=today,
            defaults={'confidence': round(score, 4)}
        )

        if created:
            message = f'✅ Attendance marked for {matched_person.name} (Confidence: {score:.0%})'
        else:
            message = f'ℹ️ {matched_person.name} already marked present today (at {attendance.time_in.strftime("%H:%M")})'

        return JsonResponse({
            'success': True,
            'message': message,
            'person_name': matched_person.name,
            'employee_id': matched_person.employee_id,
            'score': round(score, 4),
            'already_marked': not created
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ─── Attendance Records ────────────────────────────────────────────────────────

def attendance_list(request):
    date_filter = request.GET.get('date', str(timezone.now().date()))
    records = Attendance.objects.filter(date=date_filter).select_related('person').order_by('time_in')
    persons = Person.objects.all()
    return render(request, 'recognition/attendance.html', {
        'records': records,
        'date_filter': date_filter,
        'persons': persons,
    })
