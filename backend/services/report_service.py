"""
Report Generation Service.
Exports attendance data to CSV using pandas.
"""

import os
from pathlib import Path
import pandas as pd
from datetime import datetime
from fpdf import FPDF

from backend.config import DATABASE_MODE

if DATABASE_MODE == "firebase":
    from backend.database.firebase_service import get_attendance_by_session_id
else:
    from backend.database.sqlite_service import get_attendance_by_session_id


# Uses environment variable for Azure Web App compatibility
REPORTS_DIR_ENV = os.getenv("REPORTS_DIR", "reports")
REPORTS_DIR = Path(REPORTS_DIR_ENV).resolve()


def generate_custom_report(records: list, subject_name: str, date_str: str) -> str:
    """Generate attendance sheet based on list of records with specific columns."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    if not records:
        return ""
    
    df = pd.DataFrame(records)
    
    # Required columns: Student Name, Roll Number, Subject Name, Time
    # Map from database fields
    if "name" in df.columns:
        df["Student Name"] = df["name"]
    else:
        df["Student Name"] = "N/A"
        
    if "roll_number" not in df.columns:
        df["Roll Number"] = "N/A" # Ideally caller augments this
    else:
        df["Roll Number"] = df["roll_number"]
        
    if "subject_name" in df.columns:
        df["Subject Name"] = df["subject_name"]
    else:
        df["Subject Name"] = subject_name
        
    if "time" in df.columns:
        df["Time"] = df["time"]
    else:
        df["Time"] = "N/A"
        
    df = df[["Student Name", "Roll Number", "Subject Name", "Time"]]
    
    safe_subject = "".join(c for c in subject_name if c.isalnum() or c in (' ', '_', '-')).strip()
    safe_subject = safe_subject.replace(' ', '_')
    if not safe_subject:
        safe_subject = "All_Subjects"
        
    filename = f"attendance_{safe_subject}_{date_str}.csv"
    filepath = REPORTS_DIR / filename
    
    df.to_csv(filepath, index=False)
    print(f"✅ Report generated: {filepath}")
    return str(filepath)


def generate_excel_report(records: list, subject_name: str, date_str: str, absent_records: list = None) -> str:
    """Generate professional Excel attendance sheet, including absent students if provided."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    if not records and not absent_records:
        return ""
    
    df = pd.DataFrame(records)
    
    df["Student Name"] = df.get("name", "N/A")
    df["Roll Number"] = df.get("roll_number", "N/A")
    df["Subject Name"] = df.get("subject_name", subject_name)
    df["Date"] = df.get("date", date_str)
    df["Time"] = df.get("time", "N/A")
    df["Status"] = "Present"
        
    df = df[["Student Name", "Roll Number", "Subject Name", "Date", "Time", "Status"]]
    
    safe_subject = "".join(c for c in subject_name if c.isalnum() or c in (' ', '_', '-')).strip()
    safe_subject = safe_subject.replace(' ', '_')
    if not safe_subject:
        safe_subject = "All_Subjects"
        
    filename = f"attendance_{safe_subject}_{date_str}.xlsx"
    filepath = REPORTS_DIR / filename
    
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Attendance")
        worksheet = writer.sheets["Attendance"]
        
        # Simple formatting
        for col in worksheet.columns:
            max_length = 0
            column_letter = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            worksheet.column_dimensions[column_letter].width = adjusted_width
            
        # Summary row
        summary_row = len(df) + 3
        worksheet.cell(row=summary_row, column=1, value="Summary:")
        worksheet.cell(row=summary_row+1, column=1, value="Total Present:")
        worksheet.cell(row=summary_row+1, column=2, value=len(df))
        
        last_row = summary_row + 2
        
        if absent_records:
            absent_df = pd.DataFrame(absent_records)
            absent_df["Student Name"] = absent_df.get("name", "N/A")
            absent_df["Roll Number"] = absent_df.get("roll_number", "N/A")
            absent_df["Subject Name"] = absent_df.get("subject_name", subject_name)
            absent_df["Date"] = absent_df.get("date", date_str)
            absent_df["Time"] = absent_df.get("time", "--:--")
            absent_df["Status"] = "Absent"
            absent_df = absent_df[["Student Name", "Roll Number", "Subject Name", "Date", "Time", "Status"]]
            
            # Start absent table
            absent_start = last_row + 2
            worksheet.cell(row=absent_start, column=1, value="Absent Students")
            absent_start += 1
            
            # Write headers
            for col_idx, column_title in enumerate(absent_df.columns, 1):
                worksheet.cell(row=absent_start, column=col_idx, value=column_title)
            
            # Write data rows
            for r_idx, row in enumerate(absent_df.itertuples(index=False), 1):
                for c_idx, value in enumerate(row, 1):
                    worksheet.cell(row=absent_start + r_idx, column=c_idx, value=value)
                    
            worksheet.cell(row=absent_start + len(absent_df) + 2, column=1, value="Total Absent:")
            worksheet.cell(row=absent_start + len(absent_df) + 2, column=2, value=len(absent_df))
    
    print(f"✅ Excel Report generated: {filepath}")
    return str(filepath)


def generate_pdf_report(records: list, subject_name: str, date_str: str, absent_records: list = None) -> str:
    """Generate professional PDF attendance report, including absent students if provided."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    if not records and not absent_records:
        return ""
        
    df = pd.DataFrame(records)
    
    df["Student Name"] = df.get("name", "N/A")
    df["Roll Number"] = df.get("roll_number", "N/A")
    df["Subject Name"] = df.get("subject_name", subject_name)
    df["Date"] = df.get("date", date_str)
    df["Time"] = df.get("time", "N/A")
    df["Status"] = "Present"
        
    df = df[["Student Name", "Roll Number", "Subject Name", "Date", "Time", "Status"]]
    
    safe_subject = "".join(c for c in subject_name if c.isalnum() or c in (' ', '_', '-')).strip()
    safe_subject = safe_subject.replace(' ', '_')
    if not safe_subject:
        safe_subject = "All_Subjects"
        
    filename = f"attendance_{safe_subject}_{date_str}.pdf"
    filepath = REPORTS_DIR / filename
    
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Attendance Report", ln=True, align="C")
    
    # Meta
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, txt=f"Subject: {subject_name}", ln=True)
    pdf.cell(200, 10, txt=f"Date: {date_str}", ln=True)
    pdf.ln(10)
    
    # Table Header
    pdf.set_font("Arial", 'B', 10)
    col_widths = [45, 30, 45, 25, 25, 20]
    headers = ["Student Name", "Roll Number", "Subject Name", "Date", "Time", "Status"]
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, str(header), border=1, align='C')
    pdf.ln()
    
    # Table Rows
    pdf.set_font("Arial", '', 10)
    for _, row in df.iterrows():
        for i, item in enumerate(row):
            encoded_item = str(item).encode('latin-1', 'ignore').decode('latin-1')
            pdf.cell(col_widths[i], 10, encoded_item, border=1)
        pdf.ln()

    if absent_records:
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt="Absent Students", ln=True)
        
        absent_df = pd.DataFrame(absent_records)
        absent_df["Student Name"] = absent_df.get("name", "N/A")
        absent_df["Roll Number"] = absent_df.get("roll_number", "N/A")
        absent_df["Subject Name"] = absent_df.get("subject_name", subject_name)
        absent_df["Date"] = absent_df.get("date", date_str)
        absent_df["Time"] = absent_df.get("time", "--:--")
        absent_df["Status"] = "Absent"
        absent_df = absent_df[["Student Name", "Roll Number", "Subject Name", "Date", "Time", "Status"]]
        
        # Table Header
        pdf.set_font("Arial", 'B', 10)
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, str(header), border=1, align='C')
        pdf.ln()
        
        # Table Rows
        pdf.set_font("Arial", '', 10)
        for _, row in absent_df.iterrows():
            for i, item in enumerate(row):
                encoded_item = str(item).encode('latin-1', 'ignore').decode('latin-1')
                pdf.cell(col_widths[i], 10, encoded_item, border=1)
            pdf.ln()
        
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Summary", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, txt=f"Total Students Present: {len(df)}", ln=True)
    if absent_records:
        pdf.cell(200, 10, txt=f"Total Students Absent: {len(absent_records)}", ln=True)
    
    pdf.output(str(filepath))
    print(f"✅ PDF Report generated: {filepath}")
    return str(filepath)


def generate_session_report(session_id: str, subject_name: str) -> str:
    """
    Generate a CSV report for a specific session.
    
    Args:
        session_id: The ID of the session
        subject_name: The name of the subject
        
    Returns:
        The path to the generated CSV file
    """
    # Ensure directory exists
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Fetch data
    records = get_attendance_by_session_id(session_id)
    
    if not records:
        print(f"⚠️  No attendance records found for session {session_id}")
        return ""
    
    # Convert to DataFrame
    df = pd.DataFrame(records)
    
    # Required columns: student_id, name, subject, confidence, timestamp
    # Ensure we map or extract them
    if "subject_name" in df.columns:
        df.rename(columns={"subject_name": "subject"}, inplace=True)
    else:
        df["subject"] = subject_name
        
    # Standardize columns to match requirements
    required_cols = ["student_id", "name", "subject", "confidence", "timestamp"]
    for col in required_cols:
        if col not in df.columns:
            df[col] = "N/A"
            
    df = df[required_cols]
    
    # Generate filename: attendance_<subject>_<date>.csv
    # Note: Using current date for report generation date
    date_str = datetime.now().strftime("%Y-%m-%d")
    # Sanitize subject name for filename
    safe_subject = "".join(c for c in subject_name if c.isalnum() or c in (' ', '_', '-')).strip()
    safe_subject = safe_subject.replace(' ', '_')
    
    filename = f"attendance_{safe_subject}_{date_str}.csv"
    filepath = REPORTS_DIR / filename
    
    # Write to CSV
    df.to_csv(filepath, index=False)
    
    print(f"✅ Report generated: {filepath}")
    return str(filepath)
