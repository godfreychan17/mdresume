from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class ResumeHeader(BaseModel):
    name: str
    title: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None


class ExperienceEntry(BaseModel):
    role: str
    company: str
    dates: str
    bullets: list[str] = Field(default_factory=list)


class EducationEntry(BaseModel):
    degree: str
    institution: str
    dates: str
    details: list[str] = Field(default_factory=list)


class ResumeLayout(BaseModel):
    columns: int = 1
    margins_mm: list[int] = Field(default_factory=lambda: [15, 20, 15, 20])


class ResumeMeta(BaseModel):
    page: str = "A4"
    theme: str = "classic"


class Resume(BaseModel):
    meta: ResumeMeta = Field(default_factory=ResumeMeta)
    layout: ResumeLayout = Field(default_factory=ResumeLayout)
    sections_order: list[str] = Field(
        default_factory=lambda: ["header", "summary", "experience", "education", "skills"]
    )
    header: ResumeHeader
    summary: Optional[str] = None
    experience: list[ExperienceEntry] = Field(default_factory=list)
    education: list[EducationEntry] = Field(default_factory=list)
    skills: dict[str, str] = Field(default_factory=dict)
