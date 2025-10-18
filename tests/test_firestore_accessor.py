import os
import uuid
from typing import Iterator

import pytest

from google.cloud import firestore

from api.firebase import FirestoreAccessor, FirestoreError
from api import models


def _integration_enabled() -> bool:
    """Integration enabled if either emulator host or service account is configured."""
    return bool(
        os.getenv("FIRESTORE_EMULATOR_HOST")
        or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        or os.getenv("FIRESTORE_PROJECT")
    )


def _recursive_delete_document(doc_ref: firestore.DocumentReference) -> None:
    """
    Recursively delete a document and all nested subcollections.
    This implementation walks subcollections and deletes documents iteratively.
    """
    # Delete subcollections first
    for subcol in doc_ref.collections():
        _recursive_delete_collection(subcol)
    # Delete the document itself
    doc_ref.delete()


def _recursive_delete_collection(col_ref: firestore.CollectionReference) -> None:
    """
    Recursively delete all documents in a collection.
    Note: For large collections prefer the Firestore managed bulk-delete or admin tools.
    """
    # Use list_documents to get DocumentReference objects (no need to fetch snapshots)
    docs = list(col_ref.list_documents())
    for doc_ref in docs:
        _recursive_delete_document(doc_ref)


@pytest.fixture(scope="module")
def firestore_client() -> Iterator[firestore.Client]:
    """
    Return a real Firestore client if integration is enabled; otherwise skip tests.
    Uses emulator if FIRESTORE_EMULATOR_HOST is set.
    """
    if not _integration_enabled():
        pytest.skip(
            "Skipping Firestore integration tests; set FIRESTORE_EMULATOR_HOST or GOOGLE_APPLICATION_CREDENTIALS"
        )
    # Construct a client; the google-cloud library will respect the emulator env var if present.
    client = firestore.Client()
    yield client
    # nothing global to cleanup here


@pytest.fixture
def accessor(firestore_client: firestore.Client) -> Iterator[FirestoreAccessor]:
    """
    Return a FirestoreAccessor configured to use the environment credentials (emulator or service account).
    Cleanup of created test documents should be done by the test using the created IDs.
    """
    # The accessor uses environment for client initialization; ensure the env is present.
    acc = FirestoreAccessor(use_emulator=bool(os.getenv("FIRESTORE_EMULATOR_HOST")))
    yield acc
    # accessor does not own cleanup responsibilities here


def _random_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def test_integration_create_and_cleanup(
    accessor: FirestoreAccessor, firestore_client: firestore.Client
):
    """
    Integration test that creates an organization, project, asset, generation and variant,
    then verifies reads and finally performs a recursive cleanup of the organization path.
    """

    # Generate unique IDs so tests are isolated and safe to run concurrently
    org_id = _random_id("testorg")
    project_id = _random_id("testproj")
    asset_id = _random_id("testasset")
    gen_id = _random_id("testgen")
    var_id = _random_id("testvar")

    # Create organization and resources with explicit IDs
    org = models.Organization(name="Integration Org")
    created_org = accessor.create_organization(org, org_id=org_id)
    assert created_org is not None
    assert created_org.id == org_id
    assert created_org.name == "Integration Org"

    project = models.Project(name="Integration Project")
    created_proj = accessor.create_project(org_id, project, project_id=project_id)
    assert created_proj is not None
    assert created_proj.id == project_id
    assert created_proj.name == "Integration Project"
    assert created_proj.org_id == org_id

    asset = models.Asset(name="Integration Asset")
    created_asset = accessor.create_asset(org_id, project_id, asset, asset_id=asset_id)
    assert created_asset is not None
    assert created_asset.id == asset_id
    assert created_asset.name == "Integration Asset"

    generation = models.Generation(prompt_text="integration prompt")
    created_gen = accessor.create_generation(
        org_id, project_id, asset_id, generation, generation_id=gen_id
    )
    assert created_gen is not None
    assert created_gen.id == gen_id
    assert created_gen.prompt_text == "integration prompt"

    variant = models.Variant(image_url="gs://example-bucket/integration-var.png")
    created_var = accessor.create_variant(
        org_id, project_id, asset_id, gen_id, variant, variant_id=var_id
    )
    assert created_var is not None
    assert created_var.id == var_id
    assert created_var.image_url == "gs://example-bucket/integration-var.png"

    # Read back a few things via accessor to verify
    got_asset = accessor.get_asset(org_id, project_id, asset_id)
    assert got_asset is not None
    assert got_asset.id == asset_id
    assert got_asset.name == "Integration Asset"

    got_gen = accessor.get_generation(org_id, project_id, asset_id, gen_id)
    assert got_gen is not None
    assert got_gen.id == gen_id
    assert got_gen.prompt_text == "integration prompt"

    got_var = accessor.get_variant(org_id, project_id, asset_id, gen_id, var_id)
    assert got_var is not None
    assert got_var.id == var_id
    assert got_var.image_url == "gs://example-bucket/integration-var.png"

    # Now perform cleanup: recursively delete the organization document and its subcollections
    # This ensures the test leaves Firestore in the previous state.
    org_doc_ref = firestore_client.document(f"organizations/{org_id}")
    _recursive_delete_document(org_doc_ref)

    # Verify deletion: document should not exist
    snap = org_doc_ref.get()
    assert not snap.exists


def test_integration_list_and_query(
    accessor: FirestoreAccessor, firestore_client: firestore.Client
):
    """
    Additional integration smoke test: create multiple concept images and query by tag.
    Clean up after the test.
    """
    org_id = _random_id("testorg")
    project_id = _random_id("testproj")

    # create org & project
    accessor.create_organization(models.Organization(name="ConceptOrg"), org_id=org_id)
    accessor.create_project(
        org_id, models.Project(name="ConceptProject"), project_id=project_id
    )

    # create concept images
    ci1 = models.ConceptImage(
        image_url="gs://example/ci1.png", tags=["robot", "sci-fi"]
    )
    ci2 = models.ConceptImage(image_url="gs://example/ci2.png", tags=["robot", "retro"])
    accessor.create_concept_image(org_id, project_id, ci1)
    accessor.create_concept_image(org_id, project_id, ci2)

    # list by tag using the accessor helper
    results = accessor.list_concept_images(org_id, project_id, tag="robot")
    # Expect at least two results; depending on timing and environment this may include others, but we assert count >= 2
    assert len(results) >= 2
    urls = {r.image_url for r in results}
    assert "gs://example/ci1.png" in urls and "gs://example/ci2.png" in urls

    # cleanup
    org_doc_ref = firestore_client.document(f"organizations/{org_id}")
    _recursive_delete_document(org_doc_ref)
    # verify deletion
    snap = org_doc_ref.get()
    assert not snap.exists


if __name__ == "__main__":
    # Allow running the integration tests directly if environment is configured
    pytest.main([__file__])
