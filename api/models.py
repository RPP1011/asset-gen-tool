from __future__ import annotations

from typing import Any, Dict, List, Optional
from enum import Enum
from datetime import datetime, timezone
from pydantic import BaseModel, Field


def now() -> datetime:
    return datetime.now(timezone.utc)


class GenerationStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class FirestoreBase(BaseModel):
    """
    Base model with common Firestore doc fields.
    Use `id` to hold the document id when convenient.
    """

    id: Optional[str] = Field(None, description="Document ID (Firestore doc id)")
    org_id: Optional[str] = Field(None, description="Organization ID (tenant)")
    project_id: Optional[str] = Field(None, description="Project ID if applicable")
    created_at: Optional[datetime] = Field(default_factory=now)
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class Membership(BaseModel):
    org_id: str
    role: str = Field(..., description="Role in the org (admin/editor/viewer/etc.)")


class ProjectMembership(BaseModel):
    project_id: str
    role: str = Field(..., description="Role in the project (contributor/viewer/etc.)")


class Organization(FirestoreBase):
    name: str
    owner_user_id: Optional[str] = None
    plan_tier: Optional[str] = None
    # Note: members are typically stored in a subcollection; this field can be used
    # for denormalized quick-access lists (not recommended for large orgs).
    members_summary: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Optional denormalized summary of members (name, email, role) for quick display",
    )


class StyleGuide(BaseModel):
    markdown_text: str = Field(..., description="Style guide content in markdown")
    title: Optional[str] = None
    last_edited_by: Optional[str] = None
    last_edited_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class Project(FirestoreBase):
    name: str
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict)
    # Optionally keep a short project-level style guide directly on the project doc.
    style_guide_markdown: Optional[str] = Field(
        default=None,
        description="Optional project-level style guide markdown. Exempt from indexing where appropriate.",
    )
    # project-level style guide as a nested object if desired
    style_guide: Optional[StyleGuide] = None
    # optional denormalized counts
    asset_count: Optional[int] = 0
    theme_count: Optional[int] = 0


class Theme(FirestoreBase):
    name: str
    style_keywords: List[str] = Field(default_factory=list)
    color_palette: List[str] = Field(
        default_factory=list, description="List of color hex codes"
    )
    description: Optional[str] = None
    example_image: Optional[str] = Field(
        None, description="URL or storage path to an example image"
    )
    created_by: Optional[str] = None
    style_guide_markdown: Optional[str] = None
    concept_image_ids: List[str] = Field(default_factory=list)


class ConceptImage(FirestoreBase):
    image_url: str = Field(
        ..., description="URL or storage path for the concept/reference image"
    )
    thumbnail_url: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    attribution: Optional[str] = None
    uploaded_by: Optional[str] = None
    theme_id: Optional[str] = None
    asset_id: Optional[str] = None
    usage_count: Optional[int] = 0


class Variant(FirestoreBase):
    image_url: str = Field(
        ..., description="URL or storage path to the generated image variant"
    )
    thumbnail_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    is_selected: Optional[bool] = False
    feedback: Optional[str] = None
    # You can store small per-variant fields like seed here (or in metadata)
    # generated_at mirrors created_at (kept for clarity)
    generated_at: Optional[datetime] = None


class Generation(FirestoreBase):
    prompt_text: str = Field(
        ..., description="The exact prompt text used for this generation run"
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Model and generation parameters"
    )
    theme_id: Optional[str] = None
    # Snapshot of theme info to make this generation self-contained
    theme_snapshot: Optional[Dict[str, Any]] = Field(default=None)
    concept_image_ids: List[str] = Field(default_factory=list)
    # Optionally store weights or usage details for concept images
    concept_image_weights: Optional[Dict[str, float]] = None
    variant_count: int = Field(ge=0, default=0)
    triggered_by: Optional[str] = None
    status: GenerationStatus = Field(default=GenerationStatus.PENDING)
    notes: Optional[str] = None
    # versioning alternatives
    version_number: Optional[int] = None
    # created_at is inherited from FirestoreBase
    # Subcollection `variants` will contain Variant documents; here we optionally keep a small summary list
    variant_summary: Optional[List[Dict[str, Any]]] = None


class Asset(FirestoreBase):
    name: str
    description: Optional[str] = None
    prompt: Optional[str] = Field(
        default=None, description="Base prompt or core idea for the asset"
    )
    # Size can be a preset string like "512x512" or explicit width/height fields
    size: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    theme_id: Optional[str] = None
    # Denormalized theme name for quick listing (keeps read performance)
    theme_name: Optional[str] = None
    concept_image_ids: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    created_by: Optional[str] = None
    # Reference to the chosen final variant (if selected)
    final_variant_id: Optional[str] = None
    current_image_url: Optional[str] = None
    # Asset has a generations subcollection; optionally keep latest generation metadata here
    latest_generation_id: Optional[str] = None
    latest_generation_at: Optional[datetime] = None


class User(FirestoreBase):
    """
    User profile document. Typically this doc's ID matches Firebase Auth UID.
    """

    name: Optional[str] = None
    email: Optional[str] = None
    profile_picture_url: Optional[str] = None
    org_memberships: Optional[List[Membership]] = Field(
        default_factory=list,
        description="List of organizations and roles the user belongs to",
    )
    project_memberships: Optional[List[ProjectMembership]] = Field(
        default_factory=list, description="Optional per-project memberships and roles"
    )
    last_login: Optional[datetime] = None
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)


# Convenience container models for API usage or batched writes/reads


class AssetWithGenerations(Asset):
    generations: Optional[List[Generation]] = None


class GenerationWithVariants(Generation):
    variants: Optional[List[Variant]] = None


# Example alias types for readability in code that interacts with Firestore.
OrgID = str
ProjectID = str
AssetID = str
GenerationID = str
VariantID = str
ThemeID = str
ConceptImageID = str
UserID = str
