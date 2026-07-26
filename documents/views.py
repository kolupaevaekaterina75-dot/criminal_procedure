from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Document, Participant
from .forms import DocumentForm
from django.views.generic import ListView
from .docx_constructor import generate_docx_from_document


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
    # Было: {"doc": document} — переменная document не определена. Правильно: {"doc": doc}
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


# Этот класс нужен для URL-маршрута на основе CBV (class-based view)
class ParticipantList(ListView):
    model = Participant
    template_name = "documents/participant_list.html"
    context_object_name = "participants"