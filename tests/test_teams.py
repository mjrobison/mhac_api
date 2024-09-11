import pytest

from apis.team import TeamBase


@pytest.fixture
def create_team_payload():
    return {
    "team_name": "New ",
    "team_mascot": "team",
    "main_color": "3a1e43",
    "secondary_color": "24d234",
    "website": "",
    "logo_color": "new.png",
    "logo_grey": "new.png",
    "slug": "new_team",
    "active": True
}

def test_marshal_team(create_team_payload):
    team = TeamBase(**create_team_payload)
    assert team.model_dump == create_team_payload
