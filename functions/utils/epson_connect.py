import os
import epson_connect

class EpsonConnectUtility:
    def __init__(self, printer_email, client_id, client_secret):
        """Initialize Epson Connect client with provided credentials or environment variables."""
        self.printer_email = printer_email
        self.client_id = client_id
        self.client_secret = client_secret
        
        if not all([self.printer_email, self.client_id, self.client_secret]):
            raise ValueError("Missing Epson Connect API credentials. Provide email, client ID, and client secret.")

        self.client = epson_connect.Client(
            printer_email=self.printer_email,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

    def print_pdf(self, file_path: str) -> str:
        """Print a PDF file and return the job ID."""
        if not file_path.endswith(".pdf"):
            raise ValueError("Only PDF files are supported.")
        
        try:
            job_id = self.client.printer.print(file_path)
            print(f"Print job successfully created with job ID: {job_id}")
            return job_id
        except Exception as e:
            print(f"Failed to create print job: {e}")
            raise e
