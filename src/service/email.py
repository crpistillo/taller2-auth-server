import logging
from src.constants import messages
from src.model.user_token import UserToken
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTPHeloError, SMTPException, SMTPRecipientsRefused, \
    SMTPSenderRefused, SMTPDataError, SMTPAuthenticationError


class EmailService:
    """
    Model entity for sending an email
    """
    logger = logging.getLogger(__name__)
    local_email = "chotuve.noreply@gmail.com"
    local_password = "TallerII_7552"

    def __init__(self):
        pass

    @classmethod
    def send_email(self, email: str, user_token: UserToken) -> str:
        """
        :param email: The email of the user who receives the message
        :param user_token: The token to be sent
        :return: A message indicating a SUCCESS or an ERROR
        """
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587, None, 30)
            server.ehlo()
            server.starttls()
            server.login(user=self.local_email, password=self.local_password)

            msg = MIMEMultipart()
            msg['From'] = self.local_email
            msg['To'] = email
            msg['Subject'] = "Chotuve " + user_token.get_type() + " Token"

            msg.attach(MIMEText("Token: " + user_token.get_token(), 'plain')) #arreglar para que quede mas lindo
            server.send_message(msg)
            del msg
            server.quit()

        except SMTPHeloError:
            self.logger().error(messages.TOKEN_EMAIL_ERROR_MESSAGE + messages.SMTP_HELO_ERROR_MESSAGE)
            return messages.TOKEN_EMAIL_ERROR_MESSAGE
        except SMTPException:
            self.logger().error(messages.TOKEN_EMAIL_ERROR_MESSAGE + messages.SMTP_EXCEPTION_MESSAGE)
            return messages.TOKEN_EMAIL_ERROR_MESSAGE
        except RuntimeError:
            self.logger().error(messages.TOKEN_EMAIL_ERROR_MESSAGE + messages.SMTP_RUNTIME_ERROR_MESSAGE)
            return messages.TOKEN_EMAIL_ERROR_MESSAGE
        except SMTPRecipientsRefused:
            self.logger().error(messages.TOKEN_EMAIL_ERROR_MESSAGE + messages.SMTP_RECIPIENTS_REFUSED_MESSAGE)
            return messages.TOKEN_EMAIL_ERROR_MESSAGE
        except SMTPSenderRefused:
            self.logger().error(messages.TOKEN_EMAIL_ERROR_MESSAGE + messages.SMTP_SENDER_REFUSED_MESSAGE)
            return messages.TOKEN_EMAIL_ERROR_MESSAGE
        except SMTPDataError:
            self.logger().error(messages.TOKEN_EMAIL_ERROR_MESSAGE + messages.SMTP_DATA_ERROR_MESSAGE)
            return messages.TOKEN_EMAIL_ERROR_MESSAGE
        except SMTPAuthenticationError:
            self.logger().error(messages.TOKEN_EMAIL_ERROR_MESSAGE + messages.SMTP_AUTHENTICATION_ERROR_MESSAGE)
            return messages.TOKEN_EMAIL_ERROR_MESSAGE
        return messages.TOKEN_SENT_MESSAGE % email











