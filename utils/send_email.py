import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
import traceback
load_dotenv()

GM_EMAIL = os.getenv("gm_sender_email")
GM_PW = os.getenv("gm_sender_pw")

def send_email_to_address(receiver_email, user, analysis_result):
    # Gmail SMTP server credentials
    sender_email = GM_EMAIL
    sender_password = GM_PW
    
    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = "GMA - 您上傳的影片已經分析完畢"
    
    # 建構 HTML, 記得換成HTTPS
    html_body = f"""
    <html>
    <body>
        <p>Hi, {user}：</p>
        <p>這是來自Game Map Analyzer的訊息。</p>
        <p>您上傳的影片已經分析完畢，結果為： {analysis_result} 。</p>
        <p>您可點選<a href='https://traces.fun'>此連結</a>，進入會員中心，以下載相關分析結果。</p>
        <p>祝您有個美好的一天！</p>
        <p>Game Map Analyzer(GMA)</p>
    </body>
    </html>
    """

    message.attach(MIMEText(html_body, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Secure the connection
        server.login(sender_email, sender_password)
        
        text = message.as_string()
        server.sendmail(sender_email, receiver_email, text)
        
        server.quit()
        print("Email sent successfully!")

    except Exception as e:
        traceback.print_exc()
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    # test script
    send_email_to_address("brian3961@gmail.com", "Red ㄎㄎ Hong", "分析成功")
