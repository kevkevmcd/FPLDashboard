import pandas as pd
import util

def players_history():   
    # Extracting players information
    players = {player['id']: player for player in util.get_static_elements()}

    # Extracting team details
    team_entries = util.get_league_entries()

    # Initialize an empty list to store data for all gameweeks
    all_gameweeks_data = []

    # Loop through all 36 gameweeks
    for gw in range(1, 2):
        live_data = util.get_live_gameweek_response(gw).json()

        # If live data for the gameweek is not available, we continue with an empty dict
        player_points = {}
        if live_data:
            # Creating a mapping of player IDs to their points for the gameweek
            player_points = {int(k): v['stats']['total_points'] for k, v in live_data['elements'].items()}

        for team in team_entries:
            team_id = team['entry_id']
            team_name = team['entry_name']
            owner = team['player_first_name']

            # Fetch team-specific player details for the current gameweek
            team_details = util.get_team_details_response(gw, team_id).json()

            if team_details and 'picks' in team_details:
                for pick in team_details['picks']:
                    player_id = pick['element']
                    player_info = players.get(player_id, {})
                    player_points_scored = player_points.get(player_id, 'NaN')  # 'NaN' if the gameweek hasn't happened yet
                    all_gameweeks_data.append({
                        'Team Name': team_name,
                        'Player Name': f"{player_info.get('first_name', '')} {player_info.get('second_name', '')}".strip(),
                        'Gameweek': gw,
                        'Points': player_points_scored
                    })
            else:
                all_gameweeks_data.append({
                    'Team Name': team_name,
                    'Player Name': 'NaN',
                    'Gameweek': gw,
                    'Points': 'NaN'
                })

    # Creating the DataFrame
    df = pd.DataFrame(all_gameweeks_data)

    # Now, 'df' contains the player names, their respective teams, the gameweek, and the points they scored in that gameweek
    return df

def find_trades(df):
    # First sort the DataFrame by 'Team Name' and 'Gameweek' for sequential access
    df_sorted = df.sort_values(by=['Team Name', 'Gameweek'])

    # A dictionary to hold players for each team and gameweek
    team_gw_players = {team: {} for team in df_sorted['Team Name'].unique()}

    # Populate the dictionary with players' names from each team for every gameweek
    for (team, gameweek), group in df_sorted.groupby(['Team Name', 'Gameweek']):
        team_gw_players[team][gameweek] = set(group['Player Name'])

    trades_list = []
    trade_id_counter = 1
    trade_id_map = {}  # Map to keep track of existing trades to maintain the same Trade ID

    # Compare each team's roster with the previous gameweek to detect transfers
    for team, gw_players in team_gw_players.items():
        for gw in range(2, max(gw_players.keys()) + 1):
            current_gw_players = gw_players.get(gw, set())
            previous_gw_players = gw_players.get(gw - 1, set())

            # Players that are new to the team in the current gameweek
            new_players = current_gw_players - previous_gw_players
            # Players that have left the team since the last gameweek
            dropped_players = previous_gw_players - current_gw_players

            # Check if these new players came from any other teams
            for new_player in new_players:
                for other_team, other_gw_players in team_gw_players.items():
                    if other_team != team and new_player in other_gw_players.get(gw - 1, set()):
                        # Player came from another team, this is a trade
                        trade_key = frozenset({team, other_team, gw})

                        if trade_key not in trade_id_map:
                            trade_id_map[trade_key] = trade_id_counter
                            trade_id_counter += 1

                        trades_list.append({
                            'Trade ID': trade_id_map[trade_key],
                            'Player Name': new_player,
                            'From Team': other_team,
                            'To Team': team,
                            'Gameweek': gw
                        })

            # (Optional) Check for dropped players
            for dropped_player in dropped_players:
                for other_team, other_gw_players in team_gw_players.items():
                    if other_team != team and dropped_player in other_gw_players.get(gw, set()):
                        # Player went to another team, this is also a trade
                        trade_key = frozenset({team, other_team, gw})

                        if trade_key not in trade_id_map:
                            trade_id_map[trade_key] = trade_id_counter
                            trade_id_counter += 1

                        trades_list.append({
                            'Trade ID': trade_id_map[trade_key],
                            'Player Name': dropped_player,
                            'From Team': team,
                            'To Team': other_team,
                            'Gameweek': gw
                        })

    trades_df = pd.DataFrame(trades_list)
    return trades_df

def trade_tracker():
    # Use the function to find trades
    tradetracker_df = find_trades(players_history())
    #remove duplicates 
    tradetracker_df = tradetracker_df.drop_duplicates()

    return tradetracker_df

def sum_points_from_gameweek(player_name, start_gameweek):
    player_points = players_history()[(players_history()['Player Name'] == player_name) & (players_history()['Gameweek'] >= start_gameweek)]['Points']
    return player_points.sum()

def net_points_trades():
    # Initialize an empty list to hold the trade values.
    trade_values = []

    # Iterate over each unique trade ID.
    for trade_id in trade_tracker()['Trade ID'].unique():
        # Get all trades with the same Trade ID.
        trades = trade_tracker()[trade_tracker()['Trade ID'] == trade_id]
        
        # Get the gameweek of the trade.
        gameweek_of_trade = trades.iloc[0]['Gameweek']
        
        # Calculate points for each team involved in the trade.
        for owner in trades['From Team'].unique():
            # Sum the points of players received by the owner from the trade gameweek onwards.
            received_players = trades[trades['To Team'] == owner]['Player Name']
            received_points = sum(sum_points_from_gameweek(player, gameweek_of_trade) for player in received_players)
            
            # Sum the points of players given away by the owner from the trade gameweek onwards.
            given_players = trades[trades['From Team'] == owner]['Player Name']
            given_points = sum(sum_points_from_gameweek(player, gameweek_of_trade) for player in given_players)
            
            # Calculate net points and add to the list.
            net_points = received_points - given_points
            trade_values.append({
                'TradeID': trade_id,
                'Owner': owner,
                'Total points': net_points
            })

    # Convert to DataFrame.
    trade_values_df = pd.DataFrame(trade_values)

    return trade_values_df