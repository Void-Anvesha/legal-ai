"""Rule-based first-pass complaint classification."""
from typing import Dict, List


class CaseClassificationAgent:
    """Classify complaint type from victim narrative."""

    category_keywords: Dict[str, List[str]] = {
        "physical_assault": ["hit", "beat", "assault", "hurt", "injury", "slap", "attack"],
        "theft_or_robbery": ["stole", "stolen", "theft", "robbed", "snatched", "wallet", "chain"],
        "cybercrime": ["online", "upi", "bank", "otp", "hacked", "account", "cyber", "phone"],
        "domestic_violence": ["husband", "wife", "dowry", "domestic", "in-laws", "marriage"],
        "harassment_or_stalking": ["harass", "stalk", "follow", "messages", "calls", "threatening"],
        "fraud": ["fraud", "cheated", "scam", "deceived", "fake", "money"],
        "threat_or_intimidation": ["threat", "threatened", "blackmail", "intimidate", "warned"],
        "property_dispute": ["land", "property", "house", "plot", "boundary", "possession"],
        "sexual_offence": ["rape", "molest", "sexual", "modesty", "touch", "assaulted me"],
        "missing_person": ["missing", "not returned", "disappeared", "cannot find"],
    }

    def classify(self, text: str) -> str:
        lowered = text.lower()
        best_category = "other_complaint"
        best_score = 0

        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in lowered)
            if score > best_score:
                best_category = category
                best_score = score

        return best_category


case_classification_agent = CaseClassificationAgent()
