import streamlit as st
from google import genai
from google.genai import types
from twilio.rest import Client as TwilioClient
from prompts import (
    SUMMARY_REQUEST_PROMPT,
    SYSTEM_PROMPT,
    WELCOME_MESSAGE_TEMPLATE,
)
MODEL_NAME = "gemini-3.5-flash"
st.set_page_config(
    page_title="Snap & Study",
    page_icon="📚"
)

# API keys and Twilio configuration
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
TWILIO_ACCOUNT_SID = st.secrets["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = st.secrets["TWILIO_AUTH_TOKEN"]
TWILIO_WHATSAPP_FROM = st.secrets["TWILIO_WHATSAPP_FROM"]


# Gemini client
@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)


# Twilio client
@st.cache_resource
def get_twilio_client():
    return TwilioClient(
        TWILIO_ACCOUNT_SID,
        TWILIO_AUTH_TOKEN
    )


gemini_client = get_gemini_client()
twilio_client = get_twilio_client()


# Display a message in the chat
def render_message(message):
    with st.chat_message(message["role"]):

        if message["kind"] == "text":
            st.write(message["content"])

        elif message["kind"] == "image":
            st.image(message["content"])


# Add a message to chat history
def add_message(role, kind, content):
    st.session_state.messages.append(
        {
            "role": role,
            "kind": kind,
            "content": content
        }
    )

    render_message(st.session_state.messages[-1])


# Send message to Gemini
def ask_gemini(parts):
    try:
        return st.session_state.chat.send_message(parts).text

    except Exception as error:
        return f"Sorry, something went wrong: {error}"


# Clean WhatsApp message
def clean_whatsapp_text(text):

    if not text:
        return "No study explanation available."

    text = text.strip()

    return text[:4000] + "..." if len(text) > 4000 else text


# Send explanation to WhatsApp
def send_whatsapp(to_number, summary):

    try:

        message = twilio_client.messages.create(
            from_=TWILIO_WHATSAPP_FROM,
            to=f"whatsapp:{to_number}",
            body=clean_whatsapp_text(summary),
        )

        return True, message.sid

    except Exception as error:

        return False, str(error)

# ============================================================
# STEP 1: ONBOARDING
# ============================================================

if "onboarded" not in st.session_state:

    st.title("📚 Snap & Study")

    st.caption(
        "Snap it. Understand it. Study smarter."
    )

    with st.form("onboarding_form"):

        name = st.text_input(
            "Your name"
        )

        whatsapp_number = st.text_input(
            "WhatsApp number (with country code)",
            placeholder="+91XXXXXXXXXX",
            help="This is the number Snap & Study will send your study explanations to.",
        )

        submitted = st.form_submit_button(
            "Let's study 🚀"
        )

    if submitted:

        if not name.strip() or not whatsapp_number.strip():

            st.warning(
                "Please fill in both your name and WhatsApp number."
            )

        else:

            st.session_state.name = name.strip()

            st.session_state.whatsapp_number = (
                whatsapp_number.strip()
            )

            # Create Gemini chat
            st.session_state.chat = gemini_client.chats.create(
                model=MODEL_NAME,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT
                ),
            )

            # Initialize chat history
            st.session_state.messages = []

            st.session_state.onboarded = True

            st.rerun()

    st.stop()


# ============================================================
# STEP 2: CHAT INTERFACE
# ============================================================

header_col, button_col = st.columns(
    [5, 2],
    vertical_alignment="center"
)


# Header
with header_col:

    st.title("📚 Snap & Study")


# WhatsApp button
# WhatsApp button
with button_col:

    if st.button(
        "📤 Send to WhatsApp",
        use_container_width=True
    ):

        with st.spinner(
            "Preparing your study explanation..."
        ):

            summary = ask_gemini(
                [SUMMARY_REQUEST_PROMPT]
            )

        success, info = send_whatsapp(
            st.session_state.whatsapp_number,
            summary
        )

        if success:
            st.success("Sent! Check your WhatsApp 📲")
        else:
            st.error(f"Couldn't send that: {info}")
# User information
st.caption(
    f"Logged in as {st.session_state.name} "
    f"- explanations go to {st.session_state.whatsapp_number}"
)


# ============================================================
# WELCOME MESSAGE
# ============================================================

if not st.session_state.messages:

    add_message(
        "assistant",
        "text",
        WELCOME_MESSAGE_TEMPLATE.format(
            name=st.session_state.name
        )
    )

else:

    for message in st.session_state.messages:

        render_message(message)


# ============================================================
# CHAT INPUT
# ============================================================

user_input = st.chat_input(
    "Ask a question, or attach a study photo",
    accept_file=True,
    file_type=[
        "jpg",
        "jpeg",
        "png"
    ],
)


# ============================================================
# PROCESS USER INPUT
# ============================================================

if user_input:

    photo = (
        user_input.files[0]
        if user_input.files
        else None
    )

    text = user_input.text

    parts = []


    # --------------------------------------------------------
    # Process uploaded image
    # --------------------------------------------------------

    if photo is not None:

        photo_bytes = photo.getvalue()

        # Display uploaded image
        add_message(
            "user",
            "image",
            photo_bytes
        )

        # Send image to Gemini
        parts.append(
            types.Part.from_bytes(
                data=photo_bytes,
                mime_type=photo.type
            )
        )


    # --------------------------------------------------------
    # Process text
    # --------------------------------------------------------

    if text:

        add_message(
            "user",
            "text",
            text
        )

        parts.append(text)


    # --------------------------------------------------------
    # If only an image was uploaded
    # --------------------------------------------------------

    elif photo is not None:

        parts.append(
            "Explain this study material clearly. "
            "Identify the main concept, explain it in simple "
            "student-friendly language, and break down the "
            "solution or important points step by step."
        )


    # --------------------------------------------------------
    # Get Gemini response
    # --------------------------------------------------------

    with st.spinner(
        "Understanding your study material..."
    ):

        answer = ask_gemini(parts)


    # --------------------------------------------------------
    # Display Gemini response
    # --------------------------------------------------------

    add_message(
        "assistant",
        "text",
        answer
    )