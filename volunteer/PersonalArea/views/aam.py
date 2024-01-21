
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.conf import settings
from MainApp.models import *
from PersonalArea.forms import *
from Accounts import decorators
import io
import xlsxwriter

@decorators.is_admin_or_methodist
def events_list(request, search=None):
    return render(request, "aam/events_list.html", {"section": "events"})


@decorators.is_admin_or_methodist
def give_points(request, id):
    event = Events.objects.get(pk=id)
    volunteers = event.volunteer.all().filter(points=None)
    if request.method == "POST":
        user = request.POST.get("user")
        points = request.POST.get("points")
        if user is not None and points is not None:
            volunteer = volunteers.get(pk=user)
            volunteer.points = points
            volunteer.save()
            user_account = volunteer.user
            user_account.points += int(points)
            user_account.save()
            return redirect(f"/lk/events/{event.pk}/points/give")
    else:

        return render(request, "aam/give_points.html", {"event": event, "volunteers": volunteers, "section": "events",})


@decorators.is_admin_or_methodist
def events_archive_list(request):
    return render(request, "aam/events_archive_list.html", {"section": "events"})


@decorators.is_admin_or_methodist
def event_export(request, id):
    event = Events.objects.get(pk=id)
    buffer = io.BytesIO()
    workbook = xlsxwriter.Workbook(buffer)
    worksheet = workbook.add_worksheet()
    worksheet.write('A1', 'ФИО')
    worksheet.write('B1', 'Баллов')
    m = 1
    points = 0
    for i in event.volunteer.all():
        m += 1
        if i.points is not None:
            points += i.points
            worksheet.write(f'B{m}', i.points)
        else:
            worksheet.write(f'B{m}', 0)
        worksheet.write(f'A{m}', i.user.full_name())
    worksheet.write(f'A{m + 1}', "Всего")
    worksheet.write(f'B{m + 1}', points)
    worksheet.autofit()
    workbook.close()
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename=f'{event.name}.xlsx')


@decorators.is_admin_or_methodist
def event_archive(request, id):
    event = Events.objects.get(pk=id)
    event.archive = True
    event.save()
    return redirect("/lk/events/")


@decorators.is_admin_or_methodist
def event_unarchived(request, id):
    event = Events.objects.get(pk=id)
    event.archive = False
    event.save()
    return redirect("/lk/events/archive/")


@decorators.is_admin_or_methodist
def events_view(request, id):
    if request.user.role == "admin" or request.user.role == "director" or request.user.role == "head_teacher":
        event = Events.objects.get(pk=id)
    elif request.user.role == "methodist":
        categories = EventCategory.objects.all().filter(methodists=request.user)
        if Events.objects.all().filter(pk=id, category__in=categories).exists():
            event = Events.objects.get(pk=id)
        else:
            return redirect("events_list")
    context = {
        "event": event,
        "reqs": event.volunteer.filter(is_active=False),
        "members": event.volunteer.filter(is_active=True),
        "section": "events",
        "wait": Events.objects.all().filter(pk=event.pk, start_date__gt=timezone.now()).exists(),
        "end": Events.objects.all().filter(pk=event.pk, end_date__lt=timezone.now()).exists()
    }
    return render(request, "aam/event_view.html", context)


@login_required
def event_create(request):
    if request.user.role == "admin" or request.user.role == "director":
        if request.method == "GET":
            form = EventAddForm()
        else:
            form = EventAddForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                form.save_m2m()
            else:
                return render(request, "aam/event_create.html", {"form": form, "section": "events"})
            return redirect("/lk/events/")
    elif request.user.role == "methodist":
        if request.method == "GET":
            form = EventAddFormMethodist(loggedin_user=request.user)
        else:
            form = EventAddFormMethodist(None, request.POST, request.FILES)
            if form.is_valid():
                form.save()
                form.save_m2m()
            else:
                return render(request, "aam/event_create.html", {"form": form, "section": "events"})
            return redirect("/lk/events/")
    elif request.user.role == "head_teacher":
        if request.method == "GET":
            form = EventAddFormHeadTeacher(loggedin_user=request.user)
        else:
            form = EventAddFormHeadTeacher(None, request.POST, request.FILES)
            if form.is_valid():
                form.save()
                form.save_m2m()
            else:
                return render(request, "aam/event_create.html", {"form": form, "section": "events"})
            return redirect("/lk/events/")
    else:
        return redirect("/lk/")
    return render(request, "aam/event_create.html", {"form": form, "section": "events"})


@decorators.is_admin_or_methodist
def event_accept_user(request, id, user):
    user = EventsMembers.objects.get(id=user)
    user.is_active = True
    user.save()
    return redirect(f"/lk/events/{id}/view")


@decorators.is_admin_or_methodist
def event_reject_user(request, id, user):
    user = EventsMembers.objects.get(id=user)
    user.delete()
    return redirect(f"/lk/events/{id}/view")


@decorators.is_admin_or_methodist
def photo_report(request, id):
    event = get_object_or_404(Events, pk=id)
    context = {
        "section": "events",
        "event": event,
        "report": PhotoReport.objects.all().filter(event=event, deleted=False)
    }
    if request.method == "GET":
        context['form'] = UploadPhotoReport()
        return render(request, "aam/photo_report.html", context)
    else:
        form = UploadPhotoReport(request.POST, request.FILES)
        files = request.FILES.getlist("file")
        for f in files:
            if f.name.split(".")[-1] in ["jpg", "jpeg", "png", "gif"]:
                p = PhotoReport(image=f, event=event, author=request.user)
                p.save()
        return redirect(f"/lk/events/{event.pk}/photo/report")


@decorators.is_admin_or_methodist
def photo_delete(request, id, image):
    photo = get_object_or_404(PhotoReport, pk=image)
    photo.delete()
    return redirect(f"/lk/events/{photo.event.pk}/photo/report")
