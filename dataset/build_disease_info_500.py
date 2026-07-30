"""
build_disease_info_500.py
--------------------------
One-time generation script: builds utils/disease_info.py with templated
(category-based) metadata for all ~500 diseases in generate_dataset.py.

Run this AFTER generate_dataset.py (it imports DISEASE_SYMPTOMS/DISEASE_CATEGORY
from there) and BEFORE train_model.py.

Content is intentionally template-based rather than individually hand-written
per disease, given the scale (~500 diseases) - it fills every field with
medically-reasonable, category-appropriate guidance, personalized with the
disease's own name and its most distinctive symptoms.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generate_dataset import DISEASE_SYMPTOMS, DISEASE_CATEGORY, CATEGORY_META

def humanize(symptom):
    return symptom.replace("_", " ")

# Category-level template phrases (causes / precautions / lifestyle / diet / exercise)
CATEGORY_TEMPLATES = {
    "Respiratory": dict(
        causes=["Viral or bacterial infection", "Air pollution or irritant exposure", "Smoking or secondhand smoke", "Weakened immune system"],
        precautions=["Rest and stay well-hydrated", "Avoid smoke and airborne irritants", "Practice good hand hygiene", "Complete any prescribed antibiotics/medication fully"],
        lifestyle=["Avoid smoking and secondhand smoke", "Keep indoor air clean and well-ventilated", "Get an annual flu vaccine if advised", "Practice deep-breathing exercises"],
        diet=["Warm fluids (soups, herbal tea)", "Vitamin C rich fruits", "Avoid cold or fried foods during flare-ups"],
        exercise=["Light walking as tolerated", "Breathing exercises (pursed-lip breathing)", "Avoid strenuous exertion during active symptoms"],
        when_to_consult="Seek medical care if breathing difficulty worsens, fever persists beyond 3 days, or lips/fingertips turn bluish.",
    ),
    "Cardiovascular": dict(
        causes=["High blood pressure or cholesterol", "Smoking", "Sedentary lifestyle", "Family history of heart disease"],
        precautions=["Monitor blood pressure regularly", "Avoid smoking and excess alcohol", "Manage stress levels", "Take prescribed heart medication consistently"],
        lifestyle=["Follow a heart-healthy routine", "Maintain a healthy weight", "Sleep 7-8 hours nightly", "Limit salt intake"],
        diet=["Low-sodium, low-saturated-fat meals", "Omega-3 rich fish and nuts", "Plenty of fruits and vegetables", "Limit processed and fried foods"],
        exercise=["Doctor-supervised light cardio (walking)", "Avoid strenuous exertion without medical clearance", "Relaxation and breathing exercises"],
        when_to_consult="Seek emergency care immediately for chest pain, breathlessness, fainting, or irregular heartbeat.",
    ),
    "Gastrointestinal": dict(
        causes=["Infection or food contamination", "Poor diet or food intolerance", "Chronic inflammation", "Stress"],
        precautions=["Stay hydrated", "Avoid spicy, oily, or irritant foods", "Eat smaller, more frequent meals", "Take prescribed medication as directed"],
        lifestyle=["Eat at regular times", "Avoid lying down right after eating", "Manage stress levels", "Avoid excess alcohol"],
        diet=["Bland, easily digestible foods", "Plenty of fiber and water", "Avoid spicy, fried, and acidic foods", "Small, frequent meals"],
        exercise=["Light walking after meals", "Gentle stretching", "Avoid vigorous exercise right after eating"],
        when_to_consult="See a doctor if you notice blood in stool/vomit, severe or persistent abdominal pain, or unexplained weight loss.",
    ),
    "Neurological": dict(
        causes=["Nerve or brain-related dysfunction", "Genetic predisposition", "Stress or lack of sleep", "Injury or infection affecting the nervous system"],
        precautions=["Get adequate sleep and rest", "Avoid known personal triggers", "Take prescribed medication consistently", "Avoid sudden strenuous activity during flare-ups"],
        lifestyle=["Maintain a consistent sleep schedule", "Manage stress with relaxation techniques", "Stay well-hydrated", "Avoid excess caffeine and alcohol"],
        diet=["Regular balanced meals (avoid skipping meals)", "Stay well-hydrated", "Limit caffeine and processed foods"],
        exercise=["Gentle regular activity as tolerated", "Yoga or stretching for relaxation", "Avoid overexertion during symptomatic periods"],
        when_to_consult="Seek urgent care for sudden severe headache, seizures, confusion, slurred speech, or one-sided weakness.",
    ),
    "Musculoskeletal": dict(
        causes=["Joint or muscle overuse", "Age-related wear and tear", "Inflammation or autoimmune activity", "Injury"],
        precautions=["Rest the affected area", "Apply hot/cold therapy as advised", "Avoid activities that worsen pain", "Maintain good posture"],
        lifestyle=["Maintain a healthy weight to reduce joint strain", "Stretch regularly", "Use supportive footwear", "Avoid repetitive strain"],
        diet=["Anti-inflammatory foods (leafy greens, fatty fish)", "Adequate calcium and vitamin D", "Limit processed and sugary foods"],
        exercise=["Low-impact activity (swimming, walking)", "Gentle stretching and mobility exercises", "Physiotherapist-guided strengthening"],
        when_to_consult="See a doctor if pain is severe, sudden, accompanied by significant swelling, or limits daily movement.",
    ),
    "Dermatological": dict(
        causes=["Allergic reaction or irritant exposure", "Infection (bacterial, fungal, or viral)", "Autoimmune activity", "Genetic predisposition"],
        precautions=["Keep the affected area clean and dry", "Avoid scratching or picking", "Use gentle, fragrance-free skin products", "Avoid known triggers/allergens"],
        lifestyle=["Moisturize regularly", "Wear breathable, soft fabrics", "Avoid excessive sun exposure", "Manage stress, which can worsen flare-ups"],
        diet=["Stay well-hydrated", "Include omega-3 and antioxidant-rich foods", "Identify and avoid personal trigger foods if applicable"],
        exercise=["Regular light activity supports circulation", "Shower promptly after sweating to avoid irritation"],
        when_to_consult="See a doctor if the area shows spreading redness, pus, fever, or does not improve with basic care.",
    ),
    "Endocrine_Metabolic": dict(
        causes=["Hormonal imbalance", "Genetic factors", "Autoimmune activity", "Diet and lifestyle factors"],
        precautions=["Monitor relevant levels regularly (sugar, hormones, etc.)", "Take prescribed medication on schedule", "Attend regular follow-up appointments", "Report new symptoms promptly"],
        lifestyle=["Maintain a balanced diet and healthy weight", "Exercise regularly", "Get adequate sleep", "Manage stress"],
        diet=["Balanced meals with controlled portions", "Limit refined sugar and processed foods", "Adequate protein and fiber"],
        exercise=["Moderate regular aerobic activity", "Strength training 2-3x/week if cleared by a doctor"],
        when_to_consult="See a doctor if you notice rapid weight changes, persistent fatigue, or symptoms worsening despite treatment.",
    ),
    "Renal_Urological": dict(
        causes=["Infection", "Structural or functional abnormality", "Dehydration", "Chronic conditions (diabetes, hypertension)"],
        precautions=["Stay well-hydrated", "Avoid holding urine for long periods", "Complete prescribed antibiotics fully", "Monitor for blood in urine"],
        lifestyle=["Drink adequate water daily", "Maintain good hygiene", "Avoid excessive salt intake", "Urinate when needed rather than delaying"],
        diet=["Plenty of water", "Limit salt and processed foods", "Reduce oxalate-rich foods if prone to stones"],
        exercise=["Regular moderate activity", "Avoid dehydration during exercise"],
        when_to_consult="See a doctor if you notice blood in urine, severe pain, fever, or difficulty urinating.",
    ),
    "Hematological_Oncological": dict(
        causes=["Bone marrow or blood cell abnormality", "Genetic factors", "Nutritional deficiency", "Uncontrolled cell growth"],
        precautions=["Attend all follow-up appointments and tests", "Avoid infection exposure if immunity is low", "Report unusual bruising or bleeding promptly", "Follow the treating specialist's plan closely"],
        lifestyle=["Prioritize rest and recovery", "Avoid infection risk when immunity is low", "Maintain a nutrient-dense diet", "Seek emotional/support resources"],
        diet=["Iron, folate, and B12-rich foods as advised", "Well-cooked, hygienic food to reduce infection risk", "Stay well-hydrated"],
        exercise=["Light activity as energy allows", "Avoid overexertion; prioritize rest during treatment"],
        when_to_consult="See a specialist promptly for unusual bruising, persistent fatigue, unexplained weight loss, or swollen lymph nodes.",
    ),
    "Mental_Health": dict(
        causes=["Combination of genetic, biological, and environmental factors", "Chronic stress", "Life events or trauma", "Chemical imbalances"],
        precautions=["Reach out to a mental health professional", "Maintain a consistent daily routine", "Avoid isolating from support systems", "Avoid alcohol/substance use as coping tools"],
        lifestyle=["Maintain a regular sleep schedule", "Stay connected with supportive friends/family", "Practice mindfulness or relaxation techniques", "Engage in regular physical activity"],
        diet=["Regular balanced meals", "Limit excess caffeine and alcohol", "Stay hydrated"],
        exercise=["Regular moderate exercise (shown to help mood)", "Outdoor activity/sunlight exposure", "Yoga or mindfulness-based movement"],
        when_to_consult="Seek immediate help from a mental health professional or crisis line if there are thoughts of self-harm or an inability to function day-to-day.",
    ),
    "Infectious": dict(
        causes=["Bacterial, viral, or parasitic infection", "Contaminated food or water", "Vector-borne transmission (mosquitoes, ticks)", "Close contact with an infected person"],
        precautions=["Complete the full course of any prescribed medication", "Isolate if advised to prevent spread", "Maintain good hygiene", "Stay hydrated and rested"],
        lifestyle=["Practice good hand hygiene", "Ensure safe food and water sources", "Stay up to date on relevant vaccinations", "Use protective measures against vectors (mosquito nets, repellents)"],
        diet=["Plenty of fluids", "Easily digestible, nutrient-rich foods", "Avoid raw or undercooked food during recovery"],
        exercise=["Rest is prioritized during acute illness", "Resume light activity gradually as symptoms improve"],
        when_to_consult="Seek medical care promptly for high fever, severe weakness, persistent vomiting, or symptoms that worsen rather than improve.",
    ),
    "ENT": dict(
        causes=["Infection (viral, bacterial, or fungal)", "Allergies", "Structural abnormality", "Prolonged noise or irritant exposure"],
        precautions=["Avoid inserting objects into the ear/nose", "Keep the area dry and clean", "Avoid loud noise exposure", "Complete prescribed medication fully"],
        lifestyle=["Avoid exposure to smoke and strong allergens", "Practice good hygiene", "Protect ears from loud/prolonged noise"],
        diet=["Stay well-hydrated", "Warm fluids for throat-related discomfort"],
        exercise=["Light activity as tolerated", "Avoid activities affecting balance if dizziness is present"],
        when_to_consult="See a specialist if pain is severe, hearing/vision changes occur, or symptoms persist beyond a week.",
    ),
    "Ophthalmological": dict(
        causes=["Infection or inflammation", "Age-related changes", "Prolonged screen exposure or eye strain", "Underlying systemic disease (e.g., diabetes)"],
        precautions=["Avoid rubbing the eyes", "Use prescribed eye drops/medication as directed", "Wear protective eyewear when needed", "Take regular breaks from screens"],
        lifestyle=["Follow the 20-20-20 rule for screen use", "Wear sunglasses in bright sunlight", "Maintain good eye hygiene", "Get regular eye check-ups"],
        diet=["Vitamin A and antioxidant-rich foods", "Omega-3 fatty acids", "Stay well-hydrated"],
        exercise=["Regular eye-relaxation breaks", "General aerobic activity supports eye health"],
        when_to_consult="See an eye specialist promptly for sudden vision loss, severe eye pain, or persistent redness/discharge.",
    ),
    "Gynecological_Obstetric": dict(
        causes=["Hormonal changes", "Infection", "Structural abnormality (fibroids, cysts)", "Pregnancy-related changes"],
        precautions=["Track symptoms/cycle patterns", "Attend regular gynecological check-ups", "Take prescribed medication as directed", "Report unusual bleeding or pain promptly"],
        lifestyle=["Maintain a balanced diet and regular exercise", "Manage stress", "Practice good hygiene", "Stay informed about your reproductive health"],
        diet=["Iron-rich foods, especially with heavy bleeding", "Balanced, nutrient-dense meals", "Stay well-hydrated"],
        exercise=["Regular moderate activity", "Pelvic floor exercises where appropriate"],
        when_to_consult="See a gynecologist for severe pain, heavy or irregular bleeding, or symptoms during pregnancy that concern you.",
    ),
    "Pediatric": dict(
        causes=["Infection", "Developmental or congenital factors", "Immature immune or digestive system", "Genetic factors"],
        precautions=["Monitor fever and hydration closely", "Follow the pediatrician's care plan", "Keep vaccinations up to date", "Watch for feeding or behavior changes"],
        lifestyle=["Maintain a consistent feeding/sleep routine", "Ensure a safe, clean environment", "Keep regular pediatric check-ups"],
        diet=["Age-appropriate, nutrient-rich feeding", "Adequate fluids", "Follow pediatrician's dietary guidance"],
        exercise=["Age-appropriate activity and play", "Encourage motor development through play"],
        when_to_consult="See a pediatrician promptly for high fever, poor feeding, lethargy, difficulty breathing, or if the child seems unusually unwell.",
    ),
    "Allergic_Immunological": dict(
        causes=["Allergen exposure (food, pollen, dust, insect stings)", "Genetic predisposition", "Immune system dysfunction", "Environmental triggers"],
        precautions=["Identify and avoid known triggers", "Carry emergency medication if prescribed (e.g., epinephrine)", "Read food/product labels carefully", "Seek immediate care for severe reactions"],
        lifestyle=["Keep living spaces free of common allergens", "Inform close contacts about known allergies", "Carry an allergy action plan if applicable"],
        diet=["Avoid known trigger foods strictly", "Read ingredient labels carefully", "Consult an allergist/dietitian for safe alternatives"],
        exercise=["Regular activity is fine unless it's a known trigger", "Have medication accessible during exercise if needed"],
        when_to_consult="Seek emergency care immediately for difficulty breathing, throat tightness, swelling of the face/lips, or dizziness after exposure.",
    ),
    "Dental_Oral": dict(
        causes=["Poor oral hygiene", "Bacterial infection", "Diet high in sugar", "Structural or developmental factors"],
        precautions=["Brush and floss regularly", "Avoid excessive sugary foods/drinks", "See a dentist for regular cleanings", "Avoid delaying treatment for pain or bleeding gums"],
        lifestyle=["Brush twice daily and floss once daily", "Limit sugary snacks and drinks", "Avoid tobacco products", "Schedule routine dental check-ups"],
        diet=["Limit sugary and acidic foods/drinks", "Adequate calcium for dental health", "Drink water after meals"],
        exercise=["Not typically relevant, though overall health supports oral health"],
        when_to_consult="See a dentist promptly for persistent pain, swelling, bleeding gums, or loose teeth.",
    ),
    "Nutritional": dict(
        causes=["Inadequate dietary intake", "Malabsorption", "Increased nutritional needs (growth, pregnancy, illness)", "Chronic illness affecting nutrient absorption"],
        precautions=["Follow a balanced, nutrient-rich diet", "Take prescribed supplements as directed", "Get regular check-ups to monitor levels", "Address any underlying digestive conditions"],
        lifestyle=["Eat a varied, balanced diet", "Get regular sunlight exposure if vitamin D is low", "Address underlying causes with a doctor's guidance"],
        diet=["Nutrient-dense whole foods", "Supplements as recommended by a doctor", "Address specific deficiencies with targeted foods"],
        exercise=["Light to moderate activity as energy allows", "Gradually increase as nutritional status improves"],
        when_to_consult="See a doctor if you notice persistent fatigue, poor growth, unusual bruising/bleeding, or symptoms not improving with diet changes.",
    ),
}

DISEASE_INFO = {}

for disease, symptoms in DISEASE_SYMPTOMS.items():
    category = DISEASE_CATEGORY[disease]
    tmpl = CATEGORY_TEMPLATES[category]
    specialist, base_risk = CATEGORY_META[category]

    top_symptoms = [humanize(s) for s in symptoms[:3]]
    symptom_phrase = ", ".join(top_symptoms) if top_symptoms else "a range of symptoms"

    DISEASE_INFO[disease] = {
        "description": f"{disease} is a {category.replace('_', '/').lower()} condition commonly presenting with {symptom_phrase}, among other symptoms.",
        "causes": tmpl["causes"],
        "precautions": tmpl["precautions"],
        "lifestyle_tips": tmpl["lifestyle"],
        "diet": tmpl["diet"],
        "exercise": tmpl["exercise"],
        "when_to_consult": tmpl["when_to_consult"],
        "specialist": specialist,
        "base_risk": base_risk,
    }

# ---------------------------------------------------------------------
# Write utils/disease_info.py
# ---------------------------------------------------------------------
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "utils", "disease_info.py")

with open(OUTPUT_PATH, "w") as f:
    f.write('"""\n')
    f.write('disease_info.py\n')
    f.write('----------------\n')
    f.write('Static knowledge base of disease metadata used to populate the Result Page.\n\n')
    f.write('AUTO-GENERATED for ~500 diseases via dataset/build_disease_info_500.py.\n')
    f.write('Content is templated by medical category (with the disease name and its\n')
    f.write('top symptoms filled in) rather than individually hand-written per disease,\n')
    f.write('given the scale involved - it is intentionally general guidance, not a\n')
    f.write('clinical reference.\n\n')
    f.write('IMPORTANT: This content is for EDUCATIONAL purposes only and is a\n')
    f.write('simplified summary. It is not medical advice.\n')
    f.write('"""\n\n')
    f.write("DISEASE_INFO = {\n")
    for disease, info in DISEASE_INFO.items():
        f.write(f"    {disease!r}: {{\n")
        f.write(f"        \"description\": {info['description']!r},\n")
        f.write(f"        \"causes\": {info['causes']!r},\n")
        f.write(f"        \"precautions\": {info['precautions']!r},\n")
        f.write(f"        \"lifestyle_tips\": {info['lifestyle_tips']!r},\n")
        f.write(f"        \"diet\": {info['diet']!r},\n")
        f.write(f"        \"exercise\": {info['exercise']!r},\n")
        f.write(f"        \"when_to_consult\": {info['when_to_consult']!r},\n")
        f.write(f"        \"specialist\": {info['specialist']!r},\n")
        f.write(f"        \"base_risk\": {info['base_risk']!r},\n")
        f.write("    },\n")
    f.write("}\n\n\n")
    f.write('def get_disease_info(disease_name: str) -> dict:\n')
    f.write('    """\n')
    f.write('    Safely retrieve metadata for a given disease name.\n')
    f.write('    Returns a default fallback dictionary if the disease is not found,\n')
    f.write('    so the app never crashes due to a missing lookup.\n')
    f.write('    """\n')
    f.write('    return DISEASE_INFO.get(disease_name, {\n')
    f.write('        "description": "Detailed information is not available for this condition.",\n')
    f.write('        "causes": ["Not available"],\n')
    f.write('        "precautions": ["Please consult a certified medical professional."],\n')
    f.write('        "lifestyle_tips": ["Maintain a healthy diet and lifestyle."],\n')
    f.write('        "diet": ["Follow a balanced, doctor-recommended diet."],\n')
    f.write('        "exercise": ["Follow doctor-recommended activity levels."],\n')
    f.write('        "when_to_consult": "Please consult a certified medical professional for guidance.",\n')
    f.write('        "specialist": "General Physician",\n')
    f.write('        "base_risk": "Medium",\n')
    f.write('    })\n')

print(f"Wrote {len(DISEASE_INFO)} disease entries to {OUTPUT_PATH}")
