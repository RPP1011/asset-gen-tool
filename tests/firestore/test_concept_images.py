from api import models


def test_concept_image_create_and_filter(accessor, create_org, create_project):
    org_id = create_org("Concept Org")
    project_id, _ = create_project(org_id, name="Concept Project")

    accessor.create_concept_image(
        org_id,
        project_id,
        models.ConceptImage(image_url="gs://example/ci1.png", tags=["robot", "sci-fi"]),
    )
    accessor.create_concept_image(
        org_id,
        project_id,
        models.ConceptImage(image_url="gs://example/ci2.png", tags=["robot", "retro"]),
    )
    accessor.create_concept_image(
        org_id,
        project_id,
        models.ConceptImage(
            image_url="gs://example/ci3.png", tags=["landscape", "fantasy"]
        ),
    )

    all_images = accessor.list_concept_images(org_id, project_id)
    assert len(all_images) >= 3

    filtered = accessor.list_concept_images(org_id, project_id, tag="robot")
    urls = {ci.image_url for ci in filtered}
    assert "gs://example/ci1.png" in urls
    assert "gs://example/ci2.png" in urls
    assert "gs://example/ci3.png" not in urls
