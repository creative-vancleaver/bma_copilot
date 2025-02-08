
from collections import defaultdict
from django.db.models import F
from django.shortcuts import render

from cells.models import Cell, CellClassification
from cells.views import CellStatsView

from cases.models import Case

CELL_ORDER = [
    'blast', 'promyelocyte', 'myelocyte', 'metamyelocyte', 'neutrophil', 'monocyte', 'eosinophil', 
    'basophil', 'lymphocyte', 'plasma-cell', 'erythroid-precursor', 'skippocyte', 'unclassified',
]

def index(request):

    return render(request, 'core/index.html')


def case(request, case_id):

    case = Case.objects.get(id=case_id)
    
    cell_total = Cell.objects.filter(region__case=case).count()
    print(cell_total)

    # classifications = (
    #     CellClassification.objects
    #     .filter(cell__region__case=case)
    #     .select_related("cell")
    #     .values(
    #         "ai_class",
    #         "cell_id",
    #         "user_class",
    #         "cell__image",  # Get image field from Cell model
    #         "myelocyte_score",
    #         "metamyelocyte_score",
    #         "neutrophil_score",
    #         "monocyte_score",
    #         "eosinophil_score",
    #         "erythroid_precursor_score",
    #         "lymphocyte_score",
    #         "plasma_cell_score",
    #         "blast_score",
    #         "skippocyte_score",

    #         "basophil_score",
    #     )
    #     .order_by("user_class", "ai_class")  # Ensures results are grouped by user_class THEN ai_class
    # )

    classifications = (
        Cell.objects
        .filter(region__case=case)
        .annotate(
            ai_class=F("classification__ai_class"),
            user_class=F("classification__user_class"),
            # image_url=F("image"),  # Ensure image URL is included
            myelocyte_score=F("classification__myelocyte_score"),
            metamyelocyte_score=F("classification__metamyelocyte_score"),
            neutrophil_score=F("classification__neutrophil_score"),
            monocyte_score=F("classification__monocyte_score"),
            eosinophil_score=F("classification__eosinophil_score"),
            erythroid_precursor_score=F("classification__erythroid_precursor_score"),
            lymphocyte_score=F("classification__lymphocyte_score"),
            plasma_cell_score=F("classification__plasma_cell_score"),
            blast_score=F("classification__blast_score"),
            skippocyte_score=F("classification__skippocyte_score"),
            basophil_score=F("classification__basophil_score"),
        )
        .values(
            "id", "image", "ai_class", "user_class",
            "myelocyte_score", "metamyelocyte_score", "neutrophil_score",
            "monocyte_score", "eosinophil_score", "erythroid_precursor_score",
            "lymphocyte_score", "plasma_cell_score", "blast_score",
            "skippocyte_score", "basophil_score", 
        )
        .order_by("user_class", "ai_class")
    )
    print('classifications ', classifications.count())

    # Convert queryset into a structured dictionary in a single step
    classification_groups = defaultdict(list)

    for cls in classifications:
        # Ensure None values do not cause missing classifications
        user_class = cls.pop("user_class", None)
        ai_class = cls.pop("ai_class", None)

        class_label = user_class if user_class else ai_class if ai_class else "unclassified"

        cls["image_url"] = f"/media/{cls.pop('image')}" if cls.get("image") else None
        classification_groups[class_label].append(cls)

    for cell in classification_groups.get('metamyelocyte', []):
        print(cell['image_url'])


    # missing_cells = []
    # for cls in classifications:
    #     # class_label = cls.pop("user_class") or cls.pop('ai_class') # Extract class name
    #     class_label = cls.pop("user_class") or cls.pop("ai_class") or "unclassified"
    #     if not class_label:
    #         missing_cells.append(cls)
    #     cls["image_url"] = f"/media/{cls.pop('cell__image')}" if cls.get("cell__image") else None
    #     classification_groups[class_label].append(cls)

    classification_groups = dict(classification_groups)
    print("Classification groups count:", len(classification_groups))
    for key, value in classification_groups.items():
        print(f"Group: {key}, Number of Cells: {len(value)}")



    diff_view = CellStatsView()
    diff_counts = diff_view.get_diff_counts(case_id)

    context = {
        'diff_counts': diff_counts,
        'cell_groups': classification_groups,
        'cell_order': CELL_ORDER,
        'cell_total': cell_total,
    }

    return render (request, 'cases/case.html', context)

