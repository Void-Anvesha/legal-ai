# BolnaAI Multi-Agent Police Intake Architecture

## 1. Project Vision

BolnaAI is a multi-agent system that modernizes the traditional police complaint intake process.

In the traditional workflow, a victim visits the police station, explains the incident verbally, and a police officer writes down the details manually. This can be slow, inconsistent, emotionally difficult for the victim, and dependent on how well the statement is captured.

BolnaAI replaces the first layer of manual intake with a voice-based AI system. The victim speaks naturally. A voice agent listens, understands the complaint, asks necessary follow-up questions, structures the facts, and then passes the completed case summary to a legal reasoning agent that recommends applicable Indian legal sections.

The final output is not an automatic FIR. It is an officer-assistive draft containing the victim statement, extracted facts, missing information, confidence scores, and suggested sections for police review.

## 2. Current Implementation Status

The current project codebase is an early foundation for BolnaAI. It is not yet the complete voice-based multi-agent police intake system.

At this stage, the implemented system is mainly responsible for legal section classification and legal section explanation from provided text or uploaded documents.

Current working capabilities:

- Upload or provide complaint/document text.
- Extract text from uploaded files.
- Predict applicable legal sections from the extracted text.
- Match against configured Indian legal datasets such as BNS, IPC, IT Act, BNSS, and BSA.
- Use direct section-reference extraction when the text already mentions a section.
- Use keyword-based matching when the section is not directly mentioned.
- Return predicted sections with confidence, reason, punishment details, and relevant text snippets.
- Explain a selected legal section in simpler language.

Current backend modules:

```text
backend/app/api/
  upload.py       -> accepts documents and stores extracted text
  sections.py     -> predicts and explains legal sections
  summary.py      -> summarizes document text
  chat.py         -> supports document-related chat
  cases.py        -> retrieves similar case information

backend/app/services/
  section_predictor.py   -> core section classification logic
  pdf_reader.py          -> document text extraction
  legal_parser.py        -> legal text/entity parsing support
  summarizer.py          -> document summarization
  rag_engine.py          -> retrieval-augmented responses
  similarity_search.py   -> similar case search
```

Current section prediction flow:

```text
Document or complaint text
  |
  v
Text extraction / input text
  |
  v
SectionPredictor
  |
  +--> Direct legal section reference detection
  |
  +--> Keyword-based legal section matching
  |
  v
Predicted sections with confidence and explanation
```

The voice intake agent, follow-up questioning agent, HITL review flow, and full police complaint drafting workflow are target architecture components that will be built on top of this current section-classification foundation.

## 3. Target Core Goals

- Capture the victim's complaint through natural voice conversation.
- Ask sensitive and relevant follow-up questions without overwhelming the victim.
- Extract structured facts such as people, place, date, time, incident type, evidence, injuries, threats, property loss, witnesses, and suspect details.
- Generate a clean police-style complaint draft from the conversation.
- Recommend applicable legal sections from BNS, BNSS, BSA, IT Act, and other configured legal sources.
- Provide explainable section recommendations with supporting facts.
- Keep a human officer in the loop for verification, correction, and final submission.

## 4. Target High-Level Workflow

```text
Victim
  |
  v
Voice Interface
  |
  v
Speech-to-Text
  |
  v
Conversation Orchestrator
  |
  +--> Victim Intake Agent
  |
  +--> Follow-Up Question Agent
  |
  +--> Trauma-Aware Safety Agent
  |
  +--> Fact Extraction Agent
  |
  v
Case Completeness Check
  |
  v
Structured Case File
  |
  +--> Statement Drafting Agent
  |
  +--> Legal Section Recommendation Agent
  |
  +--> Similar Case / Knowledge Retrieval Agent
  |
  v
Police Review Dashboard
  |
  v
HITL Review Gate
  |
  +--> Officer approves complaint draft
  |
  +--> Officer edits incorrect or incomplete facts
  |
  +--> Officer accepts, rejects, or changes legal sections
  |
  v
Officer verifies, edits, approves, or rejects suggestions
```

## 5. Proposed Target System Architecture

```text
+---------------------------------------------------------------+
|                        Frontend Layer                          |
|                                                               |
|  Victim Voice Intake UI        Police Review Dashboard         |
|  - Mic recording              - Case timeline                  |
|  - Live transcript            - Extracted facts                |
|  - Follow-up prompts          - Draft complaint                |
|  - Consent notice             - Suggested sections             |
|  - Language selection         - Officer edits and approval     |
+-------------------------------+-------------------------------+
                                |
                                v
+---------------------------------------------------------------+
|                         API Gateway                            |
|                                                               |
|  /sessions        /voice/transcribe       /cases               |
|  /conversation    /sections/recommend     /officer/review      |
+-------------------------------+-------------------------------+
                                |
                                v
+---------------------------------------------------------------+
|                    Multi-Agent Backend Layer                   |
|                                                               |
|  Conversation Orchestrator                                      |
|  - Maintains session state                                      |
|  - Routes tasks to agents                                       |
|  - Decides when enough information has been collected           |
|                                                               |
|  Agents                                                        |
|  - Voice Intake Agent                                           |
|  - Follow-Up Question Agent                                     |
|  - Safety and Escalation Agent                                  |
|  - Fact Extraction Agent                                        |
|  - Case Classification Agent                                    |
|  - Statement Drafting Agent                                     |
|  - Legal Section Recommendation Agent                           |
|  - Explanation and Confidence Agent                             |
+-------------------------------+-------------------------------+
                                |
                                v
+---------------------------------------------------------------+
|                    HITL Review and Control Layer               |
|                                                               |
|  Human officer remains the final decision maker.                |
|  - Reviews AI-generated complaint draft                         |
|  - Confirms extracted facts against transcript/audio             |
|  - Accepts, rejects, or edits legal section suggestions          |
|  - Requests more information from victim if needed               |
|  - Approves final case packet for official use                   |
+-------------------------------+-------------------------------+
                                |
                                v
+---------------------------------------------------------------+
|                         AI / NLP Layer                         |
|                                                               |
|  Speech-to-Text        LLM Reasoning        Embeddings          |
|  Translation           RAG Retrieval        Similarity Search   |
|  PII Detection         Summarization        Section Matching    |
+-------------------------------+-------------------------------+
                                |
                                v
+---------------------------------------------------------------+
|                         Data Layer                             |
|                                                               |
|  SQL Database          Vector Database        File Storage      |
|  - Sessions            - Legal sections       - Audio files     |
|  - Statements          - Case examples        - Attachments     |
|  - Extracted facts     - Judgments            - Evidence files  |
|  - Officer actions                                             |
+---------------------------------------------------------------+
```

## 6. Target Agent Responsibilities

### 6.1 Voice Intake Agent

This agent handles the first conversation with the victim.

Responsibilities:

- Greet the victim and explain that the system will help record the complaint.
- Ask for consent before recording or processing the complaint.
- Let the victim narrate the incident freely.
- Avoid legal jargon during the initial conversation.
- Maintain a calm and respectful tone.
- Pass transcript chunks to the orchestrator in real time.

Example opening:

```text
Please tell me what happened in your own words. I will listen first, then I may ask a few questions to make sure important details are not missed.
```

### 6.2 Follow-Up Question Agent

This agent identifies missing details and asks targeted questions.

Responsibilities:

- Detect missing mandatory information.
- Ask one question at a time.
- Prioritize important details based on incident type.
- Avoid repeating questions already answered.
- Stop asking questions when the complaint is sufficiently complete.

Example missing details:

- When did the incident happen?
- Where did it happen?
- Who was involved?
- Was there physical injury?
- Was there property damage?
- Were there threats, weapons, witnesses, or digital evidence?
- Is the victim in immediate danger?

### 6.3 Safety and Escalation Agent

This agent monitors the conversation for urgent risk.

Responsibilities:

- Detect immediate danger, medical emergency, self-harm risk, ongoing violence, or child safety concerns.
- Flag cases that require urgent officer attention.
- Stop normal intake flow when emergency handling is needed.
- Recommend immediate escalation to a human officer.

Important principle:

The system should never delay emergency support in order to complete data collection.

### 6.4 Fact Extraction Agent

This agent converts the raw conversation into structured facts.

Output fields:

```json
{
  "victim": {
    "name": "",
    "age": "",
    "gender": "",
    "contact": "",
    "address": ""
  },
  "incident": {
    "type": "",
    "date": "",
    "time": "",
    "location": "",
    "description": "",
    "sequence_of_events": []
  },
  "accused": [],
  "witnesses": [],
  "evidence": [],
  "injuries": [],
  "property_loss": [],
  "threats": [],
  "digital_elements": [],
  "missing_information": []
}
```

### 6.5 Case Classification Agent

This agent identifies the broad category of the complaint.

Possible categories:

- Physical assault
- Theft or robbery
- Cybercrime
- Domestic violence
- Harassment or stalking
- Fraud
- Threat or intimidation
- Property dispute
- Sexual offence
- Missing person
- Other complaint

The classification helps the follow-up agent ask better questions and helps the legal section agent narrow the search space.

### 6.6 Statement Drafting Agent

This agent generates a clean complaint draft from the structured facts.

Responsibilities:

- Convert conversation into formal police-statement language.
- Preserve the victim's meaning.
- Avoid adding facts that were not stated.
- Mark uncertain or missing details clearly.
- Generate both a concise summary and a full narrative.

Output:

- Victim statement draft
- Incident summary
- Timeline of events
- Missing details checklist
- Officer review notes

### 6.7 Legal Section Recommendation Agent

This agent recommends applicable legal sections.

Responsibilities:

- Match extracted facts against legal datasets.
- Use retrieval over BNS, BNSS, BSA, IT Act, and other configured law sources.
- Return ranked section suggestions.
- Explain why each section may apply.
- Mention facts supporting the section.
- Mention missing facts needed to confirm the section.
- Provide confidence score.

Output example:

```json
{
  "recommended_sections": [
    {
      "law": "BNS",
      "section": "Example section number",
      "title": "Example offence title",
      "confidence": 0.82,
      "supporting_facts": [
        "Victim stated that the accused threatened physical harm",
        "Incident occurred at the victim's workplace"
      ],
      "missing_facts": [
        "Need confirmation whether a weapon was used"
      ],
      "explanation": "This section may apply because the complaint includes threat of injury."
    }
  ]
}
```

### 6.8 Explanation and Confidence Agent

This agent makes the recommendation understandable for police review.

Responsibilities:

- Convert model reasoning into plain language.
- Separate strong recommendations from weak possibilities.
- Highlight uncertain assumptions.
- Warn when evidence is insufficient.
- Ensure the final screen clearly says that an officer must verify the sections.

### 6.9 HITL Review Agent

HITL stands for Human-in-the-Loop. In BolnaAI, the human in the loop is the police officer or authorized reviewer who validates the AI output before it is used officially.

This agent does not replace the officer. It prepares the AI output for review and enforces checkpoints that require human approval.

Responsibilities:

- Package the complaint draft, transcript, extracted facts, and section recommendations into one reviewable case file.
- Highlight low-confidence facts and legal recommendations.
- Show exactly which victim statements support each extracted fact.
- Require officer approval before finalizing the complaint draft.
- Require officer approval before accepting suggested legal sections.
- Track officer edits, approvals, rejections, and comments.
- Send the case back to the follow-up agent if the officer requests more information.

HITL decision options:

- Approve the AI-generated complaint draft.
- Edit the complaint draft.
- Reject incorrect extracted facts.
- Accept suggested legal sections.
- Replace or remove suggested legal sections.
- Request more information from the victim.
- Escalate the case to a senior officer or specialist unit.

## 7. Backend Implementation Plan

The existing FastAPI backend can be extended with new modules.

Proposed structure:

```text
backend/app/
  api/
    voice.py
    intake.py
    cases.py
    officer_review.py
    section_recommendation.py

  agents/
    orchestrator.py
    voice_intake_agent.py
    followup_question_agent.py
    safety_agent.py
    fact_extraction_agent.py
    case_classification_agent.py
    statement_drafting_agent.py
    legal_section_agent.py
    explanation_agent.py
    hitl_review_agent.py

  models/
    intake_session.py
    case_file.py
    extracted_fact.py
    legal_recommendation.py
    officer_review.py
    hitl_decision.py

  services/
    speech_to_text.py
    text_to_speech.py
    conversation_memory.py
    legal_retrieval.py
    section_matcher.py
    audit_logger.py
    officer_decision_service.py

  database/
    case_repository.py
    session_repository.py
    recommendation_repository.py
```

### 7.1 Intake Session Flow

1. Frontend creates a new intake session.
2. Victim gives consent and starts speaking.
3. Audio is streamed or uploaded to the backend.
4. Speech-to-text service generates transcript chunks.
5. Conversation orchestrator stores each user message.
6. Fact extraction agent updates the structured case file.
7. Follow-up question agent checks missing details.
8. Safety agent checks whether immediate escalation is needed.
9. System asks the next follow-up question or ends intake.
10. When intake is complete, statement drafting agent creates the complaint draft.
11. Legal section agent recommends applicable sections.
12. HITL review agent prepares the case packet for officer review.
13. Officer dashboard shows the complaint draft, evidence, transcript, and section recommendations.
14. Officer approves, edits, rejects, or requests more information.
15. Only officer-approved output moves to final case status.

### 7.2 API Endpoints

```text
POST /api/intake/sessions
Create a new victim intake session.

POST /api/intake/{session_id}/audio
Upload or stream victim audio for transcription.

POST /api/intake/{session_id}/message
Send a transcript message to the conversation orchestrator.

GET /api/intake/{session_id}/next-question
Return the next follow-up question.

POST /api/intake/{session_id}/complete
Finalize the intake and generate structured case output.

GET /api/cases/{case_id}
Fetch structured case details.

POST /api/cases/{case_id}/recommend-sections
Generate legal section recommendations.

PATCH /api/officer-review/{case_id}
Allow police officer to edit, approve, or reject draft output.

POST /api/hitl/{case_id}/decision
Record an officer HITL decision such as approve, edit, reject, escalate, or request more information.

GET /api/hitl/{case_id}/audit
Fetch the HITL audit trail for the case.
```

## 8. Frontend Implementation Plan

The frontend should have two main experiences.

### 8.1 Victim Intake Screen

Features:

- Language selector.
- Consent notice.
- Microphone start and stop controls.
- Live transcript display.
- Voice or text follow-up questions.
- Progress indicator for required details.
- Emergency escalation message when needed.
- Final confirmation screen before sending to officer review.

### 8.2 Police Review Dashboard

Features:

- Case summary.
- Full victim statement draft.
- Extracted entities and timeline.
- Audio transcript.
- Recommended legal sections with confidence.
- Supporting facts for each recommendation.
- Missing facts checklist.
- Officer edit controls.
- Approve, reject, or request more information actions.

## 9. Data Model

### 9.1 Intake Session

```json
{
  "session_id": "uuid",
  "language": "en-IN",
  "status": "in_progress",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "consent_given": true,
  "emergency_flag": false
}
```

### 9.2 Conversation Message

```json
{
  "message_id": "uuid",
  "session_id": "uuid",
  "role": "victim | agent | officer",
  "content": "message text",
  "source": "voice | text",
  "timestamp": "timestamp"
}
```

### 9.3 Case File

```json
{
  "case_id": "uuid",
  "session_id": "uuid",
  "status": "draft",
  "incident_type": "physical_assault",
  "facts": {},
  "statement_draft": "",
  "summary": "",
  "missing_information": [],
  "created_at": "timestamp"
}
```

### 9.4 Legal Recommendation

```json
{
  "case_id": "uuid",
  "law": "BNS",
  "section": "",
  "title": "",
  "confidence": 0.0,
  "supporting_facts": [],
  "missing_facts": [],
  "explanation": "",
  "officer_decision": "pending"
}
```

### 9.5 HITL Decision

```json
{
  "decision_id": "uuid",
  "case_id": "uuid",
  "officer_id": "uuid",
  "decision_type": "approve | edit | reject | request_more_info | escalate",
  "target": "statement | extracted_fact | legal_section | full_case",
  "original_value": "",
  "updated_value": "",
  "reason": "",
  "timestamp": "timestamp"
}
```

## 10. Legal Section Recommendation Approach

The recommendation system should use a hybrid approach.

### 10.1 Rule-Based Filtering

Use extracted facts to narrow the legal search space.

Examples:

- If the complaint involves digital fraud, search IT Act and cybercrime-related BNS sections.
- If the complaint involves physical injury, search assault and hurt-related sections.
- If the complaint involves stolen property, search theft, robbery, or criminal breach sections.
- If the complaint involves threats, search intimidation-related sections.

### 10.2 Retrieval-Augmented Generation

Use embeddings and vector search over the legal dataset.

Steps:

1. Convert the structured complaint into a search query.
2. Retrieve relevant legal sections from the vector database.
3. Provide the retrieved law text to the LLM.
4. Ask the LLM to rank sections only from retrieved sources.
5. Return section number, law name, explanation, and confidence.

### 10.3 Confidence Scoring

Confidence should be based on:

- Number of supporting facts present.
- Whether mandatory offence ingredients are present.
- Strength of semantic match with legal section text.
- Contradictions or missing facts.
- Whether the recommendation comes from multiple matching signals.

## 11. Human-in-the-Loop Safeguards

BolnaAI should assist police officers, not replace them.

Required safeguards:

- Every section recommendation must be reviewed by an officer.
- The system should show uncertainty clearly.
- The system should not invent missing facts.
- Victim statements must be editable before final use.
- Audio, transcript, extracted facts, and officer edits should be audit logged.
- Sensitive cases should be escalated quickly to a human officer.
- The UI should clearly mark AI output as a draft.

HITL approval rules:

- No complaint draft can be marked final until an officer approves it.
- No legal section can be marked accepted until an officer accepts it.
- Any recommendation below the confidence threshold must be shown as "needs review".
- Any emergency flag must bypass normal automation and notify an officer immediately.
- Every officer change must be stored in the audit log with timestamp and reason.

## 12. Privacy and Security

Required measures:

- Store consent status for every session.
- Encrypt audio files and complaint records at rest.
- Use role-based access for police users.
- Log officer access and edits.
- Mask sensitive personal information where possible.
- Avoid exposing victim information in frontend logs.
- Add retention policies for audio and transcript data.
- Keep legal recommendation prompts free from unnecessary personal data.

## 13. Implementation Phases

### Phase 0: Current Section Classification Foundation

- Current backend accepts uploaded or provided text.
- Current section predictor classifies legal sections from text.
- Current output includes section number, law, confidence, reason, relevant snippet, and punishment details.
- Current implementation supports direct section extraction and keyword-based matching.
- This phase is the base on which the voice and multi-agent layers will be built.

### Phase 1: Text-Based Police Intake Prototype

- Build conversation orchestrator.
- Implement intake through text chat.
- Extract structured facts from complaint text.
- Ask follow-up questions.
- Generate case summary and statement draft.
- Reuse the existing section predictor to recommend sections from the structured complaint.

### Phase 2: Voice Intake

- Add speech-to-text service.
- Add microphone UI.
- Add live transcript.
- Add text-to-speech for follow-up questions if needed.
- Support Hindi/English conversation flow.

### Phase 3: Multi-Agent Refinement

- Split logic into specialized agents.
- Add safety escalation agent.
- Add confidence scoring.
- Add missing-facts reasoning.
- Improve legal retrieval and section ranking.

### Phase 4: Police Review Dashboard

- Build case review screen.
- Add officer edits.
- Add approve/reject workflow.
- Add explicit HITL decision recording.
- Add audit trail.
- Export reviewed complaint as PDF or printable format.

### Phase 5: Production Hardening

- Add authentication and role-based permissions.
- Add encryption and retention policy.
- Add monitoring and error reporting.
- Add evaluation dataset for section recommendation accuracy.
- Add legal expert review loop.

## 14. Evaluation Plan

The system should be tested on both conversation quality and legal recommendation quality.

Metrics:

- Intake completion rate.
- Number of follow-up questions needed.
- Accuracy of extracted facts.
- Accuracy of incident classification.
- Precision of recommended sections.
- Recall of relevant sections.
- Officer acceptance rate.
- Number of officer corrections.
- Average time saved per complaint.

## 15. Key Risks

| Risk | Mitigation |
|------|------------|
| Wrong legal section recommendation | Keep officer review mandatory and show confidence with supporting facts |
| Victim gives incomplete details | Use follow-up question agent and missing-information checklist |
| AI invents facts | Force outputs to cite transcript facts only |
| Sensitive emergency case delayed | Safety agent should escalate immediately |
| Language or accent transcription errors | Show transcript confirmation and allow correction |
| Privacy leakage | Encrypt data, limit logs, and apply role-based access |

## 16. Immediate Next Step

Since the current project already classifies legal sections from text, the next practical step is to build a text-based police intake layer around the existing section predictor. Voice should come after the text flow is working reliably.

Recommended first milestone:

```text
Victim complaint text
  -> follow-up questions
  -> structured case file
  -> complaint draft
  -> existing section predictor
  -> legal section recommendations with confidence
  -> officer review screen
```

This gives a working end-to-end system quickly while reusing what is already built. After that, speech-to-text can be added as an input layer without redesigning the section classification logic.
