import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Guess the Movie - Party Mode", page_icon="🎬", layout="centered")

# --- 1. DATA LOADING ---
@st.cache_data
def load_movies():
    return pd.read_csv("movies.csv")

movies_df = load_movies()

# --- 2. SESSION STATE MANAGEMENT ---
if "game_started" not in st.session_state:
    st.session_state.game_started = False
    st.session_state.players = []
    st.session_state.scores = {}
    st.session_state.current_player_idx = 0
    st.session_state.current_movie = movies_df.sample(1).iloc[0]
    st.session_state.round = 1
    st.session_state.game_over = False
    st.session_state.feedback = ""

def next_turn():
    """Advances to the next player and picks a new movie."""
    st.session_state.current_movie = movies_df.sample(1).iloc[0]
    st.session_state.round = 1
    st.session_state.game_over = False
    st.session_state.feedback = ""
    # Loop back to the first player if we reach the end of the list
    st.session_state.current_player_idx = (st.session_state.current_player_idx + 1) % len(st.session_state.players)

# --- 3. SCREEN 1: LOBBY / SETUP ---
if not st.session_state.game_started:
    st.title("🎬 Guess the Movie: Party Mode!")
    st.markdown("Enter the names of the players to start the game.")
    
    # Three explicit input boxes
    p1 = st.text_input("1st Person Name:", placeholder="Enter Player 1")
    p2 = st.text_input("2nd Person Name:", placeholder="Enter Player 2 (Optional)")
    p3 = st.text_input("3rd Person Name:", placeholder="Enter Player 3 (Optional)")
    
    if st.button("▶ Start Party"):
        # Put inputs in a list and filter out the empty ones
        raw_names = [p1, p2, p3]
        names = [name.strip() for name in raw_names if name.strip()]
        
        if names:
            st.session_state.players = names
            st.session_state.scores = {name: 0 for name in names}
            st.session_state.game_started = True
            st.rerun()
        else:
            st.error("Please enter at least one player name to start!")

# --- 4. SCREEN 2: THE MAIN GAME ---
else:
    current_player = st.session_state.players[st.session_state.current_player_idx]
    
    # Header & Current Player's Score
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(f"🎬 {current_player}'s Turn!")
    with col2:
        st.metric("🏆 Your Score", st.session_state.scores[current_player])
        
    st.divider()

    # Game Logic
    if not st.session_state.game_over:
        movie_name = st.session_state.current_movie["Movie"]
        
        st.subheader(f"Round {st.session_state.round}/3")
        
        if st.session_state.round >= 1:
            st.markdown(f"**Emoji Clue:** {st.session_state.current_movie['Emoji']}")
        if st.session_state.round >= 2:
            st.markdown(f"**Plot Hint:** {st.session_state.current_movie['Plot Hint']}")
        if st.session_state.round == 3:
            st.markdown(f"**Famous Quote:** {st.session_state.current_movie['Famous Quote']}")

        guess = st.text_input(f"What's your guess, {current_player}?", key=f"guess_{st.session_state.round}")

        if st.button("Submit Guess"):
            # Check answer (ignoring case and colons)
            if guess.strip().lower() == movie_name.lower() or guess.strip().lower() == movie_name.replace(":", "").lower():
                points = {1: 30, 2: 20, 3: 10}[st.session_state.round]
                st.session_state.scores[current_player] += points
                st.session_state.feedback = f"✅ Correct, {current_player}! +{points} Points."
                st.session_state.game_over = True
                st.rerun()
            else:
                if st.session_state.round < 3:
                    st.session_state.round += 1
                    st.warning(f"❌ Wrong, {current_player}! Here is your next hint.")
                    st.rerun()
                else:
                    st.session_state.feedback = f"❌ Out of hints, {current_player}! The correct answer was **{movie_name}**."
                    st.session_state.game_over = True
                    st.rerun()
    else:
        st.info(st.session_state.feedback)
        
        # Figure out who is next to prompt the button
        next_player = st.session_state.players[(st.session_state.current_player_idx + 1) % len(st.session_state.players)]
        
        if st.button(f"▶ Hand over to {next_player}"):
            next_turn()
            st.rerun()

    # --- 5. SIDEBAR: LIVE LEADERBOARD ---
    with st.sidebar:
        st.header("🏆 Live Leaderboard")
        # Convert dictionary to DataFrame for a clean table
        leaderboard_df = pd.DataFrame(list(st.session_state.scores.items()), columns=['Player', 'Score'])
        leaderboard_df = leaderboard_df.sort_values(by="Score", ascending=False).reset_index(drop=True)
        st.dataframe(leaderboard_df, use_container_width=True, hide_index=True)
        
        st.divider()
        if st.button("🔄 End Party & Restart"):
            st.session_state.clear()
            st.rerun()