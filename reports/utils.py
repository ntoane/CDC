import os
import csv
import logging
from datetime import datetime, timedelta
from resources.utilities.database.oracle import exadata_db

class ReportingBase:
    """Base class for all reporting functionality with shared methods."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def execute_query(self, query, fetch_data=True):
        """Execute a query and return formatted results."""
        try:
            conn = exadata_db.get_connection_handle()
            cursor = conn.cursor()
            cursor.execute(query)
            
            if fetch_data:
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                result = [dict(zip(columns, row)) for row in rows]
                return result
            else:
                conn.commit()
                return True
        except Exception as e:
            self.logger.error(f"Database error in reporting: {str(e)}")
            raise
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'conn' in locals() and conn:
                conn.close()
    
    def get_date_range(self, interval_type=None, reference_date=None):
        """
        Calculate start and end dates for different report intervals.
        
        Args:
            interval_type: 'daily', 'weekly', 'monthly', 'quarterly', or 'yearly'
            reference_date: Date to calculate from, defaults to today
            
        Returns:
            tuple: (start_date, end_date) for the reporting period
        """
        if interval_type is None:
            raise ValueError("interval_type is required")
            
        reference_date = reference_date or datetime.now()
        
        if interval_type == 'daily':
            start_date = datetime(reference_date.year, reference_date.month, reference_date.day, 0, 0, 0)
            end_date = start_date + timedelta(days=1)
            
        elif interval_type == 'weekly':
            # Get the Monday of the current week
            start_date = reference_date - timedelta(days=reference_date.weekday())
            start_date = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)
            end_date = start_date + timedelta(days=7)
            
        elif interval_type == 'monthly':
            start_date = datetime(reference_date.year, reference_date.month, 1, 0, 0, 0)
            # Go to first day of next month
            if reference_date.month == 12:
                end_date = datetime(reference_date.year + 1, 1, 1, 0, 0, 0)
            else:
                end_date = datetime(reference_date.year, reference_date.month + 1, 1, 0, 0, 0)
                
        elif interval_type == 'quarterly':
            quarter = (reference_date.month - 1) // 3 + 1
            start_date = datetime(reference_date.year, (quarter - 1) * 3 + 1, 1, 0, 0, 0)
            if quarter == 4:
                end_date = datetime(reference_date.year + 1, 1, 1, 0, 0, 0)
            else:
                end_date = datetime(reference_date.year, quarter * 3 + 1, 1, 0, 0, 0)
                
        elif interval_type == 'yearly':
            start_date = datetime(reference_date.year, 1, 1, 0, 0, 0)
            end_date = datetime(reference_date.year + 1, 1, 1, 0, 0, 0)
            
        else:
            raise ValueError(f"Unknown interval type: {interval_type}")
            
        return start_date, end_date
    
    def ensure_reports_directory(self, subdir=None):
        """Ensure the reports directory exists."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        report_dir = os.path.join(base_dir, 'generated_reports')
        
        if subdir:
            report_dir = os.path.join(report_dir, subdir)
            
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)
            
        return report_dir