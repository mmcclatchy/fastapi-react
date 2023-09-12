import asyncio

import pytest

from db.models.account import Account


async def test__provided_loop__is_running_loop(event_loop):
    assert event_loop is asyncio.get_running_loop()


@pytest.mark.asyncio
async def test__health_check__is_returning_200(client):
    response = await client.get("/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test__get_account__valid_id__returns_account(account, client):
    response = await client.get(f"/accounts/{account.id}")
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["username"] == account.username
    assert response_data["email"] == account.email


@pytest.mark.asyncio
async def test__get_accounts__valid_id__returns_account(accounts, client):
    account_usernames = {account.username for account in accounts}
    emails = {account.email for account in accounts}

    response = await client.get(f"/accounts")
    response_data = response.json()

    assert response.status_code == 200
    for account in response_data:
        assert account["username"] in account_usernames
        assert account["email"] in emails


@pytest.mark.asyncio
async def test__create__valid_request__creates_account(session, client):
    request_json = {"username": "John Doe", "email": "john.doe@email.com"}
    response = await client.post("/accounts", json=request_json)
    response_data = response.json()
    db_account = await Account.get_by_id(session, response_data["id"])

    assert response.status_code == 201
    assert db_account.username == "John Doe"
    assert db_account.email == "john.doe@email.com"


@pytest.mark.parametrize(
    ("request_json", "err_loc", "err_msg", "err_type"),
    [
        (
            {"username": "John Doe"},
            ["body", "email"],
            "field required",
            "value_error.missing",
        ),
        (
            {"email": "john.doe@email.com"},
            ["body", "username"],
            "field required",
            "value_error.missing",
        ),
        (
            {"username": "John Doe", "email": "not_an_email"},
            ["body", "email"],
            "value is not a valid email address",
            "value_error.email",
        ),
    ],
)
@pytest.mark.asyncio
async def test__create__invalid_request__returns_422(
    request_json, err_loc, err_msg, err_type, client
):
    response = await client.post("/accounts", json=request_json)
    data_detail = response.json()["detail"][0]
    assert response.status_code == 422
    assert data_detail["loc"] == err_loc
    assert data_detail["msg"] == err_msg
    assert data_detail["type"] == err_type


@pytest.mark.parametrize(
    "data,expected_name,expected_email",
    [
        ({"username": "Jack Doe"}, "Jack Doe", "john.doe@email.com"),
        ({"email": "jdoe@new.com"}, "John Doe", "jdoe@new.com"),
    ],
)
@pytest.mark.asyncio
async def test__update__valid_request__updates_account(
    data, expected_name, expected_email, session, client, account
):
    response = await client.patch(f"/accounts/{account.id}", json=data)
    response_data = response.json()
    await session.refresh(account)
    db_account = await Account.get_by_id(session, response_data["id"])

    assert response.status_code == 200
    assert db_account.username == expected_name
    assert db_account.email == expected_email


@pytest.mark.asyncio
async def test__delete__valid_id__returns_204(session, client, account):
    response = await client.delete(f"/accounts/{account.id}")
    assert response.status_code == 204

    deleted_account = await Account.get_by_id(session, account.id)
    assert deleted_account is None


@pytest.mark.parametrize("request_type_name", ["get", "patch", "delete"])
@pytest.mark.asyncio
async def test__invalid_id__returns_404(request_type_name, client):
    request_type_method = getattr(client, request_type_name)
    kwargs = {"json": {"username": "John Doe"}} if request_type_name == "patch" else {}
    response = await request_type_method("/accounts/1", **kwargs)
    assert response.status_code == 404
    assert response.json()["detail"] == "Account not found"
