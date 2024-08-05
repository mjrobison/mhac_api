import pytest
from datetime import date
from my_module import (
    calc_age,
    break_height,
    combine_height,
    player_row_mapper,
    get_list,
    update,
    create_player,
    import_player,
    get_still_active_players,
)

@pytest.fixture
def mock_db(mocker):
    # Mock the database object
    return mocker.patch('my_module.db')

@pytest.fixture
def mock_date(mocker):
    # Mock the date class to ensure consistent results in calc_age function
    return mocker.patch('my_module.date')

def test_calc_age(mock_date):
    # Test the calc_age function
    birth_date = date(1990, 1, 1)
    mock_date.today.return_value = date(2023, 1, 1)  # Set current date for consistent testing
    result = calc_age(birth_date)
    assert result == 33  # Adjust the expected age based on the current year

def test_break_height():
    # Test the break_height function
    result = break_height(72)
    assert result == (6, 0)

def test_combine_height():
    # Test the combine_height function
    height_dict = {"feet": 6, "inches": 0}
    result = combine_height(height_dict)
    assert result == 72

def test_player_row_mapper():
    # Test the player_row_mapper function
    row = {
        "id": "player_id",
        "first_name": "John",
        "last_name": "Doe",
        "age": 25,
        "height": {"feet": 6, "inches": 0},
        "person_type": 1,
        "team_id": "team_id",
        "number": 10,
        "position": "Forward",
        "season_roster": "1,2,3",
    }
    result = player_row_mapper(row)
    expected_result = {
        "id": "player_id",
        "first_name": "John",
        "last_name": "Doe",
        "age": 25,
        "height": {"feet": 6, "inches": 0},
        "person_type": 1,
        "team": "team_id",
        "team_id": "team_id",
        "player_number": 10,
        "position": "Forward",
        "season_roster": ["season_1", "season_2", "season_3"],
    }
    assert result == expected_result

# Add similar tests for other functions

# Use fixtures to mock the database object in other tests
def test_get_list(mock_db):
    # Example test for get_list function
    # Mock the database response
    mock_db.return_value.__enter__.return_value.execute.return_value = [
        {"id": "player_id", "first_name": "John", "last_name": "Doe", "age": 25}
    ]
    result = get_list(1)
    assert len(result) == 1
    assert result[0]["id"] == "player_id"

# Add more tests for other functions
