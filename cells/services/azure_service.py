from typing import Optional, List
from azure_db_manager import DatabaseManager
from django.utils.text import slugify

from cells.models import Cell, CellClassification, CellDetection
