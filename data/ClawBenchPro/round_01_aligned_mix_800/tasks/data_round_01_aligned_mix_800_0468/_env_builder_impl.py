import os
import json
import csv
import random
from datetime import datetime, timedelta

def build_env():
    # 赛会基准时间为 2024-05-18
    # Valid birthdates for 14-18 years old exactly on 2024-05-18:
    # 18 years old: Born on or after 2005-05-19, and on or before 2006-05-18
    # 14 years old: Born on or after 2009-05-19, and on or before 2010-05-18
    # Age range (14-18): Born between 2005-05-19 and 2010-05-18 (inclusive)

    random.seed(42)

    os.makedirs("rules", exist_ok=True)
    with open("rules/season_7_announcement.txt", "w") as f:
        f.write("=== TRI-CUP SEASON 7 ===\n\n")
        f.write("Welcome to the most sweaty tournament of the year.\n")
        f.write("Mark your calendars: The official tournament start date is 2024-05-18.\n")
        f.write("All ages will be verified against this exact date. No exceptions.\n")

    base_dir = "server_backups"
    
    # 诱饵目录
    for year in ["2022_season_archived", "2023_season_archived"]:
        os.makedirs(f"{base_dir}/{year}/teams", exist_ok=True)
        with open(f"{base_dir}/{year}/teams/old_teams.json", "w") as f:
            json.dump([{"team_id": "T_OLD_1", "team_name": "Ghost_Squad"}], f)

    live_dir = f"{base_dir}/2024_season_live"
    teams_dir = f"{live_dir}/teams"
    players_dir = f"{live_dir}/players"
    ac_dir = f"{live_dir}/anticheat"

    os.makedirs(teams_dir, exist_ok=True)
    os.makedirs(ac_dir, exist_ok=True)

    # 封禁名单生成 (加入日志噪音)
    banlist_players = set()
    with open(f"{ac_dir}/banlist.txt", "w") as f:
        f.write("--- ANTICHEAT BANLOG ---\n")
        for i in range(50):
            p_id = f"P_BANNED_{i}"
            banlist_players.add(p_id)
            timestamp = datetime(2024, 4, random.randint(1, 30)).strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] ACTION: PERMABAN | BannedID: {p_id} | Reason: Detected memory hook (Aimbot)\n")

    # 构建队伍和玩家数据
    # 一共生成 300 支队伍，部分合规，部分违规
    teams_data = []
    players_data = []

    def random_date(start_year, end_year):
        start = datetime(start_year, 1, 1)
        end = datetime(end_year, 12, 31)
        return start + timedelta(days=random.randint(0, (end - start).days))

    # valid boundaries
    # valid_birth_range = 2005-05-19 to 2010-05-18
    def get_valid_bday():
        return random_date(2006, 2009).strftime("%Y-%m-%d")

    def get_too_young_bday():
        # 13 or younger
        return random_date(2011, 2013).strftime("%Y-%m-%d")

    def get_too_old_bday():
        # 19 or older
        return random_date(2000, 2004).strftime("%Y-%m-%d")

    team_counter = 1
    player_counter = 1

    # 1. Valid teams (exactly 3 players, 14-18, not banned) : 80 teams
    for _ in range(80):
        t_id = f"T_{team_counter}"
        t_name = f"ValidSweats_{team_counter}"
        teams_data.append({"team_id": t_id, "team_name": t_name})
        for _ in range(3):
            players_data.append([f"P_{player_counter}", f"Player_{player_counter}", t_id, get_valid_bday()])
            player_counter += 1
        team_counter += 1

    # 2. Invalid size (2 players) : 40 teams
    for _ in range(40):
        t_id = f"T_{team_counter}"
        t_name = f"DuoQueue_{team_counter}"
        teams_data.append({"team_id": t_id, "team_name": t_name})
        for _ in range(2):
            players_data.append([f"P_{player_counter}", f"Player_{player_counter}", t_id, get_valid_bday()])
            player_counter += 1
        team_counter += 1

    # 3. Invalid size (4 players) : 40 teams
    for _ in range(40):
        t_id = f"T_{team_counter}"
        t_name = f"SquadFam_{team_counter}"
        teams_data.append({"team_id": t_id, "team_name": t_name})
        for _ in range(4):
            players_data.append([f"P_{player_counter}", f"Player_{player_counter}", t_id, get_valid_bday()])
            player_counter += 1
        team_counter += 1

    # 4. Invalid size (0 players) : 20 teams
    for _ in range(20):
        t_id = f"T_{team_counter}"
        t_name = f"GhostTeam_{team_counter}"
        teams_data.append({"team_id": t_id, "team_name": t_name})
        team_counter += 1

    # 5. Invalid Age (Too young) : 30 teams
    for _ in range(30):
        t_id = f"T_{team_counter}"
        t_name = f"Squeakers_{team_counter}"
        teams_data.append({"team_id": t_id, "team_name": t_name})
        players_data.append([f"P_{player_counter}", f"Player_{player_counter}", t_id, get_too_young_bday()])
        player_counter += 1
        for _ in range(2):
            players_data.append([f"P_{player_counter}", f"Player_{player_counter}", t_id, get_valid_bday()])
            player_counter += 1
        team_counter += 1

    # 6. Invalid Age (Too old) : 30 teams
    for _ in range(30):
        t_id = f"T_{team_counter}"
        t_name = f"Boomers_{team_counter}"
        teams_data.append({"team_id": t_id, "team_name": t_name})
        players_data.append([f"P_{player_counter}", f"Player_{player_counter}", t_id, get_too_old_bday()])
        player_counter += 1
        for _ in range(2):
            players_data.append([f"P_{player_counter}", f"Player_{player_counter}", t_id, get_valid_bday()])
            player_counter += 1
        team_counter += 1

    # 7. Invalid (Banned Player) : 30 teams
    banned_list = list(banlist_players)
    for i in range(30):
        t_id = f"T_{team_counter}"
        t_name = f"Hackers_{team_counter}"
        teams_data.append({"team_id": t_id, "team_name": t_name})
        # Insert a banned player
        players_data.append([banned_list[i], f"Hacker_{banned_list[i]}", t_id, get_valid_bday()])
        for _ in range(2):
            players_data.append([f"P_{player_counter}", f"Player_{player_counter}", t_id, get_valid_bday()])
            player_counter += 1
        team_counter += 1

    # 8. Edge Cases for Age
    # Just turned 14 exactly on start date (Valid) - Born 2010-05-18
    t_id = f"T_{team_counter}"
    teams_data.append({"team_id": t_id, "team_name": "Edge_Valid_14"})
    players_data.append([f"P_{player_counter}", f"Player_{player_counter}", t_id, "2010-05-18"])
    player_counter += 1
    for _ in range(2):
        players_data.append([f"P_{player_counter}", f"Player_{player_counter}", t_id, get_valid_bday()])
        player_counter += 1
    team_counter += 1

    # Missed 14 by one day (Invalid) - Born 2010-05-19 (Still 13 on 2024-05-18)
    t_id = f"T_{team_counter}"
    teams_data.append({"team_id": t_id, "team_name": "Edge_Invalid_13"})
    players_data.append([f"P_{player_counter}", f"Player_{player_counter}", t_id, "2010-05-19"])
    player_counter += 1
    for _ in range(2):
        players_data.append([f"P_{player_counter}", f"Player_{player_counter}", t_id, get_valid_bday()])
        player_counter += 1
    team_counter += 1

    # Just about to turn 19, still 18 (Valid) - Born 2005-05-19
    t_id = f"T_{team_counter}"
    teams_data.append({"team_id": t_id, "team_name": "Edge_Valid_18"})
    players_data.append([f"P_{player_counter}", f"Player_{player_counter}", t_id, "2005-05-19"])
    player_counter += 1
    for _ in range(2):
        players_data.append([f"P_{player_counter}", f"Player_{player_counter}", t_id, get_valid_bday()])
        player_counter += 1
    team_counter += 1

    # Just turned 19 on start date (Invalid) - Born 2005-05-18
    t_id = f"T_{team_counter}"
    teams_data.append({"team_id": t_id, "team_name": "Edge_Invalid_19"})
    players_data.append([f"P_{player_counter}", f"Player_{player_counter}", t_id, "2005-05-18"])
    player_counter += 1
    for _ in range(2):
        players_data.append([f"P_{player_counter}", f"Player_{player_counter}", t_id, get_valid_bday()])
        player_counter += 1
    team_counter += 1


    # 打乱 teams 写入多个 JSON 碎片，增加系统日志混淆文件
    random.shuffle(teams_data)
    chunk_size = 30
    for i in range(0, len(teams_data), chunk_size):
        chunk = teams_data[i:i+chunk_size]
        with open(f"{teams_dir}/team_batch_{i}.json", "w") as f:
            json.dump(chunk, f)
            
    # Noise file in teams
    with open(f"{teams_dir}/system_status.tmp", "w") as f:
        f.write('{"status": "degraded", "last_restart": "2024-05-01"}')

    # 打乱 players 写入以地区首字母命名的深层 CSV 碎片
    regions = ["NA", "EU", "AS", "SA", "AF", "OC"]
    for reg in regions:
        os.makedirs(f"{players_dir}/region_{reg}/data_shards", exist_ok=True)
    
    random.shuffle(players_data)
    for i, p in enumerate(players_data):
        reg = random.choice(regions)
        shard_idx = i % 15 # 拆分成多个小csv
        file_path = f"{players_dir}/region_{reg}/data_shards/shard_{shard_idx}.csv"
        
        file_exists = os.path.exists(file_path)
        with open(file_path, "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["player_id", "player_name", "team_id", "birth_date"])
            writer.writerow(p)

    # Noise file in players
    os.makedirs(f"{players_dir}/region_XX/data_shards", exist_ok=True)
    with open(f"{players_dir}/region_XX/data_shards/corrupted.csv", "w") as f:
        f.write("player_id,player_name\nN/A,ERR_0912\n")

if __name__ == "__main__":
    build_env()
