from api import models


def test_create_and_get_organization(accessor, create_org):
    org_id = create_org("Acceptance Org")
    fetched = accessor.get_organization(org_id)
    assert fetched is not None
    assert fetched.id == org_id
    assert fetched.name == "Acceptance Org"


def test_list_update_and_delete_organization(accessor, create_org):
    org_id = create_org("Lifecycle Org")
    accessor.update_organization(org_id, {"plan_tier": "pro"})

    updated = accessor.get_organization(org_id)
    assert updated is not None
    assert updated.plan_tier == "pro"

    orgs = accessor.list_organizations()
    assert any(org.id == org_id and org.plan_tier == "pro" for org in orgs)

    accessor.delete_organization(org_id)
    assert accessor.get_organization(org_id) is None
