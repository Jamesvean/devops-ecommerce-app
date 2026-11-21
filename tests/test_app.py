import pytest
from app import create_app

@pytest.fixture
def client(tmp_path):
    app = create_app({"TESTING": True, "SECRET_KEY": "test-key", "DATABASE": str(tmp_path / "test.db")})
    return app.test_client()

def test_home_lists_products(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Wireless Headphones" in response.data

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "ok", "database": "ok"}

def test_add_to_cart_and_checkout(client):
    response = client.post("/cart/add/1")
    assert response.status_code == 302
    assert b"Wireless Headphones" in client.get("/cart").data
    response = client.post("/checkout")
    assert response.status_code == 200
    assert b"49.99" in response.data
    assert b"Demo order placed" in response.data
    assert b"Your cart is empty" in client.get("/cart").data

def test_unknown_product(client):
    assert client.post("/cart/add/999").status_code == 404

def test_empty_checkout(client):
    assert client.post("/checkout").status_code == 302
