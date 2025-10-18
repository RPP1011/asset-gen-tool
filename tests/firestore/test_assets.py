def test_asset_crud_and_listing(accessor, create_org, create_project, create_asset):
    org_id = create_org("Asset Org")
    project_id, _ = create_project(org_id, name="Asset Project")

    asset_id, _ = create_asset(org_id, project_id, name="Hero Asset")
    accessor.update_asset(
        org_id,
        project_id,
        asset_id,
        {"description": "Primary asset", "tags": ["robot", "featured"]},
    )

    fetched = accessor.get_asset(org_id, project_id, asset_id)
    assert fetched is not None
    assert fetched.id == asset_id
    assert fetched.project_id == project_id
    assert fetched.org_id == org_id
    assert fetched.description == "Primary asset"

    # create a second asset for filter testing
    create_asset(org_id, project_id, name="Background Asset")

    assets = accessor.list_assets(org_id, project_id)
    assert any(a.id == asset_id and a.org_id == org_id for a in assets)

    filtered = accessor.list_assets(
        org_id, project_id, where=[("tags", "array_contains", "robot")]
    )
    assert any(a.id == asset_id for a in filtered)

    accessor.delete_asset(org_id, project_id, asset_id)
    assert accessor.get_asset(org_id, project_id, asset_id) is None
