"""
src/models.py
Pydantic schemas and enums enforcing exact Excel workbook dropdowns and column types.
Strictly complies with IncuBrix Option 3 validation rules.
"""

from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel, Field, field_validator, model_validator


class IntentEnum(str, Enum):
    INFORMATIONAL = "Informational"
    COMPARISON = "Comparison"
    TRANSACTIONAL = "Transactional"
    NAVIGATIONAL = "Navigational"


class MarketEnum(str, Enum):
    US = "US"
    GB = "GB"  # Rule: NEVER use 'UK', always 'GB'
    CA = "CA"
    AU = "AU"
    IN = "IN"
    SG = "SG"
    OTHER = "Other"


class AnswerBoxEnum(str, Enum):
    ANSWER_BOX = "Answer box"
    AI_OVERVIEW = "AI Overview"
    BOTH = "Both"
    NONE = "None"


class VisibilityStatusEnum(str, Enum):
    CITED = "Cited"
    MENTIONED = "Mentioned"
    NOT_MENTIONED = "Not mentioned"


class ChangedDay2Enum(str, Enum):
    YES = "Yes"
    NO = "No"


class PriorityEnum(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class ItemTypeEnum(str, Enum):
    PAGE = "Page"
    CITATION_TARGET = "Citation target"


class ItemStatusEnum(str, Enum):
    READY = "Ready"
    DRAFT = "Draft"


class FixImpactEnum(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class FixEffortEnum(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class YesNoEnum(str, Enum):
    YES = "Yes"
    NO = "No"


class QuestionRecord(BaseModel):
    """
    Schema for a single tracked query row.
    Enforces the exact 20 input columns of tab `02_QUESTIONS` (rows 5 to 304).
    """
    question_id: str = Field(..., description="Unique alphanumeric identifier (e.g., Q001)")
    question: str = Field(..., description="Globally unique query text creators search or ask AI")
    intent: IntentEnum = Field(..., description="Query search/user intent")
    source_type: str = Field(..., description="Recorded source (e.g., Reddit, PAA, Google Suggest, Quora)")
    source_url: str = Field(..., description="URL to the forum thread, query suggestion, or keyword seed")
    market: MarketEnum = Field(..., description="Target market code (US, GB, CA, AU, IN, SG, Other)")
    google_position: Union[int, str] = Field(..., description="IncuBrix ranking position (1-100 or '>100')")
    answer_box_or_ai_overview: AnswerBoxEnum = Field(..., description="Whether Answer Box or AI Overview appeared")
    quoted_source_url: str = Field(..., description="URL quoted by Google in Answer Box or AI Overview")
    chatgpt: VisibilityStatusEnum = Field(..., description="ChatGPT visibility status")
    gemini: VisibilityStatusEnum = Field(..., description="Gemini visibility status")
    perplexity: VisibilityStatusEnum = Field(..., description="Perplexity visibility status")
    claude_or_copilot: VisibilityStatusEnum = Field(..., description="Claude or Copilot visibility status")
    competitors_named: str = Field(..., description="Comma-separated competitors mentioned")
    check_date_day1: str = Field(..., description="Measurement Date 1 (YYYY-MM-DD)")
    check_date_day2: str = Field(..., description="Measurement Date 2 (YYYY-MM-DD)")
    changed_on_day2: ChangedDay2Enum = Field(..., description="Whether visibility changed between Day 1 and Day 2")
    raw_answers_url: str = Field(..., description="Relative path or URL to raw JSON/HTML snapshots")
    priority: PriorityEnum = Field(..., description="Action priority for content or technical intervention")
    notes: str = Field(default="", description="Strategic notes, angle, or gap analysis")

    @field_validator("market", mode="before")
    @classmethod
    def validate_market_code(cls, v: str) -> str:
        if isinstance(v, str):
            clean_v = v.strip()
            if clean_v.upper() == "UK":
                raise ValueError("Invalid market 'UK': per specification rule, use 'GB' instead of 'UK'.")
            if clean_v.upper() == "OTHER":
                return "Other"
            return clean_v.upper()
        return v

    @field_validator("question", mode="before")
    @classmethod
    def validate_question_text(cls, v: str) -> str:
        if not v or not str(v).strip():
            raise ValueError("Question text cannot be blank.")
        return str(v).strip()

    @field_validator("google_position", mode="before")
    @classmethod
    def validate_google_position(cls, v: Union[int, str]) -> Union[int, str]:
        if isinstance(v, int):
            return v
        s = str(v).strip()
        if s.isdigit():
            return int(s)
        return s

    def to_dict_20_columns(self) -> dict:
        """Returns dictionary of exact 20 columns matching 02_QUESTIONS and visibility.csv."""
        return {
            "question_id": self.question_id,
            "question": self.question,
            "intent": self.intent.value if isinstance(self.intent, Enum) else str(self.intent),
            "source_type": self.source_type,
            "source_url": self.source_url,
            "market": self.market.value if isinstance(self.market, Enum) else str(self.market),
            "google_position": self.google_position,
            "answer_box_or_ai_overview": self.answer_box_or_ai_overview.value if isinstance(self.answer_box_or_ai_overview, Enum) else str(self.answer_box_or_ai_overview),
            "quoted_source_url": self.quoted_source_url,
            "chatgpt": self.chatgpt.value if isinstance(self.chatgpt, Enum) else str(self.chatgpt),
            "gemini": self.gemini.value if isinstance(self.gemini, Enum) else str(self.gemini),
            "perplexity": self.perplexity.value if isinstance(self.perplexity, Enum) else str(self.perplexity),
            "claude_or_copilot": self.claude_or_copilot.value if isinstance(self.claude_or_copilot, Enum) else str(self.claude_or_copilot),
            "competitors_named": self.competitors_named,
            "check_date_day1": self.check_date_day1,
            "check_date_day2": self.check_date_day2,
            "changed_on_day2": self.changed_on_day2.value if isinstance(self.changed_on_day2, Enum) else str(self.changed_on_day2),
            "raw_answers_url": self.raw_answers_url,
            "priority": self.priority.value if isinstance(self.priority, Enum) else str(self.priority),
            "notes": self.notes,
        }

    def to_excel_row(self) -> List[Union[str, int]]:
        """Returns ordered list of 20 values for Excel columns A through T."""
        d = self.to_dict_20_columns()
        keys = [
            "question_id", "question", "intent", "source_type", "source_url",
            "market", "google_position", "answer_box_or_ai_overview", "quoted_source_url",
            "chatgpt", "gemini", "perplexity", "claude_or_copilot", "competitors_named",
            "check_date_day1", "check_date_day2", "changed_on_day2", "raw_answers_url",
            "priority", "notes"
        ]
        return [d[k] for k in keys]


class FixRecord(BaseModel):
    """
    Schema for tab `02b_FIXES` (20 technical fixes).
    """
    fix_id: str = Field(..., description="Unique Fix ID (e.g., FIX-001)")
    page_url: str = Field(..., description="Target URL on incubrix.com")
    problem: str = Field(..., description="Technical defect description")
    evidence_url: str = Field(..., description="Evidence URL / test screenshot")
    fix_summary: str = Field(..., description="Summary of fix implementation")
    code_or_text_url: str = Field(..., description="Path or URL to ready-to-paste code")
    validator_used: str = Field(..., description="Validator name (e.g., Schema Validator, PageSpeed)")
    validated: YesNoEnum = Field(..., description="Whether verified with validator (Yes/No)")
    impact: FixImpactEnum = Field(..., description="Expected impact: High/Medium/Low")
    effort: FixEffortEnum = Field(..., description="Implementation effort: High/Medium/Low")


class PageCitationRecord(BaseModel):
    """
    Schema for tab `02c_PAGES_CITATIONS` (publish-ready pages and citation targets).
    """
    item_id: str = Field(..., description="Unique Item ID (e.g., PAGE-001, CIT-001)")
    type: ItemTypeEnum = Field(..., description="Page or Citation target")
    target_question_ids: str = Field(..., description="Comma-separated target question IDs (e.g. Q001, Q014)")
    title_or_page_url: str = Field(..., description="Page title or third-party URL")
    draft_or_evidence_url: str = Field(..., description="Draft markdown/HTML path or citation evidence URL")
    why_it_matters: str = Field(..., description="Strategic growth reason")
    angle_or_schema: str = Field(..., description="Content angle or JSON-LD schema type")
    sources_cited: str = Field(..., description="Sources cited or authoritative link targets")
    status: ItemStatusEnum = Field(..., description="Ready or Draft")


class ProgrammaticRow(BaseModel):
    """
    Schema for row in programmatic matrix generator.
    """
    topic: str
    target_platform: str
    persona: str
    market: MarketEnum
    title: str
    slug: str
    primary_kw: str
    direct_answer: str
    json_ld_type: str = "FAQPage"
