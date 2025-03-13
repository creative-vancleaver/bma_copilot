import json
from pathlib import Path
from collections import defaultdict
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import render
from decouple import config

from cells.models import Cell, CellClassification
from cells.views import CellView, JSONCellView
from .services.azure_blob_service import get_blob_url
from cases.models import Case

CELL_ORDER = [
    'blasts_and_blast_equivalents', 'promyelocytes', 'myelocytes', 'metamyelocytes', 'neutrophils', 'monocytes', 
    'eosinophils', 'lymphocytes', 'plasma_cells', 'erythroid_precursors', 'skippocytes',
]

def index(request):
    return render(request, 'core/index.html')

@login_required
def microscope_viewer(request):
    user = request.user
    context = {
        'user': user
    }
    return render(request, 'cases/microscope_viewer.html', context)

@login_required
def JSON_case(request, case_id):

    case = Case.objects.get(case_id=case_id)
    data_dir = Path('data/cells')
    try:
        with open(data_dir / f'{ case_id }.json', 'r') as f:
            cell_data = json.load(f)
    except FileNotFoundError:
        cell_data = {'cells': []}

    cell_total = len(cell_data['cells'])
    print(cell_total)

    classification_groups = defaultdict(list)

    for cell in cell_data['cells']:
        user_class = cell['classification']['user_cell_class']
        ai_class = cell['classification']['ai_cell_class']
        class_label = user_class if user_class else ai_class
        cell['user_cell_class'] = user_class
        cell['ai_cell_class'] = ai_class

        image_path = cell['cell_image_path']
        if image_path:
            filename = image_path.split('/')[-1]
            try:
                blob_url = get_blob_url('cells', filename)
                cell['image_url'] = blob_url
            except Exception as e:
                cell['image_url'] = None

        classification_groups[class_label].append(cell)

    for group in classification_groups.values():
        group.sort(key=lambda x: (
            x['user_cell_class'] or '',
            x['ai_cell_class'] or ''
        ))

    sorted_groups = {
        class_name: classification_groups.get(class_name, [])
        for class_name in CELL_ORDER
        if class_name in classification_groups
    }

    classification_groups = dict(sorted_groups)

    new_cell_total = sum(len(value) for key, value in classification_groups.items() if key != 'skippocytes')

    skippocytes_counts = len(classification_groups.get('skippocytes', []))
    # new_cell_total = cell_total - skippocytes_counts

    cell_view = JSONCellView()
    diff_counts = cell_view.get_diff_counts(case_id)
    cell_total = cell_view.get_cell_counts(case_id)
    # new_cell_total = cell_total - skippocytes_counts
    print(diff_counts, cell_total)

    context = {
        'case': case,
        'cell_groups': classification_groups,
        'cell_order': CELL_ORDER,
        'diff_counts': diff_counts,
        'cell_total': new_cell_total,
        'skippocytes_counts': skippocytes_counts
    }

    return render(request, 'cases/case.html', context)


@login_required
def case(request, case_id):

    case = Case.objects.get(case_id=case_id)
    
    cell_total = Cell.objects.filter(region__video_id__case=case).count()

    classifications = (
        Cell.objects
        .filter(region__video_id__case=case)
        .select_related('cellclassification')
        .annotate(
            ai_cell_class=F("cellclassification__ai_cell_class"),
            user_cell_class=F("cellclassification__user_cell_class"),
        )
        .values(
            "cell_id", "cell_image_path", "ai_cell_class", "user_cell_class",
        )
        .order_by("user_cell_class", "ai_cell_class")
    )

    # Convert queryset into a structured dictionary in a single step
    classification_groups = defaultdict(list)

    USE_AZURE_STORAGE = config('USE_AZURE_STORAGE', default='True').lower() == 'true'

    for cls in classifications:

        user_class = cls['user_cell_class']
        ai_class = cls['ai_cell_class']
        class_label = user_class if user_class else ai_class

        if USE_AZURE_STORAGE:
            image_path = cls.pop('cell_image_path')
            if image_path:
                filename = image_path.split('/')[-1]
                try:
                    response = get_blob_url("cells", filename)
                    cls["image_url"] = response
                except Exception as e:
                    print(f'Error getting blob URL for { filename }: { str(e)}')
                    cls["image_url"] = None
            else:
                cls['image_url'] = None
        else:
            cls["image_url"] = f"/media/{cls.pop('cell_image_path')}" if cls.get('cell_image_path') else None

        classification_groups[class_label].append(cls)

    classification_groups = dict(classification_groups)

    new_cell_total = sum(len(value) for key, value in classification_groups.items() if key != 'skippocytes')
    skippocytes_counts = len(classification_groups.get("skippocytes", []))

    diff_view = CellView()
    diff_counts = diff_view.get_diff_counts(case_id)

    context = {
        'case': case,
        'diff_counts': diff_counts,
        'cell_groups': classification_groups,
        'cell_order': CELL_ORDER,
        'cell_total': new_cell_total,
        'skippocytes_counts': skippocytes_counts,
    }

    return render (request, 'cases/case.html', context)


def preview_popup(request):
    return render(request, 'core/preview_popup.html')

