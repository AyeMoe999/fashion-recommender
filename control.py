"""
Fuzzy Logic Controller (FLC) for fashion recommendation.
Inputs: Occasion (0-10), Style Preference (0-10), Age (15-80), Culture (Traditional/Western).
Outputs: Four continuous Vibe Scores (0-1): Comfort, Trend, Formal, Sophistication.
Rules combine occasion + style + age so both occasion and style affect the result.
Cultural image mapping is done in app layer (filter by culture, then match by vibe scores).
"""
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# --- 1. Input universes and membership functions ---
# Occasion (0-10): Home (0-3), Outing (4-5.5), Work (5.5-8), Party/Event (8-10)
# Outing ends at 5.5 so Work (occ=6) does not overlap with Outing rules (which push trend/daily)
occasion = ctrl.Antecedent(np.arange(0, 11, 0.5), 'occasion')
occasion['home'] = fuzz.trapmf(occasion.universe, [0, 0, 2, 4])
occasion['outing'] = fuzz.trapmf(occasion.universe, [3, 4, 5, 5.5])
occasion['work'] = fuzz.trapmf(occasion.universe, [5.5, 6, 7, 8])
occasion['party'] = fuzz.trapmf(occasion.universe, [7, 8, 10, 10])

# Style Preference (0-10): Simple (0-3.5), Trendy (3.5-7.5), Elegant (8-10)
# Work: simple→daily, trendy→professional, elegant (8+)→event can win. Party: simple→daily, 4+→event.
# Simple ends at 3.5, Trendy starts at 3.5 so Professional wins from style 3.5+
style = ctrl.Antecedent(np.arange(0, 11, 0.5), 'style')
style['simple'] = fuzz.trapmf(style.universe, [0, 0, 2, 3.5])
style['trendy'] = fuzz.trapmf(style.universe, [3, 3.5, 6, 7.5])
style['elegant'] = fuzz.trapmf(style.universe, [8, 8.5, 10, 10])

# Age (15-80): Young (15-35), Middle (30-50), Old (45-80)
age = ctrl.Antecedent(np.arange(15, 81, 1), 'age')
age['young'] = fuzz.trapmf(age.universe, [15, 15, 25, 35])
age['middle'] = fuzz.trapmf(age.universe, [28, 36, 44, 52])
age['old'] = fuzz.trapmf(age.universe, [45, 55, 80, 80])

# Culture: categorical (used in app for image mapping; keep for optional rules)
culture = ctrl.Antecedent(np.arange(0, 11, 1), 'culture')
culture['traditional'] = fuzz.trapmf(culture.universe, [0, 0, 3, 5])
culture['western'] = fuzz.trapmf(culture.universe, [5, 7, 10, 10])

# --- 2. Output: four Vibe Scores (0-1) ---
vibe_universe = np.arange(0, 1.01, 0.02)
comfort_score = ctrl.Consequent(vibe_universe, 'comfort_score')
trend_score = ctrl.Consequent(vibe_universe, 'trend_score')
formal_score = ctrl.Consequent(vibe_universe, 'formal_score')
sophistication_score = ctrl.Consequent(vibe_universe, 'sophistication_score')

for conv in (comfort_score, trend_score, formal_score, sophistication_score):
    # Using 5 levels avoids outputs getting stuck at 0.5 (mid) too often.
    conv['very_low'] = fuzz.trimf(conv.universe, [0.0, 0.0, 0.15])
    conv['low'] = fuzz.trimf(conv.universe, [0.05, 0.2, 0.4])
    conv['mid'] = fuzz.trimf(conv.universe, [0.3, 0.5, 0.7])
    conv['high'] = fuzz.trimf(conv.universe, [0.6, 0.8, 0.95])
    conv['very_high'] = fuzz.trimf(conv.universe, [0.85, 1.0, 1.0])

# --- 3. Rule base: occasion is primary; style refines within occasion ---
# Work: MAINLY professional (formal). Simple→daily. Trendy (3.5-7.5)→professional. Elegant (8+)→event can win.
# Party: simple→daily, trendy/elegant→event. Outing: simple/trendy→daily, elegant→event. Home→comfort.
rules = [
    # ---- HOME: Comfort Wear dominates ----
    ctrl.Rule(occasion['home'], comfort_score['very_high']),
    ctrl.Rule(occasion['home'], trend_score['low']),
    ctrl.Rule(occasion['home'], formal_score['very_low']),
    ctrl.Rule(occasion['home'], sophistication_score['low']),
    ctrl.Rule(occasion['home'] & style['elegant'], sophistication_score['mid']),

    # ---- OUTING: Daily Wear (trend) for simple/trendy; Event (sophistication) for elegant ----
    ctrl.Rule(occasion['outing'] & style['simple'], trend_score['very_high']),
    ctrl.Rule(occasion['outing'] & style['simple'], formal_score['very_low']),
    ctrl.Rule(occasion['outing'] & style['simple'], sophistication_score['low']),
    ctrl.Rule(occasion['outing'] & style['simple'], comfort_score['mid']),

    ctrl.Rule(occasion['outing'] & style['trendy'], trend_score['very_high']),
    ctrl.Rule(occasion['outing'] & style['trendy'], formal_score['low']),
    ctrl.Rule(occasion['outing'] & style['trendy'], sophistication_score['low']),
    ctrl.Rule(occasion['outing'] & style['trendy'], comfort_score['mid']),

    ctrl.Rule(occasion['outing'] & style['elegant'], sophistication_score['very_high']),
    ctrl.Rule(occasion['outing'] & style['elegant'], trend_score['mid']),
    ctrl.Rule(occasion['outing'] & style['elegant'], formal_score['low']),
    ctrl.Rule(occasion['outing'] & style['elegant'], comfort_score['mid']),

    # ---- WORK: Simple (0-3.5) → Daily; Trendy (3.5-7.5) → Professional; Elegant (8+)→Event can win ----
    # Base: work pushes formal high (professional) by default
    ctrl.Rule(occasion['work'], formal_score['high']),
    ctrl.Rule(occasion['work'], sophistication_score['low']),

    ctrl.Rule(occasion['work'] & style['simple'], trend_score['very_high']),
    ctrl.Rule(occasion['work'] & style['simple'], formal_score['low']),
    ctrl.Rule(occasion['work'] & style['simple'], sophistication_score['very_low']),
    ctrl.Rule(occasion['work'] & style['simple'], comfort_score['mid']),

    ctrl.Rule(occasion['work'] & style['trendy'], formal_score['very_high']),
    ctrl.Rule(occasion['work'] & style['trendy'], sophistication_score['very_low']),
    ctrl.Rule(occasion['work'] & style['trendy'], trend_score['mid']),
    ctrl.Rule(occasion['work'] & style['trendy'], comfort_score['low']),

    ctrl.Rule(occasion['work'] & style['elegant'], formal_score['high']),
    ctrl.Rule(occasion['work'] & style['elegant'], sophistication_score['very_high']),
    ctrl.Rule(occasion['work'] & style['elegant'], trend_score['low']),
    ctrl.Rule(occasion['work'] & style['elegant'], comfort_score['low']),

    # ---- PARTY: Simple (under 4) → Daily Wear; Trendy/Elegant (4-10) → Event Wear ----
    ctrl.Rule(occasion['party'] & style['simple'], trend_score['very_high']),
    ctrl.Rule(occasion['party'] & style['simple'], sophistication_score['low']),
    ctrl.Rule(occasion['party'] & style['simple'], formal_score['very_low']),
    ctrl.Rule(occasion['party'] & style['simple'], comfort_score['mid']),

    ctrl.Rule(occasion['party'] & style['trendy'], sophistication_score['very_high']),
    ctrl.Rule(occasion['party'] & style['trendy'], trend_score['high']),
    ctrl.Rule(occasion['party'] & style['trendy'], formal_score['very_low']),
    ctrl.Rule(occasion['party'] & style['trendy'], comfort_score['low']),

    ctrl.Rule(occasion['party'] & style['elegant'], sophistication_score['very_high']),
    ctrl.Rule(occasion['party'] & style['elegant'], trend_score['mid']),
    ctrl.Rule(occasion['party'] & style['elegant'], formal_score['very_low']),

    # ---- Age refinements (subtle adjustments) ----
    ctrl.Rule(age['young'] & occasion['outing'], trend_score['high']),
    ctrl.Rule(age['old'] & occasion['work'], formal_score['high']),
    ctrl.Rule(age['middle'] & occasion['outing'] & style['elegant'], sophistication_score['high']),

    #  Outing rule for Traditional style
    ctrl.Rule(occasion['outing'], trend_score['high']),
    ctrl.Rule(occasion['outing'], formal_score['low']),
    ctrl.Rule(occasion['outing'], sophistication_score['low']),
    ctrl.Rule(occasion['outing'], comfort_score['mid']),
]

fashion_ctrl = ctrl.ControlSystem(rules)
fashion_sim = ctrl.ControlSystemSimulation(fashion_ctrl)

OUTFIT_TERMS = ['comfort_wear', 'daily_wear', 'professional_wear', 'event_wear']
OUTFIT_DISPLAY_NAMES = {
    'comfort_wear': 'Comfort Wear',
    'daily_wear': 'Daily Wear',
    'professional_wear': 'Professional Wear',
    'event_wear': 'Event Wear',
}

# Map winning vibe to style key and label for UI
VIBE_TO_STYLE = [
    ('comfort_wear', 'Comfort Wear', 'Relaxed & at ease'),
    ('daily_wear', 'Daily Wear', 'Everyday versatile look'),
    ('professional_wear', 'Professional Wear', 'Office & business ready'),
    ('event_wear', 'Event Wear', 'Party & special occasions'),
]


def get_recommendation(occasion_score, style_score, age_years, culture_val):
    """
    Runs fuzzy inference, defuzzifies to get four Vibe Scores,
    then determines Winning Style (and thus folder/image set) from the dominant vibe.
    Returns: label, description, composite_score, simulation, category_scores, winning_style_key.
    """
    fashion_sim.input['occasion'] = float(occasion_score)
    fashion_sim.input['style'] = float(style_score)
    fashion_sim.input['age'] = float(age_years)
    # culture is not used in any rule, so don't pass to sim; only used in app for image filtering
    fashion_sim.compute()

    # Use .get(): if no rule fires for a consequent, skfuzzy may omit it from output
    c = float(fashion_sim.output.get('comfort_score', 0.0))
    t = float(fashion_sim.output.get('trend_score', 0.0))
    f = float(fashion_sim.output.get('formal_score', 0.0))
    s = float(fashion_sim.output.get('sophistication_score', 0.0))

    # Clamp to [0, 1]
    c, t, f, s = np.clip([c, t, f, s], 0, 1)

    # Category scores for UI (same keys as before: comfort_wear = Comfort vibe, etc.)
    category_scores = {
        'comfort_wear': c,
        'daily_wear': t,
        'professional_wear': f,
        'event_wear': s,
    }

    # Winning style = argmax of the four vibe scores (defuzzified winning style)
    vibe_vals = [c, t, f, s]
    idx = int(np.argmax(vibe_vals))
    winning_style_key, label, desc = VIBE_TO_STYLE[idx]
    composite_score = (c * 12 + t * 37 + f * 62 + s * 87) / 4.0  # weighted toward category peaks for graph

    return label, desc, composite_score, fashion_sim, category_scores, winning_style_key


def get_recommendation_v2(culture_input, age_years, style_score, occasion_score):
    """
    Requested signature: get_recommendation(culture, age, style_score, occasion_score).
    culture_input can be 'traditional'/'western' or a numeric 0-10 value.
    """
    if isinstance(culture_input, str):
        culture_val = 2.0 if culture_input.lower().strip() == 'traditional' else 8.0
    else:
        culture_val = float(culture_input)
    return get_recommendation(occasion_score, style_score, age_years, culture_val)


# Backward-compatible name for app
def get_recommendation_data(occ_val, style_val, age_years, culture_val):
    label, desc, score, sim, category_scores, winning_style_key = get_recommendation(
        occ_val, style_val, age_years, culture_val
    )
    return label, desc, score, sim, category_scores, winning_style_key


def save_graph(simulation, composite_score):
    """Plot the four vibe scores from the last simulation."""
    c = float(simulation.output.get('comfort_score', 0.0))
    t = float(simulation.output.get('trend_score', 0.0))
    f = float(simulation.output.get('formal_score', 0.0))
    s = float(simulation.output.get('sophistication_score', 0.0))
    fig, ax = plt.subplots(figsize=(8, 4))
    vibes = ['Comfort', 'Trend', 'Formal', 'Sophistication']
    values = [np.clip(c, 0, 1), np.clip(t, 0, 1), np.clip(f, 0, 1), np.clip(s, 0, 1)]
    colors = ['C0', 'C1', 'C2', 'C3']
    x = np.arange(len(vibes))
    bars = ax.bar(x, values, color=colors, edgecolor='black', linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(vibes)
    ax.set_ylabel('Vibe score (0–1)')
    ax.set_ylim(0, 1.05)
    
    ax.set_title('Output membership (category strength)')
    ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.4)

    fig.suptitle('Fuzzy insight: inputs & output categories', fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.96])

    graph_path = 'static/images/fuzzy_graph.png'
    plt.savefig(graph_path, dpi=100)
    plt.close()
    return 'fuzzy_graph.png'
