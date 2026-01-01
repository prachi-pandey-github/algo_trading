import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict

class GoogleSheetsLogger:
    def __init__(self, creds_json_path: str, spreadsheet_name: str):
        print(f"Initializing Google Sheets logger with spreadsheet: {spreadsheet_name}")
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        try:
            self.creds = Credentials.from_service_account_file(creds_json_path, scopes=scopes)
            self.client = gspread.authorize(self.creds)
            print("Successfully authorized with Google Sheets API")
            try:
                self.spreadsheet = self.client.open(spreadsheet_name)
                print(f"Successfully opened spreadsheet: {spreadsheet_name}")
            except gspread.exceptions.SpreadsheetNotFound:
                print(f"Creating new spreadsheet: {spreadsheet_name}")
                self.spreadsheet = self.client.create(spreadsheet_name)
                print(f"Created new spreadsheet with ID: {self.spreadsheet.id}")
                print("Please share this spreadsheet with your Google account to view it")
        except Exception as e:
            print(f"Error initializing Google Sheets logger: {str(e)}")
            raise  # Re-raise the exception to handle it in the main script

    def log_trade(self, trade_data: List):
        try:
            print(f"Logging trade data: {trade_data}")
            sheet = self._get_or_create_sheet('Trade Log', ['Timestamp', 'Symbol', 'Action', 'Price', 'Quantity', 'P&L'])
            # Convert any datetime objects to strings
            formatted_data = [str(item) if hasattr(item, 'strftime') else item for item in trade_data]
            sheet.append_row(formatted_data)
            print("Successfully logged trade data")
        except Exception as e:
            print(f"Error logging trade data: {str(e)}")

    def log_summary(self, summary_data: List):
        sheet = self._get_or_create_sheet('Summary P&L', ['Date', 'Total P&L'])
        # Convert any datetime objects to strings
        formatted_data = [str(item) if hasattr(item, 'strftime') else item for item in summary_data]
        sheet.append_row(formatted_data)

    def log_win_ratio(self, win_ratio_data: List):
        sheet = self._get_or_create_sheet('Win Ratio', ['Date', 'Win Ratio'])
        # Convert any datetime objects to strings
        formatted_data = [str(item) if hasattr(item, 'strftime') else item for item in win_ratio_data]
        sheet.append_row(formatted_data)

    def share_spreadsheet(self, email: str):
        """Share the spreadsheet with a user email."""
        try:
            self.spreadsheet.share(email, perm_type='user', role='writer')
            print(f"Shared spreadsheet with: {email}")
        except Exception as e:
            print(f"Error sharing spreadsheet: {str(e)}")

    def _get_or_create_sheet(self, title: str, header: List[str]):
        """Get an existing worksheet or create a new one."""
        try:
            print(f"Attempting to get/create sheet: {title}")
            try:
                sheet = self.spreadsheet.worksheet(title)
                print(f"Found existing sheet: {title}")
            except gspread.exceptions.WorksheetNotFound:
                print(f"Sheet {title} not found, creating new one")
                sheet = self.spreadsheet.add_worksheet(title=title, rows="1000", cols=str(len(header)))
                print(f"Created new sheet: {title}")
                sheet.append_row(header)
                print(f"Added headers: {header}")
            return sheet
        except Exception as e:
            print(f"Error in _get_or_create_sheet: {str(e)}")
            raise
