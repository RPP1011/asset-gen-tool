import os
import uuid
from typing import Callable, Iterator, List, Tuple

import pytest

try:
    from google.cloud import firestore  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    firestore = None  # type: ignore

from api.firebase import FirestoreAccessor, FirestoreError
from api import models


def _integration_enabled() -> bool:
    """Integration enabled if emulator host, credentials, or project id configured."""
    return bool(
        os.getenv("FIRESTORE_EMULATOR_HOST")
        or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    )


def _recursive_delete_document(doc_ref: "firestore.DocumentReference") -> None:
    """Recursively delete a Firestore document and subcollections."""
    for subcol in doc_ref.collections():
        _recursive_delete_collection(subcol)
    doc_ref.delete()


def _recursive_delete_collection(col_ref: "firestore.CollectionReference") -> None:
    """Recursively delete all documents within a collection."""
    docs = list(col_ref.list_documents())
    for doc_ref in docs:
        _recursive_delete_document(doc_ref)


@pytest.fixture(scope="module")
def firestore_client() -> Iterator["firestore.Client"]:
    """
    Provide a Firestore client backed by emulator or live service.
    Skip the suite if firestore package missing or environment not configured.
    """
    if firestore is None:
        pytest.skip("google-cloud-firestore is not installed.")
    if not _integration_enabled():
        pytest.skip(
            "Skipping Firestore integration tests; set FIRESTORE_EMULATOR_HOST or credentials."
        )
    client = firestore.Client()
    yield client


@pytest.fixture
def accessor(firestore_client: "firestore.Client") -> Iterator[FirestoreAccessor]:
    """Return a FirestoreAccessor configured for emulator / environment usage."""
    try:
        acc = FirestoreAccessor(use_emulator=bool(os.getenv("FIRESTORE_EMULATOR_HOST")))
    except FirestoreError as exc:  # pragma: no cover - defensive
        pytest.skip(f"Firestore accessor unavailable: {exc}")
    yield acc


@pytest.fixture
def random_id() -> Callable[[str], str]:
    """Return helper to generate unique ids per test."""

    def _factory(prefix: str) -> str:
        return f"{prefix}_{uuid.uuid4().hex[:12]}"

    return _factory


@pytest.fixture
def register_cleanup(
    firestore_client: "firestore.Client",
) -> Iterator[Callable[[str], None]]:
    """
    Fixture to track created document paths for cleanup.

    Usage:
        register_cleanup(f"organizations/{org_id}")
    """
    paths: List[str] = []
    yield paths.append
    for path in paths:
        doc_ref = firestore_client.document(path)
        try:
            _recursive_delete_document(doc_ref)
        except Exception:
            # Cleanup best-effort; ignore errors (e.g., document already deleted)
            pass


@pytest.fixture
def create_org(
    accessor: FirestoreAccessor,
    random_id: Callable[[str], str],
    register_cleanup: Callable[[str], None],
) -> Callable[[str], str]:
    """Factory returning an org_id after creating an organization document."""

    def _create(name: str = "Test Org") -> str:
        org_id = random_id("org")
        accessor.create_organization(models.Organization(name=name), org_id=org_id)
        register_cleanup(f"organizations/{org_id}")
        return org_id

    return _create


@pytest.fixture
def create_project(
    accessor: FirestoreAccessor,
    random_id: Callable[[str], str],
) -> Callable[[str, str], Tuple[str, models.Project]]:
    """Factory to create a project under an organization; returns (project_id, project_model)."""

    def _create(org_id: str, name: str = "Test Project") -> Tuple[str, models.Project]:
        project_id = random_id("proj")
        project = models.Project(name=name)
        accessor.create_project(org_id, project, project_id=project_id)
        return project_id, project

    return _create


@pytest.fixture
def create_asset(
    accessor: FirestoreAccessor,
    random_id: Callable[[str], str],
) -> Callable[[str, str, str], Tuple[str, models.Asset]]:
    """Factory to create an asset; returns (asset_id, asset_model)."""

    def _create(
        org_id: str, project_id: str, name: str = "Test Asset"
    ) -> Tuple[str, models.Asset]:
        asset_id = random_id("asset")
        asset = models.Asset(name=name)
        accessor.create_asset(org_id, project_id, asset, asset_id=asset_id)
        return asset_id, asset

    return _create


@pytest.fixture
def create_generation(
    accessor: FirestoreAccessor,
    random_id: Callable[[str], str],
) -> Callable[[str, str, str], Tuple[str, models.Generation]]:
    """Factory to create a generation; returns (generation_id, generation_model)."""

    def _create(
        org_id: str, project_id: str, asset_id: str, prompt: str = "prompt"
    ) -> Tuple[str, models.Generation]:
        generation_id = random_id("gen")
        generation = models.Generation(prompt_text=prompt)
        accessor.create_generation(
            org_id, project_id, asset_id, generation, generation_id=generation_id
        )
        return generation_id, generation

    return _create


@pytest.fixture
def create_variant(
    accessor: FirestoreAccessor,
    random_id: Callable[[str], str],
) -> Callable[[str, str, str, str], Tuple[str, models.Variant]]:
    """Factory to create a variant document."""

    def _create(
        org_id: str,
        project_id: str,
        asset_id: str,
        generation_id: str,
        url: str = "gs://example/variant.png",
    ) -> Tuple[str, models.Variant]:
        variant_id = random_id("var")
        variant = models.Variant(image_url=url)
        accessor.create_variant(
            org_id, project_id, asset_id, generation_id, variant, variant_id=variant_id
        )
        return variant_id, variant

    return _create
