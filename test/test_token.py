import pytest


@pytest.mark.parametrize(
    'email, password, status, message',
    [
        (
            "kek@gmail.com",
            "23456789",
            200,
            None,
        ),
        (
            "rofl@gmail.com",
            "23456789",
            401,
            {'detail': 'Incorrect username or password'},
        ),
        (
            "ad@gmail.com",
            "23456789",
            401,
            {'detail': 'Incorrect username or password'},
        ),
    ]
)
async def test_token(
    async_client,
    email,
    password,
    status,
    message,
):
    if email != "rofl@gmail.com":
        await async_client.post(
            "/v1/user/registry", headers={"Content-Type": "application/json"}, json={
                "email": email,
                "first_name": "artyo",
                "last_name": "artyo",
                "password": password,
            },
        )

    response = await async_client.post(
        "/v1/user/login", data={"username": email, "password": password if email != "ad@gmail.com" else "2222222222", "grant_type": "password"},
                           headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == status
    if status != 200:
        assert response.json() == message
