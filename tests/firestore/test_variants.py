def test_variant_create_get_and_list(
    accessor,
    create_org,
    create_project,
    create_asset,
    create_generation,
    create_variant,
):
    org_id = create_org("Variant Org")
    project_id, _ = create_project(org_id, name="Variant Project")
    asset_id, _ = create_asset(org_id, project_id, name="Variant Asset")
    gen_id, _ = create_generation(org_id, project_id, asset_id, prompt="variant prompt")

    var_id, _ = create_variant(
        org_id,
        project_id,
        asset_id,
        gen_id,
        url="gs://example/variant_primary.png",
    )
    create_variant(
        org_id,
        project_id,
        asset_id,
        gen_id,
        url="gs://example/variant_secondary.png",
    )

    fetched = accessor.get_variant(org_id, project_id, asset_id, gen_id, var_id)
    assert fetched is not None
    assert fetched.id == var_id
    assert fetched.image_url == "gs://example/variant_primary.png"
    assert fetched.org_id == org_id
    assert fetched.project_id == project_id

    variants = accessor.list_variants(org_id, project_id, asset_id, gen_id)
    urls = {v.image_url for v in variants}
    assert "gs://example/variant_primary.png" in urls
    assert "gs://example/variant_secondary.png" in urls
