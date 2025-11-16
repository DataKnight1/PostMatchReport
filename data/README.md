# Match Database Guide

This directory contains the match database used by the PostMatchReport application for easy match selection.

## File Structure

- `match_database.json` - Main database containing leagues and matches

## Adding New Matches

### Manual Method (Direct Edit)

Edit `match_database.json` and add a new match to the appropriate league:

```json
{
  "id": "unique-match-id",
  "home_team": "Team A",
  "away_team": "Team B",
  "date": "2024-05-20",
  "score": "2-1",
  "whoscored_id": 1234567,
  "fotmob_id": 7654321,
  "display": "Team A 2-1 Team B (2024-05-20)"
}
```

### Required Fields

- `id`: Unique identifier for the match (e.g., "pl-004", "ucl-003")
- `home_team`: Home team name
- `away_team`: Away team name
- `date`: Match date in YYYY-MM-DD format
- `score`: Final score (or "vs" for scheduled matches)
- `whoscored_id`: WhoScored match ID (integer)
- `fotmob_id`: FotMob match ID (integer)
- `display`: Display text shown in dropdown (auto-generated if not provided)

### How to Find Match IDs

#### WhoScored
1. Visit [whoscored.com](https://www.whoscored.com)
2. Navigate to the match you want to add
3. Look at the URL: `https://www.whoscored.com/Matches/1821302/Live/...`
4. The number after `/Matches/` is the WhoScored ID (e.g., `1821302`)

#### FotMob
1. Visit [fotmob.com](https://www.fotmob.com)
2. Navigate to the match you want to add
3. Look at the URL: `https://www.fotmob.com/matches/3900958/...`
4. The number after `/matches/` is the FotMob ID (e.g., `3900958`)

### Programmatic Method (Python)

You can also use the `MatchDatabaseManager` class to add matches:

```python
from utils.match_database_manager import MatchDatabaseManager

# Initialize manager
db = MatchDatabaseManager()

# Add a new match
match_data = {
    'id': 'pl-004',
    'home_team': 'Newcastle',
    'away_team': 'Brighton',
    'date': '2024-05-25',
    'score': '3-2',
    'whoscored_id': 1821320,
    'fotmob_id': 3900975
}

# Add to Premier League
success = db.add_match('Premier League', match_data)
if success:
    print("Match added successfully!")
```

## Adding New Leagues

To add a new league, edit `match_database.json` and add a new league object to the `leagues` array:

```json
{
  "id": "unique-league-id",
  "name": "League Name",
  "country": "Country",
  "matches": []
}
```

### Example Leagues

- `premier-league` - Premier League (England)
- `la-liga` - La Liga (Spain)
- `serie-a` - Serie A (Italy)
- `bundesliga` - Bundesliga (Germany)
- `ligue-1` - Ligue 1 (France)
- `uefa-champions-league` - UEFA Champions League (Europe)
- `eredivisie` - Eredivisie (Netherlands)

## Database Statistics

You can view database statistics using:

```python
from utils.match_database_manager import MatchDatabaseManager

db = MatchDatabaseManager()
stats = db.get_database_stats()
print(f"Total leagues: {stats['total_leagues']}")
print(f"Total matches: {stats['total_matches']}")
```

## Best Practices

1. **Unique IDs**: Ensure each match has a unique ID within its league
2. **Consistent Formatting**: Use consistent date format (YYYY-MM-DD)
3. **Team Names**: Use official team names for consistency
4. **Testing**: After adding matches, test the dropdown in the app to ensure they appear correctly
5. **Backup**: Keep a backup of `match_database.json` before making major changes

## Troubleshooting

### Match doesn't appear in dropdown
- Check JSON syntax is valid
- Verify the match is in the correct league
- Ensure all required fields are present
- Restart the Streamlit app if needed

### IDs not working
- Verify WhoScored and FotMob IDs are correct
- Try the match URLs directly in your browser
- Check that IDs are integers, not strings

### Database errors
- Validate JSON syntax using a JSON validator
- Check file permissions
- Ensure file path is correct

## Contributing

When adding matches for popular leagues, consider contributing them back to the repository so others can benefit!
