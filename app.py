import html

import requests
import streamlit as st

# =============================
# CONFIG
# =============================
API_BASE = "https://movie-rec-466x.onrender.com" or "http://127.0.0.1:8000"
TMDB_IMG = "https://image.tmdb.org/t/p/w500"

st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

# =============================
# STYLES
# =============================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp { font-family: 'Poppins', sans-serif; }

.stApp {
    background: radial-gradient(1200px 600px at 10% -10%, #2a0b12 0%, rgba(0,0,0,0) 60%),
                radial-gradient(900px 500px at 100% 0%, #101a3a 0%, rgba(0,0,0,0) 55%),
                #0b0c10;
    color: #e5e7eb;
}
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 1.2rem; padding-bottom: 3rem; max-width: 1500px; }

section[data-testid="stSidebar"] {
    background: #0f1117;
    border-right: 1px solid rgba(255,255,255,0.06);
}
section[data-testid="stSidebar"] * { color: #e5e7eb; }

.hero-home {
    border-radius: 24px; padding: 34px 40px; margin-bottom: 8px;
    background: linear-gradient(120deg, rgba(229,9,20,0.85) 0%, rgba(120,20,60,0.85) 45%, rgba(25,40,110,0.9) 100%);
    box-shadow: 0 20px 50px rgba(229,9,20,0.18);
}
.hero-home h1 { margin: 0; font-size: 2.3rem; font-weight: 800; color: #fff; letter-spacing: -0.5px; }
.hero-home p { margin: 8px 0 0; color: rgba(255,255,255,0.85); font-size: 1rem; }

.small-muted { color: #9ca3af; font-size: 0.92rem; }

h3, h4 { color: #fff !important; font-weight: 700 !important; }

.mcard { margin-bottom: 6px; }
.poster-wrap {
    position: relative; border-radius: 16px; overflow: hidden;
    aspect-ratio: 2 / 3; background: #1a1c25;
    box-shadow: 0 8px 24px rgba(0,0,0,0.45);
    transition: transform .25s ease, box-shadow .25s ease;
}
.poster-wrap:hover { transform: translateY(-6px) scale(1.02); box-shadow: 0 18px 40px rgba(229,9,20,0.35); }
.poster-wrap img { width: 100%; height: 100%; object-fit: cover; display: block; }
.no-poster {
    width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;
    font-size: 2.6rem; color: #4b5563;
}
.badge {
    position: absolute; top: 10px; right: 10px;
    background: rgba(0,0,0,0.72); backdrop-filter: blur(6px);
    color: #fbbf24; font-weight: 600; font-size: 0.78rem;
    padding: 4px 9px; border-radius: 999px;
}
.movie-title {
    margin-top: 10px; font-size: 0.92rem; font-weight: 600; line-height: 1.2rem;
    height: 2.4rem; overflow: hidden; color: #f3f4f6;
}
.movie-year { font-size: 0.78rem; color: #9ca3af; margin-bottom: 6px; }

.stButton > button {
    width: 100%; border-radius: 12px; font-weight: 600;
    background: rgba(255,255,255,0.05); color: #fff;
    border: 1px solid rgba(255,255,255,0.14);
    transition: all .2s ease;
}
.stButton > button:hover {
    background: linear-gradient(90deg, #e50914, #ff4d4d);
    border-color: transparent; color: #fff; transform: translateY(-1px);
}

.stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
    background: #14161d !important; color: #fff !important;
    border: 1px solid rgba(255,255,255,0.12) !important; border-radius: 14px !important;
}
.stTextInput input { padding: 14px 16px; font-size: 1rem; }
.stTextInput input:focus { border-color: #e50914 !important; box-shadow: 0 0 0 2px rgba(229,9,20,0.25) !important; }

.card {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px; padding: 24px 26px;
}
.card h2 { margin: 0 0 10px; font-size: 2rem; font-weight: 800; color: #fff; }
.card h3 { margin: 18px 0 8px; color: #fff; }
.card p { color: #d1d5db; line-height: 1.75; font-size: 1rem; margin: 0; }

.chip {
    display: inline-block; padding: 5px 13px; margin: 0 8px 6px 0;
    border-radius: 999px; font-size: 0.8rem; font-weight: 500;
    background: rgba(255,255,255,0.12); color: #fff;
}
.chip.red { background: rgba(229,9,20,0.85); }

[data-testid="stImage"] img { border-radius: 20px; box-shadow: 0 12px 32px rgba(0,0,0,0.5); }

hr { border-color: rgba(255,255,255,0.08) !important; }
</style>
""",
    unsafe_allow_html=True,
)

# =============================
# STATE + ROUTING (single-file pages)
# =============================
if "view" not in st.session_state:
    st.session_state.view = "home"  # home | details
if "selected_tmdb_id" not in st.session_state:
    st.session_state.selected_tmdb_id = None

qp_view = st.query_params.get("view")
qp_id = st.query_params.get("id")
if qp_view in ("home", "details"):
    st.session_state.view = qp_view
if qp_id:
    try:
        st.session_state.selected_tmdb_id = int(qp_id)
        st.session_state.view = "details"
    except:
        pass


def goto_home():
    st.session_state.view = "home"
    st.query_params["view"] = "home"
    if "id" in st.query_params:
        del st.query_params["id"]
    st.rerun()


def goto_details(tmdb_id: int):
    st.session_state.view = "details"
    st.session_state.selected_tmdb_id = int(tmdb_id)
    st.query_params["view"] = "details"
    st.query_params["id"] = str(int(tmdb_id))
    st.rerun()


# =============================
# API HELPERS
# =============================
@st.cache_data(ttl=30)  # short cache for autocomplete
def api_get_json(path: str, params: dict | None = None):
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=25)
        if r.status_code >= 400:
            return None, f"HTTP {r.status_code}: {r.text[:300]}"
        return r.json(), None
    except Exception as e:
        return None, f"Request failed: {e}"


def poster_grid(cards, cols=6, key_prefix="grid"):
    if not cards:
        st.info("No movies to show.")
        return

    rows = (len(cards) + cols - 1) // cols
    idx = 0
    for r in range(rows):
        colset = st.columns(cols, gap="medium")
        for c in range(cols):
            if idx >= len(cards):
                break
            m = cards[idx]
            idx += 1

            tmdb_id = m.get("tmdb_id")
            title = m.get("title", "Untitled")
            poster = m.get("poster_url")
            rating = m.get("vote_average")
            year = (m.get("release_date") or "")[:4]

            img_html = (
                f"<img src='{poster}' loading='lazy'/>"
                if poster
                else "<div class='no-poster'>🎬</div>"
            )
            badge_html = (
                f"<div class='badge'>⭐ {float(rating):.1f}</div>" if rating else ""
            )

            with colset[c]:
                st.markdown(
                    f"""
                    <div class='mcard'>
                        <div class='poster-wrap'>{img_html}{badge_html}</div>
                        <div class='movie-title'>{html.escape(title)}</div>
                        <div class='movie-year'>{year or "&nbsp;"}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if st.button("▶ Open", key=f"{key_prefix}_{r}_{c}_{idx}_{tmdb_id}"):
                    if tmdb_id:
                        goto_details(tmdb_id)


def to_cards_from_tfidf_items(tfidf_items):
    cards = []
    for x in tfidf_items or []:
        tmdb = x.get("tmdb") or {}
        if tmdb.get("tmdb_id"):
            cards.append(
                {
                    "tmdb_id": tmdb["tmdb_id"],
                    "title": tmdb.get("title") or x.get("title") or "Untitled",
                    "poster_url": tmdb.get("poster_url"),
                    "release_date": tmdb.get("release_date"),
                    "vote_average": tmdb.get("vote_average"),
                }
            )
    return cards


# =============================
# IMPORTANT: Robust TMDB search parsing
# Supports BOTH API shapes:
# 1) raw TMDB: {"results":[{id,title,poster_path,...}]}
# 2) list cards: [{tmdb_id,title,poster_url,...}]
# =============================
def parse_tmdb_search_to_cards(data, keyword: str, limit: int = 24):
    """
    Returns:
      suggestions: list[(label, tmdb_id)]
      cards: list[{tmdb_id,title,poster_url}]
    """
    keyword_l = keyword.strip().lower()

    # A) If API returns dict with 'results'
    if isinstance(data, dict) and "results" in data:
        raw = data.get("results") or []
        raw_items = []
        for m in raw:
            title = (m.get("title") or "").strip()
            tmdb_id = m.get("id")
            poster_path = m.get("poster_path")
            if not title or not tmdb_id:
                continue
            raw_items.append(
                {
                    "tmdb_id": int(tmdb_id),
                    "title": title,
                    "poster_url": f"{TMDB_IMG}{poster_path}" if poster_path else None,
                    "release_date": m.get("release_date", ""),
                    "vote_average": m.get("vote_average"),
                }
            )

    # B) If API returns already as list
    elif isinstance(data, list):
        raw_items = []
        for m in data:
            # might be {tmdb_id,title,poster_url}
            tmdb_id = m.get("tmdb_id") or m.get("id")
            title = (m.get("title") or "").strip()
            poster_url = m.get("poster_url")
            if not title or not tmdb_id:
                continue
            raw_items.append(
                {
                    "tmdb_id": int(tmdb_id),
                    "title": title,
                    "poster_url": poster_url,
                    "release_date": m.get("release_date", ""),
                    "vote_average": m.get("vote_average"),
                }
            )
    else:
        return [], []

    # Word-match filtering (contains)
    matched = [x for x in raw_items if keyword_l in x["title"].lower()]

    # If nothing matched, fallback to raw list (so never blank)
    final_list = matched if matched else raw_items

    # Suggestions = top 10 labels
    suggestions = []
    for x in final_list[:10]:
        year = (x.get("release_date") or "")[:4]
        label = f"{x['title']} ({year})" if year else x["title"]
        suggestions.append((label, x["tmdb_id"]))

    # Cards = top N
    cards = [
        {
            "tmdb_id": x["tmdb_id"],
            "title": x["title"],
            "poster_url": x["poster_url"],
            "release_date": x.get("release_date"),
            "vote_average": x.get("vote_average"),
        }
        for x in final_list[:limit]
    ]
    return suggestions, cards


# =============================
# SIDEBAR (clean)
# =============================
with st.sidebar:
    st.markdown("## 🎬 Menu")
    if st.button("🏠 Home"):
        goto_home()

    st.markdown("---")
    st.markdown("### 🏠 Home Feed (only home)")
    home_category = st.selectbox(
        "Category",
        ["trending", "popular", "top_rated", "now_playing", "upcoming"],
        index=0,
    )
    grid_cols = st.slider("Grid columns", 4, 8, 6)

# =============================
# HEADER
# =============================
st.markdown(
    """
    <div class='hero-home'>
        <h1>🎬 Movie Recommender</h1>
        <p>Type keyword → dropdown suggestions + matching results → open → details + recommendations</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.divider()

# ==========================================================
# VIEW: HOME
# ==========================================================
if st.session_state.view == "home":
    typed = st.text_input(
        "Search by movie title (keyword)", placeholder="Type: avenger, batman, love..."
    )

    st.divider()

    # SEARCH MODE (Autocomplete + word-match results)
    if typed.strip():
        if len(typed.strip()) < 2:
            st.caption("Type at least 2 characters for suggestions.")
        else:
            data, err = api_get_json("/tmdb/search", params={"query": typed.strip()})

            if err or data is None:
                st.error(f"Search failed: {err}")
            else:
                suggestions, cards = parse_tmdb_search_to_cards(
                    data, typed.strip(), limit=24
                )

                # Dropdown
                if suggestions:
                    labels = ["-- Select a movie --"] + [s[0] for s in suggestions]
                    selected = st.selectbox("Suggestions", labels, index=0)

                    if selected != "-- Select a movie --":
                        # map label -> id
                        label_to_id = {s[0]: s[1] for s in suggestions}
                        goto_details(label_to_id[selected])
                else:
                    st.info("No suggestions found. Try another keyword.")

                st.markdown("### Results")
                poster_grid(cards, cols=grid_cols, key_prefix="search_results")

        st.stop()

    # HOME FEED MODE
    st.markdown(f"### 🏠 Home — {home_category.replace('_',' ').title()}")

    home_cards, err = api_get_json(
        "/home", params={"category": home_category, "limit": 24}
    )
    if err or not home_cards:
        st.error(f"Home feed failed: {err or 'Unknown error'}")
        st.stop()

    poster_grid(home_cards, cols=grid_cols, key_prefix="home_feed")

# ==========================================================
# VIEW: DETAILS
# ==========================================================
elif st.session_state.view == "details":
    tmdb_id = st.session_state.selected_tmdb_id
    if not tmdb_id:
        st.warning("No movie selected.")
        if st.button("← Back to Home"):
            goto_home()
        st.stop()

    # Top bar
    a, b = st.columns([3, 1])
    with a:
        st.markdown("### 📄 Movie Details")
    with b:
        if st.button("← Back to Home"):
            goto_home()

    # Details (your FastAPI safe route)
    data, err = api_get_json(f"/movie/id/{tmdb_id}")
    if err or not data:
        st.error(f"Could not load details: {err or 'Unknown error'}")
        st.stop()

    # Layout: Poster LEFT, Details RIGHT
    left, right = st.columns([1, 2.4], gap="large")

    with left:
        if data.get("poster_url"):
            st.markdown(
                f"<div class='poster-wrap'><img src='{data['poster_url']}'/></div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<div class='poster-wrap'><div class='no-poster'>🖼️</div></div>",
                unsafe_allow_html=True,
            )

    with right:
        release = data.get("release_date") or "-"
        genre_names = [g["name"] for g in data.get("genres", [])]
        chips = "".join(
            f"<span class='chip red'>{html.escape(g)}</span>" for g in genre_names
        )
        chips += f"<span class='chip'>📅 {html.escape(release)}</span>"
        overview = html.escape(data.get("overview") or "No overview available.")
        st.markdown(
            f"""
            <div class='card'>
                <h2>{html.escape(data.get('title', ''))}</h2>
                <div>{chips}</div>
                <h3>Overview</h3>
                <p>{overview}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if data.get("backdrop_url"):
        st.markdown("#### Backdrop")
        st.image(data["backdrop_url"], width="stretch")

    st.divider()
    st.markdown("### ✅ Recommendations")

    # Recommendations (TF-IDF + Genre) via your bundle endpoint
    title = (data.get("title") or "").strip()
    if title:
        bundle, err2 = api_get_json(
            "/movie/search",
            params={"query": title, "tfidf_top_n": 12, "genre_limit": 12},
        )

        if not err2 and bundle:
            st.markdown("#### 🔎 Similar Movies (TF-IDF)")
            poster_grid(
                to_cards_from_tfidf_items(bundle.get("tfidf_recommendations")),
                cols=grid_cols,
                key_prefix="details_tfidf",
            )

            st.markdown("#### 🎭 More Like This (Genre)")
            poster_grid(
                bundle.get("genre_recommendations", []),
                cols=grid_cols,
                key_prefix="details_genre",
            )
        else:
            st.info("Showing Genre recommendations (fallback).")
            genre_only, err3 = api_get_json(
                "/recommend/genre", params={"tmdb_id": tmdb_id, "limit": 18}
            )
            if not err3 and genre_only:
                poster_grid(
                    genre_only, cols=grid_cols, key_prefix="details_genre_fallback"
                )
            else:
                st.warning("No recommendations available right now.")
    else:
        st.warning("No title available to compute recommendations.")
