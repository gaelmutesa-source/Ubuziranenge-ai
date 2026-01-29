from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd

app = FastAPI(title="ITARA Sports Analytics API")

# --- DATA ENGINE (The same logic we perfected) ---
def get_analytics():
    # In production, this would load from a PostgreSQL Database
    df = pd.read_csv("rpl_master_data.csv")
    weights = {'Technical': 0.35, 'Tactical': 0.25, 'Physical': 0.25, 'Mental': 0.15}
    
    # Pillar Calculations
    df['Tech_Score'] = df['pass_accuracy'] * 0.6 + df['dribble_success'] * 0.4
    df['Tact_Score'] = (df['interceptions'] * 5) + (df['positioning_rating'] * 0.5)
    df['Phys_Score'] = (df['sprint_speed'] * 2) + (df['stamina'] * 0.2)
    df['Ment_Score'] = (df['composure'] * 0.7) + (df['big_game_impact'] * 0.3)
    df['TPI'] = (df['Tech_Score']*0.35 + df['Tact_Score']*0.25 + 
                 df['Phys_Score']*0.25 + df['Ment_Score']*0.15)
    
    # Financial Leakage Logic
    avg_val_tpi = df['market_value'].sum() / df['TPI'].sum() if df['TPI'].sum() > 0 else 0
    df['Leakage'] = (df['market_value'] - (df['TPI'] * avg_val_tpi)).clip(lower=0)
    
    return df

# --- API ENDPOINTS ---

@app.get("/")
def home():
    return {"message": "Welcome to ITARA Sports Analytics Official API"}

@app.get("/api/squad/{club_name}")
def get_squad_audit(club_name: str):
    """Returns the full squad audit for a specific club."""
    df = get_analytics()
    club_df = df[df['club'].str.lower() == club_name.lower()]
    
    if club_df.empty:
        raise HTTPException(status_code=404, detail="Club not found in ITARA Database")
    
    # Convert to JSON format for the website
    return club_df.to_dict(orient="records")

@app.get("/api/match-preview")
def match_preview(club_a: str, club_b: str):
    """Calculates Win Probability between two clubs."""
    df = get_analytics()
    tpi_a = df[df['club'].str.lower() == club_a.lower()]['TPI'].mean()
    tpi_b = df[df['club'].str.lower() == club_b.lower()]['TPI'].mean()
    
    win_p = round(50 + (tpi_a - tpi_b) * 3, 1)
    return {
        "home_team": club_a,
        "away_team": club_b,
        "win_probability": f"{win_p}%",
        "recommendation": "Aggressive press" if win_p > 55 else "Defensive block"
    }
