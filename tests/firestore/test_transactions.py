from api import models


def test_create_asset_with_first_generation_and_variants(
    accessor,
    create_org,
    create_project,
    create_variant,
):
    org_id = create_org("Transaction Org")
    project_id, _ = create_project(org_id, name="Transaction Project")

    asset = models.Asset(name="Transactional Asset")
    generation = models.Generation(prompt_text="transactional prompt")

    created = accessor.create_asset_with_first_generation(
        org_id,
        project_id,
        asset,
        generation,
    )
    assert created.id is not None
    assert created.generations is not None
    assert len(created.generations) == 1

    asset_id = created.id
    generation_id = created.generations[0].id

    # Verify persisted documents exist
    fetched_asset = accessor.get_asset(org_id, project_id, asset_id)
    assert fetched_asset is not None

    fetched_generation = accessor.get_generation(
        org_id, project_id, asset_id, generation_id
    )
    assert fetched_generation is not None

    # create a variant and ensure aggregation helper returns combined result
    create_variant(
        org_id,
        project_id,
        asset_id,
        generation_id,
        url="gs://example/transaction_variant.png",
    )
    combined = accessor.get_generation_with_variants(
        org_id, project_id, asset_id, generation_id
    )
    assert combined is not None
    assert combined.id == generation_id
    assert combined.variants
    assert any(
        v.image_url == "gs://example/transaction_variant.png" for v in combined.variants
    )
