import asyncio

import pytest


async def test__provided_loop__is_running_loop(event_loop):
    assert event_loop is asyncio.get_running_loop()


@pytest.mark.asyncio
async def test__health_check__is_returning_200(client):
    response = await client.get("/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test__get_user__valid_id__returns_user(user, client):
    response = await client.get(f"/users/{user.id}")
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["username"] == user.username
    assert response_data["email"] == user.email
    assert response_data["name"] == user.name


@pytest.mark.asyncio
async def test__get_users__valid_id__returns_user(users, client):
    user_usernames = {user.username for user in users}
    emails = {user.email for user in users}
    names = {user.name for user in users}

    response = await client.get(f"/users")
    response_data = response.json()

    assert response.status_code == 200
    for user in response_data:
        assert user["username"] in user_usernames
        assert user["email"] in emails
        assert user["names"] in names


@pytest.mark.asyncio
async def test__invalid_id__returns_404(client):
    response = await client.get("/users/1")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
