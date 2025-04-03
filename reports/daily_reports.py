from datetime import datetime
from .utils import ReportingBase

class DailyReports(ReportingBase):
    def __init__(self, report_date=None):
        super().__init__()
        self.report_date = report_date or datetime.now()
        # Make sure we pass the interval_type parameter
        self.start_date, self.end_date = self.get_date_range('daily', self.report_date)
    
    def get_request_summary(self):
        """Get summary of requests by type for the day"""
        query = f"""
            SELECT 
                REQUEST_TYPE, 
                COUNT(*) as REQUEST_COUNT,
                COUNT(DISTINCT MSISDN) as UNIQUE_USERS
            FROM TRANSACTION_REQUESTS
            WHERE CREATED_ON >= TO_TIMESTAMP('{self.start_date.strftime("%Y-%m-%d %H:%M:%S")}', 'YYYY-MM-DD HH24:MI:SS')
            AND CREATED_ON < TO_TIMESTAMP('{self.end_date.strftime("%Y-%m-%d %H:%M:%S")}', 'YYYY-MM-DD HH24:MI:SS')
            GROUP BY REQUEST_TYPE
            ORDER BY REQUEST_COUNT DESC
        """
        return self.execute_query(query)
    
    def get_hourly_distribution(self):
        """Get hourly distribution of requests"""
        query = f"""
            SELECT 
                TO_CHAR(CREATED_ON, 'HH24') as HOUR_OF_DAY,
                REQUEST_TYPE,
                COUNT(*) as REQUEST_COUNT
            FROM TRANSACTION_REQUESTS
            WHERE CREATED_ON >= TO_TIMESTAMP('{self.start_date.strftime("%Y-%m-%d %H:%M:%S")}', 'YYYY-MM-DD HH24:MI:SS')
            AND CREATED_ON < TO_TIMESTAMP('{self.end_date.strftime("%Y-%m-%d %H:%M:%S")}', 'YYYY-MM-DD HH24:MI:SS')
            GROUP BY TO_CHAR(CREATED_ON, 'HH24'), REQUEST_TYPE
            ORDER BY HOUR_OF_DAY, REQUEST_TYPE
        """
        return self.execute_query(query)
    
    def generate_daily_report(self):
        """Generate and export all daily reports to CSV files"""
        date_str = self.report_date.strftime("%Y-%m-%d")
        
        # Generate summary report
        summary_data = self.get_request_summary()
        summary_file = f"daily_summary_{date_str}.csv"
        self.export_to_csv(summary_data, summary_file)
        
        # Generate hourly distribution report
        hourly_data = self.get_hourly_distribution()
        hourly_file = f"daily_hourly_distribution_{date_str}.csv"
        self.export_to_csv(hourly_data, hourly_file)
        
        return {
            "summary": summary_file,
            "hourly_distribution": hourly_file,
        }