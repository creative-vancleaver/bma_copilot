import json

from django.core.exceptions import ObjectDoesNotExist
from .models import Cell, CellClassification

def import_sample_classifications(json_file_path):

    try:

        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)

        cell_classifications = []
        missing_cells = 0

        for entry in data:
            try:
                cell = Cell.objects.get(id=entry["cell_id"])
                classification = CellClassification(
                    cell=cell,
                    ai_class=entry["ai_class"],
                    user_class=entry["user_class"],
                    myelocyte_score=entry["myelocyte_score"],
                    metamyelocyte_score=entry["metamyelocyte_score"],
                    neutrophil_score=entry["neutrophil_score"],
                    monocyte_score=entry["monocyte_score"],
                    eosinophil_score=entry["eosinophil_score"],
                    erythroid_precursor_score=entry["erythroid_precursor_score"],
                    lymphocyte_score=entry["lymphocyte_score"],
                    plasma_cell_score=entry["plasma_cell_score"],
                    blast_score=entry["blast_score"],
                    skippocyte_score=entry["skippocyte_score"],
                    model_id=entry["model_id"]                    
                )
                cell_classifications.append(classification)
            
            except ObjectDoesNotExist:
                missing_cells += 1
                print(f"warning: cell with id { id } not found. skipping.")

        if cell_classifications:
            CellClassification.objects.bulk_create(cell_classifications)

    except Exception as e:
        print(f"ERROR: { e }")
