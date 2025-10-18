import os
from datetime import datetime
from functools import lru_cache
from typing import Any, Dict, List, Optional, Type, TypeVar

from dotenv import load_dotenv
from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    HTTPException,
    Query,
    Response,
    status,
)
from pydantic import BaseModel, Field

from . import models
from .firebase import FirestoreAccessor, FirestoreError
from .models import FirestoreBase

load_dotenv(".env.local")

app = FastAPI()
router = APIRouter(prefix="/api")

ModelT = TypeVar("ModelT", bound=BaseModel)


class OrganizationBase(BaseModel):
    owner_user_id: Optional[str] = None
    plan_tier: Optional[str] = None
    members_summary: Optional[List[Dict[str, Any]]] = None

    class Config:
        extra = "forbid"


class OrganizationCreate(OrganizationBase):
    id: Optional[str] = Field(
        default=None, description="Optional Firestore document id to use."
    )
    name: str


class OrganizationUpdate(OrganizationBase):
    name: Optional[str] = None


class ProjectBase(BaseModel):
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    style_guide_markdown: Optional[str] = None
    style_guide: Optional[models.StyleGuide] = None
    asset_count: Optional[int] = Field(default=None, ge=0)
    theme_count: Optional[int] = Field(default=None, ge=0)

    class Config:
        extra = "forbid"


class ProjectCreate(ProjectBase):
    id: Optional[str] = Field(
        default=None, description="Optional Firestore document id to use."
    )
    name: str


class ProjectUpdate(ProjectBase):
    name: Optional[str] = None


class AssetBase(BaseModel):
    description: Optional[str] = None
    prompt: Optional[str] = None
    size: Optional[str] = None
    width: Optional[int] = Field(default=None, ge=0)
    height: Optional[int] = Field(default=None, ge=0)
    theme_id: Optional[str] = None
    theme_name: Optional[str] = None
    concept_image_ids: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    created_by: Optional[str] = None
    final_variant_id: Optional[str] = None
    current_image_url: Optional[str] = None
    latest_generation_id: Optional[str] = None
    latest_generation_at: Optional[datetime] = None

    class Config:
        extra = "forbid"


class AssetCreate(AssetBase):
    id: Optional[str] = Field(
        default=None, description="Optional Firestore document id to use."
    )
    name: str


class AssetUpdate(AssetBase):
    name: Optional[str] = None


class GenerationBase(BaseModel):
    parameters: Optional[Dict[str, Any]] = None
    theme_id: Optional[str] = None
    theme_snapshot: Optional[Dict[str, Any]] = None
    concept_image_ids: Optional[List[str]] = None
    concept_image_weights: Optional[Dict[str, float]] = None
    variant_count: Optional[int] = Field(default=None, ge=0)
    triggered_by: Optional[str] = None
    status: Optional[models.GenerationStatus] = None
    notes: Optional[str] = None
    version_number: Optional[int] = None
    variant_summary: Optional[List[Dict[str, Any]]] = None

    class Config:
        extra = "forbid"


class GenerationCreate(GenerationBase):
    id: Optional[str] = Field(
        default=None, description="Optional Firestore document id to use."
    )
    prompt_text: str


class GenerationUpdate(GenerationBase):
    prompt_text: Optional[str] = None


class VariantBase(BaseModel):
    thumbnail_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    is_selected: Optional[bool] = None
    feedback: Optional[str] = None
    generated_at: Optional[datetime] = None

    class Config:
        extra = "forbid"


class VariantCreate(VariantBase):
    id: Optional[str] = Field(
        default=None, description="Optional Firestore document id to use."
    )
    image_url: str


class VariantUpdate(VariantBase):
    image_url: Optional[str] = None


class ThemeBase(BaseModel):
    name: Optional[str] = None
    style_keywords: Optional[List[str]] = None
    color_palette: Optional[List[str]] = None
    description: Optional[str] = None
    example_image: Optional[str] = None
    created_by: Optional[str] = None
    style_guide_markdown: Optional[str] = None
    concept_image_ids: Optional[List[str]] = None

    class Config:
        extra = "forbid"


class ThemeCreate(ThemeBase):
    id: Optional[str] = Field(
        default=None, description="Optional Firestore document id to use."
    )
    name: str


class ThemeUpdate(ThemeBase):
    pass


class ConceptImageBase(BaseModel):
    thumbnail_url: Optional[str] = None
    tags: Optional[List[str]] = None
    description: Optional[str] = None
    attribution: Optional[str] = None
    uploaded_by: Optional[str] = None
    theme_id: Optional[str] = None
    asset_id: Optional[str] = None
    usage_count: Optional[int] = Field(default=None, ge=0)

    class Config:
        extra = "forbid"


class ConceptImageCreate(ConceptImageBase):
    id: Optional[str] = Field(
        default=None, description="Optional Firestore document id to use."
    )
    image_url: str


class ConceptImageUpdate(ConceptImageBase):
    image_url: Optional[str] = None


class UserBase(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    profile_picture_url: Optional[str] = None
    org_memberships: Optional[List[models.Membership]] = None
    project_memberships: Optional[List[models.ProjectMembership]] = None
    last_login: Optional[datetime] = None
    preferences: Optional[Dict[str, Any]] = None

    class Config:
        extra = "forbid"


class UserCreate(UserBase):
    id: Optional[str] = Field(
        default=None, description="Optional Firestore document id to use."
    )


class UserUpdate(UserBase):
    pass


def _build_firestore_model(model_cls: Type[ModelT], data: Dict[str, Any]) -> ModelT:
    model = model_cls(**data)
    if isinstance(model, FirestoreBase):
        if hasattr(model, "id"):
            setattr(model, "id", None)
        if hasattr(model, "created_at"):
            setattr(model, "created_at", None)
        if hasattr(model, "updated_at"):
            setattr(model, "updated_at", None)
    return model


def _apply_metadata(model: BaseModel, **metadata: Optional[str]) -> None:
    for field, value in metadata.items():
        if value is not None and hasattr(model, field):
            setattr(model, field, value)


def _require_updates(payload: BaseModel) -> Dict[str, Any]:
    updates = payload.dict(exclude_unset=True, exclude_none=True)
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update.",
        )
    return updates


@lru_cache()
def _get_accessor_cached() -> FirestoreAccessor:
    return FirestoreAccessor(
        project=os.getenv("FIRESTORE_PROJECT"),
        credentials_path=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
        use_emulator=bool(os.getenv("FIRESTORE_EMULATOR_HOST")),
    )


def get_accessor() -> FirestoreAccessor:
    try:
        return _get_accessor_cached()
    except FirestoreError as exc:  # pragma: no cover - defensive fallback
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


@router.get("/health", response_model=Dict[str, str])
def healthcheck() -> Dict[str, str]:
    return {"status": "ok"}


@router.post(
    "/orgs",
    response_model=models.Organization,
    status_code=status.HTTP_201_CREATED,
)
def create_organization(
    payload: OrganizationCreate, accessor: FirestoreAccessor = Depends(get_accessor)
) -> models.Organization:
    data = payload.dict(exclude_unset=True, exclude_none=True)
    org_id = data.pop("id", None)
    org_model = _build_firestore_model(models.Organization, data)
    try:
        return accessor.create_organization(org_model, org_id=org_id)
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


@router.get("/orgs", response_model=List[models.Organization])
def list_organizations(
    accessor: FirestoreAccessor = Depends(get_accessor),
) -> List[models.Organization]:
    try:
        return accessor.list_organizations()
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


@router.get("/orgs/{org_id}", response_model=models.Organization)
def get_organization(
    org_id: str, accessor: FirestoreAccessor = Depends(get_accessor)
) -> models.Organization:
    try:
        organization = accessor.get_organization(org_id)
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    if organization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    return organization


@router.patch("/orgs/{org_id}", response_model=models.Organization)
def update_organization(
    org_id: str,
    payload: OrganizationUpdate,
    accessor: FirestoreAccessor = Depends(get_accessor),
) -> models.Organization:
    updates = _require_updates(payload)
    _ = get_organization(org_id, accessor)  # Raises 404 when missing.
    try:
        accessor.update_organization(org_id, updates)
        updated = accessor.get_organization(org_id)
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    assert updated is not None  # For mypy; previous call guarantees existence.
    return updated


@router.delete("/orgs/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_organization(
    org_id: str, accessor: FirestoreAccessor = Depends(get_accessor)
) -> Response:
    _ = get_organization(org_id, accessor)
    try:
        accessor.delete_organization(org_id)
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/orgs/{org_id}/projects",
    response_model=models.Project,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    org_id: str,
    payload: ProjectCreate,
    accessor: FirestoreAccessor = Depends(get_accessor),
) -> models.Project:
    data = payload.dict(exclude_unset=True, exclude_none=True)
    project_id = data.pop("id", None)
    project_model = _build_firestore_model(models.Project, data)
    _apply_metadata(project_model, org_id=org_id)
    try:
        return accessor.create_project(org_id, project_model, project_id=project_id)
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


@router.get(
    "/orgs/{org_id}/projects", response_model=List[models.Project]
)
def list_projects(
    org_id: str, accessor: FirestoreAccessor = Depends(get_accessor)
) -> List[models.Project]:
    try:
        return accessor.list_projects(org_id)
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


@router.get(
    "/orgs/{org_id}/projects/{project_id}",
    response_model=models.Project,
)
def get_project(
    org_id: str,
    project_id: str,
    accessor: FirestoreAccessor = Depends(get_accessor),
) -> models.Project:
    try:
        project = accessor.get_project(org_id, project_id)
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    return project


@router.patch(
    "/orgs/{org_id}/projects/{project_id}",
    response_model=models.Project,
)
def update_project(
    org_id: str,
    project_id: str,
    payload: ProjectUpdate,
    accessor: FirestoreAccessor = Depends(get_accessor),
) -> models.Project:
    updates = _require_updates(payload)
    _ = get_project(org_id, project_id, accessor)
    try:
        accessor.update_project(org_id, project_id, updates)
        updated = accessor.get_project(org_id, project_id)
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    assert updated is not None
    return updated


@router.delete(
    "/orgs/{org_id}/projects/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_project(
    org_id: str,
    project_id: str,
    accessor: FirestoreAccessor = Depends(get_accessor),
) -> Response:
    _ = get_project(org_id, project_id, accessor)
    try:
        accessor.delete_project(org_id, project_id)
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/orgs/{org_id}/projects/{project_id}/assets",
    response_model=models.Asset,
    status_code=status.HTTP_201_CREATED,
)
def create_asset(
    org_id: str,
    project_id: str,
    payload: AssetCreate,
    accessor: FirestoreAccessor = Depends(get_accessor),
) -> models.Asset:
    data = payload.dict(exclude_unset=True, exclude_none=True)
    asset_id = data.pop("id", None)
    asset_model = _build_firestore_model(models.Asset, data)
    _apply_metadata(asset_model, org_id=org_id, project_id=project_id)
    try:
        return accessor.create_asset(org_id, project_id, asset_model, asset_id=asset_id)
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


@router.get(
    "/orgs/{org_id}/projects/{project_id}/assets",
    response_model=List[models.Asset],
)
def list_assets(
    org_id: str,
    project_id: str,
    tag: Optional[str] = Query(default=None, description="Filter by asset tag."),
    theme_id: Optional[str] = Query(
        default=None, description="Filter by related theme id."
    ),
    accessor: FirestoreAccessor = Depends(get_accessor),
) -> List[models.Asset]:
    where = []
    if tag:
        where.append(("tags", "array_contains", tag))
    if theme_id:
        where.append(("theme_id", "==", theme_id))
    try:
        return accessor.list_assets(org_id, project_id, where=where or None)
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


@router.get(
    "/orgs/{org_id}/projects/{project_id}/assets/{asset_id}",
    response_model=models.Asset,
)
def get_asset(
    org_id: str,
    project_id: str,
    asset_id: str,
    accessor: FirestoreAccessor = Depends(get_accessor),
) -> models.Asset:
    try:
        asset = accessor.get_asset(org_id, project_id, asset_id)
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    return asset


@router.patch(
    "/orgs/{org_id}/projects/{project_id}/assets/{asset_id}",
    response_model=models.Asset,
)
def update_asset(
    org_id: str,
    project_id: str,
    asset_id: str,
    payload: AssetUpdate,
    accessor: FirestoreAccessor = Depends(get_accessor),
) -> models.Asset:
    updates = _require_updates(payload)
    _ = get_asset(org_id, project_id, asset_id, accessor)
    try:
        accessor.update_asset(org_id, project_id, asset_id, updates)
        updated = accessor.get_asset(org_id, project_id, asset_id)
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    assert updated is not None
    return updated


@router.delete(
    "/orgs/{org_id}/projects/{project_id}/assets/{asset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_asset(
    org_id: str,
    project_id: str,
    asset_id: str,
    accessor: FirestoreAccessor = Depends(get_accessor),
) -> Response:
    _ = get_asset(org_id, project_id, asset_id, accessor)
    try:
        accessor.delete_asset(org_id, project_id, asset_id)
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/orgs/{org_id}/projects/{project_id}/assets/{asset_id}/generations",
    response_model=models.Generation,
    status_code=status.HTTP_201_CREATED,
)
def create_generation(
    org_id: str,
    project_id: str,
    asset_id: str,
    payload: GenerationCreate,
    accessor: FirestoreAccessor = Depends(get_accessor),
) -> models.Generation:
    data = payload.dict(exclude_unset=True, exclude_none=True)
    generation_id = data.pop("id", None)
    generation_model = _build_firestore_model(models.Generation, data)
    _apply_metadata(
        generation_model, org_id=org_id, project_id=project_id, asset_id=asset_id
    )
    try:
        return accessor.create_generation(
            org_id, project_id, asset_id, generation_model, generation_id=generation_id
        )
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


@router.get(
    "/orgs/{org_id}/projects/{project_id}/assets/{asset_id}/generations",
    response_model=List[models.Generation],
)
def list_generations(
    org_id: str,
    project_id: str,
    asset_id: str,
    order_by: str = Query(default="created_at"),
    descending: bool = Query(default=True),
    accessor: FirestoreAccessor = Depends(get_accessor),
) -> List[models.Generation]:
    try:
        return accessor.list_generations(
            org_id, project_id, asset_id, order_by=order_by, desc=descending
        )
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


@router.get(
    "/orgs/{org_id}/projects/{project_id}/assets/{asset_id}/generations/{generation_id}",
    response_model=models.Generation,
)
def get_generation(
    org_id: str,
    project_id: str,
    asset_id: str,
    generation_id: str,
    accessor: FirestoreAccessor = Depends(get_accessor),
) -> models.Generation:
    try:
        generation = accessor.get_generation(
            org_id, project_id, asset_id, generation_id
        )
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    if generation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    return generation


@router.patch(
    "/orgs/{org_id}/projects/{project_id}/assets/{asset_id}/generations/{generation_id}",
    response_model=models.Generation,
)
def update_generation(
    org_id: str,
    project_id: str,
    asset_id: str,
    generation_id: str,
    payload: GenerationUpdate,
    accessor: FirestoreAccessor = Depends(get_accessor),
) -> models.Generation:
    updates = _require_updates(payload)
    _ = get_generation(org_id, project_id, asset_id, generation_id, accessor)
    try:
        accessor.update_generation(
            org_id, project_id, asset_id, generation_id, updates
        )
        updated = accessor.get_generation(org_id, project_id, asset_id, generation_id)
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    assert updated is not None
    return updated


@router.delete(
    "/orgs/{org_id}/projects/{project_id}/assets/{asset_id}/generations/{generation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_generation(
    org_id: str,
    project_id: str,
    asset_id: str,
    generation_id: str,
    accessor: FirestoreAccessor = Depends(get_accessor),
) -> Response:
    _ = get_generation(org_id, project_id, asset_id, generation_id, accessor)
    try:
        accessor.delete_generation(org_id, project_id, asset_id, generation_id)
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/orgs/{org_id}/projects/{project_id}/assets/{asset_id}/generations/{generation_id}/variants",
    response_model=models.Variant,
    status_code=status.HTTP_201_CREATED,
)
def create_variant(
    org_id: str,
    project_id: str,
    asset_id: str,
    generation_id: str,
    payload: VariantCreate,
    accessor: FirestoreAccessor = Depends(get_accessor),
) -> models.Variant:
    data = payload.dict(exclude_unset=True, exclude_none=True)
    variant_id = data.pop("id", None)
    variant_model = _build_firestore_model(models.Variant, data)
    _apply_metadata(
        variant_model,
        org_id=org_id,
        project_id=project_id,
        asset_id=asset_id,
        generation_id=generation_id,
    )
    try:
        return accessor.create_variant(
            org_id,
            project_id,
            asset_id,
            generation_id,
            variant_model,
            variant_id=variant_id,
        )
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


@router.get(
    "/orgs/{org_id}/projects/{project_id}/assets/{asset_id}/generations/{generation_id}/variants",
    response_model=List[models.Variant],
)
def list_variants(
    org_id: str,
    project_id: str,
    asset_id: str,
    generation_id: str,
    accessor: FirestoreAccessor = Depends(get_accessor),
) -> List[models.Variant]:
    try:
        return accessor.list_variants(org_id, project_id, asset_id, generation_id)
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


@router.get(
    "/orgs/{org_id}/projects/{project_id}/assets/{asset_id}/generations/{generation_id}/variants/{variant_id}",
    response_model=models.Variant,
)
def get_variant(
    org_id: str,
    project_id: str,
    asset_id: str,
    generation_id: str,
    variant_id: str,
    accessor: FirestoreAccessor = Depends(get_accessor),
) -> models.Variant:
    try:
        variant = accessor.get_variant(
            org_id, project_id, asset_id, generation_id, variant_id
        )
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    if variant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    return variant


@router.patch(
    "/orgs/{org_id}/projects/{project_id}/assets/{asset_id}/generations/{generation_id}/variants/{variant_id}",
    response_model=models.Variant,
)
def update_variant(
    org_id: str,
    project_id: str,
    asset_id: str,
    generation_id: str,
    variant_id: str,
    payload: VariantUpdate,
    accessor: FirestoreAccessor = Depends(get_accessor),
) -> models.Variant:
    updates = _require_updates(payload)
    _ = get_variant(org_id, project_id, asset_id, generation_id, variant_id, accessor)
    try:
        accessor.update_variant(
            org_id, project_id, asset_id, generation_id, variant_id, updates
        )
        updated = accessor.get_variant(
            org_id, project_id, asset_id, generation_id, variant_id
        )
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    assert updated is not None
    return updated


@router.delete(
    "/orgs/{org_id}/projects/{project_id}/assets/{asset_id}/generations/{generation_id}/variants/{variant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_variant(
    org_id: str,
    project_id: str,
    asset_id: str,
    generation_id: str,
    variant_id: str,
    accessor: FirestoreAccessor = Depends(get_accessor),
) -> Response:
    _ = get_variant(org_id, project_id, asset_id, generation_id, variant_id, accessor)
    try:
        accessor.delete_variant(
            org_id, project_id, asset_id, generation_id, variant_id
        )
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/orgs/{org_id}/projects/{project_id}/themes",
    response_model=models.Theme,
    status_code=status.HTTP_201_CREATED,
)
def create_theme(
    org_id: str,
    project_id: str,
    payload: ThemeCreate,
    accessor: FirestoreAccessor = Depends(get_accessor),
) -> models.Theme:
    data = payload.dict(exclude_unset=True, exclude_none=True)
    theme_id = data.pop("id", None)
    theme_model = _build_firestore_model(models.Theme, data)
    _apply_metadata(theme_model, org_id=org_id, project_id=project_id)
    try:
        return accessor.create_theme(org_id, project_id, theme_model, theme_id=theme_id)
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


@router.get(
    "/orgs/{org_id}/projects/{project_id}/themes",
    response_model=List[models.Theme],
)
def list_themes(
    org_id: str,
    project_id: str,
    accessor: FirestoreAccessor = Depends(get_accessor),
) -> List[models.Theme]:
    try:
        return accessor.list_themes(org_id, project_id)
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


@router.get(
    "/orgs/{org_id}/projects/{project_id}/themes/{theme_id}",
    response_model=models.Theme,
)
def get_theme(
    org_id: str,
    project_id: str,
    theme_id: str,
    accessor: FirestoreAccessor = Depends(get_accessor),
) -> models.Theme:
    try:
        theme = accessor.get_theme(org_id, project_id, theme_id)
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    if theme is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    return theme


@router.patch(
    "/orgs/{org_id}/projects/{project_id}/themes/{theme_id}",
    response_model=models.Theme,
)
def update_theme(
    org_id: str,
    project_id: str,
    theme_id: str,
    payload: ThemeUpdate,
    accessor: FirestoreAccessor = Depends(get_accessor),
) -> models.Theme:
    updates = _require_updates(payload)
    _ = get_theme(org_id, project_id, theme_id, accessor)
    try:
        accessor.update_theme(org_id, project_id, theme_id, updates)
        updated = accessor.get_theme(org_id, project_id, theme_id)
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    assert updated is not None
    return updated


@router.delete(
    "/orgs/{org_id}/projects/{project_id}/themes/{theme_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_theme(
    org_id: str,
    project_id: str,
    theme_id: str,
    accessor: FirestoreAccessor = Depends(get_accessor),
) -> Response:
    _ = get_theme(org_id, project_id, theme_id, accessor)
    try:
        accessor.delete_theme(org_id, project_id, theme_id)
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/orgs/{org_id}/projects/{project_id}/concept-images",
    response_model=models.ConceptImage,
    status_code=status.HTTP_201_CREATED,
)
def create_concept_image(
    org_id: str,
    project_id: str,
    payload: ConceptImageCreate,
    accessor: FirestoreAccessor = Depends(get_accessor),
) -> models.ConceptImage:
    data = payload.dict(exclude_unset=True, exclude_none=True)
    image_id = data.pop("id", None)
    concept_image_model = _build_firestore_model(models.ConceptImage, data)
    _apply_metadata(concept_image_model, org_id=org_id, project_id=project_id)
    try:
        return accessor.create_concept_image(
            org_id, project_id, concept_image_model, image_id=image_id
        )
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


@router.get(
    "/orgs/{org_id}/projects/{project_id}/concept-images",
    response_model=List[models.ConceptImage],
)
def list_concept_images(
    org_id: str,
    project_id: str,
    tag: Optional[str] = Query(default=None, description="Filter by image tag."),
    accessor: FirestoreAccessor = Depends(get_accessor),
) -> List[models.ConceptImage]:
    try:
        return accessor.list_concept_images(org_id, project_id, tag=tag)
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


@router.get(
    "/orgs/{org_id}/projects/{project_id}/concept-images/{image_id}",
    response_model=models.ConceptImage,
)
def get_concept_image(
    org_id: str,
    project_id: str,
    image_id: str,
    accessor: FirestoreAccessor = Depends(get_accessor),
) -> models.ConceptImage:
    try:
        concept_image = accessor.get_concept_image(org_id, project_id, image_id)
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    if concept_image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    return concept_image


@router.patch(
    "/orgs/{org_id}/projects/{project_id}/concept-images/{image_id}",
    response_model=models.ConceptImage,
)
def update_concept_image(
    org_id: str,
    project_id: str,
    image_id: str,
    payload: ConceptImageUpdate,
    accessor: FirestoreAccessor = Depends(get_accessor),
) -> models.ConceptImage:
    updates = _require_updates(payload)
    _ = get_concept_image(org_id, project_id, image_id, accessor)
    try:
        accessor.update_concept_image(org_id, project_id, image_id, updates)
        updated = accessor.get_concept_image(org_id, project_id, image_id)
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    assert updated is not None
    return updated


@router.delete(
    "/orgs/{org_id}/projects/{project_id}/concept-images/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_concept_image(
    org_id: str,
    project_id: str,
    image_id: str,
    accessor: FirestoreAccessor = Depends(get_accessor),
) -> Response:
    _ = get_concept_image(org_id, project_id, image_id, accessor)
    try:
        accessor.delete_concept_image(org_id, project_id, image_id)
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/users",
    response_model=models.User,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    payload: UserCreate, accessor: FirestoreAccessor = Depends(get_accessor)
) -> models.User:
    data = payload.dict(exclude_unset=True, exclude_none=True)
    user_id = data.pop("id", None)
    user_model = _build_firestore_model(models.User, data)
    try:
        return accessor.create_user(user_model, user_id=user_id)
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


@router.get("/users", response_model=List[models.User])
def list_users(
    accessor: FirestoreAccessor = Depends(get_accessor),
) -> List[models.User]:
    try:
        return accessor.list_users()
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


@router.get("/users/{user_id}", response_model=models.User)
def get_user(
    user_id: str, accessor: FirestoreAccessor = Depends(get_accessor)
) -> models.User:
    try:
        user = accessor.get_user(user_id)
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    return user


@router.patch("/users/{user_id}", response_model=models.User)
def update_user(
    user_id: str,
    payload: UserUpdate,
    accessor: FirestoreAccessor = Depends(get_accessor),
) -> models.User:
    updates = _require_updates(payload)
    _ = get_user(user_id, accessor)
    try:
        accessor.update_user(user_id, updates)
        updated = accessor.get_user(user_id)
    except FirestoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    assert updated is not None
    return updated


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str, accessor: FirestoreAccessor = Depends(get_accessor)
) -> Response:
    _ = get_user(user_id, accessor)
    try:
        accessor.delete_user(user_id)
    except FirestoreError as exc:
        raise HTTPException(
app.include_router(router)
