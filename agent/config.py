"""Settings for the carousel agent. Edit these to change the brand or the AI model."""

HANDLE = "@paediatrick_or_treats"
BRAND_NAME = "Pediatrics Made Simple"

# Who the posts are written for. This shapes the tone and depth of every carousel.
AUDIENCE = (
    "MBBS students, interns, NEET-PG / INI-CET aspirants and paediatric PG residents in India. "
    "They want high-yield, exam-oriented, clinically accurate paediatrics they can save and revise."
)

# Free Gemini models that write the slides, tried in order (best first).
# If Google renames or retires one, the next is used. Check aistudio.google.com/docs/pricing for current free models.
GEMINI_MODELS = [
    "gemini-4-hydrogen",
    "gemini-3.8-flash",
    "gemini-3.6-flash",
    "gemini-2.5-flash",
]

MIN_SLIDES = 6
MAX_SLIDES = 10  # Instagram allows at most 10 images per carousel

# Pastel accent colours, one per slide (cycled).
ACCENTS = ["#F7A8C4", "#8FD3C7", "#9CC7F2", "#C7B5F0", "#FFC59E", "#F6D77E"]

# Instagram API version (graph.instagram.com)
GRAPH_VERSION = "v27.0"
