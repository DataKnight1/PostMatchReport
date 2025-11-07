"""
Database Loader
Handles loading transformed data into relational databases (SQLite, PostgreSQL, etc.)
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import logging

try:
    from sqlalchemy import create_engine, Table, Column, Integer, String, Float, Boolean, DateTime, Text, MetaData, ForeignKey
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.dialects.postgresql import JSONB
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    logging.warning("SQLAlchemy not available. Install with: pip install sqlalchemy")


class DatabaseLoader:
    """Load processed match data into relational databases."""

    def __init__(self, database_url: str = "sqlite:///whoscored_matches.db"):
        """
        Initialize database loader.

        Args:
            database_url: SQLAlchemy database URL
                - SQLite: "sqlite:///matches.db"
                - PostgreSQL: "postgresql://user:password@localhost/dbname"
        """
        if not SQLALCHEMY_AVAILABLE:
            raise ImportError("SQLAlchemy is required. Install with: pip install sqlalchemy psycopg2-binary")

        self.database_url = database_url
        self.engine = create_engine(database_url, echo=False)
        self.metadata = MetaData()

        # Define tables
        self._define_tables()

        # Create all tables
        self.metadata.create_all(self.engine)

        # Create session
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def _define_tables(self):
        """Define database schema."""

        # Matches table
        self.matches_table = Table(
            'matches', self.metadata,
            Column('match_id', Integer, primary_key=True),
            Column('whoscored_id', Integer, unique=True, nullable=False),
            Column('competition', String(200)),
            Column('season', String(50)),
            Column('week', Integer),
            Column('date', DateTime),
            Column('venue', String(200)),
            Column('attendance', Integer),
            Column('referee', String(200)),
            Column('home_team_id', Integer),
            Column('away_team_id', Integer),
            Column('home_team_name', String(200)),
            Column('away_team_name', String(200)),
            Column('home_score', Integer),
            Column('away_score', Integer),
            Column('home_score_ht', Integer),
            Column('away_score_ht', Integer),
            Column('home_formation', String(20)),
            Column('away_formation', String(20)),
            Column('extracted_at', DateTime, default=datetime.utcnow),
        )

        # Teams table
        self.teams_table = Table(
            'teams', self.metadata,
            Column('team_id', Integer, primary_key=True),
            Column('name', String(200), nullable=False),
            Column('country', String(100)),
        )

        # Players table
        self.players_table = Table(
            'players', self.metadata,
            Column('player_id', Integer, primary_key=True),
            Column('name', String(200), nullable=False),
            Column('shirt_no', Integer),
            Column('position', String(50)),
            Column('age', Integer),
            Column('height', Float),
            Column('weight', Float),
        )

        # Match Players (players in specific match)
        self.match_players_table = Table(
            'match_players', self.metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('match_id', Integer, nullable=False),
            Column('player_id', Integer, nullable=False),
            Column('team_id', Integer, nullable=False),
            Column('is_first_eleven', Boolean, default=False),
            Column('is_captain', Boolean, default=False),
            Column('is_man_of_match', Boolean, default=False),
            Column('subon_minute', Integer),
            Column('suboff_minute', Integer),
            Column('rating', Float),
        )

        # Events table
        self.events_table = Table(
            'events', self.metadata,
            Column('event_id', Integer, primary_key=True, autoincrement=True),
            Column('match_id', Integer, nullable=False),
            Column('team_id', Integer, nullable=False),
            Column('player_id', Integer),
            Column('period', Integer),
            Column('minute', Integer),
            Column('second', Float),
            Column('cumulative_mins', Float),
            Column('type', String(50)),
            Column('type_value', Integer),
            Column('outcome', String(50)),
            Column('is_successful', Boolean),
            Column('x', Float),
            Column('y', Float),
            Column('end_x', Float),
            Column('end_y', Float),
            Column('distance', Float),
            Column('angle', Float),
            Column('is_progressive', Boolean),
            Column('is_key_pass', Boolean),
            Column('is_assist', Boolean),
            Column('is_goal', Boolean),
            Column('is_own_goal', Boolean),
            Column('xg', Float),
            Column('qualifiers', Text),  # JSON string
        )

        # Match Statistics table
        self.match_stats_table = Table(
            'match_stats', self.metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('match_id', Integer, nullable=False),
            Column('team_id', Integer, nullable=False),
            Column('stat_type', String(50), nullable=False),  # 'passing', 'shooting', etc.
            Column('stat_name', String(100), nullable=False),
            Column('stat_value', Float),
        )

    def load_match_data(self, match_id: int, match_info: Dict[str, Any],
                       home_team: Dict[str, Any], away_team: Dict[str, Any]) -> int:
        """
        Load match basic information.

        Args:
            match_id: WhoScored match ID
            match_info: Match information dictionary
            home_team: Home team data
            away_team: Away team data

        Returns:
            Internal match ID
        """
        # Parse score
        score_str = match_info.get('score', '0 : 0')
        try:
            home_score, away_score = map(int, score_str.split(':'))
        except:
            home_score, away_score = 0, 0

        ht_score = match_info.get('ht_score', '0 : 0')
        try:
            home_score_ht, away_score_ht = map(int, ht_score.split(':'))
        except:
            home_score_ht, away_score_ht = 0, 0

        # Parse date
        date_str = match_info.get('date')
        match_date = None
        if date_str:
            try:
                match_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except:
                pass

        # Insert or update match
        insert_stmt = self.matches_table.insert().values(
            whoscored_id=match_id,
            competition=match_info.get('competition', {}).get('name'),
            season=match_info.get('season'),
            week=match_info.get('week'),
            date=match_date,
            venue=match_info.get('venue'),
            attendance=match_info.get('attendance'),
            referee=match_info.get('referee'),
            home_team_id=home_team.get('team_id'),
            away_team_id=away_team.get('team_id'),
            home_team_name=home_team.get('name'),
            away_team_name=away_team.get('name'),
            home_score=home_score,
            away_score=away_score,
            home_score_ht=home_score_ht,
            away_score_ht=away_score_ht,
            home_formation=self._format_formation(home_team.get('formation')),
            away_formation=self._format_formation(away_team.get('formation')),
            extracted_at=datetime.utcnow()
        )

        try:
            self.engine.execute(insert_stmt)
        except Exception as e:
            # Update if exists
            logging.info(f"Match {match_id} already exists, updating...")
            update_stmt = self.matches_table.update().where(
                self.matches_table.c.whoscored_id == match_id
            ).values(
                competition=match_info.get('competition', {}).get('name'),
                season=match_info.get('season'),
                week=match_info.get('week'),
                date=match_date,
                venue=match_info.get('venue'),
                attendance=match_info.get('attendance'),
                referee=match_info.get('referee'),
                home_score=home_score,
                away_score=away_score,
                home_score_ht=home_score_ht,
                away_score_ht=away_score_ht,
                extracted_at=datetime.utcnow()
            )
            self.engine.execute(update_stmt)

        return match_id

    def _format_formation(self, formation_data) -> Optional[str]:
        """Extract formation string from formation data."""
        if not formation_data:
            return None

        if isinstance(formation_data, list) and len(formation_data) > 0:
            return formation_data[0].get('formationName')
        elif isinstance(formation_data, dict):
            return formation_data.get('formationName')
        elif isinstance(formation_data, str):
            return formation_data

        return None

    def load_teams(self, home_team: Dict[str, Any], away_team: Dict[str, Any]):
        """Load team information."""
        for team in [home_team, away_team]:
            if not team.get('team_id'):
                continue

            insert_stmt = self.teams_table.insert().values(
                team_id=team.get('team_id'),
                name=team.get('name'),
                country=team.get('country_name'),
            )

            try:
                self.engine.execute(insert_stmt)
            except:
                pass  # Team already exists

    def load_players(self, players_data: Dict[str, Any]):
        """Load player information."""
        all_players = players_data.get('all_players', [])

        for player in all_players:
            if not player.get('player_id'):
                continue

            insert_stmt = self.players_table.insert().values(
                player_id=player.get('player_id'),
                name=player.get('name'),
                shirt_no=player.get('shirt_no'),
                position=player.get('position'),
                age=player.get('age'),
                height=player.get('height'),
                weight=player.get('weight'),
            )

            try:
                self.engine.execute(insert_stmt)
            except:
                pass  # Player already exists

    def load_match_players(self, match_id: int, players_data: Dict[str, Any]):
        """Load player participation in specific match."""
        all_players = players_data.get('all_players', [])

        # Delete existing match players
        delete_stmt = self.match_players_table.delete().where(
            self.match_players_table.c.match_id == match_id
        )
        self.engine.execute(delete_stmt)

        # Insert new data
        for player in all_players:
            if not player.get('player_id'):
                continue

            insert_stmt = self.match_players_table.insert().values(
                match_id=match_id,
                player_id=player.get('player_id'),
                team_id=player.get('team_id'),
                is_first_eleven=player.get('is_first_eleven', False),
                is_captain=player.get('is_captain', False),
                is_man_of_match=player.get('substitute_info', {}).get('is_man_of_match', False),
                subon_minute=player.get('substitute_info', {}).get('subon_minute'),
                suboff_minute=player.get('substitute_info', {}).get('suboff_minute'),
                rating=player.get('ratings', {}).get('overall'),
            )

            self.engine.execute(insert_stmt)

    def load_events(self, match_id: int, events_df: pd.DataFrame):
        """
        Load match events.

        Args:
            match_id: Match ID
            events_df: Events DataFrame from EventProcessor
        """
        if events_df is None or events_df.empty:
            return

        # Delete existing events
        delete_stmt = self.events_table.delete().where(
            self.events_table.c.match_id == match_id
        )
        self.engine.execute(delete_stmt)

        # Prepare data
        events_to_insert = []
        for _, row in events_df.iterrows():
            # Convert qualifiers to JSON string
            qualifiers_str = None
            if 'qualifiers_dict' in row and row['qualifiers_dict']:
                try:
                    qualifiers_str = json.dumps(row['qualifiers_dict'])
                except:
                    pass

            event_data = {
                'match_id': match_id,
                'team_id': row.get('teamId'),
                'player_id': row.get('playerId'),
                'period': row.get('period_value'),
                'minute': row.get('minute'),
                'second': row.get('second'),
                'cumulative_mins': row.get('cumulative_mins'),
                'type': row.get('type_display'),
                'type_value': row.get('type_value'),
                'outcome': row.get('outcome_display'),
                'is_successful': bool(row.get('is_successful')),
                'x': row.get('x'),
                'y': row.get('y'),
                'end_x': row.get('endX'),
                'end_y': row.get('endY'),
                'distance': row.get('distance'),
                'angle': row.get('angle'),
                'is_progressive': bool(row.get('is_progressive')),
                'is_key_pass': bool(row.get('is_key_pass')),
                'is_assist': bool(row.get('is_assist')),
                'is_goal': bool(row.get('is_goal')),
                'is_own_goal': bool(row.get('is_own_goal')),
                'xg': row.get('xg'),
                'qualifiers': qualifiers_str,
            }

            # Replace NaN with None
            event_data = {k: (None if pd.isna(v) else v) for k, v in event_data.items()}

            events_to_insert.append(event_data)

        # Bulk insert
        if events_to_insert:
            self.engine.execute(self.events_table.insert(), events_to_insert)

    def load_match_statistics(self, match_id: int, team_stats: Dict[str, Any]):
        """
        Load aggregated match statistics.

        Args:
            match_id: Match ID
            team_stats: Team statistics from TeamProcessor
        """
        # Delete existing stats
        delete_stmt = self.match_stats_table.delete().where(
            self.match_stats_table.c.match_id == match_id
        )
        self.engine.execute(delete_stmt)

        stats_to_insert = []

        # Process home and away stats
        for side in ['home', 'away']:
            if side not in team_stats:
                continue

            team_id = team_stats[side].get('info', {}).get('id')
            if not team_id:
                continue

            # Passing stats
            for stat_name, stat_value in team_stats[side].get('passing', {}).items():
                stats_to_insert.append({
                    'match_id': match_id,
                    'team_id': team_id,
                    'stat_type': 'passing',
                    'stat_name': stat_name,
                    'stat_value': float(stat_value) if stat_value is not None else None
                })

            # Shooting stats
            for stat_name, stat_value in team_stats[side].get('shooting', {}).items():
                stats_to_insert.append({
                    'match_id': match_id,
                    'team_id': team_id,
                    'stat_type': 'shooting',
                    'stat_name': stat_name,
                    'stat_value': float(stat_value) if stat_value is not None else None
                })

            # Defensive stats
            for stat_name, stat_value in team_stats[side].get('defensive', {}).items():
                stats_to_insert.append({
                    'match_id': match_id,
                    'team_id': team_id,
                    'stat_type': 'defensive',
                    'stat_name': stat_name,
                    'stat_value': float(stat_value) if stat_value is not None else None
                })

            # Territorial stats
            for stat_name, stat_value in team_stats[side].get('territorial', {}).items():
                stats_to_insert.append({
                    'match_id': match_id,
                    'team_id': team_id,
                    'stat_type': 'territorial',
                    'stat_name': stat_name,
                    'stat_value': float(stat_value) if stat_value is not None else None
                })

        # Possession stats
        possession = team_stats.get('possession', {})
        if possession:
            # Get team IDs
            home_id = team_stats.get('home', {}).get('info', {}).get('id')
            away_id = team_stats.get('away', {}).get('info', {}).get('id')

            if home_id:
                stats_to_insert.append({
                    'match_id': match_id,
                    'team_id': home_id,
                    'stat_type': 'possession',
                    'stat_name': 'possession_pct',
                    'stat_value': float(possession.get('home', 50))
                })

            if away_id:
                stats_to_insert.append({
                    'match_id': match_id,
                    'team_id': away_id,
                    'stat_type': 'possession',
                    'stat_name': 'possession_pct',
                    'stat_value': float(possession.get('away', 50))
                })

        # Bulk insert
        if stats_to_insert:
            self.engine.execute(self.match_stats_table.insert(), stats_to_insert)

    def load_complete_match(self, whoscored_data: Dict[str, Any],
                          match_processor) -> bool:
        """
        Load complete match data (convenience method).

        Args:
            whoscored_data: Raw WhoScored data
            match_processor: MatchProcessor instance with transformed data

        Returns:
            Success status
        """
        try:
            match_centre = whoscored_data.get('match_centre', {})

            if not match_centre.get('success'):
                logging.error("Match data extraction failed")
                return False

            match_id = whoscored_data.get('match_id')
            match_info = match_centre.get('match_info', {})
            home_team = match_centre.get('home_team', {})
            away_team = match_centre.get('away_team', {})
            players = match_centre.get('players', {})

            # Load in order
            logging.info(f"Loading match {match_id} to database...")

            self.load_match_data(match_id, match_info, home_team, away_team)
            self.load_teams(home_team, away_team)
            self.load_players(players)
            self.load_match_players(match_id, players)

            # Load events
            events_df = match_processor.get_events_dataframe()
            self.load_events(match_id, events_df)

            # Load statistics
            team_stats = match_processor.team_processor.get_comprehensive_team_stats() if match_processor.team_processor else {}
            self.load_match_statistics(match_id, team_stats)

            logging.info(f"Successfully loaded match {match_id} to database")
            return True

        except Exception as e:
            logging.error(f"Error loading match to database: {e}")
            import traceback
            traceback.print_exc()
            return False

    def query_match_stats(self, match_id: int) -> pd.DataFrame:
        """Query match statistics."""
        query = f"""
        SELECT m.*, t1.name as home_name, t2.name as away_name
        FROM matches m
        LEFT JOIN teams t1 ON m.home_team_id = t1.team_id
        LEFT JOIN teams t2 ON m.away_team_id = t2.team_id
        WHERE m.whoscored_id = {match_id}
        """
        return pd.read_sql(query, self.engine)

    def query_events(self, match_id: int) -> pd.DataFrame:
        """Query match events."""
        query = f"""
        SELECT e.*, p.name as player_name, t.name as team_name
        FROM events e
        LEFT JOIN players p ON e.player_id = p.player_id
        LEFT JOIN teams t ON e.team_id = t.team_id
        WHERE e.match_id = {match_id}
        ORDER BY e.cumulative_mins
        """
        return pd.read_sql(query, self.engine)

    def close(self):
        """Close database connection."""
        if hasattr(self, 'session'):
            self.session.close()
        if hasattr(self, 'engine'):
            self.engine.dispose()
