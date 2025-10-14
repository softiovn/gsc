from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime, date
import pandas as pd

@dataclass
class GSCDataPoint:
    date: date
    clicks: int
    impressions: int
    ctr: float
    position: float
    query: str = ""
    page: str = ""
    country: str = ""
    device: str = ""

@dataclass
class AnalysisResult:
    summary: str
    trends: List[str]
    opportunities: List[str]
    issues: List[str]
    recommendations: List[str]

@dataclass
class Suggestion:
    category: str
    title: str
    description: str
    priority: str  # high, medium, low
    impact: str   # high, medium, low
    implementation: str