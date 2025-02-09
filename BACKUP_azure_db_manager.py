import pyodbc
from datetime import datetime, date, time
from typing import List, Dict, Optional, Union
import os
import pandas as pd
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    DatabaseManager class for Azure SQL Database operations
    """
    def __init__(self, server: str = 'bmacopilotv1-sql-entra.database.windows.net',
                 database: str = 'BMACopilotV1DB',
                 username: str = 'bmacopilotv1-admin',
                 password: str = 'gregLV1!',
                 driver: str = 'ODBC Driver 18 for SQL Server'):
        """
        Initialize database connection using Azure SQL credentials
        """
        self.conn_str = (
            f"Driver={driver};"
            f"Server={server};"
            f"Database={database};"
            f"UID={username};"
            f"PWD={password};"
            "Encrypt=yes;"
        )
        self.conn = None
        self.connect()

    def connect(self):
        """Establish database connection"""
        try:
            self.conn = pyodbc.connect(self.conn_str)
            logger.info("Successfully connected to database")
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def does_user_id_exist(self, user_id: str) -> bool:
        """Check if a user ID exists in the database"""
        try:
            cursor = self.conn.cursor()
            result = cursor.execute("SELECT 1 FROM users WHERE user_id = ?", user_id).fetchone()
            return result is not None
        except Exception as e:
            logger.error(f"Error checking user existence: {e}")
            return False
        finally:
            cursor.close()

    def does_case_id_exist(self, case_id: str) -> bool:
        """Check if a case ID exists in the database"""
        try:
            cursor = self.conn.cursor()
            result = cursor.execute("SELECT 1 FROM cases WHERE case_id = ?", case_id).fetchone()
            return result is not None
        except Exception as e:
            logger.error(f"Error checking case existence: {e}")
            return False
        finally:
            cursor.close()

    def does_video_id_exist(self, video_id: str) -> bool:
        """Check if a video ID exists in the database"""
        try:
            cursor = self.conn.cursor()
            result = cursor.execute("SELECT 1 FROM videos WHERE video_id = ?", video_id).fetchone()
            return result is not None
        except Exception as e:
            logger.error(f"Error checking video existence: {e}")
            return False
        finally:
            cursor.close()

    def does_region_id_exist(self, region_id: str) -> bool:
        """Check if a region ID exists in the database"""
        try:
            cursor = self.conn.cursor()
            result = cursor.execute("SELECT 1 FROM region WHERE region_id = ?", region_id).fetchone()
            return result is not None
        except Exception as e:
            logger.error(f"Error checking region existence: {e}")
            return False
        finally:
            cursor.close()

    def does_cell_id_exist(self, cell_id: str) -> bool:
        """Check if a cell ID exists in the database"""
        try:
            cursor = self.conn.cursor()
            result = cursor.execute("SELECT 1 FROM cells WHERE cell_id = ?", cell_id).fetchone()
            return result is not None
        except Exception as e:
            logger.error(f"Error checking cell existence: {e}")
            return False
        finally:
            cursor.close()

    def new_user(self, user_id: str) -> bool:
        """Add a new user to the database"""
        try:
            if self.does_user_id_exist(user_id):
                logger.info(f"User {user_id} already exists")
                return False

            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO users (user_id)
                VALUES (?)
            """, user_id)
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            return False
        finally:
            cursor.close()

    def add_regions_from_df(self, region_metadata: pd.DataFrame) -> bool:
        """Add regions from a pandas DataFrame to the database"""
        try:
            cursor = self.conn.cursor()
            
            # Convert DataFrame to list of tuples
            data = [
                (
                    record['region_id'],
                    record['video_id'],
                    str(pd.Timestamp.fromtimestamp(record['time_stamp'])),
                    record['TL_x_in_frame'],
                    record['TL_y_in_frame'],
                    record['BR_x_in_frame'],
                    record['BR_y_in_frame'],
                    record['group_id']
                )
                for record in region_metadata.to_dict('records')
            ]
            
            cursor.executemany("""
                INSERT INTO region (
                    region_id, video_id, time_stamp,
                    TL_x_in_frame, TL_y_in_frame,
                    BR_x_in_frame, BR_y_in_frame,
                    group_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, data)
            
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding regions from DataFrame: {e}")
            return False
        finally:
            cursor.close()

    def add_region_classifications_from_df(self, region_clf_metadata: pd.DataFrame) -> bool:
        """Add region classifications from a pandas DataFrame to the database"""
        try:
            cursor = self.conn.cursor()
            
            data = [
                (
                    record['region_id'],
                    record['region_classification_score'],
                    record['is_selected_by_region_classifier'],
                    record['region_classifier_id']
                )
                for record in region_clf_metadata.to_dict('records')
            ]
            
            cursor.executemany("""
                INSERT INTO region_classification (
                    region_id, region_classification_score,
                    is_selected_by_region_classifier, region_classifier_id
                ) VALUES (?, ?, ?, ?)
            """, data)
            
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding region classifications from DataFrame: {e}")
            return False
        finally:
            cursor.close()

    def add_cell_detections_from_df(self, cell_detection_metadata: pd.DataFrame) -> bool:
        """Add cell detections from a pandas DataFrame to the database"""
        try:
            cursor = self.conn.cursor()
            
            data = [
                (
                    record['cell_id'],
                    record['cell_detection_score'],
                    record['cell_detection_model_id'],
                    record['is_user_added']
                )
                for record in cell_detection_metadata.to_dict('records')
            ]
            
            cursor.executemany("""
                INSERT INTO cell_detection (
                    cell_id, cell_detection_score,
                    cell_detection_model_id, is_user_added
                ) VALUES (?, ?, ?, ?)
            """, data)
            
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding cell detections from DataFrame: {e}")
            return False
        finally:
            cursor.close()

    def add_cells_from_df(self, cells_metadata: pd.DataFrame) -> bool:
        """Add cells from a pandas DataFrame to the database"""
        try:
            cursor = self.conn.cursor()
            
            data = [
                (
                    record['cell_id'],
                    record['region_id'],
                    record['cell_image_path'],
                    record['center_x_in_region'],
                    record['center_y_in_region'],
                    record['TL_x_in_region'],
                    record['TL_y_in_region'],
                    record['BR_x_in_region'],
                    record['BR_y_in_region']
                )
                for record in cells_metadata.to_dict('records')
            ]
            
            cursor.executemany("""
                INSERT INTO cells (
                    cell_id, region_id, cell_image_path,
                    center_x_in_region, center_y_in_region,
                    TL_x_in_region, TL_y_in_region,
                    BR_x_in_region, BR_y_in_region
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, data)
            
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding cells from DataFrame: {e}")
            return False
        finally:
            cursor.close()

    def add_cell_classifications_from_df(self, cell_clf_metadata: pd.DataFrame) -> bool:
        """Add cell classifications from a pandas DataFrame to the database"""
        try:
            cursor = self.conn.cursor()
            
            data = [
                (
                    record['cell_id'],
                    record['ai_cell_class'],
                    record['user_cell_class'],
                    record['myelocytes_score'],
                    record['metamyelocytes_score'],
                    record['neutrophils_bands_score'],
                    record['monocytes_score'],
                    record['eosinophils_score'],
                    record['erythroid_precursors_score'],
                    record['lymphocytes_score'],
                    record['plasma_cells_score'],
                    record['blasts_and_blast_equivalents_score'],
                    record['skippocyte_score'],
                    record['cell_classification_model_id']
                )
                for record in cell_clf_metadata.to_dict('records')
            ]
            
            cursor.executemany("""
                INSERT INTO cell_classification (
                    cell_id, ai_cell_class, user_cell_class,
                    myelocytes_score, metamyelocytes_score,
                    neutrophils_bands_score, monocytes_score,
                    eosinophils_score, erythroid_precursors_score,
                    lymphocytes_score, plasma_cells_score,
                    blasts_and_blast_equivalents_score,
                    skippocyte_score, cell_classification_model_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, data)
            
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding cell classifications from DataFrame: {e}")
            return False
        finally:
            cursor.close()

    def add_regions_images_selected_from_df(self, regions_image_selected_metadata: pd.DataFrame) -> bool:
        """Add region image selected data from a DataFrame to the database"""
        try:
            cursor = self.conn.cursor()
            
            data = [
                (
                    record['region_id'],
                    record['region_image_path']
                )
                for record in regions_image_selected_metadata.to_dict('records')
            ]
            
            cursor.executemany("""
                INSERT INTO region_image_selected (
                    region_id,
                    region_image_path
                ) VALUES (?, ?)
            """, data)
            
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding region images selected from DataFrame: {e}")
            return False
        finally:
            cursor.close()

    def create_case(self, case_id: str, case_name: str, case_description: str, 
                   case_date: str, case_time: str, user_id: str) -> bool:
        """Create a new case in the database"""
        try:
            if self.does_case_id_exist(case_id):
                return True
                
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO cases (
                    case_id, case_name, case_description,
                    case_date, case_time, case_status, user_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, [case_id, case_name, case_description, case_date, case_time, "pending", user_id])
            
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error creating case: {e}")
            return False
        finally:
            cursor.close()

    def add_video(self, video_id: str, video_file_path: str, case_id: str) -> bool:
        """Add a new video to the database"""
        try:
            if self.does_video_id_exist(video_id):
                return True
                
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO videos (video_id, video_file_path, case_id)
                VALUES (?, ?, ?)
            """, [video_id, video_file_path, case_id])
            
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding video: {e}")
            return False
        finally:
            cursor.close()

    def get_video_file_path_from_video_id(self, video_id: str) -> str:
        """Get the file path of a video from its ID"""
        try:
            cursor = self.conn.cursor()
            result = cursor.execute(
                "SELECT video_file_path FROM videos WHERE video_id = ?", 
                [video_id]
            ).fetchone()
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting video file path: {e}")
            return None
        finally:
            cursor.close()