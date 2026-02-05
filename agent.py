"""
Simple web agent that queries the Sports Centers API using natural language.
Uses the Anthropic API (Claude) to interpret questions and call the right endpoint.

Usage:
    pip install anthropic requests
    set ANTHROPIC_API_KEY=your_key_here
    python agent.py "Find tennis centers near Tours"
"""
import sys
import json
import requests

API_BASE = "https://regionalcenters.onrender.com"


def query_api(endpoint: str) -> dict:
    """Call the Sports Centers API."""
    response = requests.get(f"{API_BASE}{endpoint}")
    response.raise_for_status()
    return response.json()


def agent(question: str):
    """Simple rule-based agent that routes questions to the right API endpoint."""
    q = question.lower()

    # Location-based queries
    city_coords = {
        "tours": (47.39, 0.69),
        "orléans": (47.90, 1.91),
        "orleans": (47.90, 1.91),
        "bourges": (47.08, 2.40),
        "chartres": (48.45, 1.48),
        "blois": (47.59, 1.33),
        "châteauroux": (46.81, 1.69),
        "chateauroux": (46.81, 1.69),
        "paris": (48.86, 2.35),
    }

    # Check for nearby/location queries
    for city, (lat, lng) in city_coords.items():
        if city in q:
            if any(word in q for word in ["près", "near", "proche", "around", "autour"]):
                data = query_api(f"/nearby?lat={lat}&lng={lng}&radius_km=50")
                print(f"\n📍 Centers near {city.title()} (within 50km):")
                print(f"   Found: {data['count']} centers\n")
                for c in data["data"]:
                    print(f"   • {c['Name']} ({c['distance_km']}km)")
                    print(f"     {c['address']}\n")
                return

    # Discipline queries
    sports = ["tennis", "basket", "football", "natation", "karaté", "karate",
              "badminton", "escalade", "randonnée", "cyclisme", "danse",
              "gymnastique", "yoga", "canoë"]
    for sport in sports:
        if sport in q:
            data = query_api(f"/discipline?name={sport}")
            print(f"\n🏅 Centers offering {sport.title()}:")
            print(f"   Found: {data['count']} centers\n")
            for c in data["data"]:
                print(f"   • {c['Name']}")
                print(f"     {c['address']}\n")
            return

    # Pathology queries
    pathologies = ["cancer", "diabète", "diabete", "cardiovasculaire",
                   "respiratoire", "neuro", "obésité", "obesite"]
    for patho in pathologies:
        if patho in q:
            data = query_api(f"/pathology?name={patho}")
            print(f"\n🏥 Centers for {patho.title()}:")
            print(f"   Found: {data['count']} centers\n")
            for c in data["data"]:
                print(f"   • {c['Name']}")
                print(f"     Disciplines: {c['Discipline'][:60]}...\n")
            return

    # List queries
    if "discipline" in q or "sport" in q or "activit" in q:
        data = query_api("/disciplines")
        print(f"\n📋 All available disciplines ({data['count']}):\n")
        for d in data["disciplines"]:
            print(f"   • {d}")
        return

    if "patholog" in q or "maladie" in q or "condition" in q:
        data = query_api("/pathologies")
        print(f"\n📋 All pathologies handled ({data['count']}):\n")
        for p in data["pathologies"]:
            print(f"   • {p}")
        return

    # Default: search
    words = question.strip()
    data = query_api(f"/search?q={words}")
    print(f"\n🔍 Search results for '{words}':")
    print(f"   Found: {data['count']} centers\n")
    for c in data["data"]:
        print(f"   • {c['Name']}")
        print(f"     {c['address']}\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = input("\nAsk a question about sports centers: ")

    agent(question)
