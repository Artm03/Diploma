import pytest


@pytest.mark.parametrize(
    'request_body, response_code, response_body',
    [
        (
            {
                "email": "gavrilovartyo@gmail.com",
                "first_name": "artyo",
                "last_name": "artyo",
                "password": "123456789",
            },
            201,
            None
        ),
        (
            {
                "email": "gavrilovartyo@gmail.com",
                "first_name": "artyo",
                "last_name": "artyo",
                "password": "123456789",
            },
            409,
            {
                "message": "User with email gavrilovartyo@gmail.com already exists",
            },
        ),
    ],
)
async def test_registry(
    async_client,
    request_body,
    response_code,
    response_body,
):
    response = await async_client.post(
        "/v1/user/registry", headers={"Content-Type": "application/json"}, json=request_body,
    )
    if response_code == 409:
        response = await async_client.post(
            "/v1/user/registry", headers={"Content-Type": "application/json"}, json=request_body,
        )
        assert response.json() == response_body
    assert response.status_code == response_code
