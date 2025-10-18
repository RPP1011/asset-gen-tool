from api.models import GenerationStatus


def test_generation_crud_and_listing(
    accessor,
    create_org,
    create_project,
    create_asset,
    create_generation,
):
    org_id = create_org("Generation Org")
    project_id, _ = create_project(org_id, name="Generation Project")
    asset_id, _ = create_asset(org_id, project_id, name="Generation Asset")

    gen_id, _ = create_generation(org_id, project_id, asset_id, prompt="first prompt")
    accessor.update_generation(
        org_id,
        project_id,
        asset_id,
        gen_id,
        {"status": GenerationStatus.COMPLETED.value},
    )

    fetched = accessor.get_generation(org_id, project_id, asset_id, gen_id)
    assert fetched is not None
    assert fetched.id == gen_id
    assert fetched.status == GenerationStatus.COMPLETED
    assert fetched.project_id == project_id
    assert fetched.org_id == org_id

    # create another generation to exercise list ordering
    gen2_id, _ = create_generation(org_id, project_id, asset_id, prompt="second prompt")
    generations = accessor.list_generations(
        org_id, project_id, asset_id, order_by="created_at", desc=False
    )

    ids = [g.id for g in generations]
    assert gen_id in ids and gen2_id in ids
