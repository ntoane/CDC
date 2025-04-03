from datetime import datetime, timedelta
from .utils import ReportingBase

class MonthlyReports(ReportingBase):
    def __init__(self, report_date=None):
        super().__init__()
        self.report_date = report_date or datetime.now()
        # Make sure we pass the interval_type parameter
        self.start_date, self.end_date = self.get_date_range('monthly', self.report_date)
        
        # Adjust end date for wider data query window if needed
        # This helps find data in test environments
        self.query_end_date = datetime.now() + timedelta(days=365)  # Look ahead a year for test data
    
    def get_weekly_trend(self):
        """Get weekly trend of requests within the month"""
        query = f"""
            SELECT 
                TO_CHAR(CREATED_ON, 'YYYY-IW') as YEAR_WEEK,
                TO_CHAR(MIN(CREATED_ON), 'YYYY-MM-DD') as WEEK_START_DATE,
                TO_CHAR(MAX(CREATED_ON), 'YYYY-MM-DD') as WEEK_END_DATE,
                REQUEST_TYPE,
                COUNT(*) as REQUEST_COUNT,
                COUNT(DISTINCT MSISDN) as UNIQUE_USERS
            FROM TRANSACTION_REQUESTS
            WHERE CREATED_ON >= TO_TIMESTAMP('{self.start_date.strftime("%Y-%m-%d %H:%M:%S")}', 'YYYY-MM-DD HH24:MI:SS')
            AND CREATED_ON < TO_TIMESTAMP('{self.end_date.strftime("%Y-%m-%d %H:%M:%S")}', 'YYYY-MM-DD HH24:MI:SS')
            GROUP BY TO_CHAR(CREATED_ON, 'YYYY-IW'), REQUEST_TYPE
            ORDER BY YEAR_WEEK, REQUEST_TYPE
        """
        return self.execute_query(query)
    
    def get_user_retention(self):
        """Calculate user retention metrics for the month"""
        query = f"""
            WITH FirstUsage AS (
                SELECT 
                    MSISDN,
                    MIN(TO_CHAR(CREATED_ON, 'YYYY-MM-DD')) as FIRST_USAGE_DATE
                FROM TRANSACTION_REQUESTS
                WHERE CREATED_ON < TO_TIMESTAMP('{self.query_end_date.strftime("%Y-%m-%d %H:%M:%S")}', 'YYYY-MM-DD HH24:MI:SS')
                GROUP BY MSISDN
            ),
            CurrentMonthUsers AS (
                SELECT DISTINCT
                    MSISDN
                FROM TRANSACTION_REQUESTS
                WHERE CREATED_ON >= TO_TIMESTAMP('{self.start_date.strftime("%Y-%m-%d %H:%M:%S")}', 'YYYY-MM-DD HH24:MI:SS')
                AND CREATED_ON < TO_TIMESTAMP('{self.end_date.strftime("%Y-%m-%d %H:%M:%S")}', 'YYYY-MM-DD HH24:MI:SS')
            )
            SELECT
                'New Users' as USER_TYPE,
                COUNT(*) as USER_COUNT
            FROM FirstUsage f
            JOIN CurrentMonthUsers c ON f.MSISDN = c.MSISDN
            WHERE TO_DATE(f.FIRST_USAGE_DATE, 'YYYY-MM-DD') >= TO_DATE('{self.start_date.strftime("%Y-%m-%d")}', 'YYYY-MM-DD')
            
            UNION ALL
            
            SELECT
                'Returning Users' as USER_TYPE,
                COUNT(*) as USER_COUNT
            FROM FirstUsage f
            JOIN CurrentMonthUsers c ON f.MSISDN = c.MSISDN
            WHERE TO_DATE(f.FIRST_USAGE_DATE, 'YYYY-MM-DD') < TO_DATE('{self.start_date.strftime("%Y-%m-%d")}', 'YYYY-MM-DD')
        """
        return self.execute_query(query)
    
    def get_monthly_summary(self):
        """Generate comprehensive monthly summary"""
        query = f"""
            SELECT
                TO_CHAR(TO_DATE('{self.start_date.strftime("%Y-%m-%d")}', 'YYYY-MM-DD'), 'Month YYYY') as REPORT_MONTH,
                COUNT(*) as TOTAL_REQUESTS,
                COUNT(DISTINCT MSISDN) as TOTAL_UNIQUE_USERS,
                SUM(CASE WHEN REQUEST_TYPE = 'AIRTIME_TRANSFER' THEN 1 ELSE 0 END) as AIRTIME_TRANSFER_REQUESTS,
                SUM(CASE WHEN REQUEST_TYPE = 'BUNDLE_PURCHASE' THEN 1 ELSE 0 END) as BUNDLE_PURCHASE_REQUESTS,
                SUM(CASE WHEN REQUEST_TYPE = 'CALL_RECORDS' THEN 1 ELSE 0 END) as CALL_RECORDS_REQUESTS,
                COUNT(DISTINCT TO_CHAR(CREATED_ON, 'YYYY-MM-DD')) as ACTIVE_DAYS,
                ROUND(COUNT(*) / COUNT(DISTINCT TO_CHAR(CREATED_ON, 'YYYY-MM-DD')), 2) as AVG_DAILY_REQUESTS,
                ROUND(COUNT(DISTINCT MSISDN) / COUNT(DISTINCT TO_CHAR(CREATED_ON, 'YYYY-MM-DD')), 2) as AVG_DAILY_USERS
            FROM TRANSACTION_REQUESTS
            WHERE CREATED_ON >= TO_TIMESTAMP('{self.start_date.strftime("%Y-%m-%d %H:%M:%S")}', 'YYYY-MM-DD HH24:MI:SS')
            AND CREATED_ON < TO_TIMESTAMP('{self.end_date.strftime("%Y-%m-%d %H:%M:%S")}', 'YYYY-MM-DD HH24:MI:SS')
        """
        return self.execute_query(query)