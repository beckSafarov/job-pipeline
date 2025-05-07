import streamlit as st  # type: ignore

roles = [
    {"name": "bi-analyst", "id": 156, "emoji": "📊"},
    {"name": "devops", "id": 160, "emoji": "⚙️"},
    {"name": "analyst", "id": 10, "emoji": "📈"},
    {"name": "art-director", "id": 12, "emoji": "🎨"},
    {"name": "business-analyst", "id": 150, "emoji": "🕵️‍♂️"},
    {"name": "game-designer", "id": 25, "emoji": "🎮"},
    {"name": "data-scientist", "id": 165, "emoji": "🧪"},
    {"name": "designer", "id": 34, "emoji": "🖌️"},
    {"name": "cio", "id": 36, "emoji": "👨‍💼"},
    {"name": "product-manager", "id": 73, "emoji": "📦"},
    {"name": "methodologist", "id": 155, "emoji": "📚"},
    {"name": "programmer", "id": 96, "emoji": "👨‍💻"},
    {"name": "product-analyst", "id": 164, "emoji": "🔍"},
    {"name": "dev-team-lead", "id": 104, "emoji": "🧑‍🏫"},
    {"name": "analytics-head", "id": 157, "emoji": "📊"},
    {"name": "project-manager", "id": 107, "emoji": "🗂️"},
    {"name": "network-engineer", "id": 112, "emoji": "🌐"},
    {"name": "system-admin", "id": 113, "emoji": "🛠️"},
    {"name": "system-analyst", "id": 148, "emoji": "🧠"},
    {"name": "system-engineer", "id": 114, "emoji": "💻"},
    {"name": "security-specialist", "id": 116, "emoji": "🔐"},
    {"name": "support-specialist", "id": 121, "emoji": "🧰"},
    {"name": "tester", "id": 124, "emoji": "🧪"},
    {"name": "cto", "id": 125, "emoji": "🚀"},
    {"name": "technical-writer", "id": 126, "emoji": "📝"},
]


currencies = [
    {"name": "usd", "symbol": "$"},
    {"name": "uzs", "symbol": "лв"},
    {"name": "kzt", "symbol": "₸"},
    {"name": "rub", "symbol": "₽"},
    {"name": "kgs", "symbol": "KGS"},
    {"name": "byn", "symbol": "Rbl"},
]

countries = [
    {"id": 16, "code": "be", "emoji": "🇧🇾"},  # Belarus
    {"id": 113, "code": "ru", "emoji": "🇷🇺"},  # Russia
    {"id": 40, "code": "kz", "emoji": "🇰🇿"},  # Kazakhstan
    {"id": 48, "code": "kg", "emoji": "🇰🇬"},  # Kyrgyzstan
    {"id": 97, "code": "uz", "emoji": "🇺🇿"},  # Uzbekistan
]

languages = [
    {"id": "en", "label": "🇬🇧 English"},
    {"id": "ru", "label": "🇷🇺 Русский"},
]
