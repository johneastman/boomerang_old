import pytest
from flask_app import app as main_app
from flask import session


@pytest.fixture()
def app():
    main_app.secret_key = "test_secret_key"
    main_app.config.update({
        "TESTING": True,
    })

    # other setup can go here

    yield main_app

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def test_request_index(client):
    response = client.get("/")
    assert response.status_code == 200


def test_request_clear(client):
    with client.session_transaction() as s:
        s["source_code"] = "x = 1; print <- (x,);"
        s["results"] = "[1]"

    with client:
        response = client.post("/clear", follow_redirects=True)
        assert "source_code" not in session
        assert "results" not in session

    assert response.status_code == 200

    # Check that there was one redirect response.
    assert len(response.history) == 1

    # Check that the second request was to the index page.
    assert response.request.path == "/"


def test_request_interpret(client):
    with client:
        response = client.post("/interpret", follow_redirects=True, data={
            "source": "x = 1;"
        })

        assert session.get("source_code") == "x = 1;"
        assert session.get("results") == "[]"

    assert response.status_code == 200

    # Check that there was one redirect response.
    assert len(response.history) == 1

    # Check that the second request was to the index page.
    assert response.request.path == "/"

