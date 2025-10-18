from api import models


def test_user_create_get_list(accessor, register_cleanup):
    user_id = "user_" + models.now().strftime("%H%M%S%f")
    user = models.User(name="Test User", email="test@example.com")
    register_cleanup(f"users/{user_id}")

    created = accessor.create_user(user, user_id=user_id)
    assert created.id == user_id
    assert created.name == "Test User"

    fetched = accessor.get_user(user_id)
    assert fetched is not None
    assert fetched.id == user_id
    assert fetched.email == "test@example.com"

    users = accessor.list_users()
    assert any(u.id == user_id for u in users)
