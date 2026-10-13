def test_request_example(client):
    response = client.get("/", follow=True)
    assert b"eCOBIDAS" in response.content
    response = client.get("/en/faq/")
    assert b"FAQ" in response.content
    response = client.get("/fr/about/")
    assert b"about" in response.content
    response = client.get("/de/protocol/neurovault/mri_acquisition")
    assert response.status_code == 200
    assert b"neurovault" in response.content


def test_unknown_page(client):
    response = client.get("/en/protocol/foo")
    assert response.status_code == 404
    assert b"unknown protocol_name" in response.content


def test_method_not_allowed(client):
    response = client.post("/en/about/")
    assert response.status_code == 405


def test_activity_post(client):
    response = client.post("/en/protocol/neurovault/mri_acquisition", {"submit": ""})
    assert response.status_code == 200
    assert b"Your data was saved." in response.content


def test_download_report(client):
    response = client.get("/en/generate/download")

    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/markdown")
    assert 'filename="report.md"' in response["Content-Disposition"]
    # filled with the data of the generate page
    assert "Siemens" in response.content.decode()
