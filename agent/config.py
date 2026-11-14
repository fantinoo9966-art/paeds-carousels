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

# Pastel accent colours, one per slide (cycled). Used by the "pastel" theme.
ACCENTS = ["#F7A8C4", "#8FD3C7", "#9CC7F2", "#C7B5F0", "#FFC59E", "#F6D77E"]

# Design themes. Each post gets the next theme in this order, so the grid looks varied.
# paper=background, card=box, ink=text, on_accent=text on coloured chips, mark=highlighter behind bold words.
THEMES = {
    "pastel": dict(
        paper="#FFF8F1", card="#FFFFFF", ink="#2B2440", muted="#6B6380", border="#2B2440",
        hl_bg="#2B2440", hl_ink="#FFFFFF", on_accent="#2B2440", strong_ink="#2B2440", mark="mix",
        head="Fredoka:wght@500;600;700", head_family="Fredoka", head_weight=700,
        body="Nunito:wght@500;700;800", body_family="Nunito", pattern="dots", radius=36, shadow=12,
        accents=ACCENTS),
    "midnight": dict(
        paper="#12132A", card="#1D1F45", ink="#F5F3FF", muted="#A9A6CF", border="#3A3D7A",
        hl_bg="#7CF2D0", hl_ink="#12132A", on_accent="#12132A", strong_ink="accent", mark="none",
        head="Poppins:wght@600;700;800", head_family="Poppins", head_weight=800,
        body="Inter:wght@400;500;700;800", body_family="Inter", pattern="grid", radius=28, shadow=0,
        accents=["#7CF2D0", "#FF8FB8", "#8FB8FF", "#FFD27A", "#C9A2FF"]),
    "notebook": dict(
        paper="#FDFBF3", card="#FFFDF7", ink="#1F2A44", muted="#5D6680", border="#1F2A44",
        hl_bg="#FFE45C", hl_ink="#1F2A44", on_accent="#1F2A44", strong_ink="#1F2A44", mark="mix",
        head="Caveat:wght@600;700", head_family="Caveat", head_weight=700,
        body="Nunito:wght@500;700;800", body_family="Nunito", pattern="lines", radius=10, shadow=8, head_scale=1.3,
        accents=["#FFE45C", "#9BF0B5", "#FFB3D1", "#A8D8FF"]),
    "mint": dict(
        paper="#E9F6F1", card="#FFFFFF", ink="#103B2E", muted="#4D7266", border="#103B2E",
        hl_bg="#103B2E", hl_ink="#E9F6F1", on_accent="#103B2E", strong_ink="#0E7A5A", mark="none",
        head="DM+Serif+Display", head_family="DM Serif Display", head_weight=400,
        body="DM+Sans:wght@400;500;700;800", body_family="DM Sans", pattern="none", radius=24, shadow=0,
        accents=["#9FE3C9", "#C8EBDD", "#7FD1B9", "#BFE8D6"]),
    "sunset": dict(
        paper="#FFF0E5", card="#FFFFFF", ink="#3B1E2A", muted="#7A5563", border="#3B1E2A",
        hl_bg="#E8566C", hl_ink="#FFFFFF", on_accent="#3B1E2A", strong_ink="#C2364E", mark="none",
        head="Baloo+2:wght@600;700;800", head_family="Baloo 2", head_weight=800,
        body="Nunito:wght@500;700;800", body_family="Nunito", pattern="dots", radius=40, shadow=10,
        accents=["#FFB38A", "#FF8FA3", "#FFD08A", "#F7A1C4"]),
    "lavender": dict(
        paper="#F4F1FF", card="#FFFFFF", ink="#1E1A3C", muted="#625C8A", border="#D9D2FF",
        hl_bg="#5B4BDB", hl_ink="#FFFFFF", on_accent="#1E1A3C", strong_ink="#5B4BDB", mark="none",
        head="Outfit:wght@600;700;800", head_family="Outfit", head_weight=800,
        body="Outfit:wght@400;500;700", body_family="Outfit", pattern="none", radius=32, shadow=0,
        accents=["#CFC6FF", "#B9E6FF", "#FFD6EC", "#D7F5C8"]),
}
THEME_ORDER = ["pastel", "midnight", "notebook", "mint", "sunset", "lavender"]

# Daily slots: who each post is for and which formats it rotates through.
SLOTS = {
    "morning": dict(
        audience="MBBS students, interns and NEET-PG / INI-CET aspirants",
        level=("NEET-PG / INI-CET high-yield exam revision: crisp, clean, standard-textbook facts, numbers, one-liners "
               "and PYQ-style points; no clutter, no controversy"),
        formats=[
            "High-yield summary of the topic",
            "Mnemonic-led revision (one strong mnemonic slide plus supporting facts)",
            "Compare & contrast (two or three look-alike conditions in tables)",
            "Red flags and must-not-miss signs",
            "Rapid-fire exam one-liners (PYQ style)",
        ]),
    "evening": dict(
        audience="paediatric postgraduates (MD/DNB residents)",
        level=("PG level for MD/DNB theory and viva: biostatistics, mechanical ventilation, social paediatrics and "
               "Government of India national health programmes. Use the latest official programme names, targets and "
               "components (MoHFW, NHM); for biostatistics give formulas with a worked example"),
        formats=[
            "Concept explained simply, with a worked example or real-life scenario",
            "Viva questions with crisp model answers",
            "Step-by-step approach / algorithm / framework",
            "Exam pearls and common mistakes",
            "Test yourself: 4-5 questions, answers revealed on the later slides",
        ]),
}

# Instagram API version
GRAPH_VERSION = "v27.0"

# Instagram account ID of @paediatrick_or_treats (shown in the Meta app dashboard; not a secret)
IG_USER_ID = "17841456619533432"
