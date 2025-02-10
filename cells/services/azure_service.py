from typing import Optional, List
from azure_db_manager import DatabaseManager
from django.utils.text import slugify

from cells.models import Cell, CellClassification, CellDetection

class CellAzureService:
    def __init__(self):
        self.azure_db = DatabaseManager()

    def sync_cell_classification(self, cell_id: str) -> Optional[CellClassification]:
        """Fetch classification from Azure and sync to Django"""
        try:
            cursor = self.azure_db.conn.cursor()
            cursor.execute("""
                SELECT * FROM cell_classification 
                WHERE cell_id = ?
            """, cell_id)
            
            row = cursor.fetchone()
            if not row:
                return None

            # Get or create Django cell classification
            cell = Cell.objects.get(id=cell_id)
            classification, created = CellClassification.objects.update_or_create(
                cell=cell,
                defaults={
                    'ai_class': slugify(row.ai_cell_class) if row.ai_cell_class else None,
                    'user_class': slugify(row.user_cell_class) if row.user_cell_class else None,
                    'myelocyte_score': row.myelocytes_score,
                    'metamyelocyte_score': row.metamyelocytes_score,
                    'neutrophil_score': row.neutrophils_bands_score,
                    'monocyte_score': row.monocytes_score,
                    'eosinophil_score': row.eosinophils_score,
                    'erythroid_precursor_score': row.erythroid_precursors_score,
                    'lymphocyte_score': row.lymphocytes_score,
                    'plasma_cell_score': row.plasma_cells_score,
                    'blast_score': row.blasts_and_blast_equivalents_score,
                    'skippocyte_score': row.skippocyte_score,
                    'model_id': str(row.cell_classification_model_id)
                }
            )
            return classification
        finally:
            cursor.close()

    def sync_cell_detection(self, cell_id: str) -> Optional[CellDetection]:
        """Fetch detection from Azure and sync to Django"""
        try:
            cursor = self.azure_db.conn.cursor()
            cursor.execute("""
                SELECT * FROM cell_detection 
                WHERE cell_id = ?
            """, cell_id)
            
            row = cursor.fetchone()
            if not row:
                return None

            cell = Cell.objects.get(id=cell_id)
            detection, created = CellDetection.objects.update_or_create(
                cell=cell,
                defaults={
                    'detection_score': row.cell_detection_score,
                    'model_id': str(row.cell_detection_model_id),
                    'is_user_added': row.is_user_added
                }
            )
            return detection
        finally:
            cursor.close()
