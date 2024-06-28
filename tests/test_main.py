from app import crud, schemas


def assert_experiment_json_equal_to_payload(experiment_json, experiment_payload):
    assert experiment_json["description"] == experiment_payload["description"]
    assert experiment_json["sample_ratio"] == experiment_payload["sample_ratio"]
    assert experiment_json["teams"] == experiment_payload["teams"]


def test_create_and_read_experiments(db_session, test_client, experiment_payload):
    post_response = test_client.post("/experiments/", json=experiment_payload)
    assert post_response.status_code == 201
    assert_experiment_json_equal_to_payload(post_response.json(), experiment_payload)

    get_response = test_client.get("/experiments/")
    assert get_response.status_code == 200
    assert_experiment_json_equal_to_payload(get_response.json()[0], experiment_payload)


def test_read_experiments_by_team(db_session, test_client, team_payload):
    team = crud.create_team(db_session, team=schemas.TeamCreate(**team_payload))
    response = test_client.get(f"/experiments/?team={team.name}")
    assert response.status_code == 200


def test_read_experiments_by_team_and_descendants(db_session, test_client, team_payload, team_payload_child):
    team = crud.create_team(db_session, team=schemas.TeamCreate(**team_payload))
    child_team = crud.create_team(db_session, team=schemas.TeamCreate(**team_payload_child))
    response = test_client.get(f"/experiments/?team={team.name}&descendants=true")
    assert response.status_code == 200


def test_read_experiment(db_session, test_client, experiment_payload):
    experiment = crud.create_experiment(db_session, experiment=schemas.ExperimentCreate(**experiment_payload))
    response = test_client.get(f"/experiments/{experiment.id}")
    print("response: ", response.json(), response.headers)
    assert response.status_code == 200


def test_read_experiment_not_found(test_client):
    response = test_client.get("/experiments/9999")
    assert response.status_code == 404


def test_update_experiment(db_session, test_client, experiment_payload, experiment_payload_updated):
    experiment = crud.create_experiment(db_session, experiment=schemas.ExperimentCreate(**experiment_payload))
    response = test_client.put(f"/experiments/{experiment.id}/", json=experiment_payload_updated)
    assert response.status_code == 200


def test_delete_experiment(db_session, test_client, experiment_payload):
    experiment = crud.create_experiment(db_session, experiment=schemas.ExperimentCreate(**experiment_payload))
    response = test_client.delete(f"/experiments/{experiment.id}/")
    assert response.status_code == 204


def test_create_and_read_teams(test_client, team_payload):
    post_response = test_client.post("/teams/", json=team_payload)
    assert post_response.status_code == 201
    assert post_response.json()["name"] == team_payload["name"]

    get_response = test_client.get("/teams/")
    assert get_response.status_code == 200
    assert get_response.json()[0]["name"] == team_payload["name"]


def test_read_team(db_session, test_client, team_payload):
    team = crud.create_team(db_session, team=schemas.TeamCreate(**team_payload))
    response = test_client.get(f"/teams/{team.name}")
    assert response.status_code == 200


def test_read_team_not_found(test_client):
    response = test_client.get("/teams/nonexistent_team")
    assert response.status_code == 404


def test_update_team(db_session, test_client, team_payload, team_payload_updated):
    team = crud.create_team(db_session, team=schemas.TeamCreate(**team_payload))
    response = test_client.put(f"/teams/{team.name}/", json=team_payload_updated)
    assert response.status_code == 200


def test_delete_team(db_session, test_client, team_payload):
    team = crud.create_team(db_session, team=schemas.TeamCreate(**team_payload))
    response = test_client.delete(f"/teams/{team.name}/")
    assert response.status_code == 204
