#!/usr/bin/env python3
import os
import sys
import logging
import argparse
from datetime import datetime, timedelta

# Add parent directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reports.daily_reports import DailyReports
from reports.weekly_reports import WeeklyReports
from reports.monthly_reports import MonthlyReports
from reports.custom_reports import CustomReports
from reports.exporters import ReportExporter

# Configure logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    filename=os.path.join(log_dir, 'reports.log'),
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def run_daily_reports():
    """Generate and export daily reports"""
    logging.info("Starting daily reports generation")
    
    today = datetime.now()
    
    # Use DailyReports class instead of CustomReports
    daily_report = DailyReports(today)
    exporter = ReportExporter()
    
    # Generate and export reports using DailyReports methods
    summary = daily_report.get_request_summary()
    exporter.export_to_csv(summary, "daily_summary", "daily")
    
    hourly = daily_report.get_hourly_distribution()
    exporter.export_to_csv(hourly, "daily_hourly_distribution", "daily")
    
    # Or use the built-in method to generate all reports
    # report_files = daily_report.generate_daily_report()
    # logging.info(f"Generated daily reports: {', '.join(report_files.values())}")
    
    logging.info("Daily reports generation completed")

def run_weekly_reports():
    """Generate and export weekly reports"""
    logging.info("Starting weekly reports generation")
    
    try:
        # Get current week
        today = datetime.now()
        weekly_report = WeeklyReports(today)
        exporter = ReportExporter()
        
        # Export all weekly reports with proper error handling
        export_results = {}
        
        try:
            daily_trend = weekly_report.get_daily_trend()
            if daily_trend:
                export_results['daily_trend'] = exporter.export_to_csv(daily_trend, 
                                                                      "weekly_daily_trend", 
                                                                      "weekly")
        except Exception as e:
            logging.error(f"Error generating weekly daily trend: {str(e)}")
            
        try:
            top_users = weekly_report.get_top_users()
            if top_users:
                export_results['top_users'] = exporter.export_to_csv(top_users, 
                                                                   "weekly_top_users", 
                                                                   "weekly")
        except Exception as e:
            logging.error(f"Error generating weekly top users: {str(e)}")
            
        # Add more individual report exports with error handling
        
        logging.info(f"Weekly reports generation completed. Generated {len(export_results)} reports.")
        
    except Exception as e:
        logging.error(f"Error in weekly report generation: {str(e)}")

def run_monthly_reports():
    """Generate and export monthly reports"""
    logging.info("Starting monthly reports generation")
    
    # Get previous month
    today = datetime.now()
    # If it's the first day of the month, report on the previous month
    if today.day == 1:
        previous_month = datetime(today.year, today.month-1 if today.month > 1 else 12, 1)
    else:
        previous_month = today.replace(day=1)
    
    monthly_report = MonthlyReports(previous_month)
    exporter = ReportExporter()
    
    # Export all monthly reports
    export_results = exporter.export_full_report(monthly_report, "monthly_report", "monthly")
    
    logging.info(f"Monthly reports generation completed. Generated {len(export_results)} reports.")

def run_custom_report(start_date, end_date):
    """Generate and export custom date range reports"""
    logging.info(f"Starting custom reports generation from {start_date} to {end_date}")
    
    try:
        custom_report = CustomReports(start_date, end_date)
        exporter = ReportExporter()
        
        # Generate summary with error handling
        try:
            summary = custom_report.get_transaction_summary()
            if summary:
                exporter.export_to_csv(summary, "custom_summary", "custom")
        except Exception as e:
            logging.error(f"Error generating custom summary: {str(e)}")
        
        # Generate breakdown with error handling
        try:
            breakdown = custom_report.get_request_type_breakdown()
            if breakdown:
                exporter.export_to_csv(breakdown, "custom_breakdown_by_type", "custom")
        except Exception as e:
            logging.error(f"Error generating custom breakdown: {str(e)}")
        
        # Generate daily activity with error handling
        try:
            daily = custom_report.get_daily_activity()
            if daily:
                exporter.export_to_csv(daily, "custom_daily_activity", "custom")
        except Exception as e:
            logging.error(f"Error generating custom daily activity: {str(e)}")
        
        logging.info("Custom reports generation completed")
        
    except Exception as e:
        logging.error(f"Error in custom report generation: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate CDC transaction reports')
    parser.add_argument('--type', choices=['daily', 'weekly', 'monthly', 'custom'],
                        default='daily', help='Type of report to generate')
    parser.add_argument('--start-date', help='Start date for custom report (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='End date for custom report (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    try:
        if args.type == 'daily':
            run_daily_reports()
        elif args.type == 'weekly':
            run_weekly_reports()
        elif args.type == 'monthly':
            run_monthly_reports()
        elif args.type == 'custom':
            if not args.start_date:
                print("Error: start-date is required for custom reports")
                sys.exit(1)
            run_custom_report(args.start_date, args.end_date)
    except Exception as e:
        logging.error(f"Error running reports: {str(e)}", exc_info=True)
        sys.exit(1)