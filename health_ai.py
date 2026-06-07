"""
Convofy AI Health Assistant — Response Engine
Comprehensive rule-based health knowledge system with emergency detection.
"""

EMERGENCY_KEYWORDS = [
    'chest pain', 'heart attack', "can't breathe", 'cannot breathe',
    'difficulty breathing', 'stroke', 'unconscious', 'fainted', 'passed out',
    'severe bleeding', 'suicide', 'suicidal', 'kill myself', 'overdose',
    'poisoning', 'seizure', 'convulsion', 'anaphylaxis', 'severe allergic',
    'coughing blood', 'vomiting blood', 'severe head injury', 'unresponsive'
]

HEALTH_KB = [
    {
        'keys': ['hello', 'hi ', 'hey', 'good morning', 'good evening', 'good afternoon', 'how are you', 'what can you do', 'help me', 'start'],
        'response': """**Hello! I'm Convofy AI Health Assistant** 🏥

I'm here to provide health information, symptom guidance, and wellness advice 24/7.

**I can help you with:**
- 🩺 Symptom assessment & what they might mean
- 💊 General medication & treatment information
- 🥗 Diet, nutrition & lifestyle tips
- 🧠 Mental health & wellness guidance
- 🚨 Recognising when to seek emergency care
- 📅 Guidance on booking a doctor

**Please note:** I provide general health information, not a medical diagnosis. Always consult a licensed doctor for medical decisions.

What health concern can I help you with today?""",
        'type': 'info'
    },
    {
        'keys': ['fever', 'high temperature', 'temperature', '38', '39', '40', 'chills', 'shivering'],
        'response': """**Fever Assessment** 🌡️

A fever is a body temperature **above 38°C (100.4°F)**.

**Common Causes:**
- Viral infections (flu, COVID-19, cold)
- Bacterial infections (UTI, strep throat)
- Inflammatory conditions

**What to Do:**
✅ Rest and sleep
✅ Drink plenty of fluids (water, soups, herbal teas)
✅ Take paracetamol or ibuprofen for temperature reduction
✅ Wear light, breathable clothing
✅ Apply a cool, damp cloth to forehead

**⚠️ See a Doctor Urgently if:**
- Temperature exceeds **40°C (104°F)**
- Fever persists more than **3 days**
- Accompanied by rash, stiff neck, severe headache, or confusion
- Infant under **3 months** with any fever
- You're immunocompromised

Would you like to **book an appointment** with a doctor?""",
        'type': 'warning'
    },
    {
        'keys': ['headache', 'head pain', 'migraine', 'head ache', 'forehead pain', 'temple pain'],
        'response': """**Headache & Migraine Guidance** 🧠

**Types of Headaches:**
- **Tension headache** — pressure around forehead, temples (most common)
- **Migraine** — throbbing pain, often with nausea, light sensitivity
- **Cluster headache** — intense pain around one eye
- **Sinus headache** — pressure in face/forehead

**Immediate Relief:**
✅ Rest in a quiet, dark room
✅ Stay hydrated — dehydration is a top cause
✅ Apply a warm or cold compress to head/neck
✅ Paracetamol or ibuprofen (as directed)
✅ Avoid screens and bright light during migraine

**Lifestyle Prevention:**
- Maintain regular sleep schedule
- Stay hydrated (2L+ water daily)
- Reduce stress with relaxation techniques
- Limit caffeine and alcohol

**🚨 Seek Emergency Care if:**
- Sudden, "worst headache of your life"
- Headache with fever and stiff neck
- Headache after head injury
- Progressive worsening over days
- Headache with vision changes, weakness, or confusion""",
        'type': 'info'
    },
    {
        'keys': ['cough', 'cold', 'runny nose', 'sneezing', 'sore throat', 'flu', 'influenza', 'blocked nose', 'stuffy nose', 'congestion'],
        'response': """**Cold, Flu & Respiratory Infections** 🤧

**Cold vs Flu:**
| Symptom | Cold | Flu |
|---------|------|-----|
| Onset | Gradual | Sudden |
| Fever | Rare | Common |
| Body aches | Mild | Severe |
| Fatigue | Mild | Severe |

**Home Treatment:**
✅ Rest — your immune system needs energy
✅ Stay warm and hydrated (8-10 glasses/day)
✅ Honey + lemon in warm water for sore throat
✅ Steam inhalation for nasal congestion
✅ Saline nasal drops for congestion
✅ Paracetamol for fever and body aches
✅ Throat lozenges for sore throat

**Antibiotic Note:** Antibiotics do NOT treat viruses. Never self-prescribe antibiotics.

**See a Doctor if:**
- Symptoms worsen after 7-10 days
- High fever (>39°C) for more than 3 days
- Difficulty breathing or swallowing
- Ear pain or sinus pain
- Coughing up coloured mucus/blood""",
        'type': 'info'
    },
    {
        'keys': ['stomach', 'stomach pain', 'abdominal pain', 'belly', 'cramps', 'stomach cramp', 'abdominal cramp', 'gut pain'],
        'response': """**Stomach & Abdominal Pain** 🫁

**Common Causes:**
- Gas and bloating
- Indigestion / acid reflux
- Gastroenteritis (stomach bug)
- Constipation
- Irritable Bowel Syndrome (IBS)
- Muscle strain
- Period cramps

**Home Remedies:**
✅ Apply a warm compress to abdomen
✅ Peppermint tea for gas and bloating
✅ Ginger tea for nausea and indigestion
✅ BRAT diet (Banana, Rice, Applesauce, Toast) if upset stomach
✅ Avoid fatty, spicy, or greasy foods
✅ Small, frequent meals instead of large ones

**⚠️ See a Doctor if Pain Is:**
- Severe or sudden onset
- Located in lower right (possible appendix)
- Accompanied by fever and vomiting
- Persistent for more than 2-3 days
- Associated with blood in stool

**🚨 Emergency if:** Rigid/board-like abdomen, severe pain with vomiting""",
        'type': 'info'
    },
    {
        'keys': ['nausea', 'vomiting', 'throwing up', 'sick to stomach', 'feeling sick', 'queasy'],
        'response': """**Nausea & Vomiting Management** 🤢

**Common Triggers:**
- Food poisoning or stomach bugs
- Motion sickness
- Pregnancy (morning sickness)
- Medications
- Anxiety or stress
- Migraines

**Relief Strategies:**
✅ Sip small amounts of clear fluids frequently (water, diluted juice, clear broth)
✅ Ginger — ginger tea, ginger ale, or ginger capsules
✅ Eat bland, easy-to-digest foods: crackers, toast, rice
✅ Avoid strong odours, fatty or spicy foods
✅ Rest in a semi-upright position
✅ Cold compress on forehead
✅ Fresh air can help

**Rehydration:**
If vomiting, replace lost electrolytes with oral rehydration solution (ORS) or coconut water.

**⚠️ See a Doctor if:**
- Vomiting blood or dark material ("coffee grounds")
- Vomiting for more than 24 hours
- Signs of dehydration: dark urine, dizziness, dry mouth
- Associated with severe headache or abdominal pain
- Fever above 38.5°C""",
        'type': 'info'
    },
    {
        'keys': ['diarrhea', 'diarrhoea', 'loose stool', 'loose motion', 'watery stool', 'frequent toilet'],
        'response': """**Diarrhoea Management** 💧

**Most Common Cause:** Viral/bacterial gastroenteritis — usually self-limiting (3-5 days).

**Key Priority — Stay Hydrated:**
✅ Oral Rehydration Solution (ORS) — most important
✅ Drink clear fluids: water, diluted juice, clear soups
✅ Coconut water for electrolytes
✅ Avoid dairy, caffeine, alcohol, fatty or spicy foods

**Diet (BRAT approach):**
- Bananas, Rice, Applesauce, Toast
- Boiled vegetables, plain crackers
- Gradually return to normal diet

**Probiotics:** Yogurt with live cultures can help restore gut bacteria.

**Avoid:** Loperamide (Imodium) if you have fever or blood in stool — it can trap infection.

**⚠️ See a Doctor if:**
- Blood or mucus in stool
- Fever above 38.5°C
- Severe abdominal pain
- Signs of dehydration (especially in children/elderly)
- Lasts more than 3 days in adults, 24 hours in young children""",
        'type': 'info'
    },
    {
        'keys': ['constipation', 'can\'t poop', 'cannot poop', 'not passing stool', 'hard stool', 'bowel', 'no bowel movement'],
        'response': """**Constipation Relief** 🌿

**What is it?** Fewer than 3 bowel movements per week, or hard/painful stools.

**Immediate Relief:**
✅ Increase water intake (aim 2-3L daily)
✅ Warm prune juice or warm water with lemon in the morning
✅ Light exercise — even a 20-minute walk helps
✅ Glycerin suppository (available OTC) for short-term relief

**Dietary Changes:**
✅ High-fibre foods: whole grains, legumes, fruits, vegetables
✅ Flaxseeds, chia seeds, psyllium husk
✅ Limit processed foods, dairy, and red meat

**Lifestyle Tips:**
- Establish a regular toilet routine (same time daily)
- Don't ignore the urge to go
- Elevate feet slightly (squatting position) on toilet

**When to See a Doctor:**
- Constipation lasting more than 3 weeks
- Blood in stool
- Unexplained weight loss
- Severe abdominal pain
- Alternating with diarrhoea (could be IBS)""",
        'type': 'info'
    },
    {
        'keys': ['back pain', 'backache', 'lower back', 'upper back', 'spine', 'lumbar', 'sciatica'],
        'response': """**Back Pain Management** 🦴

**Most Common Type:** Musculoskeletal (muscle strain, ligament sprain) — usually resolves within 4-6 weeks.

**Immediate Relief:**
✅ Apply ice for first 48 hours (20 min on, 20 min off)
✅ Switch to heat after 48 hours for muscle relaxation
✅ Paracetamol or NSAIDs (ibuprofen) as directed
✅ Stay gently active — complete bed rest makes it worse
✅ Gentle stretching and walking

**Posture Tips:**
- Sit with lumbar support, feet flat on floor
- Computer screen at eye level
- Sleep on your side with a pillow between knees
- Lift heavy objects by bending knees, not your back

**Exercises That Help:**
- Cat-cow stretch
- Child's pose
- Knee-to-chest stretch
- Pelvic tilts

**🚨 See a Doctor Urgently if:**
- Pain shoots down leg (sciatica nerve compression)
- Numbness or tingling in legs/feet
- Bladder or bowel changes
- Back pain after injury or fall
- Unexplained weight loss with back pain""",
        'type': 'info'
    },
    {
        'keys': ['joint pain', 'knee pain', 'arthritis', 'swollen joint', 'stiff joint', 'hip pain', 'shoulder pain', 'wrist pain', 'ankle pain'],
        'response': """**Joint Pain & Arthritis Guidance** 🦵

**Common Causes:**
- **Osteoarthritis** — wear and tear (older adults)
- **Rheumatoid arthritis** — autoimmune (any age)
- **Gout** — uric acid crystals (often big toe)
- **Injury/sprain** — acute onset
- **Bursitis/tendinitis** — inflammation

**Management:**
✅ RICE method for acute injuries: Rest, Ice, Compression, Elevation
✅ Anti-inflammatory: ibuprofen, naproxen (with food)
✅ Topical gels: diclofenac gel for localized pain
✅ Warm bath/compress for stiffness (especially morning)
✅ Gentle range-of-motion exercises
✅ Swimming or cycling — low-impact movement helps

**Diet for Joint Health:**
- Omega-3 fatty acids (oily fish, flaxseed, walnuts)
- Turmeric (anti-inflammatory)
- Vitamin D and calcium for bone health
- Maintain healthy weight — every kg lost = 4kg less pressure on knees

**When to See a Doctor:**
- Sudden, severe joint pain
- Joint hot, red, and very swollen (possible infection or gout)
- Significant limitation in movement
- Symptoms lasting more than 6 weeks""",
        'type': 'info'
    },
    {
        'keys': ['fatigue', 'tired', 'exhausted', 'no energy', 'weakness', 'lethargic', 'always sleepy', 'low energy'],
        'response': """**Fatigue & Low Energy Assessment** ⚡

**Common Causes:**
- Poor sleep quality or quantity
- Anaemia (iron, B12, folate deficiency)
- Thyroid issues (hypothyroidism)
- Depression or anxiety
- Diabetes
- Dehydration
- Sedentary lifestyle

**Energy Boosters:**
✅ Prioritise 7-9 hours of quality sleep
✅ Stay well-hydrated (fatigue is often dehydration)
✅ Regular moderate exercise — even 20-30 min/day boosts energy
✅ Balanced diet with iron-rich foods (spinach, lentils, lean red meat)
✅ Vitamin B12 sources (eggs, dairy, meat, fortified foods)
✅ Limit sugar and processed carbs (cause energy crashes)
✅ Short naps (20 min) if needed

**Lifestyle Factors:**
- Reduce screen time before bed
- Limit alcohol (disrupts sleep)
- Manage stress through mindfulness or exercise

**⚠️ See a Doctor if:**
- Fatigue persists despite good sleep and lifestyle changes
- Accompanied by weight loss, night sweats, or fever
- Difficulty performing daily activities
- Sudden onset severe fatigue
- Feeling low or hopeless alongside fatigue (depression screening)""",
        'type': 'info'
    },
    {
        'keys': ['sleep', 'insomnia', 'can\'t sleep', 'cannot sleep', 'trouble sleeping', 'sleepless', 'waking up', 'nightmares'],
        'response': """**Sleep Problems & Insomnia** 😴

**Good Sleep Hygiene (Most Effective Long-Term Fix):**
✅ Keep a consistent sleep schedule (same time every day, including weekends)
✅ Create a cool, dark, quiet sleep environment
✅ No screens (phone, TV, tablet) for at least 1 hour before bed — blue light suppresses melatonin
✅ Avoid caffeine after 2pm
✅ Avoid alcohol — it disrupts sleep architecture
✅ Regular exercise, but not within 3 hours of bedtime

**Wind-Down Routine:**
- Warm bath or shower before bed
- Reading (physical book, not screen)
- Meditation, deep breathing, or gentle yoga
- Chamomile tea, warm milk

**Cognitive Techniques:**
- If you can't sleep after 20 min, get up and do something calm until sleepy
- Avoid watching the clock
- Progressive muscle relaxation
- 4-7-8 breathing: inhale 4s, hold 7s, exhale 8s

**When to Seek Help:**
- Insomnia lasting more than 3 weeks
- Snoring loudly + gasping (possible sleep apnoea)
- Restless legs at night
- Excessive daytime sleepiness despite adequate night sleep
- Mood significantly affected by poor sleep""",
        'type': 'info'
    },
    {
        'keys': ['anxiety', 'anxious', 'panic attack', 'panic', 'nervous', 'worry', 'worried', 'stress', 'stressed', 'overwhelmed', 'tension'],
        'response': """**Anxiety & Stress Management** 🧘

**You're Not Alone:** Anxiety disorders affect 1 in 4 people. It's treatable.

**Immediate Calming Techniques:**

**Box Breathing (works in minutes):**
1. Inhale slowly for 4 counts
2. Hold for 4 counts
3. Exhale for 4 counts
4. Hold for 4 counts
5. Repeat 4 times

**5-4-3-2-1 Grounding:**
Name 5 things you see, 4 you hear, 3 you can touch, 2 you smell, 1 you taste.

**Daily Management:**
✅ Regular aerobic exercise (30 min, 5x/week) — as effective as medication for mild anxiety
✅ Limit caffeine (amplifies anxiety)
✅ Regular meals — blood sugar dips worsen anxiety
✅ Mindfulness meditation (apps: Calm, Headspace, Insight Timer)
✅ Talk to someone you trust
✅ Journaling — write out worries to "offload" your mind

**When to Seek Professional Help:**
- Anxiety significantly interferes with work, relationships, or daily activities
- Panic attacks that feel like heart attacks
- Avoiding situations due to fear
- Using alcohol to cope
- Feeling anxious most days for more than 2 weeks

**Options:** Therapy (CBT), medication, or both. Both are effective.""",
        'type': 'info'
    },
    {
        'keys': ['depression', 'depressed', 'sad', 'hopeless', 'worthless', 'empty', 'crying', 'no motivation', 'not enjoying'],
        'response': """**Depression & Low Mood Support** 💙

**What You're Feeling Is Valid — And Help Is Available.**

Depression is a medical condition, not a character flaw or weakness. It responds well to treatment.

**Signs of Depression:**
- Persistent low mood or emptiness for 2+ weeks
- Loss of interest in things you used to enjoy
- Changes in sleep, appetite, or weight
- Difficulty concentrating
- Feelings of worthlessness or excessive guilt
- Fatigue and low energy

**What Can Help:**
✅ Physical activity — even a short walk releases endorphins
✅ Social connection — reach out to someone you trust today
✅ Structure your day with small, achievable tasks
✅ Sunlight exposure (15-30 min daily)
✅ Limit alcohol — it's a depressant
✅ Write down 3 things you're grateful for each day

**Professional Treatment Options:**
- **Psychotherapy (CBT)** — often the first-line treatment
- **Antidepressants** — effective, non-addictive, usually needed for 6+ months
- **Combination** — therapy + medication most effective for moderate-severe depression

**Please Speak to a Doctor** — this is a medical condition with proven treatments.

🆘 **If you're having thoughts of harming yourself:** Contact emergency services or a crisis helpline immediately. You matter.""",
        'type': 'warning'
    },
    {
        'keys': ['diabetes', 'blood sugar', 'glucose', 'insulin', 'type 1', 'type 2', 'diabetic', 'hyperglycemia', 'hypoglycemia', 'low sugar', 'high sugar'],
        'response': """**Diabetes Management** 💉

**Types:**
- **Type 1** — Autoimmune, requires insulin. Onset usually in childhood/youth.
- **Type 2** — Lifestyle-related insulin resistance. Most common (90%+ of cases).
- **Pre-diabetes** — Blood sugar elevated but not yet diabetic. Fully reversible.

**Blood Sugar Targets (general):**
- Fasting: 4.0–7.0 mmol/L (72–126 mg/dL)
- 2 hours after meals: <10.0 mmol/L (<180 mg/dL)
- HbA1c (3-month average): <7%

**Lifestyle Management:**
✅ Low-glycaemic diet: whole grains, legumes, leafy vegetables, lean protein
✅ Limit refined carbs, sugary drinks, white bread, pastries
✅ Regular exercise: 150 min/week of moderate activity
✅ Healthy weight management
✅ Regular blood glucose monitoring
✅ Annual eye, foot, and kidney checks

**Warning Signs — Low Blood Sugar (Hypoglycaemia):**
Shakiness, sweating, confusion, rapid heartbeat
→ **Take 15g fast-acting carbs immediately** (juice, glucose tablets, 3 sweets)

**Warning Signs — High Blood Sugar:**
Frequent urination, extreme thirst, blurry vision
→ Check glucose, follow your medication plan, contact doctor if persistent

Regular medical review is essential for diabetes management.""",
        'type': 'info'
    },
    {
        'keys': ['blood pressure', 'hypertension', 'high bp', 'low bp', 'hypotension', 'systolic', 'diastolic', 'mmhg'],
        'response': """**Blood Pressure Guide** ❤️

**Blood Pressure Categories (mmHg):**
| Category | Systolic | Diastolic |
|----------|----------|-----------|
| Normal | <120 | <80 |
| Elevated | 120-129 | <80 |
| Stage 1 Hypertension | 130-139 | 80-89 |
| Stage 2 Hypertension | ≥140 | ≥90 |
| Hypertensive Crisis | >180 | >120 |

**Lowering High Blood Pressure (Lifestyle):**
✅ DASH diet: fruits, vegetables, whole grains, low-fat dairy, reduce sodium
✅ Limit salt to <5g/day (1 teaspoon)
✅ Regular aerobic exercise (30 min, most days)
✅ Maintain healthy weight
✅ Limit alcohol
✅ No smoking
✅ Stress management (yoga, meditation)
✅ Quality sleep (7-9 hours)

**For Low Blood Pressure:**
✅ Increase salt and fluid intake
✅ Rise slowly from sitting/lying
✅ Avoid standing for long periods
✅ Wear compression stockings
✅ Small, frequent meals

**🚨 Hypertensive Crisis (>180/120):**
Seek emergency care immediately if accompanied by headache, chest pain, shortness of breath, or vision changes.""",
        'type': 'info'
    },
    {
        'keys': ['allergy', 'allergic', 'rash', 'hives', 'itching', 'itchy', 'eczema', 'hay fever', 'pollen', 'dust', 'pet allergy'],
        'response': """**Allergies & Skin Reactions** 🌿

**Types:**
- **Seasonal (hay fever)** — pollen, grass, mold
- **Food allergies** — nuts, shellfish, dairy, eggs, wheat
- **Skin allergies** — contact dermatitis, eczema
- **Pet allergies** — animal dander
- **Drug allergies** — medications

**Hay Fever Relief:**
✅ Antihistamines (loratadine, cetirizine) — non-drowsy options
✅ Nasal steroid sprays (most effective for nasal symptoms)
✅ Eye drops for allergic conjunctivitis
✅ Keep windows closed during high pollen
✅ Shower after being outdoors
✅ Sunglasses outdoors

**Skin Allergy (Contact Dermatitis/Eczema):**
✅ Identify and avoid triggers
✅ Fragrance-free moisturisers (apply generously after bathing)
✅ Hydrocortisone 1% cream for inflammation (short-term)
✅ Cool compress for itching
✅ Antihistamines for itch relief
✅ Avoid hot water (use lukewarm)

**🚨 Anaphylaxis — Emergency:**
Difficulty breathing, throat swelling, sudden drop in blood pressure after exposure to allergen.
**Call 999/112/911 immediately. Use EpiPen if prescribed.**""",
        'type': 'warning'
    },
    {
        'keys': ['asthma', 'breathing difficulty', 'wheeze', 'wheezing', 'inhaler', 'shortness of breath', 'breathless'],
        'response': """**Asthma & Breathing Difficulties** 🫁

**Asthma Triggers (Common):**
- Exercise, cold air
- Respiratory infections
- Allergens (dust, pollen, pet dander)
- Smoke, strong smells, pollution
- Emotional stress
- Certain medications (aspirin, NSAIDs in some people)

**Asthma Attack — What to Do:**
1. Sit upright, stay calm
2. Use reliever inhaler (usually blue — salbutamol) — 1 puff every 30-60 seconds, up to 10 puffs
3. If no improvement after 10 puffs: **call emergency services**
4. Repeat reliever inhaler while waiting

**Daily Management:**
✅ Take preventer inhaler (steroid) every day as prescribed — even when feeling well
✅ Check peak flow meter regularly if prescribed
✅ Keep reliever inhaler with you at all times
✅ Annual asthma review with doctor
✅ Flu vaccination annually

**Inhaler Technique:**
- Breathe out fully before inhaling
- Inhale slowly and deeply
- Hold breath for 10 seconds
- Use spacer if available (improves delivery)

**Poorly controlled asthma:** Waking at night, using reliever more than 3x/week → Doctor review needed.""",
        'type': 'warning'
    },
    {
        'keys': ['skin', 'acne', 'pimple', 'blackhead', 'skincare', 'oily skin', 'dry skin', 'wrinkle', 'sunburn'],
        'response': """**Skin Health & Acne Care** ✨

**Acne Management:**
✅ Wash face twice daily with gentle, non-comedogenic cleanser
✅ Topical benzoyl peroxide (2.5-5%) for bacteria
✅ Salicylic acid for blackheads and whiteheads
✅ Don't squeeze or pop pimples — increases scarring
✅ Change pillowcases regularly
✅ Avoid touching face

**Diet & Acne:**
- Limit high-glycaemic foods (white bread, sugary drinks) — may worsen acne
- Dairy may worsen acne in some people
- Stay hydrated

**General Skincare Routine:**
1. **Cleanse** — gentle, pH-balanced
2. **Treat** — serum (vitamin C, retinol, niacinamide)
3. **Moisturise** — even oily skin needs it
4. **Protect** — SPF 30+ every morning (most important anti-ageing step)

**Sunburn Relief:**
✅ Cool shower (not cold)
✅ Aloe vera gel
✅ Moisturiser without petrolatum
✅ Ibuprofen for inflammation
✅ Stay hydrated

**See a Dermatologist if:**
- Severe acne causing scarring
- Suspicious moles (ABCDE: Asymmetry, Border, Colour, Diameter, Evolution)
- Persistent rashes or skin changes""",
        'type': 'info'
    },
    {
        'keys': ['eye', 'vision', 'blurry', 'eye pain', 'red eye', 'eye infection', 'conjunctivitis', 'pink eye', 'dry eyes'],
        'response': """**Eye Health & Common Conditions** 👁️

**Conjunctivitis (Pink Eye):**
- **Viral** — red, watery, often with cold; resolves in 1-2 weeks; cool compress
- **Bacterial** — sticky yellow/green discharge; antibiotic drops usually needed
- **Allergic** — itchy, both eyes; antihistamine eye drops

**Eye Hygiene:**
✅ Don't rub your eyes
✅ Remove contact lenses when eyes are infected
✅ Clean contact lenses properly, replace as scheduled
✅ Wash hands before touching eyes

**Digital Eye Strain (Screen Fatigue):**
- **20-20-20 rule:** Every 20 minutes, look at something 20 feet away for 20 seconds
- Blink consciously — screen use reduces blink rate
- Blue light glasses or screen filter
- Proper screen distance (arm's length)
- Lubricating eye drops for dryness

**Protective Habits:**
✅ Annual eye test (every 2 years if no issues)
✅ Sunglasses with UV protection outdoors
✅ Safety glasses for hazardous work

**🚨 See an Eye Doctor Urgently if:**
- Sudden vision loss or change
- Curtain/shadow across vision
- Seeing flashes of light or new floaters
- Eye injury
- Sudden eye pain""",
        'type': 'info'
    },
    {
        'keys': ['diet', 'nutrition', 'healthy eating', 'what to eat', 'food', 'weight loss', 'weight gain', 'bmi', 'calories', 'vitamins'],
        'response': """**Nutrition & Healthy Diet Guide** 🥗

**Balanced Plate Model:**
- **1/2 plate** — Non-starchy vegetables (leafy greens, broccoli, peppers)
- **1/4 plate** — Lean protein (chicken, fish, legumes, tofu, eggs)
- **1/4 plate** — Complex carbs (brown rice, quinoa, sweet potato, whole wheat)
- Plus healthy fats: avocado, olive oil, nuts, seeds

**Essential Nutrients:**
- **Protein:** 0.8-1.6g per kg body weight daily
- **Fibre:** 25-38g daily (most people get far too little)
- **Water:** 2-3L daily (more if active or in heat)
- **Iron:** Spinach, lentils, red meat, fortified cereals
- **Vitamin D:** Sunlight, oily fish, fortified foods
- **Calcium:** Dairy, leafy greens, fortified plant milks
- **Omega-3:** Salmon, mackerel, sardines, walnuts, flaxseed

**For Weight Loss (Sustainable):**
✅ 500 calorie deficit per day = ~0.5kg/week loss
✅ Focus on volume eating (fill up on vegetables)
✅ Protein at every meal (increases satiety)
✅ Limit ultra-processed foods and liquid calories
✅ No need to cut entire food groups

**For Weight Gain:**
✅ Calorie surplus of 300-500/day
✅ Strength training to build muscle
✅ Protein-rich diet""",
        'type': 'info'
    },
    {
        'keys': ['exercise', 'workout', 'fitness', 'gym', 'physical activity', 'sedentary', 'running', 'walking', 'yoga'],
        'response': """**Exercise & Physical Fitness** 🏃

**WHO Recommended Activity (Adults):**
- **150-300 minutes/week** of moderate aerobic activity (brisk walking, cycling, swimming)
- OR **75-150 minutes/week** of vigorous activity (running, HIIT)
- Plus **2+ days/week** muscle-strengthening exercises

**Benefits of Regular Exercise:**
- Reduces risk of heart disease, stroke, diabetes by up to 50%
- Improves mood (releases endorphins — natural antidepressant)
- Better sleep quality
- Boosts immune function
- Maintains healthy weight
- Strengthens bones and muscles

**Getting Started (Beginner):**
✅ Start with 10-15 minutes daily walks
✅ Gradually increase duration and intensity
✅ Find activities you enjoy — consistency matters most
✅ Exercise with a friend for accountability
✅ Mix cardio, strength, and flexibility training

**Stretching & Recovery:**
- Always warm up before and cool down after exercise
- Stretch major muscle groups for 20-30 seconds each
- Allow muscle groups 48 hours recovery between strength sessions
- Stay hydrated (drink before, during, and after)

**Safe Exercise Rules:**
- Stop if you feel chest pain, dizziness, or severe shortness of breath
- Progress gradually — the 10% rule (don't increase volume by >10%/week)
- Listen to your body""",
        'type': 'info'
    },
    {
        'keys': ['mental health', 'mental', 'therapy', 'counselling', 'psychologist', 'psychiatrist', 'wellbeing', 'self care'],
        'response': """**Mental Health & Wellbeing** 🧠

**Mental health is health.** Just like physical health, it requires attention and care.

**Pillars of Mental Wellbeing (PERMA):**
- **P**ositive emotions — gratitude, savoring small moments
- **E**ngagement — hobbies, flow activities
- **R**elationships — meaningful social connections
- **M**eaning — purpose, contributing to something larger
- **A**ccomplishment — achievable goals

**Daily Practices:**
✅ 10 minutes of mindfulness or meditation
✅ Physical exercise (most evidence-based mental health booster)
✅ Quality sleep (8 hours)
✅ Limit alcohol and drugs (short-term relief, long-term worsening)
✅ Social connection — even brief positive interactions help
✅ Nature exposure — even 20 min in green spaces improves mood
✅ Journaling — process thoughts and feelings

**Types of Mental Health Support:**
- **Self-help** — apps, books, exercise, diet
- **Peer support** — support groups
- **Therapy** — CBT, psychodynamic, EMDR
- **Medication** — antidepressants, anti-anxiety (prescribed by doctor)
- **Crisis support** — crisis lines, emergency services

**Remember:** Seeking help is a sign of strength, not weakness. You wouldn't ignore a broken leg — don't ignore your mental health.""",
        'type': 'info'
    },
    {
        'keys': ['covid', 'covid-19', 'coronavirus', 'corona', 'omicron', 'positive test', 'pcr', 'rapid test', 'isolation'],
        'response': """**COVID-19 Guidance** 🦠

**If You Test Positive:**
✅ Isolate to protect others (follow your local health guidelines)
✅ Rest and stay well hydrated
✅ Paracetamol or ibuprofen for fever/pain
✅ Monitor symptoms daily
✅ Use a pulse oximeter if available (normal: 95-100%)

**Seek Urgent Care if:**
- Oxygen levels drop below **94%**
- Difficulty breathing at rest
- Persistent chest pain or pressure
- Confusion or inability to wake properly
- Bluish lips or face

**Most People (vaccinated or healthy):**
Experience mild cold/flu-like illness lasting 5-10 days.

**High-Risk Groups** (need monitoring/antivirals):
- Age 60+
- Immunocompromised
- Diabetes, heart disease, severe obesity
- Pregnancy

**Long COVID:**
Symptoms (fatigue, brain fog, breathlessness) lasting 12+ weeks after infection. See your doctor for assessment and management.

**Prevention:**
✅ Stay up to date with vaccinations
✅ Good hand hygiene
✅ Ventilate indoor spaces
✅ Wear a mask in high-risk situations (crowded, enclosed)""",
        'type': 'warning'
    },
    {
        'keys': ['period', 'menstrual', 'menstruation', 'pms', 'cramps period', 'irregular period', 'women health', "women's health"],
        'response': """**Menstrual Health & Women's Wellness** 🌸

**Menstrual Cycle Facts:**
- Normal cycle: 21-35 days
- Normal flow: 3-7 days
- Some variation is normal

**Period Pain (Dysmenorrhoea) Relief:**
✅ Ibuprofen (most effective — take with food before pain peaks)
✅ Paracetamol
✅ Heat pad on lower abdomen
✅ Light exercise — yoga, walking
✅ Magnesium and vitamin D may help
✅ Omega-3 fatty acids

**PMS (Premenstrual Syndrome):**
- Occurs 1-2 weeks before period
- Symptoms: mood changes, bloating, breast tenderness, fatigue
✅ Regular exercise, reduce salt, caffeine, and alcohol
✅ Calcium and magnesium supplements
✅ Good sleep and stress management
✅ If severe (PMDD), see doctor

**When to See a Doctor:**
- Periods suddenly become very heavy or very painful
- Cycles become very irregular
- Periods stop for 3+ months (not pregnant)
- Severe pain that disrupts daily life (endometriosis?)
- Bleeding between periods

**Regular Screenings:**
- Smear test (cervical screening) as per national schedule
- Breast self-examination monthly
- STI testing if sexually active""",
        'type': 'info'
    },
    {
        'keys': ['medication', 'medicine', 'drug', 'side effect', 'antibiotic', 'painkiller', 'paracetamol', 'ibuprofen', 'prescription'],
        'response': """**Medication Safety & Guidance** 💊

**General Medication Safety Rules:**
✅ Always read the patient information leaflet
✅ Take medications at the prescribed time
✅ Complete the full course of antibiotics even if you feel better
✅ Never share your prescription medications
✅ Store medications properly (away from heat, moisture, children)
✅ Check expiry dates

**Common OTC Medications:**

**Paracetamol (Acetaminophen):**
- Max: 1g every 4-6 hours, max 4g/day
- Safe for most people including pregnancy
- Risk: Liver damage in overdose or with alcohol

**Ibuprofen (NSAID):**
- Take with food to protect stomach
- Avoid if: stomach ulcers, kidney disease, heart disease, pregnancy (3rd trimester)
- Max: 400mg every 6-8 hours

**Antibiotics:**
- Only work against bacteria, not viruses
- Never self-prescribe
- Complete the full course
- Common side effects: nausea, diarrhoea

**Drug Interactions to Watch:**
- Blood thinners + NSAIDs = increased bleeding risk
- Alcohol + many medications = dangerous
- Always tell your doctor ALL medications you take (including supplements)

**⚠️ Never Stop Prescribed Medication Without Consulting Your Doctor.**""",
        'type': 'info'
    },
    {
        'keys': ['book appointment', 'see a doctor', 'book a doctor', 'need a doctor', 'consult doctor', 'appointment'],
        'response': """**Booking a Doctor Appointment on Convofy** 📅

You can book an appointment with our verified doctors right here on Convofy!

**How to Book:**
1. Go to **Book Appointment** in your dashboard
2. Select your required specialty
3. Choose a convenient time slot
4. Enter your details
5. Confirm — you'll receive an email notification

**Available Specialties Include:**
🩺 General Physician
💊 Internal Medicine
🦴 Orthopaedics
🧠 Neurology
❤️ Cardiology
👶 Paediatrics
🧬 Dermatology
👁️ Ophthalmology
And many more...

**For Urgent Concerns:**
If this is an emergency, please call emergency services (911/112/999) or go to your nearest A&E department immediately.

**Video Consultations:**
Many of our doctors also offer video consultations via our built-in video call feature.

[→ Click here to Book an Appointment](/book-appointment)""",
        'type': 'info'
    },
    {
        'keys': ['thank', 'thanks', 'goodbye', 'bye', 'great', 'helpful', 'awesome'],
        'response': """**You're Welcome!** 😊

I'm glad I could help. Remember:

✅ Always follow the advice of your own doctor for personal medical decisions
✅ This AI provides general health information, not personalised diagnosis
✅ For any emergency, call **999 / 112 / 911** immediately

**Take care of yourself!** 💙

Is there anything else I can help you with today?""",
        'type': 'info'
    },
]

FALLBACK_RESPONSE = """**I'm here to help with health questions!** 🏥

I didn't quite understand your query, but I can assist with topics like:

🩺 **Symptoms** — fever, headache, cough, stomach pain, fatigue
💊 **Medications** — dosage, safety, side effects
🥗 **Nutrition** — healthy diet, vitamins, weight management
🏃 **Fitness** — exercise guidance, activity levels
🧠 **Mental Health** — stress, anxiety, depression support
🌡️ **Chronic Conditions** — diabetes, blood pressure, asthma
📅 **Booking** — how to book a doctor appointment

Could you rephrase your question? For example:
- "I have a headache and fever"
- "How do I manage diabetes?"
- "What foods should I eat to lose weight?"

For medical emergencies, please call **999 / 112 / 911** immediately."""


def generate_ai_response(message: str) -> dict:
    """
    Generate an AI health response for the given user message.
    Returns a dict with 'response' (str) and 'type' (str: 'emergency'|'warning'|'info').
    """
    msg = message.lower().strip()

    # Priority 1: Emergency detection
    for kw in EMERGENCY_KEYWORDS:
        if kw in msg:
            return {
                'response': """🚨 **EMERGENCY ALERT** 🚨

This sounds like a **potential medical emergency**.

**Please take immediate action:**
1. Call **emergency services — 911 / 112 / 999** NOW
2. Or go to your **nearest Emergency Room** immediately
3. If with someone, have them call while you focus on the patient

**Do NOT:**
- Wait to see if it gets better
- Drive yourself if you're the one affected
- Delay calling for help

⚠️ This AI assistant **cannot** provide emergency medical care. Every second matters — please get professional help immediately.

If you called the emergency number, stay on the line with the operator and follow their instructions.""",
                'type': 'emergency'
            }

    # Priority 2: Knowledge base matching
    for entry in HEALTH_KB:
        for key in entry['keys']:
            if key in msg:
                return {
                    'response': entry['response'],
                    'type': entry['type']
                }

    # Priority 3: Partial word matching for common health words
    health_words = {
        'heart': 'chest pain',
        'lung': 'asthma',
        'kidney': """**Kidney Health Information** 🫘

Your kidneys filter ~200 litres of blood daily. Here's how to keep them healthy:

**Signs of Kidney Problems:**
- Swelling in legs, ankles, feet, or face
- Decreased urine output or changes in colour
- Persistent fatigue
- Shortness of breath
- Nausea and vomiting
- High blood pressure that's hard to control

**Protecting Your Kidneys:**
✅ Stay well hydrated (2-3L water daily)
✅ Control blood pressure and diabetes
✅ Maintain healthy weight
✅ Exercise regularly
✅ Avoid excess salt, processed foods
✅ Limit OTC painkillers (NSAIDs) — they reduce kidney blood flow
✅ Don't smoke
✅ Limit alcohol

**Regular Checks:**
- Blood pressure monitoring
- Blood test: eGFR (kidney filtration rate), creatinine
- Urine test for protein (early sign of kidney damage)

Annual kidney function tests are recommended if you have diabetes, high blood pressure, or family history of kidney disease.""",
        'liver': """**Liver Health Information** 🫀

The liver performs 500+ vital functions. Protect it:

**Signs of Liver Issues:**
- Yellowing of skin or eyes (jaundice)
- Dark urine, pale stools
- Abdominal swelling or pain (upper right)
- Persistent fatigue
- Easy bruising or bleeding
- Itchy skin

**Liver Protection:**
✅ Limit alcohol (max 14 units/week, with 2+ alcohol-free days)
✅ Healthy weight (fatty liver disease is rising)
✅ Hepatitis B vaccination
✅ Safe sex practices (prevents Hepatitis B and C)
✅ Avoid sharing needles, razors, toothbrushes
✅ Be cautious with medications and supplements (acetaminophen in overdose is a top cause of liver failure)
✅ Regular exercise reduces fatty liver

**Common Liver Conditions:**
- Fatty liver disease (NAFLD) — linked to obesity, diabetes
- Hepatitis A, B, C — viral infections
- Cirrhosis — scarring from long-term damage

Regular liver function blood tests recommended if you're at risk.""",
    }

    for word, response_text in health_words.items():
        if word in msg:
            if isinstance(response_text, str) and len(response_text) > 20:
                return {'response': response_text, 'type': 'info'}
            else:
                # It's a redirect key
                for entry in HEALTH_KB:
                    for key in entry['keys']:
                        if response_text in key:
                            return {'response': entry['response'], 'type': entry['type']}

    # Fallback
    return {
        'response': FALLBACK_RESPONSE,
        'type': 'info'
    }
