def test_request_example(client):
    response = client.get("/")
    assert b"eCOBIDAS" in response.data
    response = client.get("/en/faq/")
    assert b"FAQ" in response.data
    response = client.get("/fr/about/")
    assert b"about" in response.data
    response = client.get("/de/protocols/neurovault/mri_acquisition")
    assert b"neurovault" in response.data
