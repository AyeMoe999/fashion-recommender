from flask import Flask, render_template, request
from control import get_recommendation_data, save_graph, OUTFIT_TERMS, OUTFIT_DISPLAY_NAMES

app = Flask(__name__)

OCCASION_MAP = {'home': 1, 'outing': 4, 'work': 6, 'party': 9}
CULTURE_MAP = {'traditional': 2, 'western': 8}
AGE_MIN, AGE_MAX = 15, 80
AGE_YOUNG_THRESHOLD = 35   # ≤35 → Young, >35 → Mature (for image filter)

COLOR_OPTIONS = [
    ('neutral', 'Neutral (Black, White, Grey)'),
    ('dark', 'Dark (Navy, Black, Charcoal)'),
    ('pastel', 'Pastel (Soft Pink, Mint, Lavender)'),
    ('earth', 'Earth Tones (Brown, Olive, Beige)'),
    ('bold', 'Bold (Red, Bright Blue, Statement)'),
]
# Extract color keys from COLOR_OPTIONS
COLOR_KEYS = [v for v, _ in COLOR_OPTIONS]

# Output categories
STYLE_KEYS = ['comfort_wear', 'daily_wear', 'professional_wear', 'event_wear']

# Image filter: Traditional + Young | Traditional + Mature | Western + Young | Western + Mature
# Each combination has its own set of 4 styles × 6 descriptions (set1: 3, set2: 3).
# Filename pattern: {age}_{culture}_{style_key}_1.png .. _6.png  (age=young|mature, culture=traditional|western)

def _outfit_set(prefix, descs):
    """Build set1 (first 3) and set2 (next 3) from prefix and 6 descriptions."""
    return {
        'set1': [{"img": f"{prefix}_{i}.png", "desc": d} for i, d in enumerate(descs[:3], 1)],
        'set2': [{"img": f"{prefix}_{i}.png", "desc": d} for i, d in enumerate(descs[3:6], 4)],
    }


# Descriptions per filter (Traditional+Young, Traditional+Mature, Western+Young, Western+Mature) and per style.
# You can replace images later; filenames stay as {age}_{culture}_{style_key}_1..6.png
DESCS_TRADITIONAL_YOUNG = {
    'comfort_wear': [
        "Young Traditional · Comfort (Soft set)",
        "Young Traditional · Comfort (Lightweight)",
        "Young Traditional · Comfort (Relaxed)",
        "Young Traditional · Comfort (Everyday)",
        "Young Traditional · Comfort (Home wear)",
        "Young Traditional · Comfort (Simple set)",
    ],
    'daily_wear': [
        "Young Traditional · Neutral · Daily (Cream lace set)",
        "Young Traditional · Pastel · Daily (Pink floral set)",
        "Young Traditional · Neutral · Daily (Cream floral set)",
        "Young Traditional · Daily (Look 4)",
        "Young Traditional · Daily (Look 5)",
        "Young Traditional · Daily (Look 6)",
    ],
    'professional_wear': [
        "Young Traditional · Work (Neat set)",
        "Young Traditional · Work (Formal blouse + htamein)",
        "Young Traditional · Work (Office ready)",
        "Young Traditional · Work (Look 4)",
        "Young Traditional · Work (Look 5)",
        "Young Traditional · Work (Look 6)",
    ],
    'event_wear': [
        "Young Traditional · Bold · Event (Red set)",
        "Young Traditional · Dark · Event (Maroon set)",
        "Young Traditional · Neutral · Event (Gold-trim cream set)",
        "Young Traditional · Event (Look 4)",
        "Young Traditional · Event (Look 5)",
        "Young Traditional · Event (Look 6)",
    ],
}

DESCS_TRADITIONAL_MATURE = {
    'comfort_wear': [
        "Mature Traditional · Comfort (Soft set)",
        "Mature Traditional · Comfort (Lightweight)",
        "Mature Traditional · Comfort (Relaxed)",
        "Mature Traditional · Comfort (Everyday)",
        "Mature Traditional · Comfort (Home wear)",
        "Mature Traditional · Comfort (Simple set)",
    ],
    'daily_wear': [
        "Mature Traditional · Bold · Daily (Red set)",
        "Mature Traditional · Neutral · Daily (Green Chake set)",
        "Mature Traditional · Neutral · Daily (Cream floral set)",
        "Mature Traditional · Daily (Look 4)",
        "Mature Traditional · Daily (Look 5)",
        "Mature Traditional · Daily (Look 6)",
    ],
    'professional_wear': [
        "Mature Traditional · Work (Uniform set)",
        "Mature Traditional · Work (White + Green htamein)",
        "Mature Traditional · Work (White + Navy longyi Uniform)",
        "Mature Traditional · Work (Look 4)",
        "Mature Traditional · Work (Look 5)",
        "Mature Traditional · Work (Look 6)",
    ],
    'event_wear': [
        "Mature Traditional · Bold · Event (Marron set)",
        "Mature Traditional · Dark · Event (Maroon set)",
        "Mature Traditional · Neutral · Event (Red set)",
        "Mature Traditional · Event (Look 4)",
        "Mature Traditional · Event (Look 5)",
        "Mature Traditional · Event (Look 6)",
    ],
}
DESCS_WESTERN_YOUNG = {
    'comfort_wear': [
        "Minimalist Jeans and Tee", "Hoodie & Joggers", "Relaxed Young Casual",
        "Comfy Young Set", "Weekend Young Look", "Easy Young Comfort",
    ],
    'daily_wear': [
        "Shirt & Jeans Young", "Blouse & Skirt Daily", "Young Daily Street Look",
        "Young Versatile Outfit", "Casual Young Daily", "Young Everyday Set",
    ],
    'professional_wear': [
        "Blazer and Tailored Trousers", "Young Office Shirt & Slacks", "Smart Young Professional",
        "Young Business Casual", "Young Professional Set", "Office Young Look",
    ],
    'event_wear': [
        "Young Party Dress", "Young Evening Look", "Young Event Outfit",
        "Young Statement Set", "Young Night Out", "Young Special Occasion",
    ],
}
DESCS_WESTERN_MATURE = {
    'comfort_wear': [
        "Knit & Chinos (Comfort)", "Mature Relaxed Casual", "Soft Mature Set",
        "Mature Comfort Casual", "Elegant Relaxed Look", "Mature Weekend Wear",
    ],
    'daily_wear': [
        "Mature Shirt & Trousers", "Blouse & Tailored Pants", "Mature Daily Smart Casual",
        "Classic Daily Mature", "Mature Versatile Outfit", "Mature Everyday Look",
    ],
    'professional_wear': [
        "Mature Business Suit", "Blazer & Dress Pants", "Mature Professional Set",
        "Executive Mature Look", "Mature Office Formal", "Professional Mature Western",
    ],
    'event_wear': [
        "Mature Evening Gown", "Mature Cocktail Dress", "Mature Event Suit",
        "Mature Party Elegant", "Mature Special Occasion", "Mature Formal Event",
    ],
}


def _build_outfits():
    out = {}

    # Define the mapping of descs dictionaries for Traditional and Western styles
    descs_mapping = {

        ('young', 'western'): DESCS_WESTERN_YOUNG,
        ('mature', 'western'): DESCS_WESTERN_MATURE,
    }

    # Western styles remain unchanged
    for age_group, culture_key, descs in [
        ('young', 'western', DESCS_WESTERN_YOUNG),
        ('mature', 'western', DESCS_WESTERN_MATURE),
    ]:
        if age_group not in out:
            out[age_group] = {}
        out[age_group][culture_key] = {}
        for sk in STYLE_KEYS:
            prefix = f"{age_group}_{culture_key}_{sk}"
            out[age_group][culture_key][sk] = _outfit_set(prefix, descs[sk])

   

    return out

def _build_traditional_outfits():
    """Handles Traditional style outfits without color."""
    out = {}

    # Define the mapping of descs dictionaries for Traditional styles
    descs_mapping = {
        ('young', 'traditional'): DESCS_TRADITIONAL_YOUNG,
        ('mature', 'traditional'): DESCS_TRADITIONAL_MATURE,
    }

    # Traditional styles need custom handling (without color key)
    for age_group in ('young', 'mature'):
        out.setdefault(age_group, {})
        for culture_key in ('traditional',):
            out[age_group].setdefault(culture_key, {})

            # Fetch the correct descs based on age and culture (only for traditional)
            descs = descs_mapping.get((age_group, culture_key))

            if descs:
                for sk in STYLE_KEYS:
                    # Handle "outing" for Traditional daily_wear specifically
                    if culture_key == 'traditional' and sk == 'daily_wear':
                        # For Traditional, map daily_wear to outing
                        prefix = f"{age_group}_{culture_key}_outing"
                    else:
                        # Regular prefix for other styles (comfort_wear, professional_wear, event_wear)
                        prefix = f"{age_group}_{culture_key}_{sk}"

                    # Assign images based on the prefix
                    out[age_group][culture_key][sk] = _outfit_set(prefix, descs[sk])

    return out

OUTFITS_BY_AGE_AND_CULTURE = _build_outfits()
# When you need to get Traditional styles, simply call:
traditional_outfits = _build_traditional_outfits()


@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        occ_key = request.form.get('occasion', 'outing')
        occ = float(OCCASION_MAP.get(occ_key, 4))
        style = float(request.form.get('style', 5))
        try:
            age_years = int(request.form.get('age', 25))
        except (TypeError, ValueError):
            age_years = 25
        age_years = max(AGE_MIN, min(AGE_MAX, age_years))
        culture_key = request.form.get('culture', 'western')
        culture_val = float(CULTURE_MAP.get(culture_key, 8))
        color_key = request.form.get('color', 'neutral')

        label, desc, score, sim, category_scores, winning_style_key = get_recommendation_data(
            occ, style, age_years, culture_val
        )

        # Normalize vibe scores so the displayed percentages are responsive and sum to 100%
        raw_total = float(sum(category_scores.values())) if category_scores else 0.0
        if raw_total <= 1e-9:
            norm_scores = {k: 0.25 for k in OUTFIT_TERMS}
        else:
            norm_scores = {k: float(category_scores.get(k, 0.0)) / raw_total for k in OUTFIT_TERMS}

        # Confidence = winning share (lower when styles are close)
        confidence = round(100 * max(norm_scores.values()), 1)
        confidence = max(25, min(98, confidence))

        graph_filename = save_graph(sim, score)

        style_key = winning_style_key
        age_group = 'young' if age_years <= AGE_YOUNG_THRESHOLD else 'mature'
        
        # Get the correct outfits based on culture (Traditional or Western)
        if culture_key == 'western':
            # Get Western outfits
            age_outfits = OUTFITS_BY_AGE_AND_CULTURE[age_group]
            culture_outfits = age_outfits[culture_key]
            style_outfits = culture_outfits[style_key]
            outfits = list(style_outfits['set1'])
            outfits_more = list(style_outfits['set2'])
        else:
            # Get Traditional outfits (using _build_traditional_outfits)
            traditional_outfits = _build_traditional_outfits()  # Call for Traditional
            age_outfits = traditional_outfits[age_group]
            culture_outfits = age_outfits[culture_key]
            style_outfits = culture_outfits[style_key]
            outfits = list(style_outfits['set1'])
            outfits_more = list(style_outfits['set2'])

        category_scores_display = [
            {'label': OUTFIT_DISPLAY_NAMES[k], 'pct': round(100 * norm_scores[k], 1)}
            for k in OUTFIT_TERMS
        ]

        color_label = next((t for v, t in COLOR_OPTIONS if v == color_key), COLOR_OPTIONS[0][1])
        age_culture_label = f"{age_group.capitalize()} · {'Traditional' if culture_key == 'traditional' else 'Western'}"

        result = {
            'label': label,
            'description': desc,
            'score': round(score, 1),
            'confidence': confidence,
            'graph': graph_filename,
            'outfits': outfits,
            'outfits_more': outfits_more,
            'category_scores': category_scores_display,
            'color_label': color_label,
            'age_culture_label': age_culture_label,
            'inputs': {
                'occasion': occ_key,
                'style': style,
                'age': age_years,
                'culture': culture_key,
                'color': color_key
            }
        }

    return render_template('index.html', result=result, color_options=COLOR_OPTIONS)


if __name__ == '__main__':
    app.run(debug=True, port=5001)
