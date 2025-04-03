import os
import csv
import json
import logging
from datetime import datetime
from .utils import ReportingBase

class ReportExporter(ReportingBase):
    """Export report data to various formats"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
    
    def export_to_csv(self, data, filename, report_type=None):
        """
        Export data to a CSV file
        
        Args:
            data: List of dictionaries with data to export
            filename: Base filename without extension
            report_type: Optional subfolder name
            
        Returns:
            str: Path to the created CSV file
        """
        if not data or not isinstance(data, list) or len(data) == 0:
            self.logger.warning(f"No data to export for {filename}")
            return None
            
        # Ensure directory exists
        output_dir = self.ensure_reports_directory(report_type)
        
        # Add timestamp to filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        full_filename = f"{filename}_{timestamp}.csv"
        file_path = os.path.join(output_dir, full_filename)
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                # Get fields from first row
                fieldnames = data[0].keys()
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for row in data:
                    writer.writerow(row)
                    
            self.logger.info(f"Successfully exported {len(data)} rows to {file_path}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"Error exporting data to CSV: {str(e)}")
            return None
    
    def export_to_json(self, data, filename, report_type=None):
        """
        Export data to a JSON file
        
        Args:
            data: List of dictionaries or dictionary with data to export
            filename: Base filename without extension
            report_type: Optional subfolder name
            
        Returns:
            str: Path to the created JSON file
        """
        if data is None:
            self.logger.warning(f"No data to export for {filename}")
            return None
            
        # Ensure directory exists
        output_dir = self.ensure_reports_directory(report_type)
        
        # Add timestamp to filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        full_filename = f"{filename}_{timestamp}.json"
        file_path = os.path.join(output_dir, full_filename)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, indent=4, default=str)
                    
            self.logger.info(f"Successfully exported data to {file_path}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"Error exporting data to JSON: {str(e)}")
            return None
    
    def export_full_report(self, report_obj, report_name, report_type):
        """
        Export all available reports from a report object
        
        Args:
            report_obj: Report object (WeeklyReports, MonthlyReports, etc.)
            report_name: Base name for the report files
            report_type: Type of report (weekly, monthly, etc.)
            
        Returns:
            dict: Mapping of report method names to export file paths
        """
        results = {}
        
        # Get all methods in the report object that start with "get_"
        report_methods = [method for method in dir(report_obj) 
                          if method.startswith('get_') and callable(getattr(report_obj, method))]
        
        for method_name in report_methods:
            try:
                # Call the method to get the report data
                method = getattr(report_obj, method_name)
                report_data = method()
                
                # Skip empty results
                if not report_data:
                    self.logger.warning(f"No data returned from {method_name}")
                    continue
                
                # Export the data to CSV
                filename = f"{report_name}_{method_name[4:]}"  # Remove 'get_' prefix
                csv_path = self.export_to_csv(report_data, filename, report_type)
                
                if csv_path:
                    results[method_name] = csv_path
                    
            except Exception as e:
                self.logger.error(f"Error generating report {method_name}: {str(e)}")
        
        return results