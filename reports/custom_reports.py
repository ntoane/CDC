from datetime import datetime
from .utils import ReportingBase

class CustomReports(ReportingBase):
    def __init__(self, start_date=None, end_date=None):
        """
        Initialize custom report with specific date range
        
        Args:
            start_date: Start date for reporting (inclusive)
            end_date: End date for reporting (exclusive)
        """
        super().__init__()
        
        if not start_date:
            raise ValueError("Start date is required for custom reports")
            
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            
        if end_date and isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            
        if not end_date:
            # If end date not provided, use start date + 1 day
            self.start_date = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)
            self.end_date = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)
            self.end_date = self.start_date.replace(hour=23, minute=59, second=59)
        else:
            self.start_date = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)
            self.end_date = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59)
    
    def get_transaction_summary(self):
        """Generate transaction summary for the custom date range"""
        query = f"""
            SELECT
                TO_CHAR(TO_DATE('{self.start_date.strftime("%Y-%m-%d")}', 'YYYY-MM-DD'), 'YYYY-MM-DD') || ' to ' ||
                TO_CHAR(TO_DATE('{self.end_date.strftime("%Y-%m-%d")}', 'YYYY-MM-DD'), 'YYYY-MM-DD') as DATE_RANGE,
                COUNT(*) as TOTAL_REQUESTS,
                COUNT(DISTINCT MSISDN) as TOTAL_UNIQUE_USERS,
                COUNT(DISTINCT TO_CHAR(CREATED_ON, 'YYYY-MM-DD')) as DAYS_WITH_ACTIVITY
            FROM TRANSACTION_REQUESTS
            WHERE CREATED_ON >= TO_TIMESTAMP('{self.start_date.strftime("%Y-%m-%d %H:%M:%S")}', 'YYYY-MM-DD HH24:MI:SS')
            AND CREATED_ON <= TO_TIMESTAMP('{self.end_date.strftime("%Y-%m-%d %H:%M:%S")}', 'YYYY-MM-DD HH24:MI:SS')
        """
        return self.execute_query(query)
    
    def get_request_type_breakdown(self):
        """Get breakdown of request types for the custom date range"""
        query = f"""
            SELECT
                REQUEST_TYPE,
                COUNT(*) as REQUEST_COUNT,
                COUNT(DISTINCT MSISDN) as UNIQUE_USERS,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as PERCENTAGE
            FROM TRANSACTION_REQUESTS
            WHERE CREATED_ON >= TO_TIMESTAMP('{self.start_date.strftime("%Y-%m-%d %H:%M:%S")}', 'YYYY-MM-DD HH24:MI:SS')
            AND CREATED_ON <= TO_TIMESTAMP('{self.end_date.strftime("%Y-%m-%d %H:%M:%S")}', 'YYYY-MM-DD HH24:MI:SS')
            GROUP BY REQUEST_TYPE
            ORDER BY REQUEST_COUNT DESC
        """
        return self.execute_query(query)
    
    def get_daily_activity(self):
        """Get daily activity for the custom date range"""
        query = f"""
            SELECT
                TO_CHAR(CREATED_ON, 'YYYY-MM-DD') as ACTIVITY_DATE,
                COUNT(*) as TOTAL_REQUESTS,
                COUNT(DISTINCT MSISDN) as UNIQUE_USERS,
                SUM(CASE WHEN REQUEST_TYPE = 'AIRTIME_TRANSFER' THEN 1 ELSE 0 END) as AIRTIME_REQUESTS,
                SUM(CASE WHEN REQUEST_TYPE = 'BUNDLE_PURCHASE' THEN 1 ELSE 0 END) as BUNDLE_REQUESTS,
                SUM(CASE WHEN REQUEST_TYPE = 'CALL_RECORDS' THEN 1 ELSE 0 END) as CALL_RECORD_REQUESTS
            FROM TRANSACTION_REQUESTS
            WHERE CREATED_ON >= TO_TIMESTAMP('{self.start_date.strftime("%Y-%m-%d %H:%M:%S")}', 'YYYY-MM-DD HH24:MI:SS')
            AND CREATED_ON <= TO_TIMESTAMP('{self.end_date.strftime("%Y-%m-%d %H:%M:%S")}', 'YYYY-MM-DD HH24:MI:SS')
            GROUP BY TO_CHAR(CREATED_ON, 'YYYY-MM-DD')
            ORDER BY ACTIVITY_DATE
        """
        return self.execute_query(query)