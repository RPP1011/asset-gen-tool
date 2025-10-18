def test_project_create_get_list_update(accessor, create_org, create_project):
    org_id = create_org("Project Org")
    project_id, _ = create_project(org_id, name="World Builder")

    fetched = accessor.get_project(org_id, project_id)
    assert fetched is not None
    assert fetched.id == project_id
    assert fetched.name == "World Builder"
    assert fetched.org_id == org_id

    accessor.update_project(org_id, project_id, {"description": "Updated description"})
    updated = accessor.get_project(org_id, project_id)
    assert updated is not None
    assert updated.description == "Updated description"

    projects = accessor.list_projects(org_id)
    assert any(p.id == project_id and p.org_id == org_id for p in projects)
