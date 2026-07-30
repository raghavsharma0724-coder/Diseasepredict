"""
generate_dataset.py
--------------------
Generates a synthetic-but-medically-plausible Disease-Symptom dataset
for the AI-Based Disease Prediction & Healthcare Recommendation System.

EXPANDED VERSION: ~500 diseases across ~18 medical categories, with a
much larger symptom pool (~150 symptoms) for finer-grained differentiation.

Why synthetic generation instead of a raw downloaded CSV?
- Fully transparent: every row's origin can be explained in a viva.
- Reproducible: running this script always regenerates the same structure.
- Controllable: we can tune noise/variability to make the ML problem
  realistic (diseases with overlapping symptoms) rather than trivial.

Output: dataset/disease_symptom_dataset.csv
    Columns: Age, Gender, <one column per symptom (0/1)>, Disease

NOTE ON ACCURACY: with ~500 disease classes drawn from a shared symptom
pool, many diseases necessarily share very similar symptom profiles
(this mirrors real medicine - symptoms alone rarely pinpoint one exact
diagnosis out of hundreds). Expect noticeably lower model accuracy than
the original 22-disease version. This is expected, not a bug.
"""

import random
import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

# =======================================================================
# 1. CATEGORY SYMPTOM POOLS
# =======================================================================
CATEGORY_SYMPTOMS = {
    "Respiratory": [
        "coughing", "dry_cough", "productive_cough", "shortness_of_breath", "wheezing",
        "chest_tightness", "difficulty_breathing", "sore_throat", "runny_nose", "sneezing",
        "congestion", "mild_fever", "high_fever", "chills", "fatigue", "chest_pain",
        "rapid_breathing", "hoarseness", "night_sweats", "coughing_blood",
    ],
    "Cardiovascular": [
        "chest_pain", "shortness_of_breath", "fatigue", "irregular_heartbeat", "palpitations",
        "dizziness", "swelling_in_legs", "swelling_ankles", "cold_sweats", "nausea",
        "fainting", "high_blood_pressure_feeling", "rapid_heartbeat", "leg_pain_walking",
        "bluish_skin", "jaw_pain",
    ],
    "Gastrointestinal": [
        "abdominal_pain", "nausea", "vomiting", "diarrhea", "constipation", "bloating",
        "heartburn", "acid_reflux", "loss_of_appetite", "weight_loss", "blood_in_stool",
        "difficulty_swallowing", "gas", "cramping", "yellowish_skin", "dark_urine",
        "pale_stool", "rectal_pain", "indigestion", "belching",
    ],
    "Neurological": [
        "headache", "severe_headache", "dizziness", "vertigo", "confusion", "memory_loss",
        "numbness", "tingling", "muscle_weakness", "tremor", "seizures", "blurred_vision",
        "sensitivity_to_light", "sensitivity_to_sound", "vomiting", "nausea", "slurred_speech",
        "loss_of_coordination", "difficulty_concentrating", "fainting", "facial_drooping",
    ],
    "Musculoskeletal": [
        "joint_pain", "joint_stiffness", "swelling_joints", "muscle_pain", "back_pain",
        "reduced_range_of_motion", "muscle_weakness", "muscle_cramps", "bone_pain",
        "fatigue", "morning_stiffness", "difficulty_walking", "localized_swelling",
        "tenderness", "limited_mobility",
    ],
    "Dermatological": [
        "skin_rash", "itching", "redness", "dry_skin", "skin_peeling", "blisters",
        "swelling", "hives", "discoloration", "skin_lesion", "burning_sensation",
        "hair_loss", "excessive_sweating", "pus_filled_bumps", "scaly_patches",
    ],
    "Endocrine_Metabolic": [
        "excessive_thirst", "frequent_urination", "fatigue", "weight_loss", "weight_gain",
        "blurred_vision", "slow_healing_wounds", "increased_appetite", "sweating",
        "heat_intolerance", "cold_intolerance", "hair_thinning", "irregular_periods",
        "mood_swings", "muscle_weakness", "tremor",
    ],
    "Renal_Urological": [
        "frequent_urination", "burning_urination", "cloudy_urine", "abdominal_pain",
        "back_pain", "fatigue", "swelling_in_legs", "blood_in_urine", "foamy_urine",
        "difficulty_urinating", "urgency", "flank_pain", "pelvic_pain", "reduced_urine_output",
    ],
    "Hematological_Oncological": [
        "fatigue", "weakness", "pale_skin", "shortness_of_breath", "dizziness",
        "easy_bruising", "unexplained_weight_loss", "night_sweats", "swollen_lymph_nodes",
        "frequent_infections", "bone_pain", "abnormal_bleeding", "loss_of_appetite",
        "lump_or_mass",
    ],
    "Mental_Health": [
        "low_mood", "loss_of_interest", "anxiety", "excessive_worry", "sleep_disturbance",
        "fatigue", "difficulty_concentrating", "irritability", "mood_swings",
        "restlessness", "social_withdrawal", "racing_thoughts", "panic_attacks",
        "intrusive_thoughts", "appetite_changes",
    ],
    "Infectious": [
        "high_fever", "chills", "sweating", "headache", "muscle_pain", "fatigue",
        "nausea", "vomiting", "skin_rash", "joint_pain", "swollen_lymph_nodes",
        "loss_of_appetite", "diarrhea", "abdominal_pain", "sore_throat",
    ],
    "ENT": [
        "ear_pain", "hearing_loss", "ringing_in_ears", "sore_throat", "hoarseness",
        "nasal_congestion", "loss_of_smell", "difficulty_swallowing", "sinus_pressure",
        "ear_discharge", "dizziness", "vertigo", "nosebleed",
    ],
    "Ophthalmological": [
        "blurred_vision", "eye_pain", "eye_redness", "watery_eyes", "itching",
        "sensitivity_to_light", "vision_loss", "double_vision", "eye_discharge",
        "seeing_halos", "dry_eyes", "eye_swelling",
    ],
    "Gynecological_Obstetric": [
        "pelvic_pain", "irregular_periods", "heavy_bleeding", "abdominal_pain",
        "vaginal_discharge", "bloating", "back_pain", "fatigue", "breast_pain",
        "nausea", "spotting", "painful_intercourse", "missed_period",
    ],
    "Pediatric": [
        "high_fever", "irritability", "poor_feeding", "rash", "vomiting", "diarrhea",
        "difficulty_breathing", "lethargy", "failure_to_gain_weight", "excessive_crying",
        "delayed_milestones",
    ],
    "Allergic_Immunological": [
        "sneezing", "itching", "skin_rash", "runny_nose", "watery_eyes", "hives",
        "swelling", "difficulty_breathing", "wheezing", "nasal_congestion",
        "frequent_infections", "throat_tightness",
    ],
    "Dental_Oral": [
        "tooth_pain", "gum_bleeding", "gum_swelling", "bad_breath", "mouth_sores",
        "difficulty_chewing", "tooth_sensitivity", "jaw_pain", "loose_teeth",
    ],
    "Nutritional": [
        "fatigue", "weight_loss", "weakness", "pale_skin", "hair_loss", "brittle_nails",
        "poor_growth", "loss_of_appetite", "muscle_wasting", "bone_pain", "swelling",
    ],
}

ALL_SYMPTOMS = sorted({s for pool in CATEGORY_SYMPTOMS.values() for s in pool})

# =======================================================================
# 2. DISEASE LIST BY CATEGORY (~500 total, real disease names)
# =======================================================================
CATEGORY_DISEASES = {
    "Respiratory": [
        "Common Cold", "Influenza", "Pneumonia", "Acute Bronchitis", "Chronic Bronchitis",
        "COPD", "Bronchial Asthma", "Tuberculosis", "Pleurisy", "Pulmonary Embolism",
        "Pulmonary Fibrosis", "Sarcoidosis", "Bronchiectasis", "Whooping Cough", "COVID-19",
        "Sinusitis", "Laryngitis", "Pharyngitis", "Tonsillitis", "Croup", "Emphysema",
        "Silicosis", "Asbestosis", "Lung Cancer", "Sleep Apnea", "Cystic Fibrosis",
        "Atelectasis", "Acute Respiratory Distress Syndrome", "Empyema", "Lung Abscess",
        "Byssinosis", "Farmer's Lung", "Aspiration Pneumonia", "Pneumothorax",
        "Legionnaires' Disease", "RSV Infection", "Bronchiolitis",
        "Hypersensitivity Pneumonitis", "Pulmonary Hypertension", "Chronic Sinusitis",
    ],
    "Cardiovascular": [
        "Hypertension", "Hypotension", "Coronary Artery Disease", "Myocardial Infarction",
        "Heart Failure", "Cardiac Arrhythmia", "Atrial Fibrillation", "Bradycardia",
        "Tachycardia", "Angina Pectoris", "Cardiomyopathy", "Myocarditis", "Pericarditis",
        "Endocarditis", "Mitral Valve Disease", "Aortic Valve Disease", "Deep Vein Thrombosis",
        "Varicose Veins", "Peripheral Artery Disease", "Atherosclerosis", "Aortic Aneurysm",
        "Ischemic Stroke", "Hemorrhagic Stroke", "Rheumatic Heart Disease",
        "Congenital Heart Disease", "Cardiogenic Shock", "Raynaud's Disease", "Vasculitis",
        "Hyperlipidemia", "Cardiac Tamponade", "Wolff-Parkinson-White Syndrome",
        "Long QT Syndrome", "Mitral Valve Prolapse", "Aortic Dissection",
        "Takotsubo Cardiomyopathy", "Restrictive Cardiomyopathy", "Dilated Cardiomyopathy",
        "Hypertrophic Cardiomyopathy", "Buerger's Disease", "Superficial Thrombophlebitis",
    ],
    "Gastrointestinal": [
        "GERD", "Peptic Ulcer Disease", "Gastritis", "Gastroenteritis", "Irritable Bowel Syndrome",
        "Crohn's Disease", "Ulcerative Colitis", "Appendicitis", "Diverticulitis", "Diverticulosis",
        "Chronic Constipation", "Hemorrhoids", "Anal Fissure", "Celiac Disease",
        "Lactose Intolerance", "Food Poisoning", "Cholecystitis", "Gallstones",
        "Acute Pancreatitis", "Chronic Pancreatitis", "Hepatitis A", "Hepatitis B", "Hepatitis C",
        "Cirrhosis", "Fatty Liver Disease", "Liver Failure", "Colorectal Cancer",
        "Stomach Cancer", "Esophageal Cancer", "Hiatal Hernia", "Intestinal Obstruction",
        "Peritonitis", "Malabsorption Syndrome", "Dysentery", "Esophagitis",
        "Barrett's Esophagus", "Achalasia", "Short Bowel Syndrome", "Intestinal Ischemia",
        "Volvulus", "Rectal Prolapse", "Anal Fistula", "Biliary Colic",
        "Primary Biliary Cholangitis", "Wilson's Disease",
    ],
    "Neurological": [
        "Migraine", "Tension Headache", "Cluster Headache", "Epilepsy", "Parkinson's Disease",
        "Alzheimer's Disease", "Vascular Dementia", "Multiple Sclerosis", "ALS", "Bell's Palsy",
        "Trigeminal Neuralgia", "Peripheral Neuropathy", "Sciatica", "Bacterial Meningitis",
        "Viral Meningitis", "Encephalitis", "Brain Tumor", "Concussion",
        "Traumatic Brain Injury", "Vertigo", "Tinnitus", "Narcolepsy", "Restless Leg Syndrome",
        "Guillain-Barre Syndrome", "Myasthenia Gravis", "Huntington's Disease", "Cerebral Palsy",
        "Hydrocephalus", "Transient Ischemic Attack", "Essential Tremor", "Insomnia",
        "Chronic Fatigue Syndrome", "Neuralgia", "Cervical Spondylosis",
        "Chronic Daily Headache", "Complex Regional Pain Syndrome", "Cerebral Aneurysm",
        "Subdural Hematoma", "Epidural Hematoma", "Autonomic Neuropathy",
        "Charcot-Marie-Tooth Disease", "Postherpetic Neuralgia", "Wernicke's Encephalopathy",
    ],
    "Musculoskeletal": [
        "Osteoarthritis", "Rheumatoid Arthritis", "Gout", "Osteoporosis", "Fibromyalgia",
        "Lupus", "Ankylosing Spondylitis", "Psoriatic Arthritis", "Bursitis", "Tendinitis",
        "Carpal Tunnel Syndrome", "Frozen Shoulder", "Herniated Disc", "Scoliosis",
        "Spinal Stenosis", "Sprains and Strains", "Bone Fracture", "Osteomyelitis",
        "Muscular Dystrophy", "Myositis", "Plantar Fasciitis", "Rotator Cuff Injury",
        "Whiplash", "TMJ Disorder", "Rickets", "Paget's Disease of Bone", "Sjogren's Syndrome",
        "Polymyalgia Rheumatica", "Costochondritis", "Scleroderma", "Kyphosis", "Lordosis",
        "Meniscus Tear", "ACL Tear", "Achilles Tendon Rupture", "Shin Splints",
        "Stress Fracture", "Dupuytren's Contracture", "Ganglion Cyst", "Spondylolisthesis",
    ],
    "Dermatological": [
        "Acne", "Atopic Dermatitis", "Psoriasis", "Vitiligo", "Rosacea", "Urticaria",
        "Contact Dermatitis", "Seborrheic Dermatitis", "Tinea (Ringworm)", "Scabies",
        "Head Lice", "Warts", "Cold Sores", "Shingles", "Chicken Pox", "Impetigo",
        "Cellulitis", "Skin Abscess", "Melanoma", "Basal Cell Carcinoma",
        "Squamous Cell Carcinoma", "Alopecia Areata", "Hyperhidrosis", "Keratosis Pilaris",
        "Lichen Planus", "Hidradenitis Suppurativa", "Pemphigus", "Actinic Keratosis",
        "Melasma", "Keloid", "Perioral Dermatitis", "Erythema Nodosum", "Ichthyosis",
        "Folliculitis", "Intertrigo", "Nummular Eczema", "Dyshidrotic Eczema", "Cutaneous Lupus",
    ],
    "Endocrine_Metabolic": [
        "Diabetes Type 1", "Diabetes Type 2", "Gestational Diabetes", "Hypothyroidism",
        "Hyperthyroidism", "Hashimoto's Thyroiditis", "Graves' Disease", "Cushing's Syndrome",
        "Addison's Disease", "Obesity", "Metabolic Syndrome", "PCOS", "Hypoglycemia",
        "Diabetic Ketoacidosis", "Goiter", "Thyroid Nodules", "Thyroid Cancer", "Acromegaly",
        "Diabetes Insipidus", "Hyperparathyroidism", "Hypoparathyroidism",
        "Pheochromocytoma", "Hyperaldosteronism", "Hypopituitarism", "Precocious Puberty",
    ],
    "Renal_Urological": [
        "Urinary Tract Infection", "Kidney Stones", "Chronic Kidney Disease",
        "Acute Kidney Injury", "Glomerulonephritis", "Nephrotic Syndrome",
        "Polycystic Kidney Disease", "Kidney Cancer", "Bladder Infection", "Bladder Cancer",
        "Interstitial Cystitis", "Overactive Bladder", "Urinary Incontinence", "Prostatitis",
        "Benign Prostatic Hyperplasia", "Prostate Cancer", "Testicular Torsion",
        "Epididymitis", "Hydrocele", "Varicocele", "Erectile Dysfunction", "Renal Colic",
        "Renal Artery Stenosis", "Horseshoe Kidney", "Priapism", "Phimosis",
    ],
    "Hematological_Oncological": [
        "Iron Deficiency Anemia", "Aplastic Anemia", "Sickle Cell Disease", "Thalassemia",
        "Hemophilia", "Leukemia", "Hodgkin's Lymphoma", "Non-Hodgkin's Lymphoma",
        "Multiple Myeloma", "Thrombocytopenia", "Polycythemia Vera", "Von Willebrand Disease",
        "Neutropenia", "Breast Cancer", "Pancreatic Cancer", "Ovarian Cancer",
        "Cervical Cancer", "Bone Cancer", "Metastatic Cancer", "Myelodysplastic Syndrome",
        "Chronic Myeloid Leukemia", "Chronic Lymphocytic Leukemia", "Acute Myeloid Leukemia",
        "Acute Lymphoblastic Leukemia", "Waldenstrom Macroglobulinemia", "Hemochromatosis",
        "Disseminated Intravascular Coagulation",
    ],
    "Mental_Health": [
        "Major Depressive Disorder", "Generalized Anxiety Disorder", "Panic Disorder",
        "Obsessive-Compulsive Disorder", "PTSD", "Bipolar Disorder", "Schizophrenia",
        "Social Anxiety Disorder", "Specific Phobia", "ADHD", "Autism Spectrum Disorder",
        "Anorexia Nervosa", "Bulimia Nervosa", "Binge Eating Disorder", "Postpartum Depression",
        "Seasonal Affective Disorder", "Adjustment Disorder", "Dissociative Disorder",
        "Borderline Personality Disorder", "Substance Use Disorder", "Alcohol Use Disorder",
        "Somatic Symptom Disorder", "Burnout Syndrome", "Body Dysmorphic Disorder",
        "Trichotillomania", "Kleptomania", "Pyromania", "Conduct Disorder",
    ],
    "Infectious": [
        "Malaria", "Dengue Fever", "Typhoid Fever", "Cholera", "Tetanus", "Diphtheria",
        "Rabies", "HIV/AIDS", "Syphilis", "Gonorrhea", "Chlamydia", "Genital Herpes",
        "HPV Infection", "Mumps", "Measles", "Rubella", "Zika Virus", "Chikungunya",
        "Yellow Fever", "Leptospirosis", "Lyme Disease", "Plague", "Anthrax", "Botulism",
        "Toxoplasmosis", "Giardiasis", "Amoebiasis", "Hookworm Infection", "Tapeworm Infection",
        "Scarlet Fever", "Infectious Mononucleosis", "Ebola Virus Disease",
        "Nipah Virus Infection", "Q Fever", "Brucellosis", "Listeriosis", "Trichinosis",
        "Schistosomiasis", "Filariasis",
    ],
    "ENT": [
        "Otitis Media", "Otitis Externa", "Sensorineural Hearing Loss", "Conductive Hearing Loss",
        "Meniere's Disease", "Nasal Polyps", "Deviated Septum", "Epistaxis",
        "Vocal Cord Nodules", "Adenoiditis", "Mastoiditis", "Eustachian Tube Dysfunction",
        "Throat Cancer", "Salivary Gland Stones", "Oral Thrush", "Laryngeal Cancer",
        "Cholesteatoma", "Perforated Eardrum",
    ],
    "Ophthalmological": [
        "Conjunctivitis", "Cataract", "Glaucoma", "Macular Degeneration", "Diabetic Retinopathy",
        "Dry Eye Syndrome", "Stye", "Blepharitis", "Uveitis", "Retinal Detachment",
        "Astigmatism", "Myopia", "Hyperopia", "Corneal Ulcer", "Keratitis", "Optic Neuritis",
        "Strabismus", "Amblyopia", "Ptosis", "Chalazion", "Scleritis", "Retinitis Pigmentosa",
    ],
    "Gynecological_Obstetric": [
        "Endometriosis", "Uterine Fibroids", "Ovarian Cysts", "Dysmenorrhea",
        "Premenstrual Syndrome", "Menopause", "Vaginitis", "Pelvic Inflammatory Disease",
        "Cervical Dysplasia", "Ectopic Pregnancy", "Preeclampsia", "Gestational Hypertension",
        "Placenta Previa", "Postpartum Hemorrhage", "Female Infertility", "Endometrial Cancer",
        "Uterine Prolapse", "Mastitis", "Fibrocystic Breast Disease",
        "Vulvovaginal Candidiasis", "Bacterial Vaginosis", "Hyperemesis Gravidarum",
        "Gestational Trophoblastic Disease",
    ],
    "Pediatric": [
        "Infantile Colic", "Diaper Rash", "Roseola", "Hand Foot and Mouth Disease",
        "Failure to Thrive", "Febrile Seizure", "Congenital Hypothyroidism", "Down Syndrome",
        "Intussusception", "Pyloric Stenosis", "Childhood Eczema", "Kawasaki Disease",
        "Reye's Syndrome", "Necrotizing Enterocolitis",
    ],
    "Allergic_Immunological": [
        "Allergic Rhinitis", "Food Allergy", "Drug Allergy", "Anaphylaxis", "Latex Allergy",
        "Insect Sting Allergy", "Chronic Urticaria", "Angioedema",
        "Common Variable Immunodeficiency", "Severe Combined Immunodeficiency",
        "Autoimmune Hepatitis", "Eosinophilic Esophagitis", "Serum Sickness",
        "Chronic Granulomatous Disease",
    ],
    "Dental_Oral": [
        "Dental Caries", "Gingivitis", "Periodontitis", "Tooth Abscess", "Halitosis",
        "Canker Sores", "Bruxism", "Oral Cancer", "Cleft Lip and Palate",
        "Impacted Wisdom Tooth",
    ],
    "Nutritional": [
        "Malnutrition", "Vitamin A Deficiency", "Scurvy", "Vitamin D Deficiency",
        "Vitamin B12 Deficiency", "Kwashiorkor", "Marasmus", "Iodine Deficiency",
        "Zinc Deficiency", "Iron Deficiency", "Pellagra", "Beriberi",
    ],
}

CATEGORY_META = {
    "Respiratory": ("Pulmonologist", "Medium"),
    "Cardiovascular": ("Cardiologist", "High"),
    "Gastrointestinal": ("Gastroenterologist", "Medium"),
    "Neurological": ("Neurologist", "Medium"),
    "Musculoskeletal": ("Rheumatologist / Orthopedist", "Low"),
    "Dermatological": ("Dermatologist", "Low"),
    "Endocrine_Metabolic": ("Endocrinologist", "Medium"),
    "Renal_Urological": ("Urologist / Nephrologist", "Medium"),
    "Hematological_Oncological": ("Oncologist / Hematologist", "High"),
    "Mental_Health": ("Psychiatrist / Psychologist", "Medium"),
    "Infectious": ("Infectious Disease Specialist", "Medium"),
    "ENT": ("ENT Specialist", "Low"),
    "Ophthalmological": ("Ophthalmologist", "Low"),
    "Gynecological_Obstetric": ("Gynecologist", "Medium"),
    "Pediatric": ("Pediatrician", "Medium"),
    "Allergic_Immunological": ("Allergist / Immunologist", "Medium"),
    "Dental_Oral": ("Dentist", "Low"),
    "Nutritional": ("General Physician / Dietitian", "Low"),
}

# =======================================================================
# 3. Build the final (deduplicated) disease -> (category, symptoms) map
# =======================================================================
DISEASE_SYMPTOMS = {}
DISEASE_CATEGORY = {}

for category, disease_names in CATEGORY_DISEASES.items():
    pool = CATEGORY_SYMPTOMS[category]
    for disease in disease_names:
        if disease in DISEASE_SYMPTOMS:
            continue
        rng = random.Random(hash(disease) % (2**32))
        k = min(len(pool), rng.randint(4, 6))
        core_symptoms = rng.sample(pool, k)
        DISEASE_SYMPTOMS[disease] = core_symptoms
        DISEASE_CATEGORY[disease] = category

DISEASES = list(DISEASE_SYMPTOMS.keys())
print(f"Total diseases: {len(DISEASES)}")
print(f"Total unique symptoms: {len(ALL_SYMPTOMS)}")

# =======================================================================
# 4. Generate patient records
# =======================================================================
RECORDS_PER_DISEASE = 25

rows = []

for disease, core_symptoms in DISEASE_SYMPTOMS.items():
    category = DISEASE_CATEGORY[disease]
    category_pool = CATEGORY_SYMPTOMS[category]

    for _ in range(RECORDS_PER_DISEASE):
        present_symptoms = set(core_symptoms)

        num_to_drop = random.randint(0, min(2, max(0, len(core_symptoms) - 2)))
        if num_to_drop > 0:
            drop = random.sample(core_symptoms, num_to_drop)
            present_symptoms -= set(drop)

        if random.random() < 0.35:
            present_symptoms.add(random.choice(category_pool))

        if random.random() < 0.15:
            present_symptoms.add(random.choice(ALL_SYMPTOMS))

        row = {symptom: (1 if symptom in present_symptoms else 0) for symptom in ALL_SYMPTOMS}

        row["Age"] = int(np.clip(np.random.normal(40, 18), 1, 95))
        row["Gender"] = random.choice(["Male", "Female"])
        row["Disease"] = disease
        rows.append(row)

# =======================================================================
# 5. Build DataFrame, shuffle, and save
# =======================================================================
df = pd.DataFrame(rows)
column_order = ["Age", "Gender"] + ALL_SYMPTOMS + ["Disease"]
df = df[column_order]
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

output_path = "disease_symptom_dataset.csv"
df.to_csv(output_path, index=False)

print(f"\nDataset saved to: {output_path}")
print(f"Shape: {df.shape}")
