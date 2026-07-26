from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Document, Participant
from .forms import DocumentForm
from .docx_constructor import generate_docx_from_document  # см. ниже

# --- Участники (CRUD) ---
def participant_list(request):
    participants = Participant.objects.all()
    return render(request, 'documents/participant_list.html', {'participants': participants})

def participant_create(request):
    if request.method == 'POST':
        form = ParticipantForm(request.POST)  # создай аналогично DocumentForm
        if form.is_valid():
            form.save()
            return redirect('participant_list')
    else:
        form = ParticipantForm()
    return render(request, 'documents/participant_form.html', {'form': form, 'action': 'Создать'})

# participant_edit и participant_delete реализуй по аналогии (через get_object_or_404 и form.save())


# --- Документы (CRUD + Скачать) ---
def document_list(request):
    documents = Document.objects.select_related('participant').all()
    return render(request, 'documents/document_list.html', {'documents': documents})

def document_create(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST)
        if form.is_valid():
            doc = form.save()
            return redirect('document_detail', pk=doc.pk)
    else:
        form = DocumentForm()
    return render(request, 'documents/document_form.html', {'form': form, 'action': 'Создать документ'})

def document_detail(request, pk):
    doc = get_object_or_404(Document.objects.select_related('participant'), pk=pk)
    return render(request, 'documents/document_detail.html', {'doc': doc})

def document_download(request, pk):
    """
    Кнопка «Скачать документ»: вызывает конструктор и возвращает файл.
    """
    doc = get_object_or_404(Document.objects.select_related('participant'), pk=pk)

    # Генерируем файл с помощью docxtpl
    file_bytes = generate_docx_from_document(doc)

    response = HttpResponse(file_bytes, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = f'attachment; filename="{doc.title.replace(" ", "_")}.docx"'
    return response