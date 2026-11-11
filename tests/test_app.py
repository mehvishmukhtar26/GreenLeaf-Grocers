
def test_home_redirects_to_login(client):
    response = client.get("/")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_login_page_loads(client):
    response = client.get("/login")

    assert response.status_code == 200


def test_dashboard_requires_login(client):
    response = client.get("/dashboard/home")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
