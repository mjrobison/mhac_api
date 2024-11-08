import pytest
from unittest.mock import MagicMock
from uuid import uuid4
from sqlalchemy.exc import IntegrityError

# Assuming the models and imports are already defined above.

@pytest.fixture
def mock_db_session(mocker):
    mock_session = MagicMock()
    mocker.patch('your_module.db', return_value=mock_session)
    return mock_session

def test_final_score_mapper():
    row = {"final_home_score": 100, "final_away_score": 90}
    expected = {"home_score": 100, "away_score": 90}
    assert final_score_mapper(row) == expected

def test_get_game_success(mock_db_session):
    game_id = uuid4()
    mock_db_session.execute.return_value.mappings.return_value.one.return_value = {
        "game_id": game_id,
        "home_team_id": uuid4(),
        "away_team_id": uuid4(),
        # Add other fields as necessary
    }
    
    result = get(game_id)
    
    assert result["game_id"] == game_id

def test_get_game_not_found(mock_db_session):
    game_id = uuid4()
    mock_db_session.execute.return_value.mappings.return_value.one.side_effect = Exception("No row found")
    
    with pytest.raises(Exception):
        get(game_id)

def test_create_game_success(mock_db_session):
    game = Schedule(home_team=uuid4(), away_team=uuid4(), date='2024-10-28', time='18:00', season=uuid4(), neutral_site=False)
    
    result = create(game)
    
    assert result[200] == "success"
    mock_db_session.execute.assert_called()  # Ensure execute was called

def test_create_game_integrity_error(mock_db_session):
    game = Schedule(home_team=uuid4(), away_team=uuid4(), date='2024-10-28', time='18:00', season=uuid4(), neutral_site=False)
    
    mock_db_session.execute.side_effect = IntegrityError('Integrity Error', None, None)
    
    with pytest.raises(IntegrityError):
        create(game)

def test_update_game_success(mock_db_session):
    game = Schedule(game_id=uuid4(), home_team=uuid4(), away_team=uuid4(), date='2024-10-28', time='18:00', season=uuid4())
    
    update(game)
    
    mock_db_session.execute.assert_called()  # Ensure execute was called

def test_add_period_score_success(mock_db_session):
    game = [GameResult(period="1", home_score=10, away_score=5)]
    game_id = uuid4()
    
    result = add_period_score(game, game_id)
    
    assert result[200] == "Success"
    mock_db_session.execute.assert_called()

def test_add_final_score_success(mock_db_session):
    game = GameStats(game_id=uuid4(), final_scores={"home_score": 100, "away_score": 90})
    
    add_final_score(game)
    
    mock_db_session.execute.assert_called()  # Ensure execute was called

def test_get_game_results_success(mock_db_session):
    game_id = uuid4()
    team_id = uuid4()
    
    mock_db_session.execute.return_value = [
        {"quarter": "1", "home_score": 10, "away_score": 5, "game_order": 1},
        # Add more mock data as necessary
    ]
    
    result = get_game_results(game_id, team_id)
    
    assert len(result["game_scores"]) > 0  # Ensure there are game scores returned

def test_get_team_schedule_success(mock_db_session):
    season_team_id = uuid4()
    mock_db_session.execute.return_value.mappings.return_value.all.return_value = [
        {"schedule_id": 1, "game_date": "2024-10-28", "game_time": "18:00", "game_id": uuid4(), "home_team": uuid4(), "away_team": uuid4(), "final_scores": {"home_score": 100, "away_score": 90}, "missing_stats": False, "season": "2024", "level_name": "Pro"}
    ]
    
    result = get_team_schedule(season_team_id=season_team_id)
    
    assert len(result) > 0  # Ensure there are scheduled games returned
