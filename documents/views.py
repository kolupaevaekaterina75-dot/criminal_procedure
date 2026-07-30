from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Document, Participant
from .forms import DocumentForm
from django.views.generic import ListView
from .docx_constructor import generate_docx_from_document
from django.db.models import Count


def document_list(request):
    documents = Document.objects.select_related("participant").all()
    return render(request, "documents/document_list.html", {"documents": documents})


def document_create(request):
    if request.method == "POST":
        form = DocumentForm(request.POST)
        if form.is_valid():
            doc = form.save()
            return redirect("document_detail", pk=doc.pk)
    else:
        form = DocumentForm()
    return render(
        request,
        "documents/document_form.html",
        {"form": form, "action": "Создать документ"},
    )


def document_detail(request, pk):
    doc = get_object_or_404(Document.objects.select_related("participant"), pk=pk)
    return render(request, "documents/document_detail.html", {"doc": doc})


def document_download(request, pk):
    doc = get_object_or_404(Document.objects.select_related("participant"), pk=pk)

    file_bytes = generate_docx_from_document(doc)

    response = HttpResponse(
        file_bytes,
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    safe_title = doc.title.replace(" ", "_").replace("/", "_")
    response["Content-Disposition"] = (
        f'attachment; filename="{safe_title}_{doc.doc_type}.docx"'
    )
    return response


def participant_list(request):
    participants = Participant.objects.all()
    return render(
        request,
        "documents/participant_list.html",
        {"participants": participants},
    )


class ParticipantList(ListView):
    model = Participant
    template_name = "documents/participant_list.html"
    context_object_name = "participants"


# Шаг 9: отчёт по количеству документов по участникам
def report_documents_by_participant(request):
    """
    Возвращает список участников с количеством документов (агрегация).
    Предполагается, что в модели Participant есть related_name='documents'
    для связи с Document (ForeignKey).
    """
    participants_with_count = (
        Participant.objects
        .annotate(total_documents=Count('documents'))
        .order_by('-total_documents')
    )
    return render(
        request,
        "documents/report_documents_by_participant.html",
        {"participants": participants_with_count},
    )