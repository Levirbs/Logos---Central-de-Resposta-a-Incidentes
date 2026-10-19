import threading

from app.models import Status


def patch_status(client, incident_id: int, status: str, version: int):
    return client.patch(f"/api/v1/incidents/{incident_id}", json={"status": status, "version": version})


def test_first_patch_wins_and_second_gets_409_with_current_data(client, insert_incident):
    incident_id = insert_incident()

    first = patch_status(client, incident_id, "Em Investigação", version=1)
    second = patch_status(client, incident_id, "Fechado", version=1)

    assert first.status_code == 200
    assert first.json()["status"] == "Em Investigação"
    assert first.json()["version"] == 2

    assert second.status_code == 409
    body = second.json()
    assert body["code"] == "VERSION_CONFLICT"
    assert body["message"] == "O incidente foi atualizado por outro analista."
    assert body["current"]["status"] == "Em Investigação"
    assert body["current"]["version"] == 2
    # O segundo PATCH não pode ter alterado nada.
    assert client.get(f"/api/v1/incidents/{incident_id}").json() == body["current"]


def test_concurrent_patches_with_same_version_only_one_succeeds(make_client, insert_incident):
    incident_id = insert_incident()
    barrier = threading.Barrier(2)
    results: dict[str, int] = {}

    def worker(status: str) -> None:
        client = make_client()
        barrier.wait()
        results[status] = patch_status(client, incident_id, status, version=1).status_code

    threads = [threading.Thread(target=worker, args=(status,)) for status in ("Em Investigação", "Fechado")]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert sorted(results.values()) == [200, 409]
    final = make_client().get(f"/api/v1/incidents/{incident_id}").json()
    assert final["version"] == 2
    assert final["status"] == next(status for status, code in results.items() if code == 200)


def test_patch_with_current_version_can_continue_the_flow(client, insert_incident):
    incident_id = insert_incident()

    first = patch_status(client, incident_id, "Em Investigação", version=1).json()
    second = patch_status(client, incident_id, "Inconclusivo", version=first["version"])

    assert second.status_code == 200
    assert second.json()["version"] == 3


def test_status_transitions_are_free_including_reopening(client, insert_incident):
    incident_id = insert_incident(status=Status.CLOSED)

    response = patch_status(client, incident_id, "Aberto", version=1)

    assert response.status_code == 200
    assert response.json()["status"] == "Aberto"


def test_same_status_with_current_version_is_a_noop_without_bumping_version(client, insert_incident):
    incident_id = insert_incident(status=Status.OPEN)
    before = client.get(f"/api/v1/incidents/{incident_id}").json()

    response = patch_status(client, incident_id, "Aberto", version=1)

    assert response.status_code == 200
    assert response.json() == before


def test_same_status_with_stale_version_still_conflicts(client, insert_incident):
    incident_id = insert_incident(status=Status.OPEN)
    patch_status(client, incident_id, "Em Investigação", version=1)
    patch_status(client, incident_id, "Aberto", version=2)

    response = patch_status(client, incident_id, "Aberto", version=1)

    assert response.status_code == 409
    assert response.json()["current"]["version"] == 3


def test_patch_unknown_incident_returns_404(client):
    assert patch_status(client, 999, "Fechado", version=1).status_code == 404


def test_patch_rejects_invalid_body(client, insert_incident):
    incident_id = insert_incident()
    url = f"/api/v1/incidents/{incident_id}"

    assert client.patch(url, json={"status": "Resolvido", "version": 1}).status_code == 422
    assert client.patch(url, json={"status": "Fechado"}).status_code == 422
    assert client.patch(url, json={"status": "Fechado", "version": 0}).status_code == 422
    assert client.patch(url, json={"status": "Fechado", "version": 1, "title": "x"}).status_code == 422
