"""Legal section prediction service for Indian laws."""
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger

from ..models.section import (
    LegalAct,
    LegalSection,
    PredictedSection,
    PunishmentDetail,
    PunishmentType,
    SectionPredictionResponse,
)
from ..core.config import settings
from ..core.exceptions import SectionPredictionError


# ──────────────────────────────────────────────────────────
# BNS (Bharatiya Nyaya Sanhita) Section Database
# ──────────────────────────────────────────────────────────
BNS_SECTIONS: Dict[str, Dict[str, Any]] = {
    "63": {
        "title": "Punishment for Rape",
        "description": "A man is said to commit rape if he has sexual intercourse with a woman against her will, without her consent, or with consent obtained by fear or deception.",
        "punishment": {
            "type": "both",
            "minimum": "10 years",
            "maximum": "life imprisonment",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": False,
        },
        "keywords": ["rape", "sexual intercourse", "without consent", "against her will", "sexual assault"],
    },
    "64": {
        "title": "Punishment for Rape on Woman Under Sixteen Years of Age",
        "description": "Whoever commits rape on a woman under sixteen years of age shall be punished with rigorous imprisonment.",
        "punishment": {
            "type": "both",
            "minimum": "20 years",
            "maximum": "life imprisonment",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": False,
        },
        "keywords": ["rape", "minor", "under 16", "under sixteen", "child rape"],
    },
    "103": {
        "title": "Punishment for Murder",
        "description": "Whoever commits murder shall be punished with death or imprisonment for life, and shall also be liable to fine.",
        "punishment": {
            "type": "both",
            "minimum": "life imprisonment",
            "maximum": "death penalty",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": False,
        },
        "keywords": ["murder", "killed", "homicide", "death", "intentional killing"],
    },
    "104": {
        "title": "Punishment for Culpable Homicide not Amounting to Murder",
        "description": "Whoever commits culpable homicide not amounting to murder shall be punished with imprisonment.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "life imprisonment",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": False,
        },
        "keywords": ["culpable homicide", "not amounting to murder", "death caused"],
    },
    "109": {
        "title": "Attempt to Murder",
        "description": "Whoever attempts to murder shall be punished with imprisonment.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "10 years",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": False,
        },
        "keywords": ["attempt to murder", "attempted murder", "tried to kill"],
    },
    "110": {
        "title": "Punishment for Attempt to Commit Culpable Homicide",
        "description": "Whoever attempts to commit culpable homicide shall be punished.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "7 years",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": True,
        },
        "keywords": ["attempt to commit culpable homicide"],
    },
    "113": {
        "title": "Abetment of Offence Punishable with Death or Imprisonment for Life",
        "description": "Whoever abets the commission of an offence punishable with death or imprisonment for life.",
        "punishment": {
            "type": "imprisonment",
            "minimum": None,
            "maximum": "7 years",
            "fine": None,
            "cognizable": True,
            "bailable": True,
        },
        "keywords": ["abetment", "instigated", "aided", "conspiracy"],
    },
    "189": {
        "title": "Kidnapping or Abducting with Intent to Confine",
        "description": "Whoever kidnaps or abducts any person with intent to cause them to be secretly or wrongfully confined.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "7 years",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": False,
        },
        "keywords": ["kidnapping", "abduction", "confine", "abduct"],
    },
    "190": {
        "title": "Kidnapping or Abducting Child Under Ten Years",
        "description": "Whoever kidnaps or abducts any child under the age of ten years.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "7 years",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": False,
        },
        "keywords": ["kidnapping child", "child under ten", "abduct minor"],
    },
    "191": {
        "title": "Kidnapping or Abducting for Ransom",
        "description": "Whoever kidnaps or abducts any person for ransom or to compel government or foreign state.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "life imprisonment",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": False,
        },
        "keywords": ["kidnapping for ransom", "hostage", "ransom", "abduct for ransom"],
    },
    "221": {
        "title": "Theft",
        "description": "Whoever, intending to take dishonestly any movable property out of the possession of any person without consent.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "3 years",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": False,
        },
        "keywords": ["theft", "stole", "stolen", "dishonestly taken", "movable property"],
    },
    "222": {
        "title": "Snatching",
        "description": "Theft by snatching — sudden or forceful taking of property from the person.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "3 years",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": False,
        },
        "keywords": ["snatching", "chain snatching", "snatched"],
    },
    "223": {
        "title": "Extortion",
        "description": "Whoever intentionally puts any person in fear of injury and thereby dishonestly induces the person to deliver property.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "3 years",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": True,
        },
        "keywords": ["extortion", "threaten", "forcefully obtained", "intimidation"],
    },
    "227": {
        "title": "Robbery",
        "description": "Theft or extortion accompanied by violence or fear of instant death, hurt, or wrongful restraint.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "10 years",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": False,
        },
        "keywords": ["robbery", "armed robbery", "violent theft", "robbed"],
    },
    "229": {
        "title": "Dacoity",
        "description": "When five or more persons conjointly commit or attempt to commit robbery.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "life imprisonment",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": False,
        },
        "keywords": ["dacoity", "gang robbery", "five or more persons", "dacoit"],
    },
    "244": {
        "title": "Cheating",
        "description": "Whoever, by deceiving any person, fraudulently or dishonestly induces them to deliver any property.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "3 years",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": True,
        },
        "keywords": ["cheating", "fraud", "deceived", "defrauded", "misrepresentation"],
    },
    "245": {
        "title": "Cheating and Dishonestly Inducing Delivery of Property",
        "description": "Whoever cheats and thereby dishonestly induces the person deceived to deliver any property.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "7 years",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": True,
        },
        "keywords": ["cheating", "dishonestly induced", "delivery of property", "financial fraud"],
    },
    "253": {
        "title": "Forgery",
        "description": "Whoever makes any false document with intent to cause damage or injury.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "2 years",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": True,
        },
        "keywords": ["forgery", "false document", "fabricated document", "fake document"],
    },
    "260": {
        "title": "Defamation",
        "description": "Whoever by words, signs, or visible representation, makes or publishes any imputation concerning any person to harm their reputation.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "2 years",
            "fine": "liable to fine",
            "cognizable": False,
            "bailable": True,
        },
        "keywords": ["defamation", "reputation", "libel", "slander", "imputation"],
    },
    "270": {
        "title": "Criminal Intimidation",
        "description": "Whoever threatens another with injury to person, reputation, or property.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "2 years",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": True,
        },
        "keywords": ["criminal intimidation", "threat", "threatened"],
    },
    "296": {
        "title": "Obstructing Public Servant in Discharge of Duty",
        "description": "Whoever voluntarily obstructs any public servant in the discharge of their public functions.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "2 years",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": True,
        },
        "keywords": ["obstructing", "public servant", "obstructed"],
    },
    "299": {
        "title": "Dowry Death",
        "description": "Where the death of a woman is caused by burns or bodily injury within seven years of marriage under abnormal circumstances.",
        "punishment": {
            "type": "both",
            "minimum": "7 years",
            "maximum": "life imprisonment",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": False,
        },
        "keywords": ["dowry death", "dowry", "bride burning", "cruelty by husband", "within seven years"],
    },
    "300": {
        "title": "Cruelty by Husband or Relatives of Husband",
        "description": "Whoever, being the husband or relative of the husband, subjects a woman to cruelty.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "3 years",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": False,
        },
        "keywords": ["cruelty by husband", "domestic violence", "498A", "cruelty", "harassment for dowry"],
    },
    "304": {
        "title": "Assault or Criminal Force to Woman with Intent to Outrage Modesty",
        "description": "Whoever assaults or uses criminal force to any woman intending to outrage her modesty.",
        "punishment": {
            "type": "both",
            "minimum": "1 year",
            "maximum": "5 years",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": False,
        },
        "keywords": ["outraging modesty", "modesty", "assault on woman", "criminal force"],
    },
    "305": {
        "title": "Sexual Harassment",
        "description": "A man committing any of the following acts: physical contact, demand for sexual favours, showing pornography against will.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "3 years",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": True,
        },
        "keywords": ["sexual harassment", "unwelcome", "sexual favours", "Vishaka"],
    },
    "324": {
        "title": "Criminal Breach of Trust",
        "description": "Whoever, being in any manner entrusted with property, dishonestly misappropriates or converts it to their own use.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "3 years",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": True,
        },
        "keywords": ["criminal breach of trust", "misappropriation", "entrusted property", "embezzlement"],
    },
    "331": {
        "title": "Criminal Misappropriation of Property",
        "description": "Whoever dishonestly misappropriates or converts to their own use movable property.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "2 years",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": True,
        },
        "keywords": ["misappropriation", "criminal misappropriation"],
    },
    "349": {
        "title": "Public Nuisance",
        "description": "Whoever causes common injury, danger, or annoyance to the public.",
        "punishment": {
            "type": "fine",
            "minimum": None,
            "maximum": None,
            "fine": "liable to fine",
            "cognizable": False,
            "bailable": True,
        },
        "keywords": ["public nuisance", "nuisance", "common injury"],
    },
    "356": {
        "title": "Negligent Conduct with Respect to Machinery",
        "description": "Whoever negligently operates machinery in a manner likely to cause hurt or injury.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "1 year",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": True,
        },
        "keywords": ["negligent", "machinery", "negligence causing injury"],
    },
    "387": {
        "title": "Acts Done by Several Persons in Furtherance of Common Intention",
        "description": "When a criminal act is done by several persons in furtherance of common intention, each is liable as if done alone.",
        "punishment": {
            "type": "none",
            "minimum": None,
            "maximum": None,
            "fine": None,
            "cognizable": None,
            "bailable": None,
        },
        "keywords": ["common intention", "conspiracy", "jointly committed", "in furtherance"],
    },
}

# ──────────────────────────────────────────────────────────
# IT Act Section Database
# ──────────────────────────────────────────────────────────
IT_ACT_SECTIONS: Dict[str, Dict[str, Any]] = {
    "43": {
        "title": "Penalty and Compensation for Damage to Computer, Computer System, etc.",
        "description": "If any person without permission accesses or damages computer systems, data, or disrupts access.",
        "punishment": {
            "type": "fine",
            "minimum": None,
            "maximum": None,
            "fine": "compensation up to ₹5 crore",
            "cognizable": False,
            "bailable": True,
        },
        "keywords": ["unauthorized access", "computer damage", "data deletion", "disruption"],
    },
    "66": {
        "title": "Computer Related Offences",
        "description": "If any person dishonestly or fraudulently does any act referred to in Section 43, shall be punishable with imprisonment.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "3 years",
            "fine": "up to ₹5 lakh",
            "cognizable": True,
            "bailable": True,
        },
        "keywords": ["hacking", "computer fraud", "cyber crime", "digital fraud", "dishonestly"],
    },
    "66A": {
        "title": "Punishment for Sending Offensive Messages (Struck Down by SC)",
        "description": "Sending offensive messages through communication service. Note: This section was struck down by Supreme Court in Shreya Singhal v. Union of India (2015).",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "3 years",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": True,
        },
        "keywords": ["offensive message", "social media", "online harassment"],
    },
    "66B": {
        "title": "Punishment for Dishonestly Receiving Stolen Computer Resource",
        "description": "Whoever dishonestly receives or retains any stolen computer resource.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "3 years",
            "fine": "up to ₹1 lakh",
            "cognizable": True,
            "bailable": True,
        },
        "keywords": ["stolen computer", "receiving stolen", "computer resource"],
    },
    "66C": {
        "title": "Punishment for Identity Theft",
        "description": "Whoever fraudulently or dishonestly makes use of the electronic signature, password, or identity of another person.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "3 years",
            "fine": "up to ₹1 lakh",
            "cognizable": True,
            "bailable": True,
        },
        "keywords": ["identity theft", "password theft", "electronic signature fraud", "phishing"],
    },
    "66D": {
        "title": "Punishment for Cheating by Personation",
        "description": "Whoever cheats by personation using computer resource.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "3 years",
            "fine": "up to ₹1 lakh",
            "cognizable": True,
            "bailable": True,
        },
        "keywords": ["cheating by personation", "impersonation", "online fraud", "catfishing"],
    },
    "66E": {
        "title": "Punishment for Violation of Privacy",
        "description": "Whoever intentionally or knowingly captures, publishes, or transmits the image of private area of any person.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "3 years",
            "fine": "up to ₹2 lakh",
            "cognizable": True,
            "bailable": True,
        },
        "keywords": ["privacy violation", "voyeurism", "capturing private image", "hidden camera"],
    },
    "67": {
        "title": "Punishment for Publishing or Transmitting Obscene Material",
        "description": "Whoever publishes or transmits obscene material in electronic form.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "5 years",
            "fine": "up to ₹10 lakh",
            "cognizable": True,
            "bailable": True,
        },
        "keywords": ["obscene", "pornography", "obscene material", "electronic publication"],
    },
    "67A": {
        "title": "Punishment for Publishing or Transmitting Material Containing Sexually Explicit Act",
        "description": "Whoever publishes or transmits material containing sexually explicit act in electronic form.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "7 years",
            "fine": "up to ₹10 lakh",
            "cognizable": True,
            "bailable": True,
        },
        "keywords": ["sexually explicit", "explicit content", "electronic form"],
    },
    "72": {
        "title": "Breach of Confidentiality and Privacy",
        "description": "Any person who, pursuant to powers under this Act, accesses any electronic record without consent of the person concerned.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "2 years",
            "fine": "up to ₹1 lakh",
            "cognizable": True,
            "bailable": True,
        },
        "keywords": ["breach of confidentiality", "privacy breach", "unauthorized disclosure"],
    },
}

# ──────────────────────────────────────────────────────────
# BNSS (Bharatiya Nagarik Suraksha Sanhita) Section Database
# ──────────────────────────────────────────────────────────
BNSS_SECTIONS: Dict[str, Dict[str, Any]] = {
    "37": {
        "title": "Arrest Without Warrant",
        "description": "When any police officer may arrest without warrant.",
        "punishment": {"type": "none"},
        "keywords": ["arrest without warrant", "cognizable offence", "police arrest"],
    },
    "41": {
        "title": "Arrest by Police Without Warrant — Safeguards",
        "description": "Procedure for arrest by police without warrant and rights of the arrested person.",
        "punishment": {"type": "none"},
        "keywords": ["arrest procedure", "rights of arrested", "police procedure"],
    },
    "43": {
        "title": "Arrest by Private Person",
        "description": "Any private person may arrest any person who in their presence commits a non-bailable and cognizable offence.",
        "punishment": {"type": "none"},
        "keywords": ["citizen arrest", "private person arrest"],
    },
    "47": {
        "title": "Rights of Arrested Person",
        "description": "Every person arrested shall be informed of grounds of arrest and right to bail.",
        "punishment": {"type": "none"},
        "keywords": ["rights of arrested", "ground of arrest", "right to bail", "right to lawyer"],
    },
    "155": {
        "title": "Procedure for Investigation — Cognizable Case",
        "description": "Procedure for investigation in cognizable cases by police officer.",
        "punishment": {"type": "none"},
        "keywords": ["investigation", "cognizable case", "police investigation"],
    },
    "173": {
        "title": "Police Report on Completion of Investigation",
        "description": "Report to be submitted by police officer on completion of investigation (charge sheet / closure report).",
        "punishment": {"type": "none"},
        "keywords": ["charge sheet", "closure report", "final report", "police report", "investigation complete"],
    },
    "187": {
        "title": "Cognizance of Offences by Magistrate",
        "description": "When a Magistrate may take cognizance of an offence.",
        "punishment": {"type": "none"},
        "keywords": ["cognizance", "magistrate", "take cognizance"],
    },
    "436": {
        "title": "Bail in Bailable Offences",
        "description": "When any person accused of a bailable offence is arrested, they shall be released on bail.",
        "punishment": {"type": "none"},
        "keywords": ["bail", "bailable offence", "released on bail"],
    },
    "437": {
        "title": "Bail in Non-Bailable Offences",
        "description": "When any person accused of a non-bailable offence is arrested, bail may be granted under conditions.",
        "punishment": {"type": "none"},
        "keywords": ["bail", "non-bailable", "bail application", "bail conditions"],
    },
    "438": {
        "title": "Anticipatory Bail",
        "description": "Direction for grant of bail to person apprehending arrest.",
        "punishment": {"type": "none"},
        "keywords": ["anticipatory bail", "apprehending arrest", "pre-arrest bail"],
    },
    "482": {
        "title": "Inherent Powers of High Court",
        "description": "Nothing in this Sanhita shall be deemed to limit or affect the inherent powers of the High Court.",
        "punishment": {"type": "none"},
        "keywords": ["inherent powers", "quashing", "High Court", "482"],
    },
}

# ──────────────────────────────────────────────────────────
# BSA (Bharatiya Sakshya Adhiniyam) Section Database
# ──────────────────────────────────────────────────────────
BSA_SECTIONS: Dict[str, Dict[str, Any]] = {
    "2": {
        "title": "Definitions",
        "description": "Key definitions under the Bharatiya Sakshya Adhiniyam including evidence, proved, disproved, and fact.",
        "punishment": {"type": "none"},
        "keywords": ["definition", "evidence", "fact", "proved", "disproved"],
    },
    "56": {
        "title": "Facts of Which Evidence Need Not Be Given",
        "description": "No fact of which the Court will take judicial notice need be proved.",
        "punishment": {"type": "none"},
        "keywords": ["judicial notice", "no proof required"],
    },
    "57": {
        "title": "Facts Admitted Need Not Be Proved",
        "description": "No fact need be proved in any proceeding which the parties or their agents agree to admit.",
        "punishment": {"type": "none"},
        "keywords": ["admitted facts", "admission", "no proof needed"],
    },
    "59": {
        "title": "Proof of Facts",
        "description": "Facts can be proved by oral evidence, documentary evidence, or electronic records.",
        "punishment": {"type": "none"},
        "keywords": ["proof of facts", "oral evidence", "documentary evidence"],
    },
    "61": {
        "title": "Electronic Records as Evidence",
        "description": "Any information contained in an electronic record which is printed on a paper or stored in optical/magnetic media shall be admissible.",
        "punishment": {"type": "none"},
        "keywords": ["electronic evidence", "digital evidence", "electronic record", "e-evidence"],
    },
    "63": {
        "title": "Admissibility of Electronic Records",
        "description": "Conditions for admissibility of electronic records as evidence.",
        "punishment": {"type": "none"},
        "keywords": ["admissibility", "electronic record", "certificate", "digital signature"],
    },
    "75": {
        "title": "Opinion of Expert",
        "description": "When the Court has to form an opinion on a point of science or art, opinions of experts are relevant.",
        "punishment": {"type": "none"},
        "keywords": ["expert opinion", "expert witness", "forensic", "scientific opinion"],
    },
    "76": {
        "title": "Facts Bearing Upon Opinions of Experts",
        "description": "Facts not otherwise relevant become relevant if they support or rebut the opinions of experts.",
        "punishment": {"type": "none"},
        "keywords": ["expert opinion", "supporting facts", "rebutting expert"],
    },
    "81": {
        "title": "Presumption as to Documents Produced as Record of Evidence",
        "description": "Presumption regarding official documents and records of evidence.",
        "punishment": {"type": "none"},
        "keywords": ["presumption", "official document", "record of evidence"],
    },
}

# ──────────────────────────────────────────────────────────
# Legacy IPC Section Database (most commonly referenced)
# ──────────────────────────────────────────────────────────
IPC_SECTIONS: Dict[str, Dict[str, Any]] = {
    "302": {
        "title": "Punishment for Murder",
        "description": "Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine.",
        "punishment": {
            "type": "both",
            "minimum": "life imprisonment",
            "maximum": "death penalty",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": False,
        },
        "keywords": ["murder", "killed", "homicide", "302"],
    },
    "307": {
        "title": "Attempt to Murder",
        "description": "Whoever does any act with such intention or knowledge that it would cause death, commits attempt to murder.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "10 years",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": False,
        },
        "keywords": ["attempt to murder", "tried to kill", "307"],
    },
    "323": {
        "title": "Punishment for Voluntarily Causing Hurt",
        "description": "Whoever, except in the case provided for by section 334, voluntarily causes hurt shall be punished.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "1 year",
            "fine": "up to ₹1,000",
            "cognizable": False,
            "bailable": True,
        },
        "keywords": ["voluntarily causing hurt", "hurt", "simple hurt"],
    },
    "354": {
        "title": "Assault or Criminal Force to Woman with Intent to Outrage Modesty",
        "description": "Whoever assaults or uses criminal force to any woman, intending to outrage her modesty.",
        "punishment": {
            "type": "both",
            "minimum": "1 year",
            "maximum": "5 years",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": False,
        },
        "keywords": ["outraging modesty", "354", "assault on woman"],
    },
    "376": {
        "title": "Punishment for Rape",
        "description": "Whoever commits rape shall be punished with rigorous imprisonment for a term not less than ten years.",
        "punishment": {
            "type": "both",
            "minimum": "10 years",
            "maximum": "life imprisonment",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": False,
        },
        "keywords": ["rape", "376", "sexual assault"],
    },
    "379": {
        "title": "Punishment for Theft",
        "description": "Whoever commits theft shall be punished with imprisonment.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "3 years",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": False,
        },
        "keywords": ["theft", "379", "stole"],
    },
    "420": {
        "title": "Cheating and Dishonestly Inducing Delivery of Property",
        "description": "Whoever cheats and thereby dishonestly induces the person deceived to deliver property.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "7 years",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": True,
        },
        "keywords": ["cheating", "420", "fraud", "dishonestly induced"],
    },
    "498A": {
        "title": "Husband or Relative of Husband of a Woman Subjecting Her to Cruelty",
        "description": "Whoever being the husband or the relative of the husband subjects a woman to cruelty.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "3 years",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": False,
        },
        "keywords": ["cruelty by husband", "498A", "dowry harassment", "domestic violence"],
    },
    "34": {
        "title": "Acts Done by Several Persons in Furtherance of Common Intention",
        "description": "When a criminal act is done by several persons in furtherance of common intention, each is liable.",
        "punishment": {"type": "none"},
        "keywords": ["common intention", "34", "jointly committed"],
    },
    "120A": {
        "title": "Definition of Criminal Conspiracy",
        "description": "When two or more persons agree to do or cause to be done an illegal act.",
        "punishment": {"type": "none"},
        "keywords": ["criminal conspiracy", "conspiracy", "agreement to commit"],
    },
    "120B": {
        "title": "Punishment of Criminal Conspiracy",
        "description": "Whoever is a party to a criminal conspiracy shall be punished.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "life imprisonment",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": True,
        },
        "keywords": ["criminal conspiracy punishment", "120B", "conspiracy"],
    },
    "304B": {
        "title": "Dowry Death",
        "description": "Where the death of a woman is caused by burns or bodily injury within seven years of marriage.",
        "punishment": {
            "type": "both",
            "minimum": "7 years",
            "maximum": "life imprisonment",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": False,
        },
        "keywords": ["dowry death", "304B", "bride burning"],
    },
    "506": {
        "title": "Punishment for Criminal Intimidation",
        "description": "Whoever commits criminal intimidation shall be punished.",
        "punishment": {
            "type": "both",
            "minimum": None,
            "maximum": "2 years",
            "fine": "liable to fine",
            "cognizable": True,
            "bailable": True,
        },
        "keywords": ["criminal intimidation", "506", "threat"],
    },
}


class SectionPredictor:
    """Predict applicable legal sections from document text."""

    def __init__(self):
        self.act_databases = {
            LegalAct.BNS: BNS_SECTIONS,
            LegalAct.IT_ACT: IT_ACT_SECTIONS,
            LegalAct.BNSS: BNSS_SECTIONS,
            LegalAct.BSA: BSA_SECTIONS,
            LegalAct.IPC: IPC_SECTIONS,
        }

    def predict_sections(
        self, text: str, document_id: str = ""
    ) -> SectionPredictionResponse:
        """
        Predict applicable legal sections from document text.

        Combines:
        1. Direct section reference extraction (high confidence)
        2. Keyword-based prediction (medium confidence)
        3. Context-based prediction using LLM (if available)
        """
        if not text or len(text.strip()) == 0:
            raise SectionPredictionError("Empty text provided for section prediction")

        predicted: List[PredictedSection] = []
        acts_referenced: set = set()

        # Step 1: Extract directly referenced sections
        direct_sections = self._extract_direct_references(text)
        for section in direct_sections:
            predicted.append(section)
            acts_referenced.add(section.section.act)

        # Step 2: Predict sections based on keywords
        keyword_sections = self._predict_from_keywords(text)
        for section in keyword_sections:
            # Avoid duplicates with direct references
            existing_ids = {f"{ps.section.act.value}_{ps.section.section_number}" for ps in predicted}
            new_id = f"{section.section.act.value}_{section.section.section_number}"
            if new_id not in existing_ids:
                predicted.append(section)
                acts_referenced.add(section.section.act)

        # Sort by confidence
        predicted.sort(key=lambda x: x.confidence, reverse=True)

        return SectionPredictionResponse(
            document_id=document_id,
            predicted_sections=predicted,
            total_sections_found=len(predicted),
            acts_referenced=list(acts_referenced),
        )

    def _extract_direct_references(self, text: str) -> List[PredictedSection]:
        """Extract sections that are directly mentioned in the text."""
        results: List[PredictedSection] = []
        text_lower = text.lower()

        # BNS sections
        bns_refs = re.findall(
            r"(?:Section|Sec\.?|S\.?)\s*(\d+(?:\([a-z]\))?)\s*(?:of\s+)?(?:the\s+)?(?:BNS|Bharatiya\s+Nyaya\s+Sanhita)",
            text, re.IGNORECASE
        )
        for sec_num in bns_refs:
            section_data = BNS_SECTIONS.get(sec_num)
            if section_data:
                results.append(self._create_predicted_section(
                    LegalAct.BNS, sec_num, section_data, text, confidence=0.95
                ))

        # IPC sections
        ipc_refs = re.findall(
            r"(?:Section|Sec\.?|S\.?)\s*(\d+(?:[A-Z]?(?:\([a-z]\))?)?)\s*(?:of\s+)?(?:the\s+)?(?:IPC|Indian\s+Penal\s+Code)",
            text, re.IGNORECASE
        )
        for sec_num in ipc_refs:
            section_data = IPC_SECTIONS.get(sec_num)
            if section_data:
                results.append(self._create_predicted_section(
                    LegalAct.IPC, sec_num, section_data, text, confidence=0.95
                ))

        # IT Act sections
        it_refs = re.findall(
            r"(?:Section|Sec\.?|S\.?)\s*(\d+(?:[A-Z]?(?:\([a-z]\))?)?)\s*(?:of\s+)?(?:the\s+)?(?:IT\s+Act|Information\s+Technology\s+Act)",
            text, re.IGNORECASE
        )
        for sec_num in it_refs:
            section_data = IT_ACT_SECTIONS.get(sec_num)
            if section_data:
                results.append(self._create_predicted_section(
                    LegalAct.IT_ACT, sec_num, section_data, text, confidence=0.95
                ))

        # BNSS sections
        bnss_refs = re.findall(
            r"(?:Section|Sec\.?|S\.?)\s*(\d+(?:\([a-z]\))?)\s*(?:of\s+)?(?:the\s+)?(?:BNSS|Bharatiya\s+Nagarik\s+Suraksha\s+Sanhita)",
            text, re.IGNORECASE
        )
        for sec_num in bnss_refs:
            section_data = BNSS_SECTIONS.get(sec_num)
            if section_data:
                results.append(self._create_predicted_section(
                    LegalAct.BNSS, sec_num, section_data, text, confidence=0.95
                ))

        # BSA sections
        bsa_refs = re.findall(
            r"(?:Section|Sec\.?|S\.?)\s*(\d+(?:\([a-z]\))?)\s*(?:of\s+)?(?:the\s+)?(?:BSA|Bharatiya\s+Sakshya\s+Adhiniyam)",
            text, re.IGNORECASE
        )
        for sec_num in bsa_refs:
            section_data = BSA_SECTIONS.get(sec_num)
            if section_data:
                results.append(self._create_predicted_section(
                    LegalAct.BSA, sec_num, section_data, text, confidence=0.95
                ))

        # Generic section references (without act name)
        generic_refs = re.findall(
            r"(?:Section|Sec\.?|S\.?)\s*(\d+(?:[A-Z]?(?:\([a-z]\))?)?)",
            text, re.IGNORECASE
        )
        for sec_num in generic_refs:
            # Try to match across all databases
            for act, db in self.act_databases.items():
                if sec_num in db:
                    existing_ids = {f"{ps.section.act.value}_{ps.section.section_number}" for ps in results}
                    new_id = f"{act.value}_{sec_num}"
                    if new_id not in existing_ids:
                        results.append(self._create_predicted_section(
                            act, sec_num, db[sec_num], text, confidence=0.7
                        ))

        return results

    def _predict_from_keywords(self, text: str) -> List[PredictedSection]:
        """Predict applicable sections based on keyword matching."""
        results: List[PredictedSection] = []
        text_lower = text.lower()

        for act, db in self.act_databases.items():
            for sec_num, data in db.items():
                keywords = data.get("keywords", [])
                matches = sum(1 for kw in keywords if kw.lower() in text_lower)
                if matches >= 2:  # At least 2 keyword matches
                    confidence = min(0.9, 0.5 + (matches * 0.1))
                    results.append(self._create_predicted_section(
                        act, sec_num, data, text, confidence=confidence
                    ))

        return results

    def _create_predicted_section(
        self,
        act: LegalAct,
        section_number: str,
        section_data: Dict[str, Any],
        text: str,
        confidence: float,
    ) -> PredictedSection:
        """Create a PredictedSection from section data."""
        punishment_data = section_data.get("punishment", {})
        punishment = None
        if punishment_data and punishment_data.get("type") != "none":
            punishment = PunishmentDetail(
                punishment_type=PunishmentType(punishment_data.get("type", "none")),
                minimum_duration=punishment_data.get("minimum"),
                maximum_duration=punishment_data.get("maximum"),
                fine_amount=punishment_data.get("fine"),
                is_cognizable=punishment_data.get("cognizable"),
                is_bailable=punishment_data.get("bailable"),
            )

        legal_section = LegalSection(
            act=act,
            section_number=section_number,
            section_title=section_data["title"],
            description=section_data["description"],
            punishment=punishment,
        )

        # Find relevant text snippet
        relevant_text = self._find_relevant_snippet(text, section_data.get("keywords", []))

        # Generate reason
        reason = self._generate_reason(act, section_number, section_data, relevant_text)

        return PredictedSection(
            section=legal_section,
            confidence=round(confidence, 2),
            reason=reason,
            relevant_text=relevant_text,
        )

    def _find_relevant_snippet(self, text: str, keywords: List[str]) -> str:
        """Find the most relevant text snippet for a section."""
        sentences = text.split(". ")
        best_sentence = ""
        best_score = 0

        for sentence in sentences:
            score = sum(1 for kw in keywords if kw.lower() in sentence.lower())
            if score > best_score:
                best_score = score
                best_sentence = sentence.strip()

        return best_sentence[:300] if best_sentence else text[:300]

    def _generate_reason(
        self, act: LegalAct, section_number: str, data: Dict[str, Any], relevant_text: str
    ) -> str:
        """Generate a human-readable reason for why this section applies."""
        keywords_matched = data.get("keywords", [])
        title = data["title"]
        return (
            f"Section {section_number} of {act.value} ({title}) is applicable because "
            f"the document contains references to: {', '.join(keywords_matched[:3])}. "
            f"Relevant text: \"{relevant_text[:200]}\""
        )

    def explain_section(self, act: str, section_number: str) -> Optional[Dict[str, Any]]:
        """Get detailed explanation of a legal section."""
        # Map act string to enum and database
        act_map = {
            "BNS": (LegalAct.BNS, BNS_SECTIONS),
            "IPC": (LegalAct.IPC, IPC_SECTIONS),
            "IT_ACT": (LegalAct.IT_ACT, IT_ACT_SECTIONS),
            "BNSS": (LegalAct.BNSS, BNSS_SECTIONS),
            "BSA": (LegalAct.BSA, BSA_SECTIONS),
        }

        if act not in act_map:
            return None

        act_enum, db = act_map[act]
        section_data = db.get(section_number)
        if not section_data:
            return None

        punishment_data = section_data.get("punishment", {})
        punishment_detail = None
        if punishment_data and punishment_data.get("type") != "none":
            punishment_detail = PunishmentDetail(
                punishment_type=PunishmentType(punishment_data.get("type", "none")),
                minimum_duration=punishment_data.get("minimum"),
                maximum_duration=punishment_data.get("maximum"),
                fine_amount=punishment_data.get("fine"),
                is_cognizable=punishment_data.get("cognizable"),
                is_bailable=punishment_data.get("bailable"),
            )

        return {
            "act": act_enum,
            "section_number": section_number,
            "section_title": section_data["title"],
            "description": section_data["description"],
            "simple_explanation": self._simplify_explanation(section_data),
            "legal_implications": self._get_legal_implications(section_data, punishment_data),
            "punishment_details": punishment_detail,
            "when_applies": f"This section applies when: {', '.join(section_data.get('keywords', [])[:5])}",
            "example_cases": self._get_example_cases(act, section_number),
        }

    def _simplify_explanation(self, section_data: Dict[str, Any]) -> str:
        """Convert legal jargon to simple English."""
        title = section_data["title"]
        description = section_data["description"]
        keywords = section_data.get("keywords", [])

        return (
            f"In simple terms: {title} deals with situations involving "
            f"{', '.join(keywords[:3])}. {description} "
            f"This means that if someone engages in activities related to "
            f"{', '.join(keywords[:2])}, they can be charged under this section."
        )

    def _get_legal_implications(self, section_data: Dict[str, Any], punishment_data: Dict[str, Any]) -> str:
        """Describe legal implications of a section."""
        implications = []
        if punishment_data.get("cognizable"):
            implications.append("This is a cognizable offence — police can arrest without warrant.")
        elif punishment_data.get("cognizable") is False:
            implications.append("This is a non-cognizable offence — police need a warrant to arrest.")

        if punishment_data.get("bailable"):
            implications.append("This is a bailable offence — bail is a right.")
        elif punishment_data.get("bailable") is False:
            implications.append("This is a non-bailable offence — bail is at the discretion of the court.")

        p_type = punishment_data.get("type", "none")
        if p_type == "both":
            implications.append(
                f"Punishment includes imprisonment (up to {punishment_data.get('maximum', 'as prescribed')}) "
                f"and fine ({punishment_data.get('fine', 'as prescribed')})."
            )
        elif p_type == "fine":
            implications.append(f"Punishment is fine only: {punishment_data.get('fine', 'as prescribed')}.")
        elif p_type == "death_penalty":
            implications.append("This offence carries the death penalty as maximum punishment.")
        elif p_type == "life_imprisonment":
            implications.append("This offence carries life imprisonment as maximum punishment.")

        return " ".join(implications) if implications else "No specific legal implications found."

    def _get_example_cases(self, act: str, section_number: str) -> List[str]:
        """Return example cases for a section."""
        # Hardcoded example landmark cases for major sections
        examples = {
            ("IPC", "302"): ["Bachan Singh v. State of Punjab (1980)", "Machhi Singh v. State of Punjab (1983)"],
            ("IPC", "376"): ["State of Punjab v. Gurmit Singh (1996)", "Mathura Rape Case (1972)"],
            ("IPC", "498A"): ["Sushil Kumar Sharma v. Union of India (2005)", "Arnesh Kumar v. State of Bihar (2014)"],
            ("IPC", "420"): ["State of Maharashtra v. Vishnu Dattatraya (2010)"],
            ("IPC", "354"): ["Vishaka v. State of Rajasthan (1997)", "Tarkeshwar Pandey v. State of Bihar (1994)"],
            ("IPC", "304B"): ["State of Punjab v. Iqbal Singh (2011)", "Shanti v. State of Haryana (1991)"],
            ("IT_ACT", "66A"): ["Shreya Singhal v. Union of India (2015) — Section struck down"],
            ("BNS", "103"): ["Applicable from July 1, 2024 — replaced IPC Section 302"],
            ("BNS", "63"): ["Applicable from July 1, 2024 — replaced IPC Section 376"],
        }
        return examples.get((act, section_number), ["No example cases available."])


# Singleton
section_predictor = SectionPredictor()
