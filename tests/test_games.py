import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from uuid import uuid4
from pydantic import BaseModel

# Import your router and any necessary components
from your_module import router  # Replace with your actual module name

# Create FastAPI instance and include the router
app = FastAPI()
app.include_router(router)

# Create a TestClient instance
client = TestClient(app)

# Mocking the DAO functions
def mock_create(game):
    return {"game_id": game.game_id}

def mock_add_period_score(game_result):
    return {"status": "success"}

def mock_get_game_results(game_id, team_id=None):
    return [{"game_id": game_id, "home_team": "Home", "away_team": "Away", "scores": {"home": 100, "away": 90}}]

# Override actual DAO methods with mocks
router.dependency_overrides[games.create] = mock_create
router.dependency_overrides[games.add_period_score] = mock_add_period_score
router.dependency_overrides[games.get_game_results] = mock_get_game_results

# Test Data
valid_game_id = uuid4()

class GameIn(BaseModel):
    home_team: UUID
    away_team: UUID
    game_id: UUID

class GameResult(BaseModel):
    period: str
    home_score: int
    away_score: int
    game_order: int

def test_add_game_success():
    game_data = {
        "home_team": uuid4(),
        "away_team": uuid4(),
        "game_id": valid_game_id,
        "date": "2024-01-01",
        "time": "10:00"
    }
    response = client.post("/addGame", json=game_data)
    assert response.status_code == 200
    assert response.json() == {"game_id": str(valid_game_id)}

def test_enter_new_period_score_success():
    game_result = {
        "period": "1st",
        "home_score": 25,
        "away_score": 20,
        "game_order": 1
    }
    response = client.post("/addPeriodScore", json=game_result)
    assert response.status_code == 200
    assert response.json() == {"status": "success"}

def test_get_game_results_success():
    response = client.get(f"/getGameResults/{valid_game_id}")
    assert response.status_code == 200
    assert len(response.json()) > 0  # Check if there are any results

def test_add_final_score_success():
    game_data = {
        "home_team": uuid4(),
        "away_team": uuid4(),
        "game_id": valid_game_id,
    }
    response = client.post("/addFinalScore", json=game_data)
    assert response.status_code == 201

def test_delete_game_success():
    game_data = {"game_id": valid_game_id}
    response = client.post("/deleteGame", json=game_data)
    assert response.status_code == 204  # No content

# Add more tests for other endpoints as needed
