from typing import Optional, List
from azure_db_manager import DatabaseManager
from django.utils.text import slugify

from cells.models import Cell, CellClassification, CellDetection
from cases.models import Case, Video
from regions.models import Region, RegionImage, RegionClassification
from core.services.base_service import BaseAzureService

class CellAzureService(BaseAzureService):
    def __init__(self):
        super().__init__()
        self.azure_db = DatabaseManager()

    def sync_cell_classification(self, cell_id: str) -> Optional[CellClassification]:
        return self.safe_azure_operation(self._sync_cell_classification, cell_id)
    
    def _sync_cell_classification(self, cell_id: str) -> Optional[CellClassification]:
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

class CaseAzureService(BaseAzureService):
    def __init__(self):
        super().__init__()
        self.azure_db = DatabaseManager()

    def sync_case(self, case_id: str) -> Optional[Case]:
        """Fetch case from Azure and sync to Django"""
        try:
            cursor = self.azure_db.conn.cursor()
            cursor.execute("""
                SELECT * FROM cases 
                WHERE case_id = ?
            """, case_id)
            
            row = cursor.fetchone()
            if not row:
                return None

            case, created = Case.objects.update_or_create(
                id=case_id,
                defaults={
                    'name': row.case_name,
                    'description': row.case_description,
                    'date': row.case_date,
                    'time': row.case_time,
                    'status': row.case_status,
                    'user_id': row.user_id
                }
            )
            return case
        finally:
            cursor.close()

    def sync_video(self, video_id: str) -> Optional[Video]:
        """Fetch video from Azure and sync to Django"""
        try:
            cursor = self.azure_db.conn.cursor()
            cursor.execute("""
                SELECT * FROM videos 
                WHERE video_id = ?
            """, video_id)
            
            row = cursor.fetchone()
            if not row:
                return None

            video, created = Video.objects.update_or_create(
                id=video_id,
                defaults={
                    'case_id': row.case_id,
                    'video_file': row.video_file_path
                }
            )
            return video
        finally:
            cursor.close()

class RegionAzureService(BaseAzureService):
    def __init__(self):
        super().__init__()
        self.azure_db = DatabaseManager()

    def sync_region(self, region_id: str) -> Optional[Region]:
        """Fetch region from Azure and sync to Django"""
        try:
            cursor = self.azure_db.conn.cursor()
            cursor.execute("""
                SELECT * FROM region 
                WHERE region_id = ?
            """, region_id)
            
            row = cursor.fetchone()
            if not row:
                return None

            region, created = Region.objects.update_or_create(
                id=region_id,
                defaults={
                    'case_id': row.case_id,
                    'video_id': row.video_id,
                    'time_stamp': row.time_stamp,
                    'TL_x_in_frame': row.TL_x_in_frame,
                    'TL_y_in_frame': row.TL_y_in_frame,
                    'BR_x_in_frame': row.BR_x_in_frame,
                    'BR_y_in_frame': row.BR_y_in_frame,
                    'group_id': row.group_id
                }
            )
            return region
        finally:
            cursor.close()

    def sync_region_classification(self, region_id: str) -> Optional[RegionClassification]:
        """Fetch region classification from Azure and sync to Django"""
        try:
            cursor = self.azure_db.conn.cursor()
            cursor.execute("""
                SELECT * FROM region_classification 
                WHERE region_id = ?
            """, region_id)
            
            row = cursor.fetchone()
            if not row:
                return None

            region = Region.objects.get(id=region_id)
            classification, created = RegionClassification.objects.update_or_create(
                region=region,
                defaults={
                    'classification_score': row.region_classification_score,
                    'is_selected': row.is_selected_by_region_classifier,
                    'classifier_id': row.region_classifier_id
                }
            )
            return classification
        finally:
            cursor.close()
