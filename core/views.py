from collections import defaultdict
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import render
from decouple import config

from cells.models import Cell, CellClassification
from cells.views import CellView
from .services.azure_blob_service import get_blob_url
from cases.models import Case

CELL_ORDER = [
    'blasts_and_blast_equivalents', 'promyelocytes', 'myelocytes', 'metamyelocytes', 'neutrophils', 'monocytes', 'eosinophils', 'lymphocytes', 'plasma_cells', 'erythroid_precursors', 'skippocytes',
]

def index(request):

    return render(request, 'core/index.html')

@login_required
def microscope_viewer(request):
    # print('case ID === ', case_id)

    return render(request, 'cases/microscope_viewer.html')

@login_required
def case(request, case_id):

    case = Case.objects.get(case_id=case_id)
    
    cell_total = Cell.objects.filter(region__video_id__case=case).count()
    print(cell_total)

    classifications = (
        Cell.objects
        .filter(region__video_id__case=case)
        .select_related('cellclassification')
        .annotate(
            ai_class=F("cellclassification__ai_cell_class"),
            user_class=F("cellclassification__user_cell_class"),
            # image_url=F("image"),  # Ensure image URL is included
            myelocyte_score=F("cellclassification__myelocytes_score"),
            metamyelocyte_score=F("cellclassification__metamyelocytes_score"),
            neutrophil_score=F("cellclassification__neutrophils_bands_score"),
            monocyte_score=F("cellclassification__monocytes_score"),
            eosinophil_score=F("cellclassification__eosinophils_score"),
            erythroid_precursor_score=F("cellclassification__erythroid_precursors_score"),
            lymphocyte_score=F("cellclassification__lymphocytes_score"),
            plasma_cell_score=F("cellclassification__plasma_cells_score"),
            blast_score=F("cellclassification__blasts_and_blast_equivalents_score"),
            skippocyte_score=F("cellclassification__skippocyte_score"),
            
        )
        .values(
            "cell_id", "cell_image_path", "ai_class", "user_class",
            "myelocyte_score", "metamyelocyte_score", "neutrophil_score",
            "monocyte_score", "eosinophil_score", "erythroid_precursor_score",
            "lymphocyte_score", "plasma_cell_score", "blast_score",
            "skippocyte_score", 
        )
        .order_by("user_class", "ai_class")
    )

    # Convert queryset into a structured dictionary in a single step
    classification_groups = defaultdict(list)

    USE_AZURE_STORAGE = config('USE_AZURE_STORAGE', default='True').lower() == 'true'

    for cls in classifications:

        # user_class = cls.pop("user_class", None)
        # ai_class = cls.pop("ai_class", None)
        user_class = cls['user_class']
        ai_class = cls['ai_class']
        class_label = user_class if user_class else ai_class

        if USE_AZURE_STORAGE:
            # print('use blob')
            image_path = cls.pop('cell_image_path')
            if image_path:
                print('image_path ', image_path)
                filename = image_path.split('/')[-1]
                try:
                    response = get_blob_url("cells", filename)
                    cls["image_url"] = response
                    # print('cell_image_path == ', response)
                except Exception as e:
                    print(f'Error getting blob URL for { filename }: { str(e)}')
                    cls["image_url"] = None
            else:
                cls['image_url'] = None
        else:
            cls["image_url"] = f"/media/{cls.pop('cell_image_path')}" if cls.get('cell_image_path') else None

        # cls["image_url"] = f"/media/{cls.pop('image')}" if cls.get("image") else None
        classification_groups[class_label].append(cls)

    classification_groups = dict(classification_groups)
    print("Classification groups count:", len(classification_groups))
    for key, value in classification_groups.items():
        print(f"Group: {key}, Number of Cells: {len(value)}")

    new_cell_total = sum(len(value) for key, value in classification_groups.items() if key != 'skippocytes')
    skippocytes_counts = len(classification_groups.get("skippocytes", []))

    diff_view = CellView()
    diff_counts = diff_view.get_diff_counts(case_id)

    context = {
        'case': case,
        'diff_counts': diff_counts,
        'cell_groups': classification_groups,
        'cell_order': CELL_ORDER,
        # 'cell_total': cell_total
        'cell_total': new_cell_total,
        'skippocytes_counts': skippocytes_counts,
    }

    return render (request, 'cases/case.html', context)


def preview_popup(request):
    return render(request, 'core/preview_popup.html')

