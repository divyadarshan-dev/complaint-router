"""
router.py - the brain of the Hinglish Complaint Router (Gemini Edition).

One function matters: route_complaint(text). It sends the complaint to Gemini,
reads back a JSON answer, and decides which queue the ticket goes to.
"""
import json
import time

from google import genai
from google.genai import types

# ---------- Settings you can change ----------
# Tries the primary model first; if Google returns 503 (busy), automatically falls back!
MODELS = ["gemini-3.1-flash-lite", "gemini-3.5-flash", "gemini-3.7-flash"]
CONFIDENCE_THRESHOLD = 0.70        # below this -> human review queue

# Published Flash rates (US dollars per 1 million tokens)
PRICE_INPUT_PER_MILLION = 0.30
PRICE_OUTPUT_PER_MILLION = 2.50

DEPARTMENTS = ["Plumbing", "Electrical", "Wi-Fi", "Mess", "Academic", "Other"]

SYSTEM_PROMPT = SYSTEM_PROMPT = """You are a complaint-routing assistant for a university campus and hostels in India (such as LPU).
Students write complaints in English, Hinglish (Hindi written in English letters) or
romanised Punjabi, often with spelling mistakes, slang and missing details.

Read the complaint and reply with ONLY a JSON object (no extra text, no markdown) in exactly this format:
{
  "department": one of ["Plumbing", "Electrical", "Wi-Fi", "Mess", "Academic", "Other"],
  "block": the block/building code or letter if mentioned (e.g. "BH-4", "GH-2", "Block 34", "A"), else null,
  "floor": the floor number as an integer if mentioned (ground floor = 0, basement = -1), else null,
  "room": the room number as a string if mentioned, else null,
  "urgency": one of ["low", "medium", "high"],
  "confidence": a number from 0.0 to 1.0 showing how sure you are that ONE single department handles this,
  "reason": one short English sentence explaining your choice
}

Department guide:
- Plumbing: taps, tooti, leaks, washroom, flush, geyser, water supply, water cooler leak, drainage, paani bharna.
- Electrical: fans, pankha, lights, tubelight, switch boards, sparks, power cuts, bijli, AC, sockets.
- Wi-Fi: internet, wifi, router, 24online login, LAN port, slow network, no connection.
- Mess: food quality, dal/roti/paneer, hygiene, dining hall, mess timings, mess staff, drinking water in mess.
- Academic: classes, timetable, attendance, marks, faculty, exams, UMS academic portal, classroom projector.
- Other: security/guards, housekeeping/kachra, noise complaints, lost parcels, carpentry/furniture/locks, laundry, stray animals.

Urgency guide:
- high: safety/health hazard (sparks, fire, electric shock, flooding/paani bharna, insects/keede in food, stray animals) or essential utility down for multiple days.
- medium: a clear functional problem needing normal maintenance soon.
- low: minor inconvenience, policy/timing suggestion, or non-urgent request.

CRITICAL Confidence & Ambiguity Rules:
- Never invent a block, floor or room. Use null if not explicitly stated.
- Note: drinking water or plates/hygiene INSIDE the mess/dining hall belongs 100% to Mess (not Plumbing).
- If a complaint genuinely combines TWO SEPARATE departments (e.g. fan + washroom tap leak, or mess food + hostel wifi), set confidence <= 0.55 so a human splits the ticket.
- If a complaint is vague, gibberish, or ambiguous without specifying the actual problem (e.g. "bohot dikkat ho rhi hai", "portal pe login nahi ho rha" without saying UMS vs 24online, "warden se baat karni hai"), set confidence <= 0.50.
- Only give confidence >= 0.85 when the complaint clearly belongs to ONE department.
"""


_client = None


def _get_client():
    """Create the API client once. It reads GEMINI_API_KEY from the environment."""
    global _client
    if _client is None:
        _client = genai.Client()
    return _client


def _parse_json(text):
    """The model should return pure JSON, but remove code fences just in case."""
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


def route_complaint(complaint):
    """Classify one complaint and return a ticket dictionary."""
    start = time.time()
    input_tokens = 0
    output_tokens = 0
    last_error = None

    for model_name in MODELS:
        try:
            response = _get_client().models.generate_content(
                model=model_name,
                contents=complaint,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    max_output_tokens=1000,
                    temperature=0.1,
                ),
            )
            if response.usage_metadata:
                input_tokens = response.usage_metadata.prompt_token_count or 0
                output_tokens = response.usage_metadata.candidates_token_count or 0

            data = _parse_json(response.text)

            department = data.get("department")
            if department not in DEPARTMENTS:
                raise ValueError("Unknown department: %s" % department)
            confidence = float(data.get("confidence", 0))
            last_error = None
            break  # Success! Stop trying backup models.
        except Exception as error:
            last_error = error
            if "429" in str(error) or "RESOURCE_EXHAUSTED" in str(error):
                time.sleep(2)

    if last_error is not None:
        data = {
            "department": "Other",
            "block": None,
            "floor": None,
            "room": None,
            "urgency": "medium",
            "reason": "Could not process automatically (%s)" % last_error,
        }
        department = "Other"
        confidence = 0.0

    latency = time.time() - start
    cost = (
        input_tokens * PRICE_INPUT_PER_MILLION
        + output_tokens * PRICE_OUTPUT_PER_MILLION
    ) / 1_000_000

    # Low confidence -> a human must look at it
    queue = department if confidence >= CONFIDENCE_THRESHOLD else "Human Review"

    return {
        "complaint": complaint,
        "department": department,
        "block": data.get("block"),
        "floor": data.get("floor"),
        "room": data.get("room"),
        "urgency": data.get("urgency"),
        "confidence": round(confidence, 2),
        "reason": data.get("reason"),
        "queue": queue,
        "latency_s": round(latency, 2),
        "cost_usd": round(cost, 6),
    }
