import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from config import settings
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        
    def send_email(self, to_email: str, subject: str, body: str, is_html: bool = False) -> bool:
        """Send email notification."""
        if not all([self.smtp_server, self.smtp_username, self.smtp_password]):
            logger.warning("Email configuration not complete, skipping email notification")
            return False
            
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.smtp_username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_request_submitted_notification(self, client_email: str, request_id: int, data_type: str) -> bool:
        """Send notification when request is submitted."""
        subject = "Data Request Submitted Successfully"
        body = f"""
        Your synthetic data generation request has been submitted successfully.
        
        Request Details:
        - Request ID: #{request_id}
        - Data Type: {data_type}
        - Status: Pending
        
        You will be notified when your request is processed and ready for download.
        
        Thank you for using our service!
        """
        
        return self.send_email(client_email, subject, body)
    
    def send_request_processing_notification(self, client_email: str, request_id: int) -> bool:
        """Send notification when request processing starts."""
        subject = "Data Request Processing Started"
        body = f"""
        Your synthetic data generation request is now being processed.
        
        Request ID: #{request_id}
        Status: Processing
        
        You will be notified once the data generation is complete.
        """
        
        return self.send_email(client_email, subject, body)
    
    def send_request_completed_notification(self, client_email: str, request_id: int, download_url: str) -> bool:
        """Send notification when request is completed."""
        subject = "Data Request Completed - Ready for Download"
        body = f"""
        Your synthetic data generation request has been completed successfully!
        
        Request ID: #{request_id}
        Status: Completed
        
        You can now download your generated dataset using the following link:
        {download_url}
        
        Note: This download link will expire in 1 hour for security reasons.
        
        Thank you for using our service!
        """
        
        return self.send_email(client_email, subject, body)
    
    def send_request_failed_notification(self, client_email: str, request_id: int, error_message: str) -> bool:
        """Send notification when request fails."""
        subject = "Data Request Failed"
        body = f"""
        Unfortunately, your synthetic data generation request has failed.
        
        Request ID: #{request_id}
        Status: Failed
        Error: {error_message}
        
        Please try submitting a new request or contact support if the issue persists.
        
        We apologize for the inconvenience.
        """
        
        return self.send_email(client_email, subject, body)
    
    def send_admin_notification(self, admin_email: str, message: str) -> bool:
        """Send notification to admin."""
        subject = "Synthetic Data Service - Admin Notification"
        body = f"""
        {message}
        
        Please check the admin panel for more details.
        """
        
        return self.send_email(admin_email, subject, body)

# Global notification service instance
notification_service = NotificationService()
