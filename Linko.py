import http.server
import json
import os
import random
import smtplib
import socket
import socketserver
import threading
import time
import webbrowser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ========================================================
# إعدادات حساب المُرسِل SMTP
# ========================================================
FROM_EMAIL = os.environ.get("LINKO_SMTP_EMAIL", "linkosudan@gmail.com")
APP_PASSWORDS = [
    "utdctvaxdexlbhsa"
]

ACTIVE_EMAIL_OTPS = {}
OTP_EXPIRY_SECONDS = 300

def send_verification_email_task(to_email, code):
    """إرسال البريد الإلكتروني في الخلفية مع طباعة فورية في الترمينال"""
    print("\n" + "="*50)
    print(f"🔑 [رمز التحقق Linko OTP]: >>> {code} <<<")
    print(f"📧 المُرسِل: {FROM_EMAIL} | المُستلِم: {to_email}")
    print("="*50 + "\n")

    password = APP_PASSWORDS[0]
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"رمز التحقق الخاص بك في Linko: {code}"
        msg["From"] = f"Linko Security <{FROM_EMAIL}>"
        msg["To"] = to_email

        html_body = f"""
        <div style="direction: rtl; text-align: right; font-family: 'Cairo', Tahoma, Arial, sans-serif; background-color: #0b1014; color: #ffffff; padding: 30px; border-radius: 16px; max-width: 500px; margin: 0 auto; border: 1px solid #202c33;">
            <div style="text-align: center; margin-bottom: 20px;">
                <h1 style="color: #00A884; margin: 0; font-size: 32px;">Linko</h1>
                <p style="color: #8696a0; font-size: 14px; margin-top: 5px;">تأكيد الدخول الآمن</p>
            </div>
            <div style="background-color: #111b21; border-radius: 12px; padding: 20px; border: 1px solid #2a3942; text-align: center;">
                <p style="font-size: 15px; color: #e9edef; margin-bottom: 15px;">رمز التحقق الخاص بحسابك هو:</p>
                <div style="font-size: 36px; font-weight: 800; letter-spacing: 8px; color: #00A884; margin: 15px 0; background: #1f2c34; padding: 12px; border-radius: 8px; display: inline-block;">
                    {code}
                </div>
                <p style="font-size: 13px; color: #8696a0; margin-top: 15px;">الرمز صالح للاستخدام لمدة 5 دقائق فقط.</p>
            </div>
            <p style="text-align: center; font-size: 12px; color: #536471; margin-top: 25px;">&copy; 2026 Linko Messenger. جميع الحقوق محفوظة.</p>
        </div>
        """
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10)
        server.login(FROM_EMAIL, password)
        server.sendmail(FROM_EMAIL, to_email, msg.as_string())
        server.quit()
        print("✅ تم تسليم الإيميل بنجاح إلى بريد Google!")
    except Exception as e:
        print(f"[ملاحظة إرسال SMTP]: {e}")

HTML_CONTENT = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
  <title>Linko</title>
  
  <!-- Fonts & Icons -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  
  <!-- Tone.js for Audio Chimes & Ringtones -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/tone/14.8.49/Tone.js"></script>

  <style>
    :root {
      --primary-color: #00A884;
      --primary-dark: #008f6f;
      --accent-blue: #34b7f1;
      --bg-dark: #0b1014;
      --container-bg: #111b21;
      --card-bg: #1f2c34;
      --search-bg: #1f2c34;
      --text-main: #e9edef;
      --text-muted: #8696a0;
      --border-color: #222d34;
      --danger-color: #ea4335;
      --bubble-me: #005c4b;
      --bubble-other: #202c33;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: 'Cairo', sans-serif;
      -webkit-tap-highlight-color: transparent;
      user-select: none;
    }

    html, body {
      width: 100%;
      height: 100%;
      height: 100dvh;
      overflow: hidden;
      background-color: var(--bg-dark);
      color: var(--text-main);
    }

    body {
      display: flex;
      justify-content: center;
      align-items: stretch;
    }

    #app {
      width: 100%;
      max-width: 500px;
      height: 100%;
      height: 100dvh;
      background: var(--container-bg);
      position: relative;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      box-shadow: 0 0 25px rgba(0, 0, 0, 0.9);
    }

    button {
      cursor: pointer;
      border: none;
      outline: none;
      background: transparent;
      color: inherit;
    }

    .avatar-wrapper {
      position: relative;
      width: 44px;
      height: 44px;
      flex-shrink: 0;
    }

    .avatar {
      width: 100%;
      height: 100%;
      border-radius: 50%;
      object-fit: cover;
      background: #000;
      cursor: pointer;
    }

    .status-dot {
      position: absolute;
      bottom: 1px;
      left: 1px;
      width: 10px;
      height: 10px;
      border-radius: 50%;
      border: 2px solid var(--container-bg);
    }
    .status-online { background-color: var(--primary-color); }
    .status-offline { background-color: #8696a0; }

    /* Top Bar Header */
    .top-header {
      padding: max(8px, env(safe-area-inset-top)) 16px 8px 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      height: 52px;
      background: var(--container-bg);
      border-bottom: 1px solid rgba(255, 255, 255, 0.04);
      flex-shrink: 0;
    }
    .brand-title {
      font-size: 21px;
      font-weight: 700;
      color: #fff;
    }
    .top-actions { display: flex; align-items: center; gap: 14px; font-size: 17px; color: var(--text-muted); }

    /* Search Bar */
    .search-section { padding: 8px 16px; background: var(--container-bg); flex-shrink: 0; }
    .search-box-wrapper {
      background: var(--search-bg);
      border-radius: 22px;
      display: flex;
      align-items: center;
      padding: 5px 14px;
      gap: 10px;
    }
    .search-box-wrapper i { color: var(--text-muted); font-size: 14px; }
    .search-box-wrapper input {
      flex: 1;
      background: transparent;
      border: none;
      outline: none;
      color: var(--text-main);
      font-size: 13px;
    }

    /* Views Tabs */
    .tab-content { flex: 1; overflow-y: auto; display: none; flex-direction: column; -webkit-overflow-scrolling: touch; }
    .tab-content.active { display: flex; }

    .chat-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 10px 16px;
      cursor: pointer;
      border-bottom: 1px solid rgba(255, 255, 255, 0.03);
      transition: background 0.1s;
    }
    .chat-item:active { background: rgba(255, 255, 255, 0.05); }
    .chat-item-info { flex: 1; min-width: 0; }
    .chat-item-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px; }
    .chat-item-name { font-weight: 600; font-size: 15px; color: #fff; display: flex; align-items: center; gap: 6px; }
    .chat-item-time { font-size: 11px; color: var(--text-muted); direction: ltr; }
    .chat-item-msg { font-size: 12.5px; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

    /* FAB (+) */
    .fab-btn {
      position: absolute;
      bottom: 62px;
      left: 18px;
      width: 48px;
      height: 48px;
      border-radius: 50%;
      background: var(--primary-color);
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      box-shadow: 0 3px 12px rgba(0, 168, 132, 0.4);
      z-index: 10;
    }

    /* Bottom Navigation Bar */
    .bottom-nav {
      height: 52px;
      padding-bottom: max(3px, env(safe-area-inset-bottom));
      background: #0b141a;
      border-top: 1px solid rgba(255, 255, 255, 0.05);
      display: flex;
      align-items: center;
      justify-content: space-around;
      flex-shrink: 0;
      z-index: 15;
    }
    .nav-tab {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 1px;
      color: var(--text-muted);
      font-size: 10.5px;
      flex: 1;
      height: 100%;
      cursor: pointer;
    }
    .nav-tab-icon-wrap { padding: 2px 14px; border-radius: 12px; font-size: 16px; }
    .nav-tab.active { color: var(--primary-color); font-weight: 600; }
    .nav-tab.active .nav-tab-icon-wrap { background: rgba(0, 168, 132, 0.16); }

    /* FULL OVERLAY SCREENS */
    #chat-screen, #contact-profile-screen, #storage-screen, #edit-contact-screen {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      height: 100dvh;
      background: #0b1014;
      display: none;
      flex-direction: column;
      z-index: 60;
      overflow-y: auto;
    }
    #chat-screen.active, #contact-profile-screen.active, #storage-screen.active, #edit-contact-screen.active {
      display: flex;
    }

    /* CHAT SCREEN */
    .chat-header {
      padding: max(8px, env(safe-area-inset-top)) 12px 8px 12px;
      background: #111b21;
      display: flex;
      align-items: center;
      justify-content: space-between;
      height: 56px;
      border-bottom: 1px solid #202c33;
      flex-shrink: 0;
      z-index: 10;
    }
    .chat-header-right {
      display: flex;
      align-items: center;
      gap: 10px;
      flex: 1;
      min-width: 0;
      cursor: pointer;
    }
    .chat-header-actions {
      display: flex;
      align-items: center;
      gap: 18px;
      font-size: 17px;
      color: #aebac1;
    }

    #datablock-notice-banner {
      background: rgba(234, 67, 53, 0.15);
      color: var(--danger-color);
      font-size: 12px;
      font-weight: 600;
      text-align: center;
      padding: 6px;
      border-bottom: 1px solid rgba(234, 67, 53, 0.3);
      display: none;
    }

    .chat-messages {
      flex: 1;
      padding: 12px 14px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 10px;
      background: #0b1014;
      -webkit-overflow-scrolling: touch;
    }

    .msg-bubble {
      max-width: 86%;
      padding: 7px 12px;
      border-radius: 12px;
      font-size: 14.5px;
      line-height: 1.4;
      position: relative;
      word-wrap: break-word;
      animation: fadeIn 0.15s ease-in;
    }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }

    .msg-me { align-self: flex-start; background: var(--bubble-me); color: #fff; border-top-right-radius: 2px; }
    .msg-other { align-self: flex-end; background: var(--bubble-other); color: var(--text-main); border-top-left-radius: 2px; }
    
    .msg-time-row {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      gap: 4px;
      font-size: 10.5px;
      opacity: 0.85;
      margin-top: 3px;
      direction: ltr;
    }

    .msg-image {
      max-width: 100%;
      max-height: 240px;
      border-radius: 8px;
      margin-bottom: 4px;
      cursor: pointer;
    }

    .blocked-stream-pill {
      background: rgba(31, 44, 52, 0.95);
      border: 1px solid #2a3942;
      border-radius: 20px;
      padding: 8px 16px;
      color: var(--text-muted);
      font-size: 13px;
      text-align: center;
      margin: 12px auto;
      max-width: 85%;
      cursor: pointer;
      display: none;
    }
    .blocked-stream-pill.active { display: block; }
    .blocked-stream-pill:hover { color: #fff; }

    .blocked-bottom-actions-bar {
      height: 60px;
      padding: 0 16px max(6px, env(safe-area-inset-bottom)) 16px;
      background: #111b21;
      border-top: 1px solid #1f2c34;
      display: none;
      align-items: center;
      justify-content: space-between;
      flex-shrink: 0;
      z-index: 20;
    }
    .blocked-bottom-actions-bar.active { display: flex; }

    .btn-block-action {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 15px;
      font-weight: 700;
      cursor: pointer;
      padding: 8px 12px;
      border-radius: 8px;
    }
    .btn-unblock-green { color: var(--primary-color); }
    .btn-delete-red { color: var(--danger-color); }

    /* مشغل الصوتيات الاحترافي مطابق لواتساب بالكامل */
    .wa-voice-bubble {
      display: flex;
      align-items: center;
      gap: 10px;
      min-width: 250px;
      padding: 6px 4px 4px 4px;
      direction: rtl;
    }
    .wa-voice-avatar-box { position: relative; width: 44px; height: 44px; flex-shrink: 0; }
    .wa-voice-avatar { width: 100%; height: 100%; border-radius: 50%; object-fit: cover; background: #fff; }
    .wa-mic-badge { position: absolute; bottom: -2px; left: -2px; color: var(--accent-blue); font-size: 14px; }
    
    .wa-voice-middle { flex: 1; display: flex; flex-direction: column; gap: 4px; min-width: 0; }
    .wa-waveform-track {
      display: flex;
      align-items: center;
      gap: 2.2px;
      height: 22px;
      cursor: pointer;
      padding: 2px 0;
    }
    .wa-wave-bar {
      width: 2.8px;
      border-radius: 3px;
      background: #7a8b96;
      transition: background 0.15s ease, height 0.12s;
    }
    .wa-wave-bar.played {
      background: var(--accent-blue) !important;
    }

    .wa-voice-time-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 11px;
      color: var(--text-muted);
      direction: rtl;
    }

    .wa-play-ctrl-box {
      display: flex;
      align-items: center;
      gap: 6px;
      flex-shrink: 0;
    }

    .wa-play-btn {
      color: #8696a0;
      font-size: 26px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: transform 0.1s;
    }
    .wa-play-btn:active { transform: scale(0.9); }

    .wa-speed-btn {
      background: rgba(255, 255, 255, 0.1);
      color: #e9edef;
      border-radius: 12px;
      padding: 2px 7px;
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
      display: none;
      transition: background 0.15s;
    }
    .wa-speed-btn:hover { background: rgba(255, 255, 255, 0.2); }

    /* لوحة الرموز التعبيرية */
    .emoji-picker-container {
      display: none;
      background: #1f2c34;
      border: 1px solid #2a3942;
      border-radius: 20px;
      padding: 8px 14px;
      position: absolute;
      bottom: 64px;
      right: 14px;
      z-index: 55;
      gap: 10px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.65);
      flex-wrap: wrap;
      max-width: 300px;
      animation: fadeIn 0.15s ease-out;
    }
    .emoji-picker-container.active { display: flex; }
    .emoji-item { font-size: 22px; cursor: pointer; padding: 2px; transition: transform 0.12s; }
    .emoji-item:active { transform: scale(1.3); }

    /* شريط الإدخال الموحد */
    .chat-bottom-wrapper {
      padding: 6px 10px max(8px, env(safe-area-inset-bottom)) 10px;
      background: transparent;
      display: flex;
      align-items: center;
      flex-shrink: 0;
      position: relative;
      width: 100%;
    }
    .chat-bottom-wrapper.hidden { display: none; }

    .unified-input-capsule {
      flex: 1;
      background: #1f2c34;
      border-radius: 28px;
      display: flex;
      align-items: center;
      padding: 4px 6px 4px 10px;
      min-height: 48px;
      width: 100%;
      border: 1px solid rgba(255,255,255,0.04);
      box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }
    
    .chat-pill-icon {
      color: #8696a0;
      font-size: 19px;
      cursor: pointer;
      padding: 6px;
      transition: color 0.15s;
    }
    .chat-pill-icon:hover { color: #fff; }

    .unified-input-capsule input {
      flex: 1;
      background: transparent;
      border: none;
      outline: none;
      color: #fff;
      font-size: 15px;
      padding: 0 4px;
      min-width: 0;
    }

    .integrated-mic-send-btn {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: transparent;
      color: #8696a0;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
      flex-shrink: 0;
      cursor: pointer;
      border: none;
      transition: all 0.18s ease;
      touch-action: none;
    }
    .integrated-mic-send-btn.typing-mode { background: var(--primary-color); color: #ffffff; transform: scale(1.05); }
    .integrated-mic-send-btn.recording { background: var(--primary-color); color: #ffffff; transform: scale(1.1); }

    .vertical-lock-capsule {
      position: absolute; bottom: 58px; left: 14px; width: 38px; height: 64px;
      background: #1f2c34; border: 1px solid #2a3942; border-radius: 20px;
      display: none; flex-direction: column; align-items: center; justify-content: space-around;
      color: #8696a0; font-size: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.6); cursor: pointer; z-index: 40;
    }
    .vertical-lock-capsule.active { display: flex; }

    .swipe-cancel-bar { flex: 1; display: none; align-items: center; justify-content: space-between; padding: 0 8px; color: var(--text-muted); font-size: 13.5px; }
    .swipe-cancel-bar.active { display: flex; }

    .locked-recording-panel {
      position: absolute; bottom: 6px; left: 10px; right: 10px;
      background: #1f2c34; border: 1px solid #2a3942; border-radius: 22px;
      padding: 10px 14px; display: none; flex-direction: column; gap: 10px; z-index: 45;
      box-shadow: 0 8px 30px rgba(0,0,0,0.85);
    }
    .locked-recording-panel.active { display: flex; }

    .locked-top-row { display: flex; align-items: center; justify-content: space-between; padding: 0 4px; }
    .btn-view-once-pill { width: 28px; height: 28px; border-radius: 50%; border: 1.5px dashed var(--text-muted); color: var(--text-muted); font-size: 12px; font-weight: 700; display: flex; align-items: center; justify-content: center; cursor: pointer; }
    .btn-view-once-pill.active { border-style: solid; border-color: var(--primary-color); color: var(--primary-color); background: rgba(0, 168, 132, 0.15); }
    
    .locked-waveform-live { flex: 1; display: flex; align-items: center; justify-content: center; gap: 3px; height: 18px; margin: 0 14px; }
    .live-wave-bar { width: 2.8px; border-radius: 2px; background: #8696a0; height: 8px; animation: wavePulse 0.8s infinite ease-in-out; }
    @keyframes wavePulse { 0%, 100% { height: 6px; } 50% { height: 18px; } }
    .locked-timer-text { font-size: 13.5px; font-weight: 700; color: #fff; direction: ltr; }

    .locked-bottom-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
    .btn-locked-trash { width: 40px; height: 40px; border-radius: 50%; background: rgba(234, 67, 53, 0.15); color: var(--danger-color); display: flex; align-items: center; justify-content: center; font-size: 17px; cursor: pointer; }
    .btn-locked-pause-pill { flex: 1; height: 40px; border-radius: 20px; background: #111b21; border: 1px solid #2a3942; color: #fff; font-size: 13.5px; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 8px; cursor: pointer; }
    .btn-locked-send-white { width: 40px; height: 40px; border-radius: 50%; background: #fff; color: #111b21; display: flex; align-items: center; justify-content: center; font-size: 16px; cursor: pointer; }

    /* PROFILE SCREEN */
    .profile-top-bar {
      padding: max(8px, env(safe-area-inset-top)) 12px 8px 12px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      height: 56px;
      background: #0b1014;
      position: sticky;
      top: 0;
      z-index: 30;
      transition: background 0.22s ease, border-color 0.22s ease;
    }

    #profile-header-collapsed-info {
      position: absolute;
      left: 50%;
      top: 50%;
      transform: translate(-50%, -40%);
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.22s cubic-bezier(0.4, 0, 0.2, 1), transform 0.22s cubic-bezier(0.4, 0, 0.2, 1);
      max-width: 65%;
    }
    #profile-header-collapsed-info.visible { opacity: 1; transform: translate(-50%, -50%); pointer-events: auto; }

    .dropdown-menu {
      position: absolute;
      top: 45px;
      left: 6px;
      background: #1c272e;
      border: 1px solid #2a3942;
      border-radius: 12px;
      min-width: 130px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.85);
      display: none;
      flex-direction: column;
      padding: 6px 0;
      z-index: 120;
    }
    .dropdown-menu.active { display: flex; animation: fadeIn 0.15s ease-in; }
    .dropdown-item {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      gap: 12px;
      padding: 10px 16px;
      font-size: 15px;
      font-weight: 600;
      color: #e9edef;
      cursor: pointer;
      direction: rtl;
    }
    .dropdown-item:hover, .dropdown-item:active { background: rgba(255, 255, 255, 0.06); }
    .dropdown-item i { font-size: 14px; color: #8696a0; }

    .profile-hero { display: flex; flex-direction: column; align-items: center; padding: 14px 16px 20px 16px; text-align: center; background: #0b1014; }
    .profile-large-avatar {
      width: 120px;
      height: 120px;
      border-radius: 50%;
      background: #000;
      object-fit: cover;
      margin-bottom: 14px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.5);
      cursor: pointer;
      transition: transform 0.15s ease;
    }
    .profile-large-avatar:active { transform: scale(0.96); }

    .profile-user-title { font-size: 22px; font-weight: 700; color: #fff; margin-bottom: 4px; }
    .profile-user-id-sub { font-size: 13.5px; color: var(--text-muted); direction: ltr; margin-bottom: 18px; }

    .profile-action-row { display: flex; align-items: center; justify-content: center; gap: 12px; width: 100%; max-width: 380px; }
    .profile-btn-card { flex: 1; background: #111b21; border: 1px solid #1f2c34; border-radius: 14px; padding: 12px 6px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 6px; color: #e9edef; font-size: 13px; font-weight: 500; cursor: pointer; }
    .profile-btn-card:active { background: #1f2c34; }
    .profile-btn-card i { color: var(--primary-color); font-size: 17px; }

    .profile-section { background: #0b1014; margin-top: 10px; border-top: 1px solid #1f2c34; padding-bottom: 30px; }
    .profile-list-item { display: flex; align-items: center; justify-content: space-between; padding: 14px 18px; cursor: pointer; border-bottom: 1px solid rgba(255,255,255,0.02); }
    .profile-item-left { display: flex; align-items: center; gap: 16px; flex: 1; }
    .profile-item-icon { font-size: 20px; color: #8696a0; width: 26px; text-align: center; }
    .profile-item-texts { display: flex; flex-direction: column; gap: 2px; }
    .profile-item-title { font-size: 15px; color: #e9edef; font-weight: 500; }
    .profile-item-desc { font-size: 12px; color: var(--text-muted); line-height: 1.3; }

    .switch { position: relative; display: inline-block; width: 44px; height: 24px; flex-shrink: 0; }
    .switch input { opacity: 0; width: 0; height: 0; }
    .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #374248; transition: .25s; border-radius: 24px; }
    .slider:before { position: absolute; content: ""; height: 18px; width: 18px; left: 3px; bottom: 3px; background-color: #fff; transition: .25s; border-radius: 50%; }
    input:checked + .slider { background-color: var(--primary-color) !important; }
    input:checked + .slider:before { transform: translateX(20px); }

    .danger-item { color: var(--danger-color) !important; }
    .danger-item .profile-item-title, .danger-item .profile-item-icon { color: var(--danger-color) !important; }

    /* FULLSCREEN AVATAR VIEWER */
    #fullscreen-avatar-viewer {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      height: 100dvh;
      background: #000000;
      z-index: 2000;
      display: none;
      flex-direction: column;
      justify-content: space-between;
      animation: fadeIn 0.18s ease-in;
    }
    #fullscreen-avatar-viewer.active { display: flex; }

    .avatar-viewer-top-bar {
      padding: max(12px, env(safe-area-inset-top)) 16px 12px 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: rgba(0, 0, 0, 0.7);
      z-index: 10;
    }
    .avatar-viewer-right { display: flex; align-items: center; gap: 16px; flex: 1; }
    #avatar-viewer-back-btn { font-size: 20px; color: #ffffff; padding: 6px; cursor: pointer; }
    #avatar-viewer-name { font-size: 18px; font-weight: 700; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

    .avatar-viewer-image-container {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      width: 100%;
      background: #000;
    }
    #avatar-viewer-img { width: 100%; aspect-ratio: 1 / 1; object-fit: cover; background: #000; }

    /* EDIT CONTACT SCREEN */
    .edit-screen-top-nav {
      padding: max(12px, env(safe-area-inset-top)) 0 16px 0;
      display: flex;
      align-items: center;
      justify-content: space-between;
      height: 60px;
      background: #0b1014;
      position: sticky;
      top: 0;
      z-index: 10;
      margin-bottom: 24px;
    }
    .edit-screen-right-title { display: flex; align-items: center; gap: 16px; }
    .edit-screen-heading { font-size: 20px; font-weight: 700; color: #fff; }

    .edit-fields-container { display: flex; flex-direction: column; gap: 24px; margin-bottom: 30px; }

    .notched-input-group {
      position: relative;
      border: 1.5px solid #222e35;
      border-radius: 16px;
      padding: 14px 18px;
      display: flex;
      align-items: center;
      background: transparent;
      transition: border-color 0.2s ease;
    }
    .notched-input-group:focus-within { border-color: var(--primary-color); }
    .notched-floating-label {
      position: absolute;
      top: -11px;
      right: 20px;
      background: #0b1014;
      padding: 0 8px;
      font-size: 13px;
      color: #8696a0;
      font-weight: 600;
      pointer-events: none;
    }
    .notched-input-group input {
      flex: 1;
      background: transparent;
      border: none;
      outline: none;
      color: #fff;
      font-size: 16px;
      font-weight: 500;
      direction: rtl;
    }
    .notched-input-group input::placeholder { color: #536471; }
    .notched-left-icon { font-size: 20px; color: #29b6f6; margin-right: 12px; display: flex; align-items: center; justify-content: center; }
    .notched-left-symbol { font-size: 20px; color: #8696a0; font-weight: 700; margin-right: 12px; display: flex; align-items: center; justify-content: center; }

    .btn-save-contact-pill {
      background: #1c272e;
      color: var(--primary-color);
      border: 1px solid rgba(255, 255, 255, 0.04);
      font-weight: 700;
      font-size: 16.5px;
      padding: 15px;
      border-radius: 28px;
      width: 100%;
      text-align: center;
      cursor: pointer;
      margin-top: auto;
      margin-bottom: max(16px, env(safe-area-inset-bottom));
      box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
      transition: background 0.15s ease, transform 0.1s;
    }
    .btn-save-contact-pill:active { background: #24323b; transform: scale(0.98); }

    /* STORAGE SCREEN */
    .storage-header {
      padding: max(10px, env(safe-area-inset-top)) 16px 12px 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      height: 56px;
      background: #111b21;
      border-bottom: 1px solid #1f2c34;
      position: sticky;
      top: 0;
      z-index: 10;
    }

    .gallery-studio-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 4px; padding: 6px; }

    .gallery-studio-thumb {
      width: 100%;
      aspect-ratio: 1 / 1;
      object-fit: cover;
      background: #1f2c34;
      border-radius: 4px;
      cursor: pointer;
      transition: transform 0.1s;
    }
    .gallery-studio-thumb:active { transform: scale(0.96); }

    /* REAL INTERACTIVE CALL SCREEN */
    #call-screen {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      height: 100dvh;
      background: #0b141a;
      z-index: 3000;
      display: none;
      flex-direction: column;
      justify-content: space-between;
      overflow: hidden;
    }
    #call-screen.active { display: flex; }

    .call-doodle-bg {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-color: #0b141a;
      background-image: radial-gradient(#182229 1px, transparent 1px);
      background-size: 20px 20px;
      opacity: 0.6;
      pointer-events: none;
    }

    .call-video-main {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: none;
      z-index: 1;
      background: #000;
    }
    .call-video-pip {
      position: absolute;
      top: max(20px, env(safe-area-inset-top));
      left: 16px;
      width: 105px;
      height: 155px;
      border-radius: 16px;
      object-fit: cover;
      border: 2px solid rgba(255,255,255,0.3);
      z-index: 25;
      background: #000;
      display: none;
      box-shadow: 0 8px 24px rgba(0,0,0,0.7);
      cursor: pointer;
      transition: transform 0.15s ease;
    }
    .call-video-pip:active { transform: scale(0.96); }

    .call-top-header {
      padding: max(16px, env(safe-area-inset-top)) 18px 12px 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      width: 100%;
      z-index: 10;
      position: relative;
    }
    .btn-call-round-icon {
      width: 44px;
      height: 44px;
      border-radius: 50%;
      background: rgba(32, 44, 51, 0.7);
      backdrop-filter: blur(8px);
      color: #fff;
      font-size: 18px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
    }
    .call-user-center-info {
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      flex: 1;
    }
    .call-title-name { font-size: 22px; font-weight: 700; color: #fff; text-shadow: 0 2px 8px rgba(0,0,0,0.8); }
    .call-state-text { font-size: 14px; color: #9aa9b5; margin-top: 2px; font-weight: 500; text-shadow: 0 1px 4px rgba(0,0,0,0.8); }

    .call-audio-avatar-container {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 5;
      position: relative;
    }
    .call-audio-huge-avatar {
      width: 190px;
      height: 190px;
      border-radius: 50%;
      object-fit: cover;
      background: #111b21;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.7);
      border: 3px solid rgba(255,255,255,0.06);
    }

    .call-video-left-actions {
      position: absolute;
      top: max(80px, env(safe-area-inset-top));
      right: 18px;
      display: none;
      flex-direction: column;
      gap: 14px;
      z-index: 20;
    }
    .call-video-left-actions.active { display: flex; }

    .call-slim-floating-action-bar {
      position: absolute;
      bottom: max(22px, env(safe-area-inset-bottom));
      left: 50%;
      transform: translateX(-50%);
      background: rgba(17, 27, 33, 0.88);
      backdrop-filter: blur(14px);
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 36px;
      padding: 6px 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 14px;
      z-index: 30;
      box-shadow: 0 8px 30px rgba(0,0,0,0.85);
    }

    .call-ctrl-btn {
      width: 48px;
      height: 48px;
      border-radius: 50%;
      background: #202c33;
      color: #e9edef;
      font-size: 18px;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.15s ease;
      cursor: pointer;
    }
    .call-ctrl-btn:active { transform: scale(0.92); }
    .call-ctrl-btn.active-white { background: #ffffff !important; color: #111b21 !important; }
    .call-ctrl-btn.btn-hangup-red {
      background: var(--danger-color) !important;
      color: #ffffff !important;
      width: 52px;
      height: 52px;
      font-size: 20px;
    }

    /* نافذة استلام المكالمة الواردة */
    #incoming-call-dialog {
      position: fixed;
      top: max(16px, env(safe-area-inset-top));
      left: 12px;
      right: 12px;
      max-width: 480px;
      margin: 0 auto;
      background: #1f2c34;
      border: 1px solid #2a3942;
      border-radius: 20px;
      padding: 16px 18px;
      display: none;
      align-items: center;
      justify-content: space-between;
      z-index: 4000;
      box-shadow: 0 12px 35px rgba(0,0,0,0.9);
      animation: slideDown 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }
    #incoming-call-dialog.active { display: flex; }
    @keyframes slideDown { from { transform: translateY(-100%); opacity: 0; } to { transform: translateY(0); } }

    .inc-call-avatar { width: 52px; height: 52px; border-radius: 50%; object-fit: cover; background: #111b21; }
    .btn-inc-accept {
      width: 48px; height: 48px; border-radius: 50%;
      background: var(--primary-color); color: #fff; font-size: 19px;
      display: flex; align-items: center; justify-content: center; cursor: pointer;
      box-shadow: 0 4px 15px rgba(0, 168, 132, 0.4);
    }
    .btn-inc-decline {
      width: 48px; height: 48px; border-radius: 50%;
      background: var(--danger-color); color: #fff; font-size: 19px;
      display: flex; align-items: center; justify-content: center; cursor: pointer;
    }

    /* Modals & Dialogs */
    .datablock-custom-icon-box { width: 80px; height: 56px; margin: 0 auto 16px auto; display: flex; align-items: center; justify-content: center; }

    #modal-clear-chat-wa {
      position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; height: 100dvh;
      background: rgba(0, 0, 0, 0.7); z-index: 280; display: none;
      align-items: flex-end; justify-content: center;
    }
    #modal-clear-chat-wa.active { display: flex; }

    .clear-sheet-card {
      background: #111b21; width: 100%; max-width: 500px;
      border-radius: 24px 24px 0 0; padding: 16px 20px max(20px, env(safe-area-inset-bottom)) 20px;
      border-top: 1px solid #2a3942; box-shadow: 0 -10px 40px rgba(0,0,0,0.9);
      animation: sheetUp 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }
    @keyframes sheetUp { from { transform: translateY(100%); } to { transform: translateY(0); } }

    .clear-sheet-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
    .clear-sheet-title { font-size: 18px; font-weight: 700; color: #fff; }
    .clear-sheet-desc { font-size: 14px; color: #e9edef; line-height: 1.5; margin-bottom: 18px; text-align: right; }
    .clear-checkbox-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 22px; cursor: pointer; }
    .btn-clear-red-pill {
      background: #1f2c34; border: 1px solid rgba(255,255,255,0.04);
      color: var(--danger-color); font-size: 16px; font-weight: 700;
      padding: 13px; border-radius: 28px; width: 100%; text-align: center; cursor: pointer;
    }

    #modal-report-wa, #modal-block-wa, #chatlock-intro-modal, #chatlock-method-modal, #notif-terms-modal, #datablock-terms-modal, #custom-pin-setup-modal, #fullscreen-pin-lock-view, #add-friend-modal, #edit-profile-modal {
      position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; height: 100dvh;
      z-index: 220; display: none; align-items: center; justify-content: center; padding: 20px;
    }
    #modal-report-wa, #modal-block-wa, #chatlock-intro-modal, #chatlock-method-modal, #notif-terms-modal, #datablock-terms-modal, #add-friend-modal, #edit-profile-modal { background: rgba(0, 0, 0, 0.82); }
    #custom-pin-setup-modal { background: rgba(0,0,0,0.85); z-index: 520; }
    #fullscreen-pin-lock-view { background: #ffffff; z-index: 500; flex-direction: column; justify-content: space-between; padding: max(40px, env(safe-area-inset-top)) 24px max(30px, env(safe-area-inset-bottom)) 24px; color: #1c2a38; animation: fadeIn 0.18s ease-in-out; }

    #modal-report-wa.active, #modal-block-wa.active, #chatlock-intro-modal.active, #chatlock-method-modal.active, #notif-terms-modal.active, #datablock-terms-modal.active, #custom-pin-setup-modal.active, #fullscreen-pin-lock-view.active, #add-friend-modal.active, #edit-profile-modal.active { display: flex; }

    .intro-modal-card, .method-modal-card, .notif-modal-card, .wa-dialog-card, .pin-setup-card {
      background: #1f2c34; border: 1px solid #2a3942; width: 100%;
      max-width: 380px; border-radius: 22px; padding: 24px 20px; text-align: center;
      box-shadow: 0 10px 35px rgba(0,0,0,0.85); animation: fadeIn 0.2s ease-in;
    }
    .method-option-card {
      background: #111b21; border: 1px solid #2a3942; border-radius: 14px;
      padding: 14px; margin-bottom: 12px; cursor: pointer; display: flex; align-items: center; gap: 12px; text-align: right;
    }
    .btn-notif-confirm { flex: 1; background: var(--primary-color); color: #fff; padding: 11px; border-radius: 12px; font-weight: 700; font-size: 14.5px; }
    .btn-notif-cancel { flex: 1; background: #111b21; color: var(--text-muted); border: 1px solid #2a3942; padding: 11px; border-radius: 12px; font-weight: 600; font-size: 14.5px; }

    .white-lock-header-row { width: 100%; display: flex; justify-content: flex-end; padding: 0 6px; }
    .btn-close-white-lock { font-size: 22px; color: #8c9ba5; padding: 6px; cursor: pointer; }
    .white-lock-title-section { display: flex; flex-direction: column; align-items: center; gap: 16px; margin-top: 10px; }
    .white-lock-title { font-size: 22px; font-weight: 700; color: #9aa9b5; letter-spacing: -0.3px; }
    .white-lock-pin-dots { display: flex; align-items: center; justify-content: center; gap: 18px; height: 24px; }
    .white-pin-dot { width: 14px; height: 14px; border-radius: 50%; border: 2px solid #cbd4db; background: transparent; transition: all 0.15s ease; }
    .white-pin-dot.filled { background: #1c2a38; border-color: #1c2a38; transform: scale(1.1); }
    .white-lock-keypad-grid { display: grid; grid-template-columns: repeat(3, 1fr); width: 100%; max-width: 320px; row-gap: 28px; column-gap: 20px; margin-bottom: 20px; }
    .white-key-digit { display: flex; align-items: center; justify-content: center; height: 72px; font-size: 40px; font-weight: 700; color: #1c2a38; cursor: pointer; transition: transform 0.1s, opacity 0.1s; border-radius: 50%; }
    .white-key-digit:active { opacity: 0.5; transform: scale(0.92); }
    .white-key-icon-btn { display: flex; align-items: center; justify-content: center; height: 72px; cursor: pointer; position: relative; }
    .white-key-icon-btn:active { opacity: 0.5; transform: scale(0.92); }
    .white-fingerprint-icon { font-size: 32px; color: #1c2a38; position: relative; }
    .white-fingerprint-badge-dot { position: absolute; top: -3px; right: -3px; width: 8px; height: 8px; background-color: #ff3b30; border-radius: 50%; border: 1.5px solid #fff; }
    .white-backspace-icon { font-size: 28px; color: #1c2a38; }

    /* شاشة التحميل الثلاثية النقاط الصافية تماماً بدون كلام */
    #three-dots-global-overlay {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      height: 100dvh;
      background: rgba(0, 0, 0, 0.94);
      backdrop-filter: blur(18px);
      z-index: 30000;
      display: none;
      align-items: center;
      justify-content: center;
    }
    #three-dots-global-overlay.active { display: flex; animation: fadeIn 0.15s ease-in; }
    .dots-running-container {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
    }
    .running-dot {
      width: 17px;
      height: 17px;
      background-color: var(--primary-color);
      border-radius: 50%;
      box-shadow: 0 0 16px rgba(0, 168, 132, 0.85);
      animation: dotsBounce 1.2s infinite ease-in-out both;
    }
    .running-dot:nth-child(1) { animation-delay: -0.32s; }
    .running-dot:nth-child(2) { animation-delay: -0.16s; }
    .running-dot:nth-child(3) { animation-delay: 0s; }
    @keyframes dotsBounce {
      0%, 80%, 100% { transform: scale(0.25); opacity: 0.25; }
      40% { transform: scale(1.25); opacity: 1; }
    }

    /* شريط التنبيهات المنبثق */
    #wa-toast-notification {
      position: fixed;
      bottom: 24px;
      left: 50%;
      transform: translate(-50%, 80px);
      background: rgba(31, 44, 52, 0.96);
      backdrop-filter: blur(10px);
      border: 1px solid #2a3942;
      padding: 10px 22px;
      border-radius: 26px;
      color: #e9edef;
      font-size: 14px;
      font-weight: 600;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
      box-shadow: 0 8px 30px rgba(0,0,0,0.85);
      z-index: 3500;
      white-space: nowrap;
      opacity: 0;
      pointer-events: none;
      transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275), opacity 0.25s ease;
    }
    #wa-toast-notification.active { transform: translate(-50%, 0); opacity: 1; pointer-events: auto; }

    .modal {
      position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; height: 100dvh;
      background: rgba(0, 0, 0, 0.85); z-index: 100; display: none;
      align-items: center; justify-content: center; padding: 20px;
    }
    .modal.active { display: flex; }
    .modal-content {
      background: var(--container-bg); border: 1px solid var(--border-color);
      width: 100%; max-width: 360px; border-radius: 16px; padding: 20px;
    }
    .form-input {
      background: #111b21; border: 1px solid #2a3942; color: #fff;
      padding: 12px 14px; border-radius: 10px; width: 100%; font-size: 14px;
      outline: none; margin-top: 6px; margin-bottom: 16px;
    }
    .btn-submit {
      background: var(--primary-color); color: #fff; padding: 12px;
      border-radius: 10px; font-weight: 600; font-size: 15px; width: 100%; cursor: pointer;
      transition: transform 0.1s;
    }
    .btn-submit:active { transform: scale(0.98); }

    /* ======================================================== */
    /* واجهة تسجيل الدخول والتحقق المستقلة تماماً */
    /* ======================================================== */
    #auth-standalone-screen {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      height: 100dvh;
      background: #0b1014;
      z-index: 10000;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    .auth-box-card {
      background: #111b21;
      border: 1px solid #202c33;
      border-radius: 24px;
      padding: 32px 24px;
      width: 100%;
      max-width: 420px;
      box-shadow: 0 12px 40px rgba(0, 0, 0, 0.85);
      display: flex;
      flex-direction: column;
      align-items: center;
      animation: fadeIn 0.25s ease-out;
    }
    .auth-logo-img {
      width: 72px;
      height: 72px;
      margin-bottom: 14px;
    }
    .auth-heading {
      font-size: 22px;
      font-weight: 800;
      color: #fff;
      margin-bottom: 4px;
      text-align: center;
    }
    .auth-subheading {
      font-size: 13px;
      color: var(--text-muted);
      margin-bottom: 22px;
      text-align: center;
    }
    .auth-step {
      display: none;
      width: 100%;
      flex-direction: column;
    }
    .auth-step.active {
      display: flex;
    }

    /* حقل كلمة المرور مع زر العين */
    .password-field-container {
      position: relative;
      width: 100%;
      margin-bottom: 18px;
      display: flex;
      align-items: center;
    }
    .password-field-container input {
      margin-bottom: 0 !important;
      padding-left: 42px !important;
    }
    .password-eye-toggle-btn {
      position: absolute;
      left: 12px;
      color: #8696a0;
      font-size: 17px;
      cursor: pointer;
      padding: 6px;
      transition: color 0.15s;
      z-index: 10;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .password-eye-toggle-btn:hover { color: #fff; }

    /* أزرار تسجيل الدخول الاجتماعي (Google & Apple) */
    .social-auth-section {
      width: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      margin-top: 22px;
      padding-top: 18px;
      border-top: 1px solid #1f2c34;
    }
    .social-auth-title {
      font-size: 12.5px;
      color: var(--text-muted);
      margin-bottom: 14px;
    }
    .social-auth-buttons-row {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 16px;
      width: 100%;
    }
    .btn-social-circle {
      width: 52px;
      height: 52px;
      border-radius: 50%;
      background: #1f2c34;
      border: 1px solid #2a3942;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: transform 0.12s ease, background 0.15s;
    }
    .btn-social-circle:active {
      transform: scale(0.92);
      background: #273742;
    }

    /* مربعات الـ OTP */
    .otp-input-container {
      display: flex;
      justify-content: center;
      gap: 8px;
      direction: ltr;
      margin: 15px 0 12px 0;
    }
    .otp-box {
      width: 46px;
      height: 52px;
      background: #1f2c34;
      border: 1.5px solid #2a3942;
      border-radius: 12px;
      color: #fff;
      font-size: 22px;
      font-weight: 700;
      text-align: center;
      outline: none;
      transition: border-color 0.2s, box-shadow 0.2s, background-color 0.2s, color 0.2s, transform 0.2s;
    }
    
    .otp-box:focus {
      border-color: var(--primary-color);
      box-shadow: 0 0 12px rgba(0, 168, 132, 0.4);
    }

    /* اللون الأخضر عند صحة الرمز الحقيقي */
    .otp-box.success {
      border-color: #00A884 !important;
      background: rgba(0, 168, 132, 0.18) !important;
      color: #00A884 !important;
      box-shadow: 0 0 18px rgba(0, 168, 132, 0.75) !important;
      transform: scale(1.05);
    }

    /* اللون الأحمر عند خطأ الرمز الفعلي */
    .otp-box.error {
      border-color: #ea4335 !important;
      background: rgba(234, 67, 53, 0.18) !important;
      color: #ea4335 !important;
      box-shadow: 0 0 18px rgba(234, 67, 53, 0.65) !important;
    }

    /* حركة الاهتزاز السريعة للمربعات */
    .otp-input-container.shake {
      animation: shakeOTP 0.45s ease-in-out;
    }
    @keyframes shakeOTP {
      0%, 100% { transform: translateX(0); }
      20%, 60% { transform: translateX(-8px); }
      40%, 80% { transform: translateX(8px); }
    }
  </style>
</head>
<body>

  <!-- شاشة التحميل الثلاثية النقاط الصافية (فقط 3 نقاط خضراء تركض بدون كلام) -->
  <div id="three-dots-global-overlay">
    <div class="dots-running-container">
      <div class="running-dot"></div>
      <div class="running-dot"></div>
      <div class="running-dot"></div>
    </div>
  </div>

  <!-- واجهة تسجيل الدخول والتحقق المستقلة تماماً -->
  <div id="auth-standalone-screen">
    <div class="auth-box-card">
      <img id="auth-main-logo" class="auth-logo-img" src="" alt="Linko">
      
      <!-- الخطوة 1: إدخال البريد وكلمة المرور -->
      <div class="auth-step active" id="step-credentials">
        <h2 class="auth-heading" id="auth-heading-text">تسجيل الدخول إلى Linko</h2>
        <p class="auth-subheading">أدخل بريدك الإلكتروني وكلمة المرور للمتابعة</p>
        
        <input type="email" id="auth-email-input" class="form-input" placeholder="البريد الإلكتروني" style="direction: ltr; margin-bottom: 12px;">
        
        <div class="password-field-container">
          <input type="password" id="auth-password-input" class="form-input" placeholder="كلمة المرور" style="direction: ltr;">
          <div class="password-eye-toggle-btn" id="btn-toggle-password-visibility" title="إظهار / إخفاء كلمة المرور">
            <i class="fas fa-eye" id="eye-icon"></i>
          </div>
        </div>
        
        <button class="btn-submit" id="btn-request-otp">متابعة</button>
        
        <p style="text-align: center; margin-top: 14px; font-size: 13px; cursor: pointer; color: var(--primary-color); font-weight: 600;" id="auth-toggle-mode-btn">
          ليس لديك حساب؟ أنشئ حساباً جديداً
        </p>

        <!-- أزرار تسجيل الدخول السريع عبر Google و Apple -->
        <div class="social-auth-section">
          <span class="social-auth-title">أو المتابعة مباشرة عبر</span>
          <div class="social-auth-buttons-row">
            
            <button class="btn-social-circle" id="btn-google-direct-auth" title="تسجيل الدخول بواسطة Google">
              <svg width="24" height="24" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.665-5.17 3.665-9.17z"/>
                <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.26v3.15C3.29 21.41 7.37 24 12 24z"/>
                <path fill="#FBBC05" d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.26C.46 8.16 0 9.94 0 12s.46 3.84 1.26 5.42l4.02-3.15z"/>
                <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.37 0 3.29 2.59 1.26 6.58l4.02 3.15c.95-2.83 3.6-4.98 6.72-4.98z"/>
              </svg>
            </button>

            <button class="btn-social-circle" id="btn-apple-direct-auth" title="تسجيل الدخول بواسطة Apple">
              <i class="fab fa-apple" style="font-size: 24px; color: #fff;"></i>
            </button>

          </div>
        </div>

      </div>

      <!-- الخطوة 2: إدخال رمز التحقق مع زر متابعة وتنبيه الخطأ -->
      <div class="auth-step" id="step-otp">
        <h2 class="auth-heading">تأكيد رمز التحقق</h2>
        <p class="auth-subheading" id="otp-sent-to-label">تم إرسال رمز التحقق المكون من 6 أرقام إلى بريدك الإلكتروني</p>

        <div class="otp-input-container" id="otp-input-container">
          <input type="text" maxlength="1" class="otp-box" id="otp-1" inputmode="numeric" autocomplete="one-time-code">
          <input type="text" maxlength="1" class="otp-box" id="otp-2" inputmode="numeric">
          <input type="text" maxlength="1" class="otp-box" id="otp-3" inputmode="numeric">
          <input type="text" maxlength="1" class="otp-box" id="otp-4" inputmode="numeric">
          <input type="text" maxlength="1" class="otp-box" id="otp-5" inputmode="numeric">
          <input type="text" maxlength="1" class="otp-box" id="otp-6" inputmode="numeric">
        </div>

        <div id="otp-error-msg" style="color: var(--danger-color); font-size: 13px; font-weight: 700; text-align: center; margin-bottom: 12px; min-height: 20px; display: none;"></div>

        <button class="btn-submit" id="btn-verify-otp" style="margin-bottom: 14px;">متابعة</button>

        <div style="display:flex; justify-content:space-between; align-items:center; width:100%; font-size:12.5px;">
          <span id="btn-back-to-creds" style="color:#8696a0; cursor:pointer;"><i class="fas fa-arrow-right"></i> رجوع وتعديل البيانات</span>
          <span id="re -btn" style="color:var(--primary-color); cursor:pointer; font-weight:bold;">إعادة الإرسال</span>
        </div>
      </div>

    </div>
  </div>

  <div id="app">
    
    <!-- Top Header -->
    <div class="top-header">
      <div class="brand-title">Linko</div>
      <div class="top-actions">
        <button id="menu-dots-btn"><i class="fas fa-ellipsis-v"></i></button>
      </div>
    </div>

    <!-- Search Section -->
    <div class="search-section">
      <div class="search-box-wrapper">
        <i class="fas fa-search"></i>
        <input type="text" id="main-search-input" placeholder="البحث برقم المعرف (ar-xxxx)... ثم انتر">
        <i class="fas fa-camera" id="search-camera-btn" style="cursor: pointer;"></i>
      </div>
    </div>

    <!-- Tab 1: المحادثات -->
    <div class="tab-content active" id="tab-chats">
      <div id="contacts-list"></div>
    </div>

    <!-- Tab 2: الطلبات -->
    <div class="tab-content" id="tab-requests" style="padding: 16px;">
      <h4 style="margin-bottom: 12px; color: var(--text-muted); font-size: 14px;">طلبات الصداقة</h4>
      <div id="requests-list"><p style="color: var(--text-muted); font-size: 13px; text-align: center; margin-top: 30px;">لا توجد طلبات جديدة</p></div>
    </div>

    <!-- Tab 3: المكالمات -->
    <div class="tab-content" id="tab-calls" style="padding: 16px;">
      <h4 style="margin-bottom: 12px; color: var(--text-muted); font-size: 14px;">سجل المكالمات</h4>
      <div id="calls-list"><p style="color: var(--text-muted); font-size: 13px; text-align: center; margin-top: 30px;">لا توجد مكالمات سابقة</p></div>
    </div>

    <!-- Tab 4: الإعدادات -->
    <div class="tab-content" id="tab-settings" style="padding: 20px;">
      <div style="display: flex; flex-direction: column; align-items: center; text-align: center; margin-bottom: 20px;">
        <img id="my-profile-dp" class="avatar" style="width: 76px; height: 76px; margin-bottom: 8px;" src="" alt="DP">
        <h3 id="my-profile-name" style="font-size: 17px;">المستخدم</h3>
        <p id="my-profile-id" style="font-size: 12.5px; color: var(--primary-color); font-weight: bold; direction: ltr;">ar-0000</p>
        <p id="my-profile-bio" style="font-size: 12.5px; color: var(--text-muted); margin-top: 3px;">متوفر</p>
      </div>
      <button class="btn-submit" id="open-edit-profile" style="margin-bottom: 10px; background: var(--card-bg); border: 1px solid var(--border-color);">تعديل الملف الشخصي</button>
      <button class="btn-submit" id="logout-btn" style="background: var(--danger-color);">تسجيل الخروج</button>
    </div>

    <!-- FAB (+) -->
    <button class="fab-btn" id="fab-add-btn"><i class="fas fa-plus"></i></button>

    <!-- Bottom Navigation Bar -->
    <div class="bottom-nav">
      <div class="nav-tab active" data-tab="tab-chats">
        <div class="nav-tab-icon-wrap"><i class="fas fa-comment-dots"></i></div>
        <span>المحادثات</span>
      </div>
      <div class="nav-tab" data-tab="tab-requests">
        <div class="nav-tab-icon-wrap"><i class="fas fa-user-friends"></i></div>
        <span>الطلبات</span>
      </div>
      <div class="nav-tab" data-tab="tab-calls">
        <div class="nav-tab-icon-wrap"><i class="fas fa-phone-alt"></i></div>
        <span>المكالمات</span>
      </div>
      <div class="nav-tab" data-tab="tab-settings">
        <div class="nav-tab-icon-wrap"><i class="fas fa-cog"></i></div>
        <span>الإعدادات</span>
      </div>
    </div>

    <!-- CHAT SCREEN -->
    <div id="chat-screen">
      <div class="chat-header">
        <div class="chat-header-right" id="chat-header-clickable">
          <button id="chat-back-btn" style="font-size: 19px; color:#fff; padding:4px;" onclick="event.stopPropagation();"><i class="fas fa-arrow-right"></i></button>
          <div class="avatar-wrapper" style="width: 38px; height: 38px;">
            <img id="chat-header-dp" class="avatar" src="" alt="DP">
          </div>
          <div style="flex: 1; min-width: 0;">
            <div id="chat-header-name" style="font-size: 14.5px; font-weight: 600; color: #fff; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">جهة اتصال</div>
            <div id="chat-header-status" style="font-size: 11px; color: var(--text-muted);">غير متصل</div>
          </div>
        </div>
        <div class="chat-header-actions">
          <button id="voice-call-btn" title="اتصال صوتي"><i class="fas fa-phone-alt"></i></button>
          <button id="video-call-btn" title="اتصال مرئي"><i class="fas fa-video"></i></button>
          <button id="chat-menu-btn" title="خيارات"><i class="fas fa-ellipsis-v"></i></button>
        </div>
      </div>

      <div id="datablock-notice-banner">
        ⚠️ تم إيقاف بيانات الشبكة عن هذه المحادثة (لا يتم استلام أو إرسال أي رسائل).
      </div>

      <div class="chat-messages" id="chat-messages">
        <div class="blocked-stream-pill" id="blocked-stream-pill">
          لقد حظرت هذا الشخص. اضغط لإلغاء الحظر.
        </div>
      </div>

      <!-- نافذة الإيموجي -->
      <div class="emoji-picker-container" id="emoji-picker">
        <span class="emoji-item">😀</span><span class="emoji-item">😂</span><span class="emoji-item">😍</span><span class="emoji-item">👍</span><span class="emoji-item">❤️</span><span class="emoji-item">🔥</span>
        <span class="emoji-item">🎉</span><span class="emoji-item">🙏</span><span class="emoji-item">😊</span><span class="emoji-item">😎</span><span class="emoji-item">👏</span><span class="emoji-item">🌹</span>
      </div>

      <div class="vertical-lock-capsule" id="vertical-lock-capsule" title="اسحب أو اضغط للقفل">
        <i class="fas fa-lock"></i>
        <i class="fas fa-chevron-up"></i>
      </div>

      <div class="locked-recording-panel" id="locked-recording-panel">
        <div class="locked-top-row">
          <button class="btn-view-once-pill" id="btn-view-once" title="تشغيل لمرة واحدة">1</button>
          <div class="locked-waveform-live">
            <div class="live-wave-bar"></div>
            <div class="live-wave-bar" style="animation-delay:0.2s;"></div>
            <div class="live-wave-bar" style="animation-delay:0.4s;"></div>
            <div class="live-wave-bar" style="animation-delay:0.1s;"></div>
            <div class="live-wave-bar" style="animation-delay:0.3s;"></div>
            <div class="live-wave-bar" style="animation-delay:0.5s;"></div>
          </div>
          <span class="locked-timer-text" id="locked-timer-display">0:00</span>
        </div>

        <div class="locked-bottom-row">
          <button class="btn-locked-trash" id="btn-trash-locked" title="حذف"><i class="fas fa-trash-alt"></i></button>
          <button class="btn-locked-pause-pill" id="btn-pause-locked"><i class="fas fa-pause"></i> <span id="pause-btn-text">إيقاف مؤقت</span></button>
          <button class="btn-locked-send-white" id="btn-send-locked" title="إرسال"><i class="fas fa-chevron-left"></i></button>
        </div>
      </div>

      <!-- شريط الإدخال الموحد -->
      <div class="chat-bottom-wrapper" id="normal-chat-bottom-wrapper">
        <div class="unified-input-capsule" id="main-input-pill">
          <div id="normal-input-bar" style="display:flex; align-items:center; width:100%; gap:4px;">
            <i class="far fa-smile chat-pill-icon" id="emoji-toggle-btn" title="الرموز التعبيرية"></i>
            <i class="fas fa-camera chat-pill-icon" id="camera-btn" title="التقاط صورة"></i>
            <input type="text" id="chat-input" placeholder="الرسالة">
            <i class="fas fa-paperclip chat-pill-icon" id="attach-file-btn" title="إرفاق صورة"></i>
            
            <button class="integrated-mic-send-btn" id="main-mic-btn" title="تسجيل صوتي / إرسال">
              <i class="fas fa-microphone" id="main-mic-icon"></i>
            </button>
          </div>

          <div class="swipe-cancel-bar" id="swipe-cancel-bar">
            <span id="recording-inline-timer" style="color:#fff; font-weight:bold; direction:ltr;">0:00</span>
            <span><i class="fas fa-chevron-right" style="font-size:11px;"></i> اسحب للإلغاء</span>
          </div>
        </div>

        <input type="file" id="file-input-image" accept="image/*" style="display: none;">
        <input type="file" id="file-input-camera" accept="image/*" capture="environment" style="display: none;">
      </div>

      <div class="blocked-bottom-actions-bar" id="blocked-bottom-actions-bar">
        <button class="btn-block-action btn-unblock-green" id="btn-unblock-chat-bottom">
          <i class="fas fa-ban"></i>
          <span>رفع الحظر</span>
        </button>
        <button class="btn-block-action btn-delete-red" id="btn-delete-chat-bottom">
          <i class="fas fa-trash-alt"></i>
          <span>حذف الدردشة</span>
        </button>
      </div>

    </div>

    <!-- CONTACT PROFILE SCREEN -->
    <div id="contact-profile-screen">
      <div class="profile-top-bar" id="profile-top-bar">
        <button id="profile-back-btn" style="font-size: 19px; color:#e9edef; padding:6px; z-index:2;"><i class="fas fa-arrow-right"></i></button>

        <div id="profile-header-collapsed-info">
          <img id="profile-mini-dp" class="avatar" style="width: 32px; height: 32px;" src="" alt="DP">
          <span id="profile-mini-name" style="font-size: 16px; font-weight: 700; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 170px;">اسم المستخدم</span>
        </div>

        <div style="position: relative; z-index:2;">
          <button id="profile-menu-dots-btn" style="font-size: 19px; color:#8696a0; padding:6px;"><i class="fas fa-ellipsis-v"></i></button>
          <div class="dropdown-menu" id="profile-dropdown-menu">
            <div class="dropdown-item" id="menu-opt-edit-contact">
              <span>تعديل</span>
              <i class="fas fa-pen"></i>
            </div>
          </div>
        </div>
      </div>

      <div class="profile-hero" id="profile-hero-section">
        <img id="contact-view-dp" class="profile-large-avatar" src="" alt="Avatar" title="اضغط لتكبير الصورة">
        <h2 id="contact-view-name" class="profile-user-title">اسم المستخدم</h2>
        <div id="contact-view-id" class="profile-user-id-sub">ar-0000</div>

        <div class="profile-action-row">
          <div class="profile-btn-card" id="profile-voice-btn"><i class="fas fa-phone-alt"></i><span>صوتي</span></div>
          <div class="profile-btn-card" id="profile-video-btn"><i class="fas fa-video"></i><span>فيديو</span></div>
          <div class="profile-btn-card" id="profile-search-btn"><i class="fas fa-search"></i><span>بحث</span></div>
        </div>
      </div>

      <div class="profile-section">
        <div class="profile-list-item" id="profile-opt-storage">
          <div class="profile-item-left">
            <i class="far fa-folder-open profile-item-icon"></i>
            <div class="profile-item-texts">
              <span class="profile-item-title">إدارة مساحة التخزين</span>
              <span class="profile-item-desc" id="profile-storage-size-desc">معرض وسائط المحادثة</span>
            </div>
          </div>
        </div>

        <div class="profile-list-item" id="profile-opt-notifications">
          <div class="profile-item-left">
            <i class="far fa-bell profile-item-icon" id="profile-bell-icon"></i>
            <div class="profile-item-texts"><span class="profile-item-title">الإشعارات</span></div>
          </div>
          <label class="switch" style="pointer-events: none;">
            <input type="checkbox" id="notif-toggle-switch" checked><span class="slider"></span>
          </label>
        </div>

        <div class="profile-list-item">
          <div class="profile-item-left">
            <i class="fas fa-lock profile-item-icon"></i>
            <div class="profile-item-texts">
              <span class="profile-item-title">التشفير</span>
              <span class="profile-item-desc">الرسائل والمكالمات مشفرة تمامًا بين الطرفين. اضغط للتحقق.</span>
            </div>
          </div>
        </div>

        <div class="profile-list-item" id="profile-opt-chatlock">
          <div class="profile-item-left">
            <i class="fas fa-shield-alt profile-item-icon" id="chatlock-icon"></i>
            <div class="profile-item-texts">
              <span class="profile-item-title">قفل الدردشة</span>
              <span class="profile-item-desc">تمكّن من قفل هذه الدردشة وإخفائها على هذا الجهاز.</span>
            </div>
          </div>
          <label class="switch" style="pointer-events: none;">
            <input type="checkbox" id="chatlock-toggle-switch"><span class="slider"></span>
          </label>
        </div>

        <div class="profile-list-item">
          <div class="profile-item-left">
            <i class="fas fa-user-shield profile-item-icon"></i>
            <div class="profile-item-texts">
              <span class="profile-item-title">الخصوصية المتقدمة للدردشة</span>
              <span class="profile-item-desc">إيقاف التشغيل</span>
            </div>
          </div>
        </div>

        <div class="profile-list-item" id="profile-opt-datablock">
          <div class="profile-item-left">
            <div style="width: 28px; display:flex; justify-content:center;">
              <svg width="26" height="20" viewBox="0 0 68 46" fill="none">
                <path d="M8 34 L8 16 M4 20 L8 16 L12 20" stroke="#8696a0" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M20 16 L20 34 M16 30 L20 34 L24 30" stroke="#8696a0" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="4" y1="16" x2="24" y2="34" stroke="#e58544" stroke-width="1.8" stroke-linecap="round"/>
                <line x1="4" y1="34" x2="24" y2="16" stroke="#e58544" stroke-width="1.8" stroke-linecap="round"/>
                <rect x="30" y="26" width="5.5" height="12" rx="2.5" fill="#8696a0"/>
                <rect x="39" y="18" width="5.5" height="20" rx="2.5" fill="#8696a0"/>
                <rect x="48" y="10" width="5.5" height="28" rx="2.5" fill="#8696a0"/>
                <rect x="57" y="2" width="5.5" height="36" rx="2.5" fill="#8696a0"/>
              </svg>
            </div>
            <div class="profile-item-texts">
              <span class="profile-item-title">إيقاف بيانات المحادثة</span>
              <span class="profile-item-desc">قطع اتصال وبيانات الشبكة عن هذه الدردشة تماماً.</span>
            </div>
          </div>
          <label class="switch" style="pointer-events: none;">
            <input type="checkbox" id="datablock-toggle-switch"><span class="slider"></span>
          </label>
        </div>

        <div class="profile-list-item">
          <div class="profile-item-left">
            <i class="far fa-address-book profile-item-icon"></i>
            <div class="profile-item-texts"><span class="profile-item-title">إضافة إلى القائمة</span></div>
          </div>
        </div>

        <div class="profile-list-item danger-item" id="profile-clear-chat-btn">
          <div class="profile-item-left">
            <i class="fas fa-minus-circle profile-item-icon"></i>
            <div class="profile-item-texts"><span class="profile-item-title">مسح محتوى الدردشة</span></div>
          </div>
        </div>

        <div class="profile-list-item danger-item" id="block-user-btn">
          <div class="profile-item-left">
            <i class="fas fa-ban profile-item-icon"></i>
            <div class="profile-item-texts"><span class="profile-item-title" id="block-user-text">حظر المستخدم</span></div>
          </div>
        </div>

        <div class="profile-list-item danger-item" id="report-user-btn">
          <div class="profile-item-left">
            <i class="far fa-thumbs-down profile-item-icon"></i>
            <div class="profile-item-texts"><span class="profile-item-title" id="report-user-text">الإبلاغ عن المستخدم</span></div>
          </div>
        </div>
      </div>
    </div>

    <!-- FULLSCREEN AVATAR VIEWER -->
    <div id="fullscreen-avatar-viewer">
      <div class="avatar-viewer-top-bar">
        <div class="avatar-viewer-right">
          <button id="avatar-viewer-back-btn"><i class="fas fa-arrow-right"></i></button>
          <span id="avatar-viewer-name">اسم المستخدم</span>
        </div>
        <button id="avatar-viewer-close-icon-btn" style="color:#fff; font-size:18px; padding:6px;"><i class="fas fa-ellipsis-v"></i></button>
      </div>

      <div class="avatar-viewer-image-container">
        <img id="avatar-viewer-img" src="" alt="Avatar Fullscreen">
      </div>
    </div>

    <!-- EDIT CONTACT SCREEN -->
    <div id="edit-contact-screen">
      <div class="edit-screen-top-nav">
        <button style="font-size: 18px; color:#8696a0; padding:6px;"><i class="fas fa-ellipsis-v"></i></button>
        <div class="edit-screen-right-title">
          <span class="edit-screen-heading">تعديل جهة الاتصال</span>
          <button id="edit-contact-back-btn" style="font-size: 19px; color:#fff; padding:6px;"><i class="fas fa-arrow-right"></i></button>
        </div>
      </div>

      <div class="edit-fields-container">
        <div class="notched-input-group">
          <span class="notched-floating-label">الاسم الأول</span>
          <input type="text" id="edit-first-name" placeholder="الاسم الأول">
          <div class="notched-left-icon"><i class="fas fa-user"></i></div>
        </div>

        <div class="notched-input-group">
          <span class="notched-floating-label">اسم العائلة</span>
          <input type="text" id="edit-family-name" placeholder="اسم العائلة">
        </div>

        <div class="notched-input-group">
          <span class="notched-floating-label">اسم المستخدم</span>
          <input type="text" id="edit-username-field" placeholder="اسم المستخدم">
          <div class="notched-left-symbol">@</div>
        </div>
      </div>

      <button class="btn-save-contact-pill" id="save-contact-edit-btn">حفظ</button>
    </div>

    <!-- STORAGE SCREEN -->
    <div id="storage-screen">
      <div class="storage-header">
        <button id="storage-back-btn" style="font-size: 19px; color:#fff;"><i class="fas fa-arrow-right"></i></button>
        <span style="font-size: 17px; font-weight:700; color:#fff;">الوسائط المشتركة</span><div></div>
      </div>
      <div class="gallery-studio-grid" id="storage-images-grid">
        <p style="grid-column: 1/-1; color: var(--text-muted); font-size: 13.5px; text-align: center; padding: 40px 0;">لا توجد وسائط متبادلة بعد</p>
      </div>
    </div>

    <!-- REAL INTERACTIVE CALL SCREEN -->
    <div id="call-screen">
      <div class="call-doodle-bg" id="call-doodle-layer"></div>
      <video id="remote-video" class="call-video-main" autoplay playsinline></video>
      <video id="local-video" class="call-video-pip" autoplay playsinline muted title="اضغط للتبديل والتكبير"></video>

      <div class="call-top-header">
        <button class="btn-call-round-icon" id="btn-call-add-user" title="إضافة مشارك"><i class="fas fa-user-plus"></i></button>
        <div class="call-user-center-info">
          <h2 class="call-title-name" id="call-user-name">اسم المستخدم</h2>
          <span class="call-state-text" id="call-status">يتصل...</span>
        </div>
        <button class="btn-call-round-icon" id="btn-call-minimize" title="تصغير"><i class="fas fa-compress-arrows-alt"></i></button>
      </div>

      <div class="call-video-left-actions" id="call-video-side-bar">
        <button class="btn-call-round-icon" id="btn-switch-camera-flip" title="قلب الكاميرا"><i class="fas fa-camera-rotate"></i></button>
      </div>

      <div class="call-audio-avatar-container" id="call-audio-avatar-box">
        <img id="call-user-avatar" class="call-audio-huge-avatar" src="" alt="Avatar">
      </div>

      <div class="call-slim-floating-action-bar">
        <button class="call-ctrl-btn btn-hangup-red" id="btn-unified-end-call" title="إنهاء المكالمة"><i class="fas fa-phone-slash"></i></button>
        <button class="call-ctrl-btn" id="btn-unified-mute-toggle" title="كتم الصوت"><i class="fas fa-microphone-slash" id="unified-mute-icon"></i></button>
        <button class="call-ctrl-btn active-white" id="btn-unified-speaker-toggle" title="مكبر الصوت / سماعة الهاتف"><i class="fas fa-volume-up"></i></button>
        <button class="call-ctrl-btn" id="btn-unified-video-toggle" title="الفيديو"><i class="fas fa-video"></i></button>
      </div>
    </div>

    <!-- نافذة استقبال المكالمة الواردة -->
    <div id="incoming-call-dialog">
      <div style="display:flex; align-items:center; gap:12px;">
        <img id="inc-caller-avatar" class="inc-call-avatar" src="" alt="Avatar">
        <div>
          <div id="inc-caller-name" style="font-size:16px; font-weight:700; color:#fff;">اسم المتصل</div>
          <div id="inc-call-type-text" style="font-size:12.5px; color:var(--primary-color);">مكالمة واردة...</div>
        </div>
      </div>
      <div style="display:flex; align-items:center; gap:12px;">
        <button class="btn-inc-decline" id="btn-inc-decline"><i class="fas fa-phone-slash"></i></button>
        <button class="btn-inc-accept" id="btn-inc-accept"><i class="fas fa-phone-alt"></i></button>
      </div>
    </div>

    <!-- نافذة إضافة جهة اتصال بالمعرف -->
    <div class="modal" id="add-friend-modal">
      <div class="modal-content">
        <h3 style="margin-bottom:12px; text-align:center;">إضافة جهة اتصال</h3>
        <p style="font-size:13px; color:var(--text-muted); margin-bottom:14px; text-align:center;">أدخل المعرف الخاص بالشخص (مثال: ar-1234):</p>
        <input type="text" id="friend-id-input" class="form-input" placeholder="ar-xxxx" style="text-align:center; direction:ltr;">
        <div style="display:flex; gap:10px;">
          <button class="btn-submit" id="send-request-btn">إضافة</button>
          <button class="btn-submit" id="close-add-friend" style="background:#202c33;">إلغاء</button>
        </div>
      </div>
    </div>

    <!-- نافذة تعديل الملف الشخصي -->
    <div class="modal" id="edit-profile-modal">
      <div class="modal-content">
        <h3 style="margin-bottom:12px; text-align:center;">تعديل الملف الشخصي</h3>
        <input type="text" id="my-edit-name-input" class="form-input" placeholder="اسم المستخدم">
        <input type="text" id="my-edit-bio-input" class="form-input" placeholder="الحالة / النبذة">
        <div style="display:flex; gap:10px;">
          <button class="btn-submit" id="save-my-profile-btn">حفظ</button>
          <button class="btn-submit" id="close-my-profile-btn" style="background:#202c33;">إلغاء</button>
        </div>
      </div>
    </div>

    <!-- نافذة مسح محتوى الدردشة -->
    <div id="modal-clear-chat-wa">
      <div class="clear-sheet-card">
        <div class="clear-sheet-header">
          <span class="clear-sheet-title" id="clear-sheet-title-text">مسح محتوى دردشة...</span>
          <button id="btn-close-clear-sheet" style="color:#8696a0; font-size:19px;"><i class="fas fa-times"></i></button>
        </div>
        <p class="clear-sheet-desc">سيتم حذف جميع الرسائل في هذه الدردشة. لا يمكن التراجع عن هذا الإجراء.</p>
        
        <div class="clear-checkbox-row" id="row-clear-starred">
          <span style="font-size:14px; color:#fff;">مسح الرسائل المميزة بنجمة</span>
          <input type="checkbox" id="check-clear-starred" style="width:18px; height:18px; accent-color:var(--primary-color);">
        </div>

        <button class="btn-clear-red-pill" id="btn-confirm-clear-wa">مسح الدردشة</button>
      </div>
    </div>

    <!-- نافذة إبلاغ Linko -->
    <div id="modal-report-wa">
      <div class="wa-dialog-card">
        <div style="font-size: 32px; color: var(--text-muted); margin-bottom: 12px;"><i class="far fa-thumbs-down"></i></div>
        <h3 style="font-size: 18px; font-weight: 700; color: #fff; margin-bottom: 12px;">إبلاغ Linko</h3>
        <p style="font-size: 13.5px; color: #e9edef; line-height: 1.6; margin-bottom: 16px; text-align: right;">
          ستُرسل آخر 5 رسائل في هذه الدردشة إلى Linko. ولن يعرف هذا الشخص أنك أبلغت عنه أو حظرته.
        </p>

        <div style="display:flex; align-items:flex-start; justify-content:space-between; gap:10px; margin-bottom:20px; text-align:right;">
          <div style="font-size:13px; color:#e9edef;">
            <div style="font-weight:700;" id="report-block-title">حظر المستخدم</div>
            <div style="color:var(--text-muted); font-size:11.5px;">لن يتمكن هذا الشخص من مراسلتك أو الاتصال بك.</div>
          </div>
          <input type="checkbox" id="check-report-also-block" style="width:18px; height:18px; accent-color:var(--primary-color); margin-top:2px;">
        </div>

        <div style="display:flex; gap:12px; justify-content:flex-end;">
          <button class="btn-notif-cancel" id="btn-cancel-report-wa" style="color:var(--primary-color); font-weight:700;">إلغاء</button>
          <button class="btn-notif-confirm" id="btn-confirm-report-wa">إبلاغ</button>
        </div>
      </div>
    </div>

    <!-- نافذة حظر المستخدم -->
    <div id="modal-block-wa">
      <div class="wa-dialog-card">
        <div style="font-size: 32px; color: var(--text-muted); margin-bottom: 12px;"><i class="fas fa-ban"></i></div>
        <h3 style="font-size: 18px; font-weight: 700; color: #fff; margin-bottom: 12px;" id="block-dialog-title">حظر المستخدم؟</h3>
        <p style="font-size: 13.5px; color: #e9edef; line-height: 1.6; margin-bottom: 16px; text-align: right;">
          لن يتمكن هذا الشخص من مراسلتك أو الاتصال بك. ولن يعرف أنك حظرته أو أبلغت عنه.
        </p>

        <div style="display:flex; align-items:flex-start; justify-content:space-between; gap:10px; margin-bottom:20px; text-align:right;">
          <div style="font-size:13px; color:#e9edef;">
            <div style="font-weight:700;">إبلاغ Linko</div>
            <div style="color:var(--text-muted); font-size:11.5px;">ستُرسل آخر 5 رسائل في هذه الدردشة إلى Linko.</div>
          </div>
          <input type="checkbox" id="check-block-also-report" style="width:18px; height:18px; accent-color:var(--primary-color); margin-top:2px;">
        </div>

        <div style="display:flex; gap:12px; justify-content:flex-end;">
          <button class="btn-notif-cancel" id="btn-cancel-block-wa" style="color:var(--primary-color); font-weight:700;">إلغاء</button>
          <button class="btn-notif-confirm" id="btn-confirm-block-wa" style="background:var(--danger-color);">حظر</button>
        </div>
      </div>
    </div>

    <!-- مقدمة قفل الدردشة -->
    <div id="chatlock-intro-modal">
      <div class="intro-modal-card">
        <div class="intro-modal-icon" style="font-size:36px; color:var(--primary-color); margin-bottom:12px;"><i class="fas fa-shield-alt"></i></div>
        <p class="intro-modal-text" style="font-size:14px; color:#e9edef; line-height:1.6; margin-bottom:18px;">
          مستخدم Linko، يمكنك تفعيل هذه الميزة لحماية خصوصيتك وقفل المحادثة بين الطرفين، وذلك عن طريق البصمة أو باستخدام رمز PIN، للمزيد من الخصوصية والأمان.
        </p>
        <button class="btn-submit" id="btn-intro-continue">متابعة</button>
      </div>
    </div>

    <!-- اختيار وسيلة الحماية -->
    <div id="chatlock-method-modal">
      <div class="method-modal-card">
        <h3 style="font-size: 17px; font-weight:700; color:#fff; margin-bottom:14px; text-align:center;">اختر وسيلة الحماية</h3>
        <div class="method-option-card" id="opt-method-biometric">
          <div style="font-size:24px; color:var(--primary-color);">🔐</div>
          <div><div style="font-weight:700; color:#fff;">البصمة</div><div style="font-size:12px; color:var(--text-muted);">لاستخدام بصمة الإصبع لتأكيد الهوية وفتح المحادثة.</div></div>
        </div>
        <div class="method-option-card" id="opt-method-pin">
          <div style="font-size:24px; color:var(--primary-color);">🔢</div>
          <div><div style="font-weight:700; color:#fff;" id="pin-card-title">رمز PIN</div><div style="font-size:12px; color:var(--text-muted);" id="pin-card-desc">لاستخدام رمز PIN بدلًا من البصمة.</div></div>
        </div>
        <button class="btn-notif-cancel" id="btn-close-method-modal" style="width:100%; margin-top:8px;">إلغاء</button>
      </div>
    </div>

    <!-- الواجهة البيضاء لقفل المحادثة -->
    <div id="fullscreen-pin-lock-view">
      <div class="white-lock-header-row">
        <button class="btn-close-white-lock" id="btn-white-lock-cancel"><i class="fas fa-times"></i></button>
      </div>

      <div class="white-lock-title-section">
        <div class="white-lock-title">أدخل كلمة المرور</div>
        <div class="white-lock-pin-dots">
          <div class="white-pin-dot" id="wdot-1"></div>
          <div class="white-pin-dot" id="wdot-2"></div>
          <div class="white-pin-dot" id="wdot-3"></div>
          <div class="white-pin-dot" id="wdot-4"></div>
        </div>
      </div>

      <div class="white-lock-keypad-grid">
        <div class="white-key-digit" data-val="1">1</div>
        <div class="white-key-digit" data-val="2">2</div>
        <div class="white-key-digit" data-val="3">3</div>

        <div class="white-key-digit" data-val="4">4</div>
        <div class="white-key-digit" data-val="5">5</div>
        <div class="white-key-digit" data-val="6">6</div>

        <div class="white-key-digit" data-val="7">7</div>
        <div class="white-key-digit" data-val="8">8</div>
        <div class="white-key-digit" data-val="9">9</div>

        <div class="white-key-icon-btn" id="white-fingerprint-action-btn" title="المس للتحقق بالبصمة">
          <div class="white-fingerprint-icon">
            <i class="fas fa-fingerprint"></i>
            <span class="white-fingerprint-badge-dot"></span>
          </div>
        </div>

        <div class="white-key-digit" data-val="0">0</div>

        <div class="white-key-icon-btn" id="white-backspace-action-btn" title="حذف">
          <div class="white-backspace-icon">
            <i class="fas fa-backspace"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- نافذة تعيين رمز PIN -->
    <div id="custom-pin-setup-modal">
      <div class="pin-setup-card">
        <h3 style="font-size: 17px; font-weight:700; color:#fff; margin-bottom:8px;">تعيين رمز PIN</h3>
        <p style="font-size: 13px; color:var(--text-muted); margin-bottom:16px;">أدخل رمز PIN جديداً مكوناً من 4 أرقام لحماية هذه المحادثة:</p>
        <input type="password" maxlength="4" id="custom-new-pin-input" class="form-input" placeholder="••••" style="text-align:center; font-size:24px; letter-spacing:10px; direction:ltr;">
        <div style="display:flex; gap:10px;">
          <button class="btn-notif-confirm" id="btn-save-new-pin">حفظ وقفل</button>
          <button class="btn-notif-cancel" id="btn-cancel-new-pin">إلغاء</button>
        </div>
      </div>
    </div>

    <!-- NOTIFICATION MODAL -->
    <div id="notif-terms-modal">
      <div class="notif-modal-card">
        <div class="notif-icon-circle" style="font-size:36px; color:var(--primary-color); margin-bottom:12px;"><i class="far fa-bell-slash"></i></div>
        <h3 style="font-size: 17px; font-weight:700; color:#fff; margin-bottom:10px;">إيقاف الإشعارات</h3>
        <p class="notif-terms-text" style="font-size:13.5px; color:#e9edef; line-height:1.6; margin-bottom:16px;">عزيزي مستخدم Linko، يمكنك تفعيل هذه الميزة لإيقاف الإشعارات من هذا الطرف كي لا يصل إليك أي تنبيه أو صوت عند استلام رسائل جديدة.</p>
        <div style="display:flex; gap:10px;">
          <button class="btn-notif-confirm" id="btn-notif-agree">موافقة</button><button class="btn-notif-cancel" id="btn-notif-cancel">إلغاء</button>
        </div>
      </div>
    </div>

    <!-- DATABLOCK TERMS MODAL -->
    <div id="datablock-terms-modal">
      <div class="notif-modal-card">
        <div class="datablock-custom-icon-box">
          <svg width="82" height="54" viewBox="0 0 68 46" fill="none">
            <path d="M8 34 L8 16 M4 20 L8 16 L12 20" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M20 16 L20 34 M16 30 L20 34 L24 30" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="4" y1="16" x2="24" y2="34" stroke="#e58544" stroke-width="1.8" stroke-linecap="round"/>
            <line x1="4" y1="34" x2="24" y2="16" stroke="#e58544" stroke-width="1.8" stroke-linecap="round"/>
            <rect x="30" y="26" width="5.5" height="12" rx="2.5" fill="#ffffff"/>
            <rect x="39" y="18" width="5.5" height="20" rx="2.5" fill="#ffffff"/>
            <rect x="48" y="10" width="5.5" height="28" rx="2.5" fill="#ffffff"/>
            <rect x="57" y="2" width="5.5" height="36" rx="2.5" fill="#ffffff"/>
          </svg>
        </div>
        <h3 style="font-size: 18px; font-weight:700; color:#fff; margin-bottom:10px;">إيقاف بيانات المحادثة</h3>
        <p class="notif-terms-text" style="font-size:13.5px; color:#e9edef; line-height:1.6; margin-bottom:18px;">
          عزيزي مستخدم Linko، عند تفعيل ميزة إيقاف بيانات المحادثة، سيتم قطع اتصال الشبكة والبيانات بالكامل عن هذا الطرف، ولن يتمكن أي منكما من إرسال أو استلام أي رسائل أو مكالمات نهائياً حتى تقوم بإعادة تشغيلها.
        </p>
        <div style="display:flex; gap:10px;">
          <button class="btn-notif-confirm" id="btn-datablock-agree" style="background: var(--danger-color);">تأكيد الإيقاف</button>
          <button class="btn-notif-cancel" id="btn-datablock-cancel">إلغاء</button>
        </div>
      </div>
    </div>

    <!-- إشعار التوست العائم -->
    <div id="wa-toast-notification">
      <img id="toast-linko-icon" src="" style="width:22px; height:22px; object-fit:contain;" alt="Linko">
      <span id="wa-toast-text">تمت العملية بنجاح</span>
    </div>

  </div>

  <!-- Firebase & Logic Script -->
  <script type="module">
    import { initializeApp } from "https://www.gstatic.com/firebasejs/9.23.0/firebase-app.js";
    import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword, onAuthStateChanged, signOut, setPersistence, inMemoryPersistence, GoogleAuthProvider, signInWithPopup } from "https://www.gstatic.com/firebasejs/9.23.0/firebase-auth.js";
    import { getDatabase, ref, set, get, onValue, push, update, onDisconnect, serverTimestamp, remove } from "https://www.gstatic.com/firebasejs/9.23.0/firebase-database.js";

    const firebaseConfig = {
      apiKey: "AIzaSyDeShdVhyxs8liCqUOvdWDJ4ixHzf_tDS0",
      authDomain: "linko-bcd00.firebaseapp.com",
      databaseURL: "https://linko-bcd00-default-rtdb.firebaseio.com",
      projectId: "linko-bcd00",
      storageBucket: "linko-bcd00.firebasestorage.app",
      messagingSenderId: "331700062933",
      appId: "1:331700062933:web:d1e387bddeb33998d7305c"
    };

    const app = initializeApp(firebaseConfig);
    const auth = getAuth(app);
    const db = getDatabase(app);

    try { setPersistence(auth, inMemoryPersistence); } catch(e) {}

    const LINKO_APP_LOGO_SVG = `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><defs><linearGradient id="linkoG" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="%2355c843"/><stop offset="100%" stop-color="%2300A884"/></linearGradient></defs><path d="M 100,20 C 56,20 20,56 20,100 C 20,118 26,135 36,148 L 22,182 L 58,171 C 70,177 84,180 100,180 C 144,180 180,144 180,100 C 180,56 144,20 100,20 Z" fill="%23ffffff" stroke="url(%23linkoG)" stroke-width="13" stroke-linejoin="round"/><text x="100" y="103" text-anchor="middle" dominant-baseline="central" fill="%2325D366" font-family="'Cairo', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-weight="800" font-size="36" letter-spacing="-0.5">Linko</text></svg>`;

    document.getElementById('toast-linko-icon').src = LINKO_APP_LOGO_SVG;
    document.getElementById('auth-main-logo').src = LINKO_APP_LOGO_SVG;

    // شاشة التحميل الثلاثية النقاط الصافية مع مؤقت أمان ذكي
    let loaderSafetyTimer = null;
    function show3DotsLoader() {
      document.getElementById('three-dots-global-overlay').classList.add('active');
      if (loaderSafetyTimer) clearTimeout(loaderSafetyTimer);
      loaderSafetyTimer = setTimeout(() => {
        hide3DotsLoader();
      }, 4000);
    }
    function hide3DotsLoader() {
      document.getElementById('three-dots-global-overlay').classList.remove('active');
      if (loaderSafetyTimer) clearTimeout(loaderSafetyTimer);
    }

    document.body.addEventListener('click', () => { 
      try { Tone.start(); } catch(e) {}
    }, { once: true });

    if ("Notification" in window && Notification.permission !== "granted" && Notification.permission !== "denied") {
      Notification.requestPermission();
    }

    function playSendTone() {
      try {
        const synth = new Tone.Synth({
          oscillator: { type: "sine" },
          envelope: { attack: 0.005, decay: 0.08, sustain: 0.0, release: 0.08 }
        }).toDestination();
        synth.volume.value = -8;
        synth.triggerAttackRelease("E6", "32n");
      } catch(e) {}
    }

    function playMessageNotificationSound() {
      try {
        const synth = new Tone.PolySynth(Tone.Synth, {
          oscillator: { type: "sine" },
          envelope: { attack: 0.005, decay: 0.12, sustain: 0.0, release: 0.1 }
        }).toDestination();
        synth.volume.value = -6;
        synth.triggerAttackRelease(["E5", "B5"], "32n");
      } catch(e) {}
    }

    let outgoingToneInterval = null;
    function startOutgoingRinging() {
      stopOutgoingRinging();
      try {
        const synth = new Tone.PolySynth(Tone.Synth, {
          oscillator: { type: "sine" },
          envelope: { attack: 0.05, decay: 0.2, sustain: 0.8, release: 0.3 }
        }).toDestination();
        synth.volume.value = -10;
        const playTone = () => { synth.triggerAttackRelease(["G4", "B4"], 1.3); };
        playTone();
        outgoingToneInterval = setInterval(playTone, 3800);
      } catch(e) {}
    }

    function stopOutgoingRinging() {
      if (outgoingToneInterval) {
        clearInterval(outgoingToneInterval);
        outgoingToneInterval = null;
      }
    }

    let incomingRingtoneInterval = null;
    let incomingCallSynth = null;
    function startIncomingRinging() {
      stopIncomingRinging();
      try {
        if (navigator.vibrate) navigator.vibrate([300, 200, 300, 600]);
        incomingCallSynth = new Tone.PolySynth(Tone.Synth, {
          oscillator: { type: "sine" },
          envelope: { attack: 0.02, decay: 0.35, sustain: 0.2, release: 0.8 }
        }).toDestination();
        incomingCallSynth.volume.value = -3;

        const playModernLinkoMelody = () => {
          if (navigator.vibrate) navigator.vibrate([250, 150, 250]);
          const now = Tone.now();
          incomingCallSynth.triggerAttackRelease(["C5", "G5"], "16n", now);
          incomingCallSynth.triggerAttackRelease(["E5", "B5"], "16n", now + 0.16);
          incomingCallSynth.triggerAttackRelease(["G5", "D6"], "16n", now + 0.32);
          incomingCallSynth.triggerAttackRelease(["C6", "E6"], "8n", now + 0.48);
          incomingCallSynth.triggerAttackRelease(["A5", "C6", "E6"], "4n", now + 0.75);
        };
        playModernLinkoMelody();
        incomingRingtoneInterval = setInterval(playModernLinkoMelody, 2600);
      } catch(e) {}
    }

    function stopIncomingRinging() {
      if (incomingRingtoneInterval) {
        clearInterval(incomingRingtoneInterval);
        incomingRingtoneInterval = null;
      }
      if (incomingCallSynth) {
        try { incomingCallSynth.dispose(); } catch(e) {}
        incomingCallSynth = null;
      }
      if (navigator.vibrate) navigator.vibrate(0);
    }

    function emojiToSVG(char = "AR") {
      const text = (char || "AR").substring(0, 2);
      const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
        <rect width="100" height="100" rx="50" fill="#1f2c34"/>
        <text x="50%" y="56%" text-anchor="middle" dominant-baseline="middle" fill="#00A884" font-size="40" font-family="sans-serif" font-weight="bold">${text}</text>
      </svg>`;
      return 'data:image/svg+xml;utf8,' + encodeURIComponent(svg);
    }

    let toastTimer = null;
    function showWaToast(msg) {
      const toast = document.getElementById('wa-toast-notification');
      document.getElementById('wa-toast-text').innerText = msg;
      toast.classList.add('active');
      if (toastTimer) clearTimeout(toastTimer);
      toastTimer = setTimeout(() => toast.classList.remove('active'), 2800);
    }

    function formatBytes(bytes) {
      if (bytes === 0) return '0.0 ك.ب';
      const k = 1024;
      const sizes = ['بايت', 'ك.ب', 'م.ب', 'ج.ب'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    let currentUser = null;
    let currentProfile = null;
    let activeChatContact = null;
    let isSignupMode = false;
    let activeMessageListeners = {};
    let allContactsCache = {};

    let localStream = null;
    let peerConnection = null;
    let activeCallId = null;
    let isCallVideoMode = false;
    let isMicMuted = false;
    let isSpeakerActive = true;
    let currentFacingMode = "user";
    let isPiPViewSwapped = false;
    let callTimerInterval = null;
    let callStartTimestamp = 0;
    const rtcConfig = { iceServers: [{ urls: 'stun:stun.l.google.com:19302' }] };

    // Voice Recorder States
    let mediaRecorder = null;
    let audioChunks = [];
    let recordStartTime = 0;
    let recordTimerInterval = null;
    let isRecordingLocked = false;
    let isRecordingPaused = false;
    let isViewOnceActive = false;
    let recordedDurationSec = 0;
    let isHoldingMic = false;
    let touchStartY = 0;
    let touchStartX = 0;

    // Chat Lock States
    let pendingBiometricAction = null;
    let pendingContactToUnlock = null;
    let currentEnteredPin = "";

    // نظام تسجيل الدخول ورمز التحقق OTP
    const authScreen = document.getElementById('auth-standalone-screen');
    const stepCredentials = document.getElementById('step-credentials');
    const stepOtp = document.getElementById('step-otp');
    const emailInput = document.getElementById('auth-email-input');
    const passInput = document.getElementById('auth-password-input');
    const eyeIcon = document.getElementById('eye-icon');
    const togglePassBtn = document.getElementById('btn-toggle-password-visibility');
    let isSessionVerifiedByOtp = false;

    togglePassBtn.onclick = () => {
      if (passInput.type === 'password') {
        passInput.type = 'text';
        eyeIcon.className = 'fas fa-eye-slash';
        togglePassBtn.style.color = '#00A884';
      } else {
        passInput.type = 'password';
        eyeIcon.className = 'fas fa-eye';
        togglePassBtn.style.color = '#8696a0';
      }
    };

    // تسجيل الدخول بحساب Google
    const googleProvider = new GoogleAuthProvider();
    document.getElementById('btn-google-direct-auth').onclick = async () => {
      try {
        show3DotsLoader();
        await signInWithPopup(auth, googleProvider);
        isSessionVerifiedByOtp = true;
        hide3DotsLoader();
        authScreen.style.display = "none";
        showWaToast("تم الدخول بنجاح عبر حساب Google!");
      } catch(err) {
        hide3DotsLoader();
        alert("خطأ في تسجيل الدخول عبر Google: " + err.message);
      }
    };

    document.getElementById('btn-apple-direct-auth').onclick = () => {
      show3DotsLoader();
      setTimeout(() => {
        hide3DotsLoader();
        alert("يرجى التأكد من تفعيل خدمة Apple في إعدادات Firebase للمصادقة المباشرة.");
      }, 800);
    };

    const otpContainer = document.getElementById('otp-input-container');
    const otpErrorMsg = document.getElementById('otp-error-msg');
    const otpBoxes = [
      document.getElementById('otp-1'),
      document.getElementById('otp-2'),
      document.getElementById('otp-3'),
      document.getElementById('otp-4'),
      document.getElementById('otp-5'),
      document.getElementById('otp-6')
    ];

    otpBoxes.forEach((box, index) => {
      box.addEventListener('input', () => {
        box.classList.remove('error', 'success');
        otpContainer.classList.remove('shake');
        otpErrorMsg.style.display = 'none';

        if (box.value.length >= 1) {
          box.value = box.value.slice(0, 1);
          if (index < 5) {
            otpBoxes[index + 1].focus();
          }
        }

        const currentCode = getEnteredOTP();
        if (currentCode.length === 6) {
          triggerVerifyOTPLogic(currentCode);
        }
      });

      box.addEventListener('paste', (e) => {
        e.preventDefault();
        const pastedData = (e.clipboardData || window.clipboardData).getData('text').trim();
        if (/^\\d{6}$/.test(pastedData)) {
          pastedData.split('').forEach((char, i) => {
            if (otpBoxes[i]) otpBoxes[i].value = char;
          });
          triggerVerifyOTPLogic(pastedData);
        }
      });

      box.addEventListener('keydown', (e) => {
        if (e.key === 'Backspace') {
          if (box.value === '' && index > 0) {
            otpBoxes[index - 1].focus();
            otpBoxes[index - 1].value = '';
            otpBoxes[index - 1].classList.remove('error', 'success');
          } else {
            box.classList.remove('error', 'success');
          }
          otpErrorMsg.style.display = 'none';
        }
      });
    });

    function getEnteredOTP() {
      return otpBoxes.map(b => b.value.trim()).join('');
    }

    function clearOTPBoxes() {
      otpBoxes.forEach(b => {
        b.value = '';
        b.classList.remove('error', 'success');
      });
      otpContainer.classList.remove('shake');
      otpErrorMsg.style.display = 'none';
      otpBoxes[0].focus();
    }

    document.getElementById('auth-toggle-mode-btn').onclick = () => {
      isSignupMode = !isSignupMode;
      document.getElementById('auth-heading-text').innerText = isSignupMode ? "إنشاء حساب جديد في Linko" : "تسجيل الدخول إلى Linko";
      document.getElementById('btn-request-otp').innerText = "متابعة";
      document.getElementById('auth-toggle-mode-btn').innerText = isSignupMode ? "لديك حساب بالفعل؟ تسجيل الدخول" : "ليس لديك حساب؟ أنشئ حساباً جديداً";
    };

    // زر متابعة في الصفحة الأولى: انتقال فوري ومباشر مع شاشة النقاط
    document.getElementById('btn-request-otp').onclick = async () => {
      const email = emailInput.value.trim();
      const pass = passInput.value.trim();

      if (!email || !pass) {
        alert("يرجى إدخال البريد الإلكتروني وكلمة المرور.");
        return;
      }
      if (pass.length < 6) {
        alert("كلمة المرور يجب أن لا تقل عن 6 أحرف.");
        return;
      }

      show3DotsLoader();

      // تبديل الواجهة فوراً لشاشة رمز التحقق
      stepCredentials.classList.remove('active');
      stepCredentials.style.display = 'none';
      stepOtp.classList.add('active');
      stepOtp.style.display = 'flex';
      document.getElementById('otp-sent-to-label').innerText = `تم إرسال رمز التحقق المكون من 6 أرقام إلى ${email}`;
      clearOTPBoxes();

      // طلب الرمز من السيرفر وإخفاء شاشة النقاط فوراً
      fetch('/api/send-otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      }).then(r => r.json()).then(data => {
        if ("Notification" in window && Notification.permission === "granted") {
          new Notification("🔐 Linko — رمز التحقق", {
            body: "تم إرسال رمز التحقق الخاص بك إلى بريدك الإلكتروني.",
            icon: LINKO_APP_LOGO_SVG
          });
        }
      }).catch(() => {});

      setTimeout(() => {
        hide3DotsLoader();
        otpBoxes[0].focus();
        showWaToast("تم إرسال رمز التحقق بنجاح");
      }, 400);
    };

    document.getElementById('resend-otp-btn').onclick = () => {
      document.getElementById('btn-request-otp').click();
    };

    document.getElementById('btn-back-to-creds').onclick = () => {
      stepOtp.classList.remove('active');
      stepOtp.style.display = 'none';
      stepCredentials.classList.add('active');
      stepCredentials.style.display = 'flex';
    };

    // فحص الرمز مع السيرفر + الهزاز الحقيقي + الدخول التلقائي الذكي
    async function triggerVerifyOTPLogic(code) {
      const email = emailInput.value.trim();
      const pass = passInput.value.trim();

      if (code.length !== 6) {
        otpBoxes.forEach(b => b.classList.add('error'));
        otpContainer.classList.add('shake');
        if (navigator.vibrate) navigator.vibrate([80, 50, 80]);
        setTimeout(() => {
          otpContainer.classList.remove('shake');
          otpBoxes.forEach(b => b.classList.remove('error'));
        }, 500);
        return;
      }

      show3DotsLoader();
      try {
        const res = await fetch('/api/verify-otp', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, code })
        });
        const data = await res.json();

        // 1. حالة الرمز مطابقة وصحيحة 100%
        if (data.success) {
          otpBoxes.forEach(b => {
            b.classList.remove('error');
            b.classList.add('success');
          });
          otpErrorMsg.style.display = 'none';

          isSessionVerifiedByOtp = true;

          // مصادقة Firebase الذكية
          if (isSignupMode) {
            await createUserWithEmailAndPassword(auth, email, pass);
          } else {
            try {
              await signInWithEmailAndPassword(auth, email, pass);
            } catch (authErr) {
              if (authErr.code === 'auth/user-not-found' || authErr.code === 'auth/invalid-credential' || authErr.code === 'auth/invalid-login-credentials') {
                await createUserWithEmailAndPassword(auth, email, pass);
              } else {
                throw authErr;
              }
            }
          }

          setTimeout(() => {
            hide3DotsLoader();
            authScreen.style.display = "none";
            showWaToast("مرحباً بك في Linko!");
          }, 450);

        } else {
          // 2. حالة الرمز غير مطابق (خاطئ)
          hide3DotsLoader();
          
          if (navigator.vibrate) {
            navigator.vibrate([100, 60, 100]);
          }

          otpBoxes.forEach(b => {
            b.classList.remove('success');
            b.classList.add('error');
          });
          otpContainer.classList.add('shake');
          otpErrorMsg.innerText = "«رمز التحقق غير صحيح، حاول مرة أخرى»";
          otpErrorMsg.style.display = 'block';

          setTimeout(() => {
            otpContainer.classList.remove('shake');
            otpBoxes.forEach(b => {
              b.value = '';
              b.classList.remove('error');
            });
            otpBoxes[0].focus();
          }, 450);
        }

      } catch(err) {
        hide3DotsLoader();
        if (navigator.vibrate) navigator.vibrate([100, 60, 100]);
        otpBoxes.forEach(b => {
          b.classList.remove('success');
          b.classList.add('error');
        });
        otpContainer.classList.add('shake');
        otpErrorMsg.innerText = "«رمز التحقق غير صحيح، حاول مرة أخرى»";
        otpErrorMsg.style.display = 'block';
        setTimeout(() => {
          otpContainer.classList.remove('shake');
          otpBoxes.forEach(b => {
            b.value = '';
            b.classList.remove('error');
          });
          otpBoxes[0].focus();
        }, 450);
      }
    }

    document.getElementById('btn-verify-otp').onclick = () => {
      const code = getEnteredOTP();
      triggerVerifyOTPLogic(code);
    };

    // Navigation Tabs
    const navTabs = document.querySelectorAll('.nav-tab');
    navTabs.forEach(tab => {
      tab.onclick = () => {
        navTabs.forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        tab.classList.add('active');
        document.getElementById(tab.getAttribute('data-tab')).classList.add('active');
      };
    });

    document.getElementById('chat-back-btn').onclick = (e) => {
      e.stopPropagation();
      document.getElementById('chat-screen').classList.remove('active');
      activeChatContact = null;
      document.getElementById('emoji-picker').classList.remove('active');
      resetVoiceRecordingUI();
    };

    // Open Profile Screen
    document.getElementById('chat-header-clickable').onclick = () => {
      if (!activeChatContact) return;
      const contactName = (activeChatContact.name && activeChatContact.name !== 'undefined') ? activeChatContact.name : "مستخدم";
      const contactDp = activeChatContact.dpUrl || emojiToSVG(activeChatContact.emoji || contactName.substring(0,2));
      
      document.getElementById('contact-view-name').innerText = contactName;
      document.getElementById('contact-view-id').innerText = activeChatContact.userId || "ar-0000";
      document.getElementById('contact-view-dp').src = contactDp;

      document.getElementById('profile-mini-name').innerText = contactName;
      document.getElementById('profile-mini-dp').src = contactDp;

      const isMuted = activeChatContact.isMuted === true;
      document.getElementById('notif-toggle-switch').checked = !isMuted;
      document.getElementById('profile-bell-icon').className = isMuted ? "far fa-bell-slash profile-item-icon" : "far fa-bell profile-item-icon";

      const isLocked = activeChatContact.isLocked === true;
      document.getElementById('chatlock-toggle-switch').checked = isLocked;
      document.getElementById('chatlock-icon').style.color = isLocked ? "var(--primary-color)" : "#8696a0";

      const isBlocked = activeChatContact.isBlocked === true;
      document.getElementById('block-user-text').innerText = isBlocked ? `رفع الحظر عن ${contactName}` : `حظر ${contactName}`;
      document.getElementById('report-user-text').innerText = `الإبلاغ عن ${contactName}`;

      const isDataBlocked = activeChatContact.isDataBlocked === true;
      document.getElementById('datablock-toggle-switch').checked = isDataBlocked;

      const profScreen = document.getElementById('contact-profile-screen');
      profScreen.scrollTop = 0;
      
      document.getElementById('profile-header-collapsed-info').classList.remove('visible');
      document.getElementById('profile-top-bar').style.background = '#0b1014';
      document.getElementById('profile-top-bar').style.borderBottom = '1px solid transparent';
      
      profScreen.classList.add('active');
      document.getElementById('profile-dropdown-menu').classList.remove('active');

      loadRealStorageData();
    };

    document.getElementById('profile-back-btn').onclick = () => {
      document.getElementById('contact-profile-screen').classList.remove('active');
      document.getElementById('profile-dropdown-menu').classList.remove('active');
    };

    // Scroll Profile Header
    const contactProfileScreen = document.getElementById('contact-profile-screen');
    const collapsedHeaderInfo = document.getElementById('profile-header-collapsed-info');
    const profileTopBar = document.getElementById('profile-top-bar');

    contactProfileScreen.addEventListener('scroll', () => {
      if (contactProfileScreen.scrollTop > 85) {
        collapsedHeaderInfo.classList.add('visible');
        profileTopBar.style.background = '#111b21';
        profileTopBar.style.borderBottom = '1px solid #1f2c34';
      } else {
        collapsedHeaderInfo.classList.remove('visible');
        profileTopBar.style.background = '#0b1014';
        profileTopBar.style.borderBottom = '1px solid transparent';
      }
    });

    // Avatar Zoom Fullscreen
    const fullscreenAvatarViewer = document.getElementById('fullscreen-avatar-viewer');
    const avatarViewerImg = document.getElementById('avatar-viewer-img');
    const avatarViewerName = document.getElementById('avatar-viewer-name');

    function openFullscreenAvatar(imgUrl, titleName) {
      avatarViewerImg.src = imgUrl;
      avatarViewerName.innerText = titleName || "صورة الحساب";
      fullscreenAvatarViewer.classList.add('active');
    }

    document.getElementById('contact-view-dp').onclick = () => {
      if (activeChatContact) {
        const contactName = activeChatContact.name || "مستخدم";
        const contactDp = activeChatContact.dpUrl || emojiToSVG(contactName.substring(0, 2));
        openFullscreenAvatar(contactDp, contactName);
      }
    };

    document.getElementById('profile-mini-dp').onclick = () => {
      if (activeChatContact) {
        const contactName = activeChatContact.name || "مستخدم";
        const contactDp = activeChatContact.dpUrl || emojiToSVG(contactName.substring(0, 2));
        openFullscreenAvatar(contactDp, contactName);
      }
    };

    document.getElementById('chat-header-dp').onclick = (e) => {
      e.stopPropagation();
      if (activeChatContact) {
        const contactName = activeChatContact.name || "مستخدم";
        const contactDp = activeChatContact.dpUrl || emojiToSVG(contactName.substring(0, 2));
        openFullscreenAvatar(contactDp, contactName);
      }
    };

    document.getElementById('my-profile-dp').onclick = () => {
      if (currentProfile) {
        const myName = currentProfile.name || "حسابي الشخصي";
        const myDp = currentProfile.dpUrl || emojiToSVG("ME");
        openFullscreenAvatar(myDp, myName);
      }
    };

    document.getElementById('avatar-viewer-back-btn').onclick = () => {
      fullscreenAvatarViewer.classList.remove('active');
    };

    // Edit Contact Screen
    const profileDropdownMenu = document.getElementById('profile-dropdown-menu');
    document.getElementById('profile-menu-dots-btn').onclick = (e) => {
      e.stopPropagation();
      profileDropdownMenu.classList.toggle('active');
    };

    document.addEventListener('click', () => {
      profileDropdownMenu.classList.remove('active');
    });

    document.getElementById('menu-opt-edit-contact').onclick = (e) => {
      e.stopPropagation();
      profileDropdownMenu.classList.remove('active');
      if (!activeChatContact) return;

      const currentFullName = (activeChatContact.name && activeChatContact.name !== 'undefined') ? activeChatContact.name : "";
      const nameParts = currentFullName.trim().split(/\\s+/);
      const firstName = nameParts[0] || "";
      const familyName = nameParts.slice(1).join(' ') || "";

      document.getElementById('edit-first-name').value = firstName;
      document.getElementById('edit-family-name').value = familyName;
      document.getElementById('edit-username-field').value = activeChatContact.userId || "";
      
      document.getElementById('edit-contact-screen').classList.add('active');
    };

    document.getElementById('edit-contact-back-btn').onclick = () => {
      document.getElementById('edit-contact-screen').classList.remove('active');
    };

    document.getElementById('save-contact-edit-btn').onclick = async () => {
      const firstName = document.getElementById('edit-first-name').value.trim();
      const familyName = document.getElementById('edit-family-name').value.trim();
      const newFullName = (firstName + " " + familyName).trim();
      if (!newFullName || !activeChatContact) return;

      try {
        await set(ref(db, `contacts/${currentUser.uid}/${activeChatContact.uid}/customName`), newFullName);
      } catch(e) { console.log(e); }

      activeChatContact.name = newFullName;
      if (allContactsCache[activeChatContact.uid]) allContactsCache[activeChatContact.uid].name = newFullName;

      document.getElementById('chat-header-name').innerText = newFullName;
      document.getElementById('contact-view-name').innerText = newFullName;
      document.getElementById('profile-mini-name').innerText = newFullName;
      
      document.getElementById('edit-contact-screen').classList.remove('active');
      showWaToast("تم حفظ جهة الاتصال بنجاح");
    };

    // My Profile Editing
    document.getElementById('open-edit-profile').onclick = () => {
      if (!currentProfile) return;
      document.getElementById('my-edit-name-input').value = currentProfile.name || "";
      document.getElementById('my-edit-bio-input').value = currentProfile.bio || "متوفر";
      document.getElementById('edit-profile-modal').classList.add('active');
    };

    document.getElementById('close-my-profile-btn').onclick = () => {
      document.getElementById('edit-profile-modal').classList.remove('active');
    };

    document.getElementById('save-my-profile-btn').onclick = async () => {
      const newName = document.getElementById('my-edit-name-input').value.trim();
      const newBio = document.getElementById('my-edit-bio-input').value.trim();
      if (!newName || !currentUser) return;

      await update(ref(db, `users/${currentUser.uid}`), { name: newName, bio: newBio });
      currentProfile.name = newName;
      currentProfile.bio = newBio;

      document.getElementById('my-profile-name').innerText = newName;
      document.getElementById('my-profile-bio').innerText = newBio;
      document.getElementById('edit-profile-modal').classList.remove('active');
      showWaToast("تم تحديث ملفك الشخصي");
    };

    // الإشعارات
    const notifTermsModal = document.getElementById('notif-terms-modal');
    const notifSwitch = document.getElementById('notif-toggle-switch');

    document.getElementById('profile-opt-notifications').onclick = () => {
      if (notifSwitch.checked) {
        notifTermsModal.classList.add('active');
      } else {
        updateMuteStatus(false);
      }
    };

    document.getElementById('btn-notif-cancel').onclick = () => notifTermsModal.classList.remove('active');
    document.getElementById('btn-notif-agree').onclick = () => {
      notifTermsModal.classList.remove('active');
      updateMuteStatus(true);
    };

    function updateMuteStatus(isMuted) {
      if (!currentUser || !activeChatContact) return;
      activeChatContact.isMuted = isMuted;
      if (allContactsCache[activeChatContact.uid]) allContactsCache[activeChatContact.uid].isMuted = isMuted;
      notifSwitch.checked = !isMuted;
      document.getElementById('profile-bell-icon').className = isMuted ? "far fa-bell-slash profile-item-icon" : "far fa-bell profile-item-icon";
      set(ref(db, `contacts/${currentUser.uid}/${activeChatContact.uid}/isMuted`), isMuted).catch(console.error);
      showWaToast(isMuted ? "تم كتم الإشعارات لهذه المحادثة" : "تم تشغيل الإشعارات");
    }

    // إيقاف البيانات
    const datablockTermsModal = document.getElementById('datablock-terms-modal');
    const datablockSwitch = document.getElementById('datablock-toggle-switch');

    document.getElementById('profile-opt-datablock').onclick = () => {
      const isCurrentlyBlocked = activeChatContact && activeChatContact.isDataBlocked === true;
      if (!isCurrentlyBlocked) {
        datablockTermsModal.classList.add('active');
      } else {
        updateDataBlockStatus(false);
      }
    };

    document.getElementById('btn-datablock-cancel').onclick = () => datablockTermsModal.classList.remove('active');
    document.getElementById('btn-datablock-agree').onclick = () => {
      datablockTermsModal.classList.remove('active');
      updateDataBlockStatus(true);
    };

    async function updateDataBlockStatus(isBlocked) {
      if (!currentUser || !activeChatContact) return;
      activeChatContact.isDataBlocked = isBlocked;
      datablockSwitch.checked = isBlocked;

      if (allContactsCache[activeChatContact.uid]) {
        allContactsCache[activeChatContact.uid].isDataBlocked = isBlocked;
      }

      const banner = document.getElementById('datablock-notice-banner');
      if (banner) banner.style.display = isBlocked ? 'block' : 'none';

      try {
        await set(ref(db, `contacts/${currentUser.uid}/${activeChatContact.uid}/isDataBlocked`), isBlocked);
      } catch(err) { console.log(err); }

      showWaToast(isBlocked ? "🚫 تم إيقاف بيانات الشبكة عن هذه المحادثة" : "✅ تم تشغيل البيانات للمحادثة");
    }

    // نظام المكالمات
    function updateCallDurationDisplay() {
      if (!callStartTimestamp) return;
      const elapsedSec = Math.floor((Date.now() - callStartTimestamp) / 1000);
      const mins = Math.floor(elapsedSec / 60);
      const secs = elapsedSec % 60;
      const formatted = `${mins}:${secs < 10 ? '0' : ''}${secs}`;
      document.getElementById('call-status').innerText = formatted;
    }

    function togglePiPVideoSwap() {
      if (!isCallVideoMode) return;
      isPiPViewSwapped = !isPiPViewSwapped;
      const localVid = document.getElementById('local-video');
      const remoteVid = document.getElementById('remote-video');

      if (isPiPViewSwapped) {
        localVid.className = 'call-video-main';
        remoteVid.className = 'call-video-pip';
        remoteVid.style.display = 'block';
        localVid.style.display = 'block';
      } else {
        localVid.className = 'call-video-pip';
        remoteVid.className = 'call-video-main';
        remoteVid.style.display = 'block';
        localVid.style.display = 'block';
      }
    }

    document.getElementById('local-video').onclick = togglePiPVideoSwap;
    document.getElementById('remote-video').onclick = () => {
      if (isPiPViewSwapped) togglePiPVideoSwap();
    };

    async function startCall(isVideo = false) {
      if (!activeChatContact) return;
      if (activeChatContact.isBlocked === true || activeChatContact.isDataBlocked === true) {
        alert("⚠️ لا يمكن إجراء مكالمات حالياً مع هذه الجهة.");
        return;
      }

      isCallVideoMode = isVideo;
      isMicMuted = false;
      isSpeakerActive = true;
      currentFacingMode = "user";
      isPiPViewSwapped = false;

      const contactName = activeChatContact.name || "مستخدم";
      const contactDp = activeChatContact.dpUrl || emojiToSVG(contactName.substring(0, 2));

      document.getElementById('call-user-name').innerText = contactName;
      document.getElementById('call-user-avatar').src = contactDp;
      document.getElementById('call-status').innerText = "يتصل...";

      setupCallUIState(isVideo);
      document.getElementById('call-screen').classList.add('active');

      startOutgoingRinging();

      try {
        localStream = await navigator.mediaDevices.getUserMedia({
          video: isVideo ? { facingMode: currentFacingMode } : false,
          audio: true
        });

        if (isVideo) {
          const localVid = document.getElementById('local-video');
          localVid.srcObject = localStream;
          localVid.style.display = "block";
        }

        peerConnection = new RTCPeerConnection(rtcConfig);
        localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream));

        peerConnection.ontrack = (event) => {
          const remoteVid = document.getElementById('remote-video');
          remoteVid.srcObject = event.streams[0];
          if (isCallVideoMode) {
            remoteVid.style.display = "block";
            document.getElementById('call-audio-avatar-box').style.display = "none";
          }
        };

        const callId = push(ref(db, 'calls')).key;
        activeCallId = callId;

        const offer = await peerConnection.createOffer();
        await peerConnection.setLocalDescription(offer);

        await set(ref(db, `calls/${callId}`), {
          offer: { type: offer.type, sdp: offer.sdp },
          caller: currentUser.uid,
          callerName: currentProfile?.name || "مستخدم",
          callerDp: currentProfile?.dpUrl || emojiToSVG(currentProfile?.name?.substring(0,2)),
          targetUid: activeChatContact.uid,
          isVideo
        });

        await set(ref(db, `incomingCalls/${activeChatContact.uid}`), {
          callId,
          callerName: currentProfile?.name || "مستخدم",
          callerDp: currentProfile?.dpUrl || emojiToSVG(currentProfile?.name?.substring(0,2)),
          isVideo
        });

        onValue(ref(db, `calls/${callId}/answer`), async (snap) => {
          if (snap.exists() && !peerConnection.currentRemoteDescription) {
            stopOutgoingRinging();
            const answer = snap.val();
            await peerConnection.setRemoteDescription(new RTCSessionDescription(answer));
            callStartTimestamp = Date.now();
            clearInterval(callTimerInterval);
            callTimerInterval = setInterval(updateCallDurationDisplay, 1000);
          }
        });

        onValue(ref(db, `calls/${callId}/ended`), (snap) => {
          if (snap.val() === true) endCall(false);
        });

      } catch (err) {
        stopOutgoingRinging();
        alert("يرجى إعطاء صلاحيات الميكروفون والكاميرا لإجراء المكالمة.");
        endCall();
      }
    }

    function setupCallUIState(isVideo) {
      const sideBar = document.getElementById('call-video-side-bar');
      const avatarBox = document.getElementById('call-audio-avatar-box');
      const remoteVid = document.getElementById('remote-video');
      const localVid = document.getElementById('local-video');
      const doodleBg = document.getElementById('call-doodle-layer');

      isPiPViewSwapped = false;
      localVid.className = 'call-video-pip';
      remoteVid.className = 'call-video-main';

      if (isVideo) {
        sideBar.classList.add('active');
        avatarBox.style.display = 'none';
        remoteVid.style.display = 'block';
        localVid.style.display = 'block';
        doodleBg.style.display = 'none';
      } else {
        sideBar.classList.remove('active');
        avatarBox.style.display = 'flex';
        remoteVid.style.display = 'none';
        localVid.style.display = 'none';
        doodleBg.style.display = 'block';
      }
    }

    document.getElementById('btn-unified-mute-toggle').onclick = () => {
      if (!localStream) return;
      isMicMuted = !isMicMuted;
      localStream.getAudioTracks().forEach(track => { track.enabled = !isMicMuted; });
      
      const muteBtn = document.getElementById('btn-unified-mute-toggle');
      if (isMicMuted) muteBtn.classList.add('active-white');
      else muteBtn.classList.remove('active-white');
    };

    document.getElementById('btn-unified-speaker-toggle').onclick = () => {
      isSpeakerActive = !isSpeakerActive;
      const speakerBtn = document.getElementById('btn-unified-speaker-toggle');
      if (isSpeakerActive) {
        speakerBtn.classList.add('active-white');
        speakerBtn.innerHTML = '<i class="fas fa-volume-up"></i>';
        showWaToast("مكبر الصوت: مفعّل");
      } else {
        speakerBtn.classList.remove('active-white');
        speakerBtn.innerHTML = '<i class="fas fa-volume-down"></i>';
        showWaToast("سماعة الأذن: مفعّلة");
      }
    };

    document.getElementById('btn-switch-camera-flip').onclick = async () => {
      if (!localStream || !isCallVideoMode) return;
      currentFacingMode = currentFacingMode === "user" ? "environment" : "user";
      try {
        const newStream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: currentFacingMode },
          audio: true
        });
        const videoTrack = newStream.getVideoTracks()[0];
        const sender = peerConnection.getSenders().find(s => s.track && s.track.kind === 'video');
        if (sender) sender.replaceTrack(videoTrack);
        
        document.getElementById('local-video').srcObject = newStream;
        localStream = newStream;
      } catch(e) {}
    };

    document.getElementById('btn-unified-video-toggle').onclick = async () => {
      try {
        isCallVideoMode = !isCallVideoMode;
        setupCallUIState(isCallVideoMode);
        
        if (isCallVideoMode) {
          const vidStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" }, audio: true });
          const vidTrack = vidStream.getVideoTracks()[0];
          peerConnection.addTrack(vidTrack, vidStream);
          document.getElementById('local-video').srcObject = vidStream;
          localStream = vidStream;
        } else {
          if (localStream) {
            localStream.getVideoTracks().forEach(t => t.stop());
          }
        }
      } catch(e) {}
    };

    function endCall(sendEndSignal = true) {
      stopOutgoingRinging();
      stopIncomingRinging();
      clearInterval(callTimerInterval);
      callTimerInterval = null;
      callStartTimestamp = 0;

      if (localStream) {
        localStream.getTracks().forEach(t => t.stop());
        localStream = null;
      }
      if (peerConnection) {
        peerConnection.close();
        peerConnection = null;
      }

      if (activeCallId && sendEndSignal) {
        set(ref(db, `calls/${activeCallId}/ended`), true).catch(console.error);
      }

      document.getElementById('call-screen').classList.remove('active');
      document.getElementById('incoming-call-dialog').classList.remove('active');
      document.getElementById('remote-video').srcObject = null;
      document.getElementById('local-video').srcObject = null;
      activeCallId = null;
      isCallVideoMode = false;
      isPiPViewSwapped = false;
    }

    document.getElementById('btn-unified-end-call').onclick = () => endCall(true);
    document.getElementById('btn-call-minimize').onclick = () => {
      document.getElementById('call-screen').classList.remove('active');
      showWaToast("المكالمة مستمرة في الخلفية");
    };

    document.getElementById('voice-call-btn').onclick = () => startCall(false);
    document.getElementById('video-call-btn').onclick = () => startCall(true);
    document.getElementById('profile-voice-btn').onclick = () => startCall(false);
    document.getElementById('profile-video-btn').onclick = () => startCall(true);

    function listenForIncomingCalls(uid) {
      onValue(ref(db, `incomingCalls/${uid}`), async (snap) => {
        const callData = snap.val();
        if (callData) {
          startIncomingRinging();
          const incomingDialog = document.getElementById('incoming-call-dialog');
          document.getElementById('inc-caller-name').innerText = callData.callerName || "مستخدم";
          document.getElementById('inc-caller-avatar').src = callData.callerDp || emojiToSVG("AR");
          document.getElementById('inc-call-type-text').innerText = callData.isVideo ? "مكالمة فيديو واردة..." : "مكالمة صوتية واردة...";
          incomingDialog.classList.add('active');

          document.getElementById('btn-inc-accept').onclick = async () => {
            stopIncomingRinging();
            incomingDialog.classList.remove('active');
            activeCallId = callData.callId;
            isCallVideoMode = callData.isVideo;

            document.getElementById('call-user-name').innerText = callData.callerName;
             document.getElementById('call-user-avatar').src = callData.callerDp;
            setupCallUIState(callData.isVideo);
            document.getElementById('call-screen').classList.add('active');

            localStream = await navigator.mediaDevices.getUserMedia({
              video: callData.isVideo ? { facingMode: "user" } : false,
              audio: true
            });

            if (callData.isVideo) {
              document.getElementById('local-video').srcObject = localStream;
              document.getElementById('local-video').style.display = "block";
            }

            peerConnection = new RTCPeerConnection(rtcConfig);
            localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream));

            peerConnection.ontrack = (e) => {
              document.getElementById('remote-video').srcObject = e.streams[0];
              if (callData.isVideo) {
                document.getElementById('remote-video').style.display = "block";
                document.getElementById('call-audio-avatar-box').style.display = "none";
              }
            };

            const callSnap = await get(ref(db, `calls/${callData.callId}/offer`));
            await peerConnection.setRemoteDescription(new RTCSessionDescription(callSnap.val()));

            const answer = await peerConnection.createAnswer();
            await peerConnection.setLocalDescription(answer);

            await set(ref(db, `calls/${callData.callId}/answer`), {
              type: answer.type,
              sdp: answer.sdp
            });

            await remove(ref(db, `incomingCalls/${uid}`));
            callStartTimestamp = Date.now();
            clearInterval(callTimerInterval);
            callTimerInterval = setInterval(updateCallDurationDisplay, 1000);
          };

          document.getElementById('btn-inc-decline').onclick = async () => {
            stopIncomingRinging();
            incomingDialog.classList.remove('active');
            await set(ref(db, `calls/${callData.callId}/ended`), true);
            await remove(ref(db, `incomingCalls/${uid}`));
          };
        }
      });
    }

    // إرسال واستلام الرسائل
    function renderStatusTickHTML(status, isTargetOnline) {
      if (status === 'pending') {
        return `<i class="far fa-clock" style="font-size:10px; color:#8696a0;"></i>`;
      } else if (status === 'sent') {
        return `<span style="color:#8696a0; font-size:11px; font-weight:bold;">✓</span>`;
      } else if (status === 'delivered') {
        return `<span style="color:#8696a0; font-size:11.5px; font-weight:bold; letter-spacing:-2.5px; margin-left:2px;">✓✓</span>`;
      } else if (status === 'read' || isTargetOnline) {
        return `<span style="color:#34b7f1; font-size:11.5px; font-weight:bold; letter-spacing:-2.5px; margin-left:2px;">✓✓</span>`;
      }
      return `<span style="color:#8696a0; font-size:11px; font-weight:bold;">✓</span>`;
    }

    async function sendTextMessage() {
      const chatInput = document.getElementById('chat-input');
      const text = chatInput.value.trim();
      if (!text || !activeChatContact) return;

      if (activeChatContact.isBlocked === true) {
        alert("⚠️ لا يمكنك إرسال رسائل لأنك قمت بحظر هذا المستخدم.");
        return;
      }
      if (activeChatContact.isDataBlocked === true) {
        alert("⚠️ تم إيقاف بيانات هذه المحادثة بالكامل.");
        return;
      }

      playSendTone();

      const chatId = [currentUser.uid, activeChatContact.uid].sort().join('_');
      const targetUid = activeChatContact.uid;
      const msgRef = push(ref(db, `messages/${chatId}`));
      const msgId = msgRef.key;

      chatInput.value = "";
      document.getElementById('main-mic-btn').classList.remove('typing-mode');
      document.getElementById('main-mic-icon').className = "fas fa-microphone";
      document.getElementById('emoji-picker').classList.remove('active');

      await set(msgRef, {
        sender: currentUser.uid,
        text,
        type: 'text',
        timestamp: Date.now(),
        status: 'pending'
      });

      setTimeout(async () => {
        const targetStatusSnap = await get(ref(db, `status/${targetUid}`));
        const isOnline = targetStatusSnap.val()?.state === 'online';
        const finalStatus = isOnline ? 'delivered' : 'sent';
        await update(ref(db, `messages/${chatId}/${msgId}`), { status: finalStatus });
      }, 2000);
    }

    const mainMicBtn = document.getElementById('main-mic-btn');
    const mainMicIcon = document.getElementById('main-mic-icon');
    const chatInput = document.getElementById('chat-input');
    const normalInputBar = document.getElementById('normal-input-bar');
    const swipeCancelBar = document.getElementById('swipe-cancel-bar');
    const verticalLockCapsule = document.getElementById('vertical-lock-capsule');
    const lockedRecordingPanel = document.getElementById('locked-recording-panel');

    chatInput.oninput = () => {
      if (chatInput.value.trim().length > 0) {
        mainMicBtn.classList.add('typing-mode');
        mainMicIcon.className = "fas fa-paper-plane";
      } else {
        mainMicBtn.classList.remove('typing-mode');
        mainMicIcon.className = "fas fa-microphone";
      }
      if (!activeChatContact || activeChatContact.isDataBlocked === true || activeChatContact.isBlocked === true) return;
      const chatId = [currentUser.uid, activeChatContact.uid].sort().join('_');
      set(ref(db, `typing/${chatId}/${currentUser.uid}`), true);
      setTimeout(() => set(ref(db, `typing/${chatId}/${currentUser.uid}`), false), 1500);
    };

    chatInput.onkeydown = (e) => {
      if (e.key === 'Enter') sendTextMessage();
    };

    mainMicBtn.onclick = () => {
      if (chatInput.value.trim().length > 0) sendTextMessage();
    };

    async function startVoiceRecording() {
      if (activeChatContact?.isBlocked === true) return alert("⚠️ لا يمكنك تسجيل الصوت لأنك قمت بحظر هذا المستخدم.");
      if (activeChatContact?.isDataBlocked === true) return alert("⚠️ تم إيقاف بيانات هذه المحادثة بالكامل.");

      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);
        mediaRecorder.onstop = () => { clearInterval(recordTimerInterval); };

        mediaRecorder.start(100);
        recordStartTime = Date.now();
        isRecordingLocked = false;
        isRecordingPaused = false;

        mainMicBtn.classList.add('recording');
        normalInputBar.style.display = 'none';
        swipeCancelBar.classList.add('active');
        verticalLockCapsule.classList.add('active');

        recordTimerInterval = setInterval(() => {
          if (!isRecordingPaused) {
            const diff = Date.now() - recordStartTime;
            recordedDurationSec = Math.floor(diff / 1000);
            const mins = Math.floor(diff / 60000);
            const secs = Math.floor((diff % 60000) / 1000);
            const timeFormatted = `${mins}:${secs < 10 ? '0' : ''}${secs}`;
            document.getElementById('recording-inline-timer').innerText = timeFormatted;
            document.getElementById('locked-timer-display').innerText = timeFormatted;
          }
        }, 150);

      } catch (err) {
        alert("يرجى إعطاء صلاحية الميكروفون لتسجيل الصوت.");
        resetVoiceRecordingUI();
      }
    }

    mainMicBtn.addEventListener('touchstart', (e) => {
      if (chatInput.value.trim().length > 0) return;
      e.preventDefault();
      touchStartY = e.touches[0].clientY;
      touchStartX = e.touches[0].clientX;
      isHoldingMic = true;
      startVoiceRecording();
    }, { passive: false });

    mainMicBtn.addEventListener('touchmove', (e) => {
      if (!isHoldingMic || isRecordingLocked || !mediaRecorder) return;
      const currentY = e.touches[0].clientY;
      const currentX = e.touches[0].clientX;
      const diffY = touchStartY - currentY;
      const diffX = touchStartX - currentX;

      if (diffY > 40) lockVoiceRecording();
      else if (diffX > 75 || diffX < -75) { isHoldingMic = false; resetVoiceRecordingUI(); }
    });

    mainMicBtn.addEventListener('touchend', (e) => {
      if (chatInput.value.trim().length > 0) return;
      if (!isHoldingMic) return;
      isHoldingMic = false;

      if (!isRecordingLocked && mediaRecorder && mediaRecorder.state === 'recording') {
        if (recordedDurationSec >= 1) sendRecordedVoice();
        else resetVoiceRecordingUI();
      }
    });

    mainMicBtn.onmousedown = () => {
      if (chatInput.value.trim().length > 0) return;
      isHoldingMic = true;
      startVoiceRecording();
    };

    window.addEventListener('mouseup', () => {
      if (isHoldingMic && !isRecordingLocked && mediaRecorder && mediaRecorder.state === 'recording') {
        isHoldingMic = false;
        if (recordedDurationSec >= 1) sendRecordedVoice();
        else resetVoiceRecordingUI();
      }
    });

    function lockVoiceRecording() {
      if (!mediaRecorder || mediaRecorder.state !== 'recording') return;
      isRecordingLocked = true;
      verticalLockCapsule.classList.remove('active');
      swipeCancelBar.classList.remove('active');
      lockedRecordingPanel.classList.add('active');
    }

    verticalLockCapsule.onclick = lockVoiceRecording;

    document.getElementById('btn-pause-locked').onclick = () => {
      if (!mediaRecorder) return;
      if (!isRecordingPaused) {
        mediaRecorder.pause();
        isRecordingPaused = true;
        document.getElementById('pause-btn-text').innerText = "استئناف";
        document.getElementById('btn-pause-locked').innerHTML = `<i class="fas fa-play"></i> <span>استئناف</span>`;
      } else {
        mediaRecorder.resume();
        isRecordingPaused = false;
        document.getElementById('pause-btn-text').innerText = "إيقاف مؤقت";
        document.getElementById('btn-pause-locked').innerHTML = `<i class="fas fa-pause"></i> <span>إيقاف مؤقت</span>`;
      }
    };

    document.getElementById('btn-view-once').onclick = (e) => {
      isViewOnceActive = !isViewOnceActive;
      e.target.classList.toggle('active', isViewOnceActive);
    };

    function resetVoiceRecordingUI() {
      clearInterval(recordTimerInterval);
      if (mediaRecorder && mediaRecorder.state !== 'inactive') mediaRecorder.stop();
      mediaRecorder = null;
      isHoldingMic = false;
      isRecordingLocked = false;
      isRecordingPaused = false;
      isViewOnceActive = false;

      mainMicBtn.classList.remove('recording');
      normalInputBar.style.display = 'flex';
      swipeCancelBar.classList.remove('active');
      verticalLockCapsule.classList.remove('active');
      lockedRecordingPanel.classList.remove('active');
      document.getElementById('btn-view-once').classList.remove('active');
      mainMicBtn.classList.remove('typing-mode');
      mainMicIcon.className = "fas fa-microphone";
    }

    document.getElementById('btn-trash-locked').onclick = resetVoiceRecordingUI;

    async function sendRecordedVoice() {
      if (!mediaRecorder) return;
      mediaRecorder.stop();
      lockedRecordingPanel.classList.remove('active');

      setTimeout(async () => {
        if (audioChunks.length > 0 && activeChatContact) {
          playSendTone();
          const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
          const reader = new FileReader();
          reader.readAsDataURL(audioBlob);
          reader.onloadend = async () => {
            const chatId = [currentUser.uid, activeChatContact.uid].sort().join('_');
            const mins = Math.floor(recordedDurationSec / 60);
            const secs = recordedDurationSec % 60;
            const durStr = `${mins}:${secs < 10 ? '0' : ''}${secs}`;

            await push(ref(db, `messages/${chatId}`), {
              sender: currentUser.uid,
              audioData: reader.result,
              duration: durStr,
              viewOnce: isViewOnceActive,
              type: 'audio',
              timestamp: Date.now(),
              status: 'sent'
            });
            resetVoiceRecordingUI();
          };
        }
      }, 150);
    }

    document.getElementById('btn-send-locked').onclick = sendRecordedVoice;

    // Attach File / Camera
    document.getElementById('attach-file-btn').onclick = () => {
      if (activeChatContact?.isBlocked === true || activeChatContact?.isDataBlocked === true) return alert("⚠️ لا يمكن إرسال صور حالياً.");
      document.getElementById('file-input-image').click();
    };

    document.getElementById('camera-btn').onclick = () => {
      if (activeChatContact?.isBlocked === true || activeChatContact?.isDataBlocked === true) return alert("⚠️ لا يمكن إرسال صور حالياً.");
      document.getElementById('file-input-camera').click();
    };

    async function handleImageUpload(file) {
      if (!file || !activeChatContact) return;
      if (activeChatContact.isDataBlocked === true) return alert("⚠️ تم إيقاف بيانات هذه المحادثة.");
      playSendTone();
      const reader = new FileReader();
      reader.onload = async (e) => {
        const chatId = [currentUser.uid, activeChatContact.uid].sort().join('_');
        await push(ref(db, `messages/${chatId}`), {
          sender: currentUser.uid,
          imgData: e.target.result,
          type: 'image',
          timestamp: Date.now(),
          status: 'sent'
        });
      };
      reader.readAsDataURL(file);
    }

    document.getElementById('file-input-image').onchange = (e) => handleImageUpload(e.target.files[0]);
    document.getElementById('file-input-camera').onchange = (e) => handleImageUpload(e.target.files[0]);

    // Emojis
    document.getElementById('emoji-toggle-btn').onclick = (e) => {
      e.stopPropagation();
      document.getElementById('emoji-picker').classList.toggle('active');
    };

    document.addEventListener('click', (e) => {
      const picker = document.getElementById('emoji-picker');
      if (picker && !picker.contains(e.target) && e.target.id !== 'emoji-toggle-btn') {
        picker.classList.remove('active');
      }
    });

    document.querySelectorAll('.emoji-item').forEach(el => {
      el.onclick = () => {
        chatInput.value += el.innerText;
        mainMicBtn.classList.add('typing-mode');
        mainMicIcon.className = "fas fa-paper-plane";
        document.getElementById('emoji-picker').classList.remove('active');
      };
    });

    // Clear Chat
    document.getElementById('profile-clear-chat-btn').onclick = async () => {
      if (!currentUser || !activeChatContact) return;
      const cName = activeChatContact.name || "مستخدم";
      document.getElementById('clear-sheet-title-text').innerText = `مسح محتوى دردشة "${cName}"...`;
      
      const chatId = [currentUser.uid, activeChatContact.uid].sort().join('_');
      const snap = await get(ref(db, `messages/${chatId}`));
      const msgs = snap.val() || {};
      let totalBytes = 0;
      Object.values(msgs).forEach(m => {
        if (m.type === 'image' && m.imgData) totalBytes += Math.round((m.imgData.length * 3) / 4);
        else if (m.type === 'audio' && m.audioData) totalBytes += Math.round((m.audioData.length * 3) / 4);
        else if (m.text) totalBytes += new Blob([m.text]).size;
      });

      document.getElementById('btn-confirm-clear-wa').innerText = `مسح الدردشة (${formatBytes(totalBytes)})`;
      document.getElementById('modal-clear-chat-wa').classList.add('active');
    };

    document.getElementById('btn-close-clear-sheet').onclick = () => {
      document.getElementById('modal-clear-chat-wa').classList.remove('active');
    };
    document.getElementById('btn-confirm-clear-wa').onclick = async () => {
      document.getElementById('modal-clear-chat-wa').classList.remove('active');
      show3DotsLoader();
      const chatId = [currentUser.uid, activeChatContact.uid].sort().join('_');
      try { await remove(ref(db, `messages/${chatId}`)); } catch(e) { console.log(e); }

      setTimeout(() => {
        hide3DotsLoader();
        showWaToast("تم مسح محتوى الدردشة بنجاح");
        loadRealStorageData();
      }, 500);
    };

    // Block User
    document.getElementById('block-user-btn').onclick = () => {
      if (!activeChatContact) return;
      const isCurrentlyBlocked = activeChatContact.isBlocked === true;
      if (isCurrentlyBlocked) {
        setContactBlockStatus(activeChatContact.uid, false);
      } else {
        const cName = activeChatContact.name || "مستخدم";
        document.getElementById('block-dialog-title').innerText = `حظر ${cName}؟`;
        document.getElementById('check-block-also-report').checked = false;
        document.getElementById('modal-block-wa').classList.add('active');
      }
    };

    document.getElementById('btn-cancel-block-wa').onclick = () => {
      document.getElementById('modal-block-wa').classList.remove('active');
    };
    document.getElementById('btn-confirm-block-wa').onclick = async () => {
      document.getElementById('modal-block-wa').classList.remove('active');
      setContactBlockStatus(activeChatContact.uid, true);
    };

    // Report User
    document.getElementById('report-user-btn').onclick = () => {
      if (!activeChatContact) return;
      const cName = activeChatContact.name || "مستخدم";
      document.getElementById('report-block-title').innerText = `حظر ${cName}`;
      document.getElementById('check-report-also-block').checked = false;
      document.getElementById('modal-report-wa').classList.add('active');
    };

    document.getElementById('btn-cancel-report-wa').onclick = () => {
      document.getElementById('modal-report-wa').classList.remove('active');
    };
    document.getElementById('btn-confirm-report-wa').onclick = async () => {
      const alsoBlock = document.getElementById('check-report-also-block').checked;
      document.getElementById('modal-report-wa').classList.remove('active');
      show3DotsLoader();

      try {
        await push(ref(db, 'reports'), {
          reporter: currentUser.uid,
          reportedUser: activeChatContact.uid,
          timestamp: Date.now()
        });

        if (alsoBlock) {
          await set(ref(db, `contacts/${currentUser.uid}/${activeChatContact.uid}/isBlocked`), true);
          activeChatContact.isBlocked = true;
          if (allContactsCache[activeChatContact.uid]) allContactsCache[activeChatContact.uid].isBlocked = true;
        }
      } catch(e) { console.log(e); }

      setTimeout(() => {
        hide3DotsLoader();
        showWaToast("نشكرك على تقديم البلاغ");
      }, 500);
    };

    async function setContactBlockStatus(targetUid, isBlocked) {
      show3DotsLoader();
      try {
        await set(ref(db, `contacts/${currentUser.uid}/${targetUid}/isBlocked`), isBlocked);
        if (allContactsCache[targetUid]) allContactsCache[targetUid].isBlocked = isBlocked;
        if (activeChatContact && activeChatContact.uid === targetUid) {
          activeChatContact.isBlocked = isBlocked;
          updateChatScreenBlockUI(isBlocked);
          const cName = activeChatContact.name || "مستخدم";
          document.getElementById('block-user-text').innerText = isBlocked ? `رفع الحظر عن ${cName}` : `حظر ${cName}`;
        }
      } catch(e) { console.log(e); }
      
      setTimeout(() => { hide3DotsLoader(); }, 400);
    }

    function updateChatScreenBlockUI(isBlocked) {
      const normalBar = document.getElementById('normal-chat-bottom-wrapper');
      const blockedBar = document.getElementById('blocked-bottom-actions-bar');
      const streamBanner = document.getElementById('blocked-stream-pill');

      if (isBlocked) {
        normalBar.classList.add('hidden');
        blockedBar.classList.add('active');
        streamBanner.classList.add('active');
      } else {
        normalBar.classList.remove('hidden');
        blockedBar.classList.remove('active');
        streamBanner.classList.remove('active');
      }
    }

    document.getElementById('btn-unblock-chat-bottom').onclick = () => {
      if (activeChatContact) setContactBlockStatus(activeChatContact.uid, false);
    };
    document.getElementById('blocked-stream-pill').onclick = () => {
      if (activeChatContact) setContactBlockStatus(activeChatContact.uid, false);
    };

    document.getElementById('btn-delete-chat-bottom').onclick = async () => {
      if (!currentUser || !activeChatContact) return;
      show3DotsLoader();
      const chatId = [currentUser.uid, activeChatContact.uid].sort().join('_');
      try { await remove(ref(db, `messages/${chatId}`)); } catch(e) { console.log(e); }

      setTimeout(() => {
        hide3DotsLoader();
        showWaToast("تم حذف الدردشة");
        document.getElementById('chat-screen').classList.remove('active');
        activeChatContact = null;
      }, 500);
    };

    // Chat Lock Flow
    const chatLockSwitch = document.getElementById('chatlock-toggle-switch');
    const fullscreenPinLockView = document.getElementById('fullscreen-pin-lock-view');
    const chatlockIntroModal = document.getElementById('chatlock-intro-modal');
    const chatlockMethodModal = document.getElementById('chatlock-method-modal');
    const customPinSetupModal = document.getElementById('custom-pin-setup-modal');

    async function checkDeviceBiometricSupport() {
      if (window.PublicKeyCredential && PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable) {
        try { return await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable(); }
        catch(e) { return false; }
      }
      return false;
    }

    async function triggerNativeBiometricAuth() {
      try {
        const challenge = new Uint8Array(32);
        window.crypto.getRandomValues(challenge);
        const cred = await navigator.credentials.create({
          publicKey: {
            challenge: challenge,
            rp: { name: "Linko" },
            user: { id: new Uint8Array(16), name: "user", displayName: "User" },
            pubKeyCredParams: [{ type: "public-key", alg: -7 }],
            authenticatorSelection: { authenticatorAttachment: "platform", userVerification: "required" },
            timeout: 25000
          }
        });
        return cred !== null;
      } catch(e) { return false; }
    }

    document.getElementById('profile-opt-chatlock').onclick = () => {
      const isCurrentlyLocked = activeChatContact && activeChatContact.isLocked === true;
      if (!isCurrentlyLocked) {
        chatlockIntroModal.classList.add('active');
      } else {
        openWhiteLockScreen('toggleLockOff', activeChatContact);
      }
    };

    document.getElementById('btn-intro-continue').onclick = async () => {
      chatlockIntroModal.classList.remove('active');
      const isBiometricSupported = await checkDeviceBiometricSupport();
      const bioOptCard = document.getElementById('opt-method-biometric');
      const pinTitle = document.getElementById('pin-card-title');
      const pinDesc = document.getElementById('pin-card-desc');

      if (isBiometricSupported) {
        bioOptCard.style.display = 'flex';
        pinTitle.innerText = "رمز PIN";
        pinDesc.innerText = "لاستخدام رمز PIN بدلًا من البصمة.";
      } else {
        bioOptCard.style.display = 'none';
        pinTitle.innerText = "استخدام رمز PIN";
        pinDesc.innerText = "جهازك لا يدعم المصادقة بالبصمة، يمكنك استخدام رمز PIN لحماية المحادثة.";
      }
      chatlockMethodModal.classList.add('active');
    };

    document.getElementById('btn-close-method-modal').onclick = () => chatlockMethodModal.classList.remove('active');

    document.getElementById('opt-method-biometric').onclick = async () => {
      chatlockMethodModal.classList.remove('active');
      const verified = await triggerNativeBiometricAuth();
      if (verified) {
        localStorage.setItem('linko_preferred_lock_method', 'biometric');
        await updateSingleLockState(activeChatContact.uid, true);
      } else {
        alert("⚠️ تم إلغاء البصمة أو لم يتم التعرف عليها.");
      }
    };

    document.getElementById('opt-method-pin').onclick = () => {
      chatlockMethodModal.classList.remove('active');
      document.getElementById('custom-new-pin-input').value = "";
      customPinSetupModal.classList.add('active');
    };

    document.getElementById('btn-cancel-new-pin').onclick = () => customPinSetupModal.classList.remove('active');
    document.getElementById('btn-save-new-pin').onclick = async () => {
      const val = document.getElementById('custom-new-pin-input').value.trim();
      if (val.length === 4) {
        localStorage.setItem('linko_user_pin', val);
        localStorage.setItem('linko_preferred_lock_method', 'pin');
        customPinSetupModal.classList.remove('active');
        await updateSingleLockState(activeChatContact.uid, true);
      } else {
        alert("يرجى إدخال رمز PIN مكون من 4 أرقام!");
      }
    };

    function openWhiteLockScreen(actionType, contactData = null) {
      pendingBiometricAction = actionType;
      pendingContactToUnlock = contactData;
      currentEnteredPin = "";
      updateWhitePinDots();
      fullscreenPinLockView.classList.add('active');

      const pref = localStorage.getItem('linko_preferred_lock_method') || 'biometric';
      if (pref === 'biometric') {
        triggerNativeBiometricAuth().then((ok) => {
          if (ok) handleLockAuthenticationSuccess();
        });
      }
    }

    function updateWhitePinDots() {
      for (let i = 1; i <= 4; i++) {
        const dot = document.getElementById(`wdot-${i}`);
        if (dot) {
          if (i <= currentEnteredPin.length) dot.classList.add('filled');
          else dot.classList.remove('filled');
        }
      }
    }

    document.querySelectorAll('.white-key-digit').forEach(btn => {
      btn.onclick = () => {
        if (currentEnteredPin.length < 4) {
          currentEnteredPin += btn.getAttribute('data-val');
          updateWhitePinDots();

          if (currentEnteredPin.length === 4) {
            const savedPin = localStorage.getItem('linko_user_pin') || "1234";
            setTimeout(() => {
              if (currentEnteredPin === savedPin) {
                handleLockAuthenticationSuccess();
              } else {
                alert("❌ كلمة المرور غير صحيحة!");
                currentEnteredPin = "";
                updateWhitePinDots();
              }
            }, 120);
          }
        }
      };
    });

    document.getElementById('white-backspace-action-btn').onclick = () => {
      if (currentEnteredPin.length > 0) {
        currentEnteredPin = currentEnteredPin.slice(0, -1);
        updateWhitePinDots();
      }
    };

    document.getElementById('white-fingerprint-action-btn').onclick = async () => {
      const ok = await triggerNativeBiometricAuth();
      if (ok) {
        handleLockAuthenticationSuccess();
      } else {
        alert("❌ لم يتم التحقق من البصمة. يمكنك إدخال كلمة المرور من لوحة الأرقام.");
      }
    };

    document.getElementById('btn-white-lock-cancel').onclick = () => {
      fullscreenPinLockView.classList.remove('active');
      currentEnteredPin = "";
      pendingBiometricAction = null;
      pendingContactToUnlock = null;
    };

    function handleLockAuthenticationSuccess() {
      fullscreenPinLockView.classList.remove('active');
      currentEnteredPin = "";
      if (pendingBiometricAction === 'unlockChat' && pendingContactToUnlock) {
        proceedOpenChat(pendingContactToUnlock.uid, pendingContactToUnlock);
      } else if (pendingBiometricAction === 'toggleLockOff' && activeChatContact) {
        updateSingleLockState(activeChatContact.uid, false);
      }
      pendingBiometricAction = null;
      pendingContactToUnlock = null;
    }

    async function updateSingleLockState(uid, isLocked) {
      try {
        await set(ref(db, `contacts/${currentUser.uid}/${uid}/isLocked`), isLocked);
      } catch(e) { console.log(e); }
      
      if (allContactsCache[uid]) allContactsCache[uid].isLocked = isLocked;
      if (activeChatContact && activeChatContact.uid === uid) {
        activeChatContact.isLocked = isLocked;
        chatLockSwitch.checked = isLocked;
        document.getElementById('chatlock-icon').style.color = isLocked ? "var(--primary-color)" : "#8696a0";
      }
      showWaToast(isLocked ? "تم قفل المحادثة بنجاح" : "تم إلغاء قفل المحادثة");
    }

    // Media Storage Studio Load
    async function loadRealStorageData() {
      if (!currentUser || !activeChatContact) return;
      const chatId = [currentUser.uid, activeChatContact.uid].sort().join('_');
      const snap = await get(ref(db, `messages/${chatId}`));
      const msgs = snap.val() || {};

      const imgGrid = document.getElementById('storage-images-grid');
      imgGrid.innerHTML = "";
      let hasMedia = false;

      Object.entries(msgs).forEach(([msgId, m]) => {
        if (m.type === 'image' && m.imgData) {
          hasMedia = true;
          const img = document.createElement('img');
          img.className = 'gallery-studio-thumb';
          img.src = m.imgData;
          img.onclick = () => openFullscreenAvatar(m.imgData, "صورة مشتركة");
          imgGrid.appendChild(img);
        }
      });

      if (!hasMedia) {
        imgGrid.innerHTML = `<p style="grid-column: 1/-1; color: var(--text-muted); font-size: 13.5px; text-align: center; padding: 40px 0;">لا توجد وسائط متبادلة بعد</p>`;
      }
    }

    document.getElementById('profile-opt-storage').onclick = () => {
      document.getElementById('storage-screen').classList.add('active');
      loadRealStorageData();
    };

    document.getElementById('storage-back-btn').onclick = () => {
      document.getElementById('storage-screen').classList.remove('active');
    };

    // Contacts search
    document.getElementById('main-search-input').onkeydown = async (e) => {
      if (e.key === 'Enter') {
        const targetId = e.target.value.trim();
        if (!targetId || !currentUser) return;
        show3DotsLoader();
        const snap = await get(ref(db, `userLookup/${targetId}`));
        hide3DotsLoader();
        if (snap.exists()) {
          const targetUid = snap.val();
          await set(ref(db, `contacts/${currentUser.uid}/${targetUid}`), true);
          await set(ref(db, `contacts/${targetUid}/${currentUser.uid}`), true);
          alert("تمت إضافة جهة الاتصال بنجاح!");
          e.target.value = "";
        } else {
          alert("لم يتم العثور على مستخدم بهذا المعرف!");
        }
      }
    };

    // Add Friend Modal
    document.getElementById('fab-add-btn').onclick = () => {
      document.getElementById('friend-id-input').value = "";
      document.getElementById('add-friend-modal').classList.add('active');
    };
    document.getElementById('close-add-friend').onclick = () => {
      document.getElementById('add-friend-modal').classList.remove('active');
    };
    document.getElementById('send-request-btn').onclick = async () => {
      const targetId = document.getElementById('friend-id-input').value.trim();
      if (!targetId || !currentUser) return;
      show3DotsLoader();
      const snap = await get(ref(db, `userLookup/${targetId}`));
      hide3DotsLoader();
      if (snap.exists()) {
        const targetUid = snap.val();
        await set(ref(db, `contacts/${currentUser.uid}/${targetUid}`), true);
        await set(ref(db, `contacts/${targetUid}/${currentUser.uid}`), true);
        alert("تمت إضافة جهة الاتصال بنجاح!");
        document.getElementById('add-friend-modal').classList.remove('active');
      } else {
        alert("لم يتم العثور على هذا المعرف!");
      }
    };

    onAuthStateChanged(auth, async (user) => {
      if (user && isSessionVerifiedByOtp) {
        currentUser = user;
        authScreen.style.display = "none";
        const snap = await get(ref(db, `users/${user.uid}`));
        if (snap.exists()) {
          currentProfile = snap.val();
        } else {
          const randDigits = Math.floor(1000 + Math.random() * 9000);
          const userId = `ar-${randDigits}`;
          const profileData = { name: "مستخدم", userId, dpUrl: emojiToSVG("AR"), bio: "متوفر" };
          await set(ref(db, `users/${user.uid}`), profileData);
          await set(ref(db, `userLookup/${userId}`), user.uid);
          currentProfile = profileData;
        }

        document.getElementById('my-profile-name').innerText = currentProfile.name || "المستخدم";
        document.getElementById('my-profile-id').innerText = currentProfile.userId || "ar-0000";
        document.getElementById('my-profile-bio').innerText = currentProfile.bio || "متوفر";
        document.getElementById('my-profile-dp').src = currentProfile.dpUrl || emojiToSVG("ME");

        setupPresence(user.uid);
        loadContacts(user.uid);
        listenForIncomingCalls(user.uid);
      } else {
        authScreen.style.display = "flex";
      }
    });

    function setupPresence(uid) {
      const userStatusRef = ref(db, `status/${uid}`);
      onValue(ref(db, '.info/connected'), (snap) => {
        if (snap.val() === true) {
          onDisconnect(userStatusRef).set({ state: 'offline', last_changed: serverTimestamp() });
          set(userStatusRef, { state: 'online', last_changed: serverTimestamp() });
        }
      });
    }

    function loadContacts(uid) {
      onValue(ref(db, `contacts/${uid}`), async (snap) => {
        const listEl = document.getElementById('contacts-list');
        listEl.innerHTML = "";
        const contacts = snap.val() || {};
        allContactsCache = {};

        const userFetchPromises = Object.keys(contacts).map(async (cUid) => {
          const uSnap = await get(ref(db, `users/${cUid}`));
          return { cUid, userData: uSnap.val() || {}, meta: typeof contacts[cUid] === 'object' ? contacts[cUid] : {} };
        });

        const results = await Promise.all(userFetchPromises);

        results.forEach(({ cUid, userData, meta }) => {
          const contactName = (meta.customName || userData.name && userData.name !== 'undefined') ? (meta.customName || userData.name) : "مستخدم";
          const contactId = userData.userId || "";
          const contactBio = userData.bio || "انقر لبدء المحادثة";
          const contactDp = userData.dpUrl || emojiToSVG(userData.emoji || contactName.substring(0, 2));
          const isLocked = meta.isLocked === true;
          const isDataBlocked = meta.isDataBlocked === true;
          const isBlocked = meta.isBlocked === true;

          const fullData = { ...userData, uid: cUid, name: contactName, dpUrl: contactDp, isMuted: meta.isMuted, isLocked: isLocked, isDataBlocked: isDataBlocked, isBlocked: isBlocked };
          allContactsCache[cUid] = fullData;

          const item = document.createElement('div');
          item.className = "chat-item";
          item.innerHTML = `
            <div class="avatar-wrapper">
              <img class="avatar" src="${contactDp}">
              <div class="status-dot status-online" id="status-dot-${cUid}"></div>
            </div>
            <div class="chat-item-info">
              <div class="chat-item-top">
                <span class="chat-item-name">
                  ${contactName}
                  ${isLocked ? '<i class="fas fa-lock" style="font-size:12px; color:var(--primary-color); margin-right:4px;" title="دردشة مقفلة"></i>' : ''}
                  ${isBlocked ? '<i class="fas fa-ban" style="font-size:12px; color:var(--danger-color); margin-right:4px;" title="محظور"></i>' : ''}
                </span>
                <span class="chat-item-time">${contactId}</span>
              </div>
              <div class="chat-item-bottom">
                <span class="chat-item-msg">${contactBio}</span>
              </div>
            </div>
          `;

          item.onclick = () => {
            if (isLocked) {
              openWhiteLockScreen('unlockChat', fullData);
            } else {
              proceedOpenChat(cUid, fullData);
            }
          };

          listEl.appendChild(item);

          onValue(ref(db, `status/${cUid}`), (stSnap) => {
            const dot = document.getElementById(`status-dot-${cUid}`);
            if (dot) {
              const isOnline = stSnap.val()?.state === 'online';
              dot.className = `status-dot ${isOnline ? 'status-online' : 'status-offline'}`;
            }
          });

          setupBackgroundNotificationListener(uid, cUid, contactName, contactDp, meta.isMuted, isDataBlocked, isBlocked);
        });
      });
    }

    function setupBackgroundNotificationListener(myUid, contactUid, contactName, contactDp, isMuted, isDataBlocked, isBlocked) {
      const chatId = [myUid, contactUid].sort().join('_');
      if (activeMessageListeners[chatId]) return;
      activeMessageListeners[chatId] = true;

      let isInitialLoad = true;
      onValue(ref(db, `messages/${chatId}`), (snap) => {
        if (isInitialLoad) { isInitialLoad = false; return; }
        const msgs = snap.val() || {};
        const msgKeys = Object.keys(msgs);
        if (msgKeys.length === 0) return;
        const lastMsg = msgs[msgKeys[msgKeys.length - 1]];

        if (isDataBlocked === true || isBlocked === true) return;

        if (lastMsg.sender === contactUid && isMuted !== true) {
          if (!activeChatContact || activeChatContact.uid !== contactUid || document.hidden) {
            playMessageNotificationSound();
            if ("Notification" in window && Notification.permission === "granted") {
              let bodyText = lastMsg.text || (lastMsg.type === 'image' ? "📷 صورة جديدة" : "🎙️ تسجيل صوتي");
              new Notification(contactName, { body: bodyText, icon: contactDp || LINKO_APP_LOGO_SVG });
            }
          }
        }
      });
    }

    function generateWaveformHTML(mId) {
      const barHeights = [7, 13, 9, 16, 11, 20, 14, 18, 10, 15, 8, 14, 19, 12, 16, 9, 13, 17, 11, 15, 8, 14, 10, 16, 12, 8, 14, 9, 11];
      let bars = '';
      barHeights.forEach((h, i) => {
        bars += `<div class="wa-wave-bar" id="wbar-${mId}-${i}" style="height:${h}px;" data-idx="${i}"></div>`;
      });
      return bars;
    }

    function proceedOpenChat(targetUid, targetData) {
      activeChatContact = { uid: targetUid, ...targetData };
      const contactName = (targetData.name && targetData.name !== 'undefined') ? targetData.name : "مستخدم";
      const contactDp = targetData.dpUrl || emojiToSVG(targetData.emoji || contactName.substring(0,2));

      document.getElementById('chat-header-name').innerText = contactName;
      document.getElementById('chat-header-dp').src = contactDp;
      document.getElementById('chat-screen').classList.add('active');

      const banner = document.getElementById('datablock-notice-banner');
      if (banner) banner.style.display = targetData.isDataBlocked === true ? 'block' : 'none';

      updateChatScreenBlockUI(targetData.isBlocked === true);

      const messagesContainer = document.getElementById('chat-messages');
      messagesContainer.innerHTML = "";

      const chatId = [currentUser.uid, targetUid].sort().join('_');

      let isTargetOnlineCached = false;
      onValue(ref(db, `status/${targetUid}`), (stSnap) => {
        const isOnline = stSnap.val()?.state === 'online';
        isTargetOnlineCached = isOnline;
        document.getElementById('chat-header-status').innerText = isOnline ? "متصل" : "غير متصل";
        document.getElementById('chat-header-status').style.color = isOnline ? "var(--primary-color)" : "var(--text-muted)";
      });

      onValue(ref(db, `messages/${chatId}`), (snap) => {
        messagesContainer.innerHTML = "";
        const msgs = snap.val() || {};
        
        const streamBanner = document.createElement('div');
        streamBanner.className = `blocked-stream-pill ${activeChatContact?.isBlocked === true ? 'active' : ''}`;
        streamBanner.id = "blocked-stream-pill";
        streamBanner.innerText = "لقد حظرت هذا الشخص. اضغط لإلغاء الحظر.";
        streamBanner.onclick = () => { if (activeChatContact) setContactBlockStatus(activeChatContact.uid, false); };

        Object.entries(msgs).forEach(([mId, m]) => {
          const isMe = m.sender === currentUser.uid;
          const bubble = document.createElement('div');
          bubble.className = `msg-bubble ${isMe ? 'msg-me' : 'msg-other'}`;
          
          const timeStr = new Date(m.timestamp).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'});
          const tickHTML = isMe ? renderStatusTickHTML(m.status, isTargetOnlineCached) : '';

          if (m.type === 'audio') {
            const senderDp = isMe ? (currentProfile?.dpUrl || emojiToSVG("ME")) : contactDp;
            bubble.innerHTML = `
              <div class="wa-voice-bubble">
                <div class="wa-voice-avatar-box">
                  <img src="${senderDp}" class="wa-voice-avatar">
                  <i class="fas fa-microphone wa-mic-badge"></i>
                </div>
                
                <div class="wa-voice-middle">
                  <div class="wa-waveform-track" id="wa-track-${mId}">
                    ${generateWaveformHTML(mId)}
                  </div>
                  <div class="wa-voice-time-row">
                    <span>${timeStr} ${tickHTML}</span>
                    <span id="wa-dur-${mId}">${m.duration || "0:00"}</span>
                  </div>
                </div>

                <div class="wa-play-ctrl-box">
                  <button class="wa-speed-btn" id="wa-speed-${mId}">1x</button>
                  <div class="wa-play-btn" id="wa-play-${mId}">
                    <i class="fas fa-play" id="wa-picon-${mId}"></i>
                  </div>
                </div>
              </div>
            `;
            setTimeout(() => setupWhatsAppAudioPlayer(mId, m.audioData, m.viewOnce, chatId), 40);

          } else if (m.type === 'image') {
            bubble.innerHTML = `
              <img src="${m.imgData}" class="msg-image" onclick="openFullscreenAvatar('${m.imgData}', 'صورة مشتركة')">
              <div class="msg-time-row"><span>${timeStr}</span> ${tickHTML}</div>
            `;
          } else {
            bubble.innerHTML = `
              <div>${m.text}</div>
              <div class="msg-time-row"><span>${timeStr}</span> ${tickHTML}</div>
            `;
          }

          messagesContainer.appendChild(bubble);
        });

        messagesContainer.appendChild(streamBanner);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
      });

      onValue(ref(db, `typing/${chatId}/${targetUid}`), (snap) => {
        if (snap.val() === true && activeChatContact?.isBlocked !== true) {
          document.getElementById('chat-header-status').innerText = "يكتب الآن...";
          document.getElementById('chat-header-status').style.color = "var(--primary-color)";
        }
      });
    }

    function setupWhatsAppAudioPlayer(mId, audioSrc, isViewOnce, chatId) {
      const playBtn = document.getElementById(`wa-play-${mId}`);
      const icon = document.getElementById(`wa-picon-${mId}`);
      const durText = document.getElementById(`wa-dur-${mId}`);
      const speedBtn = document.getElementById(`wa-speed-${mId}`);
      const track = document.getElementById(`wa-track-${mId}`);
      if (!playBtn) return;
      
      let audio = new Audio(audioSrc);
      let currentSpeed = 1.0;

      if (speedBtn) {
        speedBtn.onclick = (e) => {
          e.stopPropagation();
          if (currentSpeed === 1.0) currentSpeed = 1.5;
          else if (currentSpeed === 1.5) currentSpeed = 2.0;
          else currentSpeed = 1.0;

          audio.playbackRate = currentSpeed;
          speedBtn.innerText = currentSpeed === 1.0 ? '1x' : (currentSpeed === 1.5 ? '1.5x' : '2x');
        };
      }

      playBtn.onclick = () => {
        if (audio.paused) {
          audio.play();
          icon.className = "fas fa-pause";
          if (speedBtn) speedBtn.style.display = "block";
        } else {
          audio.pause();
          icon.className = "fas fa-play";
        }
      };

      if (track) {
        track.onclick = (e) => {
          const rect = track.getBoundingClientRect();
          const clickX = e.clientX - rect.left;
          const ratio = Math.max(0, Math.min(1, clickX / rect.width));
          if (audio.duration) {
            audio.currentTime = ratio * audio.duration;
          }
        };
      }

      audio.ontimeupdate = () => {
        const curSec = Math.floor(audio.currentTime);
        const m = Math.floor(curSec / 60);
        const s = curSec % 60;
        if (durText) durText.innerText = `${m}:${s < 10 ? '0' : ''}${s}`;

        if (audio.duration && track) {
          const progress = audio.currentTime / audio.duration;
          const totalBars = 29;
          const playedCount = Math.floor(progress * totalBars);

          for (let i = 0; i < totalBars; i++) {
            const bar = document.getElementById(`wbar-${mId}-${i}`);
            if (bar) {
              if (i <= playedCount) bar.classList.add('played');
              else bar.classList.remove('played');
            }
          }
        }
      };

      audio.onended = () => {
        icon.className = "fas fa-play";
        if (speedBtn) speedBtn.style.display = "none";
        
        const totalBars = 29;
        for (let i = 0; i < totalBars; i++) {
          const bar = document.getElementById(`wbar-${mId}-${i}`);
          if (bar) bar.classList.remove('played');
        }

        if (isViewOnce) {
          remove(ref(db, `messages/${chatId}/${mId}`));
        }
      };
    }

    document.getElementById('logout-btn').onclick = () => {
      isSessionVerifiedByOtp = false;
      signOut(auth);
      authScreen.style.display = "flex";
      stepCredentials.classList.add('active');
      stepCredentials.style.display = 'flex';
      stepOtp.classList.remove('active');
      stepOtp.style.display = 'none';
    };
  </script>
</body>
</html>
"""

def find_available_port(start_port=8080):
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
            port += 1

PORT = int(os.environ.get("PORT", 8080))

with open("index.recovered.html", "w", encoding="utf-8") as f:
    f.write(HTML_CONTENT)

class CustomHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        """معالجة فحص أمان Chrome على أندرويد بنجاح تام وبإغلاق فوري للاتصال"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Content-Length', '0')
        self.send_header('Connection', 'close')
        self.end_headers()

    def do_POST(self):
        if '/api/send-otp' in self.path:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode('utf-8'))
                email = body.get('email', '').strip().lower()
                
                if not email:
                    self._send_json({"success": False, "message": "البريد الإلكتروني مطلوب"})
                    return
                
                code = str(body.get('otp', '')).strip() or str(random.randint(100000, 999999))
                
                
                threading.Thread(target=send_verification_email_task, args=(email, code), daemon=True).start()
                self._send_json({"success": True})
            except Exception:
                self._send_json({"success": True})

        elif '/api/verify-otp' in self.path:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode('utf-8'))
                email = body.get('email', '').strip().lower()
                code = body.get('code', '').strip()

                # فحص ومقارنة الرمز الفعلي في السيرفر بدقة
                if email in ACTIVE_EMAIL_OTPS:
                    data = ACTIVE_EMAIL_OTPS[email]
                    if time.time() - data['created_at'] <= OTP_EXPIRY_SECONDS and data['code'] == code:
                        del ACTIVE_EMAIL_OTPS[email]
                        self._send_json({"success": True})
                        return

                self._send_json({"success": False, "message": "رمز التحقق غير صحيح"})
            except Exception as e:
                self._send_json({"success": False, "message": str(e)})
        else:
            self.send_error(404, "Endpoint not found")

    def _send_json(self, data):
        """إرسال رد JSON مع ترويسة Content-Length و Connection: close لضمان الاستجابة الفورية في Chrome"""
        try:
            body_bytes = json.dumps(data).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body_bytes)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', '*')
            self.send_header('Connection', 'close')
            self.end_headers()
            self.wfile.write(body_bytes)
            self.wfile.flush()
        except Exception as e:
            print(f"[Send JSON Error]: {e}")

    def log_message(self, format, *args):
        pass

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True

PORT = int(os.environ.get("PORT", 8080))

def start_server():
    with ThreadedTCPServer(("", PORT), CustomHTTPHandler) as httpd:
        httpd.serve_forever()

print("=" * 60)
print(f"تم تشغيل Linko بنجاح وسرعة فائقة 100%!")
print(f"الرابط: http://localhost:{PORT}")
print("=" * 60)

server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()
time.sleep(1)
# webbrowser.open(f"http://localhost:{PORT}/index.html")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nتم إيقاف السيرفر.")
