from bottle import Bottle, request, response
import pandas as pd
import re
from difflib import SequenceMatcher

app = Bottle()

# Load your CSVs
archive = pd.read_csv('fs/combined.csv')
youtube = pd.read_csv('data/combined.csv')


archive['title'] = archive['title'].astype(str)
archive['description'] = archive['description'].astype(str)

archive['title'] = archive['title'].str.replace('– Full Story podcast', "")


archive['title'] = archive.apply(lambda x: x['title'].replace(x['description'], '').strip(), axis=1)
archive['title'] = archive['title'].str.replace(r'Podcast\d{2}:\d{2}', '', regex=True).str.strip()


def search_similar(df,
                   queries: list[str],
                   columns: list[str],
                   threshold: float = 0.6,
                   token_overlap_min: float = 0.5):

    queries = [q.strip().casefold() for q in queries if q and str(q).strip()]
    if not queries:
        return df.iloc[0:0]

    word_re = re.compile(r"\w+")

    def token_overlap(a: str, b: str) -> float:
        sa, sb = set(word_re.findall(a)), set(word_re.findall(b))
        if not sa or not sb:
            return 0.0
        denom = min(len(sa), len(sb))
        return len(sa & sb) / denom

    def is_similar(text) -> bool:
        if pd.isna(text):
            return False
        t = str(text).casefold().strip()
        if not t:
            return False
        for q in queries:
            if q in t or t in q:
                return True
            if token_overlap(t, q) >= token_overlap_min:
                return True
            if SequenceMatcher(None, t, q).ratio() >= threshold:
                return True
        return False

    mask = df[columns].map(is_similar).any(axis=1)
    result = df[mask].copy()
    result['published'] = pd.to_datetime(result['published']).dt.strftime("%d/%m/%Y")
    return result


@app.get("/")
def index():
    return """
    <div style="min-height:100vh;display:flex;align-items:center;justify-content:center;background:#f7f7f7;margin:0;padding:0;">
      <div style="background:#fff;padding:24px 28px;box-shadow:0 6px 24px rgba(0,0,0,0.08);font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;max-width:640px;width:100%;">
        <h2 style="margin-top:0;margin-bottom:16px;text-align:center;">Let's find some clips!</h2>
        <form action="/search" method="post" style="display:flex;flex-direction:column;gap:12px;">
          
          <input type="text" id="url" name="url" placeholder="Search for something. Like David Littleproud..." 
                 style="width:100%;max-width:100%;padding:10px 12px;border:1px solid #ddd;" required>
        
          <label for="quality" style="font-size:0.9em;color:#333;">Search where?</label>
          <select id="quality" name="quality" style="padding:10px 12px;border:1px solid #ddd;">
            <option value="youtube">Youtube News channels</option>
            <option value="archive" selected>Full story archive</option>
          </select>

          <label for="threshold" style="font-size:0.9em;color:#333;">How closely should the search algorithm match?</label>
          <select id="threshold" name="threshold" style="padding:10px 12px;border:1px solid #ddd;">
            <option value="0.4">Loose (0.4)</option>
            <option value="0.6" selected>Normal (0.6)</option>
            <option value="0.75">Tight (0.75)</option>
            <option value="0.9">Very strict (0.9)</option>
          </select>
          
          <input type="submit" value="Search" 
                 style="padding:10px 14px;border:0;background:#111;color:#fff;cursor:pointer;">
        </form>
      </div>
    </div>
    """


@app.post("/search")
def searcher():
    query = (request.forms.get("url") or "").strip()
    search_type = request.forms.get("quality")  # 'youtube' or 'archive'
    threshold_str = request.forms.get("threshold", "0.6")

    if not query:
        response.status = 400
        return "Missing search term."

    try:
        threshold = float(threshold_str)
    except ValueError:
        threshold = 0.6

    df = youtube if search_type == "youtube" else archive

    cols = ["title", "description", 'Pub'] if search_type == 'youtube' else ["title", "description", 'contributors']

    results = search_similar(df, [query], cols, threshold=threshold)

    if results.empty:
        return f"<p style='font-family:sans-serif;text-align:center;'>No results found for <b>{query}</b>.</p>"

    html_results = "<ul style='font-family:sans-serif;line-height:1.6;'>"
    for _, row in results.iterrows():
        html_results += f"<li>{row['published']} - {row['title']} - <a href='{row['link']}' target='_blank'>Link</a></li>"
    html_results += "</ul>"

    return f"""
    <div style="padding:24px;font-family:sans-serif;">
      <h3>Results for "{query}"</h3>
      {html_results}
      <a href="/" style="display:inline-block;margin-top:20px;color:#111;">← New search</a>
    </div>
    """


if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True, reloader=True)
