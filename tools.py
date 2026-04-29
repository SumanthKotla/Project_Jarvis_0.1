import logging
import aiohttp
import os, asyncio, subprocess
import smtplib
import yt_dlp

from livekit.agents import llm 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import webbrowser
from livekit.agents import function_tool, RunContext
from langchain_community.tools import DuckDuckGoSearchResults
from typing import Optional

@function_tool
async def get_weather(context: RunContext, city: str) -> str:
    """Get the weather for a given city.
    Args:
        city: The city to get weather for.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://wttr.in/{city}?format=3") as response:
                if response.status == 200:
                    text = await response.text()
                    logging.info(f"Weather for {city}: {text.strip()}")
                    return text.strip()
                else:
                    logging.error(f"Failed to get weather for {city}")
                    return f"Could not retrieve weather for {city}."
    except Exception as e:
        logging.error(f"Error fetching weather for {city}: {str(e)}")
        return f"An error occurred while fetching weather for {city}."


@function_tool
async def search_web(context: RunContext, query: str) -> str:
    """Search the web for information on a given query.
    Args:
        query: The search query to look up.
    """
    try:
        url = f"https://ddg-api.herokuapp.com/search?query={query}&limit=3"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    results = await response.json()
                    output = ""
                    for r in results:
                        output += f"- {r.get('title', '')}: {r.get('snippet', '')}\n"
                    return output or "No results found."
                return f"Search failed for query: {query}"
    except Exception as e:
        logging.error(f"Error searching web for {query}: {str(e)}")
        return f"An error occurred while searching for {query}."
    
@function_tool()
async def send_email(
context: RunContext, #type: ignore
to_email: str, 
subject: str, 
message: str,
cc_email: Optional[str] = None
) -> str:
    """Send an email to a specified recipient.
    Args:
        to_email: The recipient's email address.
        subject: The subject of the email.
        message: The message content of the email.
        cc_email: Optional email address to CC.
    """
    try:
        # Gmail SMTP server configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        # Get credentials from environment variables
        Gmail_user = os.getenv("GMAIL_USER")
        Gmail_pass = os.getenv("GMAIL_PASS")

        if not Gmail_user or not Gmail_pass:
            logging.error("Gmail credentials not found in environment variables.")
            return "Email sending failed: Gmail credentials not configured."

        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = Gmail_user
        msg['To'] = to_email
        msg['Subject'] = subject

        # Add CC if provided
        recipients = [to_email]
        if cc_email:
            msg['Cc'] = cc_email
            recipients.append(cc_email)

        # Attach the message body
        msg.attach(MIMEText(message, 'plain'))

        # Connect to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls() # Enable TLS encryption
        server.login(Gmail_user, Gmail_pass)

        # Send the email
        text = msg.as_string()
        server.sendmail(Gmail_user, recipients, msg.as_string())
        server.quit()

        logging.info(f"Email sent to {to_email} with subject '{subject}'")
        return f"Email successfully sent to {to_email}."
    
    except smtplib.SMTPAuthenticationError:
        logging.error("SMTP authentication failed. Check Gmail credentials.")
        return "Email sending failed: Authentication error. Please check your Gmail credentials."
    except smtplib.SMTPException as e:
        logging.error(f"SMTP error occurred: {str(e)}")
        return f"Email sending failed: SMTP error occurred. {str(e)}"
    except Exception as e:
        logging.error(f"error sending email: {str(e)}")
        return f"An error occurred while sending the email. {str(e)}"
    



@function_tool
async def set_volume(context: RunContext, level: int) -> str:
    """Set the Mac system volume (0-100).
    Args:
        level: Volume level between 0 and 100.
    """
    level = max(0, min(100, level))
    os.system(f"osascript -e 'set volume output volume {level}'")
    return f"Volume adjusted to {level}%."

@function_tool
async def play_music(context: RunContext, song: str) -> str:
    """Search and play a song on YouTube in a dedicated Google Chrome tab.
    Args:
        song: The name of the song or artist to search and play.
    """
    def find_video():
        try:
            ydl_opts = {
                'quiet': True,
                'extract_flat': True,
                'default_search': 'ytsearch',
                'noplaylist': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                r = ydl.extract_info(f"ytsearch1:{song}", download=False)
                if r and 'entries' in r and r['entries']:
                    video_id = r['entries'][0].get('id')
                    if video_id:
                        return f"https://www.youtube.com/watch?v={video_id}"
        except Exception as e:
            logging.error(f"yt_dlp error: {e}")
        return None

    loop = asyncio.get_event_loop()
    url = await loop.run_in_executor(None, find_video)
    logging.info(f"[play_music] URL: {url}")

    if not url:
        return "Couldn't find that song."

    nav_script = f'''
    tell application "Google Chrome"
        activate
        if (count of windows) = 0 then
            make new window
        end if
        make new tab at end of tabs of window 1
        set active tab index of window 1 to (count of tabs of window 1)
        set URL of active tab of window 1 to "{url}"
    end tell
    '''

    result = subprocess.run(["osascript", "-e", nav_script], capture_output=True, text=True)
    logging.info(f"[play_music] nav result: {result.returncode} {result.stderr}")

    await asyncio.sleep(3)

    play_script = '''
    tell application "Google Chrome"
        execute active tab of window 1 javascript "var v = document.querySelector('video'); if(v) v.play();"
    end tell
    '''
    subprocess.run(["osascript", "-e", play_script], capture_output=True, text=True)

    return "Done."

@function_tool
async def control_media(context: RunContext, action: str) -> str:
    """Control YouTube playback: pause, play, or skip.
    Args:
        action: The action to perform: pause, play, or skip.
    """
    mapping = {"pause": "k", "play": "k", "skip": "n"}
    key = mapping.get(action.lower())
    if key:
        subprocess.run(["osascript", "-e", 'tell application "Google Chrome" to activate'])
        mod = "using {shift down}" if action == "skip" else ""
        subprocess.run(["osascript", "-e",
            f'tell application "System Events" to keystroke "{key}" {mod}'])
        return f"Media {action}ed."
    return f"Unsupported action: {action}"